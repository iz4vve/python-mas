"""
This module simulates the behaviour of a ESX host.
A random component has been added to simulate random breaks in the machine.

Author: Pietro Mascolo
Email: pietro_mascolo@optum.com
"""
import numpy as np
import random

import aiomas

from util.tools import get_logger
LOG = get_logger(__name__)

# mean and std of normal distribution
TELEMETRY_DISTRIBUTION_PARAMETERS = (70, 10)


class Host(object):

    def __init__(self, unique_id):
        self.unique_id = unique_id
        self.fields = ("cpu", "mem", "disk", "io", "temp", "fan")
        self.initialize_metrics()

    def initialize_metrics(self):
        for metric in self.fields:
            setattr(self, metric, 0.0)

    def telemetry(self):
        values = np.random.normal(
            *TELEMETRY_DISTRIBUTION_PARAMETERS, size=len(self.fields)
        )
        for metric, value in zip(self.fields, values):
            setattr(self, metric, value)
        return zip(self.fields, values)

    @staticmethod
    def pong():
        # there is a slim chance of non-pingability
        return True if random.random() < 0.9999 else False

    @staticmethod
    def ssh_ack():
        # there is a slim chance of non-sshability
        return True if random.random() < 0.99 else False

    def reboot(self):
        LOG.critical("Bouncing host %s", self.unique_id)


class ClusterSimulator(object):

    def __init__(self, unique_id, monitor, agents_container):
        self.unique_id = unique_id
        self.__hosts = dict()
        self.__callbacks = dict()
        self.__problems = dict()
        self.__agents = dict()
        self.__current_telemetry = dict()
        self.__threshold_high = 90
        self.__threshold_low = 5
        self.agents_container = agents_container
        self.monitor = monitor

    def register(self, name, callback):
        if name not in self.__callbacks:
            self.__callbacks[name] = callback

    def setup_monitor(self):
        self.monitor[self.unique_id] = self

    def register_fixer(self, agent_type, agent_address):
        if agent_type not in self.__agents:
            LOG.debug(
                "Adding agent %s to cluster %s", agent_type, agent_address
            )
            self.__agents[agent_type] = agent_address

    def add_host(self, host_id):
        if host_id not in self.__hosts:
            LOG.debug("Adding host %s to cluster %s",host_id, self.unique_id)
            self.__hosts[host_id] = Host(host_id)

    def pop_host(self, host_id):
        try:
            self.__hosts.pop(host_id)
        except KeyError:
            LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)

    def ping(self, host_id):
        try:
            return self.__hosts[host_id].pong()
        except KeyError:
            LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)
        except PingError:
            LOG.error(
                "Cannot ping host %s in cluster %s", host_id, self.unique_id
            )
            return False
        return False

    def ssh(self, host_id):
        try:
            return self.__hosts[host_id].ssh_ack()
        except KeyError:
            LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)
        except SSHError:
            LOG.error(
                "Cannot ssh host %s in cluster %s", host_id, self.unique_id
            )
            return False
        return False

    def collect_telemetry(self):
        self.__current_telemetry = {
            host_id: host.telemetry()
            for host_id, host in random.sample(
                self.__hosts.items(), len(self.__hosts)
            )
        }

    def get_host_telemetry(self, host_id):
        try:
            return self.__hosts[host_id].telemetry()
        except KeyError:
            LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)
        except TelemetryError:
            LOG.error(
                "Cluster %s reports no telemetry available for host %s ",
                self.unique_id,
                host_id
            )
            return None
        return None

    def check_telemetry(self):
        problems = []
        for host_id, telemetry in self.__current_telemetry.items():
            for key, value in telemetry:
                if value < self.__threshold_low or value > self.__threshold_high:
                    prbl = [(host_id, key, max(value, 100))]
                    problems += prbl
                    # the distribution can technically go ever 100...
                    LOG.warning(
                        "Problem detected in cluster %s: %s",
                        self.unique_id,
                        prbl
                    )
        self.__problems = problems

    def get_agent(self, agent_type):
        return self.__agents[agent_type]

    def handle_problems(self):
        # parse and send to fixers
        if not self.__problems:
            LOG.debug(
                "No problems found in hosts in cluster %s", self.unique_id
            )
            return
        # send report to agents
        for host_id, problem_type, problem in self.__problems:
            try:
                agent = self.get_agent(problem_type)
                aiomas.run(self.flag_problem(agent, host_id, problem))
            except KeyError:
                LOG.error(
                    "ERROR: agent %s not registered in cluster %s.",
                    problem_type,
                    self.unique_id
                )
        # TODO handle problems

    async def flag_problem(self, _agent, host_id, problem):
        agent = await self.agents_container.connect(_agent)
        res = await agent.flag_issue(self.unique_id, host_id, problem)

    def step_cluster(self):
        self.collect_telemetry()
        self.check_telemetry()
        self.handle_problems()

    def ping_all(self):
        unpingable = filter(
            lambda x: not x[1],
            [(host_id, self.ping(host_id)) for host_id in self.__hosts]
        )
        for host_id, ping in unpingable:
            aiomas.run(self.flag_unpingable(host_id))

    async def ping_request(self, host_id):
        try:
            return self.__hosts[host_id].pong()
        except KeyError:
            LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)

    def test_ssh(self):
        not_sshable = filter(
            lambda x: not x[1],
            [(host_id, self.ping(host_id)) for host_id in self.__hosts]
        )
        for host_id, ssh in not_sshable:
            aiomas.run(self.flag_not_sshable(host_id))

    async def flag_unpingable(self, host_id):
        try:
            agent = await self.agents_container.connect(
                self.__agents["connection"]
            )
        except KeyError:
            LOG.error("ERROR: No network agent in cluster %s", self.unique_id)
        else:
            res = await agent.flag_issue(self.unique_id, host_id, "ping")

    async def flag_not_sshable(self, host_id):
        try:
            agent = await self.agents_container.connect(
                self.__agents["connection"]
            )
        except KeyError:
            LOG.error("ERROR: No network agent in cluster %s", self.unique_id)
        else:
            res = await agent.flag_issue(self.unique_id, host_id, "ssh")

    @staticmethod
    async def bounce(host_id):
        ret = ("Host %s bounced" if random.random < 0.9
               else "Host %s not bounced: solution not feasible")
        LOG.info(ret, host_id)
        # TODO add similar methods to cope with other issues


class TelemetryError(Exception):
    pass


class SSHError(Exception):
    pass


class PingError(Exception):
    pass
