"""
Base agents for MAS demo.

Fixer Agents
------------
It reacts to requests coming from a Monitor Agent and verifies if it knows how
to handle the problem based on its registered callbacks. If it has an
appropriate handler for the problem, it then dispatches the callback to a
Gatekeeper Agent.

Each agent is specialised in handling a particular type of issue and should
only receive that

Gatekeeper Agent
----------------
It's the only agent that's supposed to push events to a cluster.
It receives requests for solutions to a problem from a Fixer Agent and
determines if the solution is feasible to implement.
It the solution is deemed feasible, it is implemented and sent to the cluster


Author: Pietro
Email: pietro_mascolo@optum.com
"""
import abc
import aiomas

from agents.LogicInterface import SWIPInterface
from util.tools import get_logger

LOG = get_logger(__name__)
LOGIC = SWIPInterface()


class BaseFixer(aiomas.Agent):

    def __init__(self, container, gatekeeper_address, cluster_monitor):
        super().__init__(container)
        # list of (cluster_id, host_id, problem_type, problem)
        self.__problems = list()
        self.__gatekeeper = gatekeeper_address
        self.__agents = dict()
        self.cluster_monitor = cluster_monitor
        self.__register_agents()

    def __register_agents(self):
        self.__agents = {
            "cpu": CpuFixer,
            "mem": MemFixer,
            "disk": DiskFixer,
            "io": IOFixer,
            "temp": TempFixer,
            "fan": FanFixer
        }

    def builder(self, agent_type):
        try:
            return self.__agents[agent_type]
        except KeyError:
            LOG.error("Invalid agent type: %s", agent_type)

    @abc.abstractmethod
    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        pass

    @abc.abstractmethod
    async def propose_fix(self, cluster_id, host_id):
        pass


class CpuFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class MemFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class DiskFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class IOFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class TempFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class FanFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class ConnectionFixer(BaseFixer):

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        print(self.__class__.__name__, cluster, host, problem)

    async def propose_fix(self, cluster_id, host_id):
        pass


class Gatekeeper(aiomas.Agent):
    """
    This extra layer is to ideally handle multiple similar requests
    so that the cluster monitor does not get flooded with the same request
    over and over.
    """

    def __init__(self, container, cluster_monitor):
        super().__init__(container)
        # it's not a pure queue, there will be random accesses
        self.__queue = list()
        self.monitor = cluster_monitor

    @aiomas.expose
    def flag_issue(self, cluster, host, problem):
        pass

    async def propose_fix(self, cluster_id, host_id):
        pass

    def is_feasible(self):
        # check queue
        pass
