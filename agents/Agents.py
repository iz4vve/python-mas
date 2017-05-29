"""
Base agents for MAS demo.

MonitorAgent
------------
It monitors one or more ESX Clusters. It handles event sent by the
cluster when problems are detected.
It then requests a fix from a Fixer Agent and keeps listening for further events

Fixer Agent
-----------
It reacts to requests coming from a Monitor Agent and verifies if it knows how
to handle the problem based on its registered callbacks. If it has an
appropriate handler for the problem, it then dispatches the callback to a
Gatekeeper Agent

Gatekeeper Agent
----------------
It's the only agent that's supposed to push events to a cluster.
It receives requests for solutions to a problem from a Fixer Agent and
determines if the solution is feasible to implement.
It the solution is deemed feasible, it is implemented and sent to the cluster


Author: Pietro
Email: pietro_mascolo@optum.com
"""
import ctypes
import json
import random
import aiomas

from util.tools import get_logger

LOG = get_logger(__name__)


class BaseAgent(aiomas.Agent):
    """
    Base class for agents
    """

    def __init__(self, container):
        super().__init__(container)


class MonitorAgent(BaseAgent):
    """
    Agent that dispatches collected events to a Fixer to be resolved.
    """
    router = aiomas.rpc.Service()

    def __init__(self, container, fixer_agent_address):
        super().__init__(container)
        self.fixer_agent = fixer_agent_address

    def __repr__(self):
        return f"Monitor Agent {self.addr}"

    @aiomas.expose
    def got_problem(self, host, problem):
        """

        :param host: serialized representation of the host having problems
        :type host: json str
        :param problem: list of problems being experienced by the host
        :type problem: list((metric_name, value))
        """
        LOG.info(f"""Monitor Agent {self.addr} got problem from Cluster: 
                {json.loads(host).get('host')}, {problem}.""")
        LOG.info(f"Sending fixing request to Fixer Agent {self.fixer_agent}")
        aiomas.create_task(self.request_fix(host, problem))

    async def request_fix(self, host, request):
        """
        Async request to a Fixer agent to solve a problem

        :param host: serialized representation of the host having problems
        :param request: list of problems being experienced by the host
        :type request: list((metric_name, value))
        :return:
        """
        callee = await self.container.connect(self.fixer_agent)
        result = await callee.request_fix(host, request)


class FixerAgent(BaseAgent):
    """
    Agent that holds internal logic to fix problems a host may be experiencing

    This is where a solution is investigated to solve to problem
    """

    def __init__(self, container, gatekeeper_address):
        super().__init__(container)
        self.callback_functions = dict()
        self.gatekeeper = gatekeeper_address

    def __repr__(self):
        return f"Fixer agent {self.addr}"

    def register(self, name, callback):
        self.callback_functions[name] = callback

    def batch_register(self, callbacks_dict):
        for k, v in callbacks_dict.items():
            self.register(k, v)

    @aiomas.expose
    def get_callback(self, event):
        return self.callback_functions.get(event)

    @aiomas.expose
    def request_fix(self, host, problems):
        """
        Determines if an appropriate callback can solve the problem. If a
        callback is found, it is sent to a Gatekeeper Agent.

        NOTE:
        Since functions are not serializable as json stings, the object id is
        passed to the Gatekeeper.
        TODO: implement a codec to serialize functions and avoid this workaround

        :param host: serialized representation of the host having problems
        :type host: json str
        :param problems: list of problems being experienced by the host
        :type problems: list((metric_name, value))
        """

        for problem_type, problem in problems:
            LOG.info(
                f"""{repr(self)} sending fix request to 
                GateKeeper @ {self.gatekeeper}: Fix {problem_type}={problem}"""
            )
            callback = self.get_callback(problem_type)
            LOG.info(f"Checking for cached callback: {callback}")
            if not callback:
                LOG.warn(
                    "No approprate handler found for request %s.",
                    problem_type
                )
                LOG.warn("Dropping request")
            else:
                LOG.info(f"{repr(self)} has found a possible solution for ({problem_type}={problem})")
                LOG.info(f"{repr(self)} proposing solution to Gatekeeper @ {self.gatekeeper}")
                aiomas.create_task(
                    self.propose(host, (problem_type, problem), id(callback))
                )
                # TODO: implement codec for functions

    async def propose(self, host, request, solution):
        """
        Async call to implement the found solution.

        :param host: serialized representation of the host having problems
        :param request: Problem to solve (i.e. arguments for the callback)
        :type request: (metric, value)
        :param solution: id of the solution callback
        :type solution: int
        """
        callee = await self.container.connect(self.gatekeeper)
        result = await callee.check_solution(host, request, solution)


class GateKeeper(BaseAgent):
    """
    Agent that interacts with the environment (ESX clusters).
    It receives a proposed solution from a Fixer agent and decides whether
    the solution is feasible or not.

    If the solution is deemed feasible, the callbacks are executed.
    """

    @aiomas.expose
    def check_solution(self, host, request, solution):

        callback = ctypes.cast(solution, ctypes.py_object).value

        if self.is_feasible(callback):
            sol = self.apply_solution(host, request, callback)
        else:
            # drop request
            LOG.error(
                f"{repr(self)} got an unfeasible solution: {request}. Request will be ignored..."
            )

    def is_feasible(self, solution):
        """THIS IS JUST A MOCK FOR NOW!!!!"""
        return random.random() < 0.75

    def apply_solution(self, host, request, solution):
        return solution(host, request)
