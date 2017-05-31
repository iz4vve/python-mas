"""
This module simulates the behaviour of a ESX host.
A random component has been added to simulate random breaks in the machine.

Author: Pietro Mascolo
Email: pietro_mascolo@optum.com
"""
import json
import numpy as np
import random
import time
import uuid

import aiomas

# from util.tools import get_logger
import logging
LOG = logging.getLogger()#get_logger(__name__)

# mean and std of normal distribution
TELEMETRY_DISTRIBUTION_PARAMETERS = (70, 10)


class Host(object):

    def __init__(self, unique_id):
        self.unique_id = unique_id

    @staticmethod
    def telemetry():
        fields = ("cpu", "mem", "disk", "io", "temp", "fan")
        values = np.random.normal(
            *TELEMETRY_DISTRIBUTION_PARAMETERS, size=len(fields)
        )
        return zip(fields, values)

    def pong(self):
        return True if random.random() < 0.9999 else False  # there is a slim chance of non-pingability

    def ssh(self):
        return True if random.random() < 0.99 else False  # there is a slim chance of non-sshability

    def reboot(self):
        LOG.critical("Bouncing host %s", self.unique_id)


class Cluster(object):

    def __init__(self, unique_id):
        self.unique_id = unique_id
        # self.__hosts = dict()
        self.__hosts = set()
        self.__hosts_fields = ("cpu", "mem", "disk", "io", "temp", "fan")
        self.__callbacks = dict()
        self.__problems = dict()
        self.__agents = dict()
        self.__current_telemetry = dict()
        self.__threshold_high = 99
        self.__threshold_low = 5

    def register(self, name, callback):
        if name not in self.__callbacks:
            self.__callbacks[name] = callback

    def register_fixer(self, agent_type, agent_address):
        if agent_type not in self.__hosts:
            LOG.debug("Adding agent %s to cluster %s", agent_type, agent_address)
            self.__hosts[agent_type] = agent_address

    def add_host(self, host):
        # if host.unique_id not in self.__hosts:
        #     LOG.debug("Adding host %s to cluster %s", host.unique_id, self.unique_id)
        #     self.__hosts[host.unique_id] = host
        self.__hosts.add(host)

    # def pop_host(self, host_id):
    #     try:
    #         self.__hosts.pop(host_id)
    #     except KeyError:
    #         LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)

    def ping(self, host_id):
        return True if random.random() < 0.999 else False
        # try:
        #     return self.__hosts[host_id].pong()
        # except KeyError:
        #     LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)
        # except PingError:
        #     LOG.error("Cannot ping host %s in cluster %s", host_id, self.unique_id)
        #     return False
        # return False

    def ssh(self, host_id):
        return True if random.random() < 0.99 else False
        # try:
        #     return self.__hosts[host_id].pong()
        # except KeyError:
        #     LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)
        # except SSHError:
        #     LOG.error("Cannot ssh host %s in cluster %s", host_id, self.unique_id)
        #     return False
        # return False

    def collect_telemetry(self):
        self.__current_telemetry = {
            host_id: self.get_host_telemetry(host_id) for host_id in self.__hosts
        }
        # self.__current_telemetry = {
        #     host_id: host.telemetry() for host_id, host in self.__hosts.items()
        # }

    def get_host_telemetry(self, host_id):
        return zip(self.__hosts_fields, np.random.rand(len(self.__hosts_fields)))
        # try:
        #     return self.__hosts[host_id].telemetry()
        # except KeyError:
        #     LOG.error("Host %s is not in cluster %s", host_id, self.unique_id)
        # except TelemetryError:
        #     LOG.error("Cluster %s reports no telemetry available for host %s ", self.unique_id, host_id)
        #     return None
        # return None

    def check_telemetry(self):
        problems = []
        for host_id, telemetry in self.__current_telemetry.items():
            for key, value in telemetry:
                if value < self.__threshold_low or value > self.__threshold_high:
                    problems += [(host_id, key, value)]
            # problem = [(key, value) for key, value in telemetry if self.__threshold_low < value < self.__threshold_high]
            # if problem:
            #     problems += [(host_id, prbl) for prbl in 6]
        self.__problems = problems

    def handle_problems(self):
        # parse and send to fixers
        if not self.__problems:
            LOG.debug("No problems found in hosts in cluster %s", self.unique_id)
            return
        ##TODO handle problems

    def step_cluster(self):
        pass

class TelemetryError(Exception):
    pass

class SSHError(Exception):
    pass

class PingError(Exception):
    pass


class TestAgent(aiomas.Agent):

    @aiomas.expose
    async def asd(self):
        print("asdasdasd")


c = Cluster("clust01")

c.add_host(Host("host1"))
agents_container = aiomas.Container.create(('localhost', 5555))
agent = TestAgent(agents_container)

async def asd():
    callee = await agents_container.connect(agent.addr)

    result = await callee.asd()

aiomas.run(until=asd())
#
# class Host(object):
#     """
#     Simulates a host behaviour by random changes in the tracked metrics
#     This is just for show: it does NOT aim to be a realistic simulation of a
#     server.
#     """
#     def __init__(self, unique_id, cluster_id):
#         self._unique_id = unique_id
#         self.cluster_id = cluster_id
#         self.__threshold = 99
#         self.__min_threshold = 1
#
#         self.cpu = 0.0
#         self.mem = 0.0
#         self.disk = 0.0
#         self.fan = 0.0
#         self.io = 0.0
#         self.pingable = True
#         self.sshable = True
#
#         # properties to be checked
#         self.checks = ("cpu", "mem", "disk", "fan", "io")
#         self.bools = ("pingable", "sshable")
#
#     def __str__(self):
#         _repr = ", ".join(f"{i}={getattr(self, i)}" for i in self.checks)
#         _repr_bools = ", ".join(f"{i}={getattr(self, i)}" for i in self.bools)
#         return f"Host {self.unique_id}: {', '.join([_repr, _repr_bools])}"
#
#     @property
#     def unique_id(self):
#         return self._unique_id
#
#     def update_stats(self):
#         """
#         Random shifts in the host status
#         """
#         new_stats = [random.randint(0, 100) for i in range(len(self.checks))]
#         for attr, value in zip(self.checks, new_stats):
#             setattr(self, attr, value)
#
#         new_bools = [random.random() < 0.9999 for _ in self.bools]
#         for attr, value in zip(self.bools, new_bools):
#             setattr(self, attr, value)
#
#     def check_stats(self):
#         """
#         Checks if any value is an outlier wrt to host's thresholds
#         :return: outliers wrt host's thresholds
#         :rtype: list((metric_name, value))
#         """
#         values = [getattr(self, i) for i in self.checks]
#         bool_values = [getattr(self, i) for i in self.bools]
#
#         problems = [
#             (name, value) for name, value in zip(self.checks, values)
#             if not self.__min_threshold < value < self.__threshold
#         ] + [
#             (name, value) for name, value in zip(self.bools, bool_values)
#             if not value
#         ]
#
#         return problems
#
#     def step(self):
#         """
#         Updates status of the host
#         :return: outliers wrt host's thresholds
#         :rtype: list((metric_name, value))
#         """
#         self.update_stats()  # this would be telemetry collection in reality...
#         check = self.check_stats()
#
#         if check:
#             return check
#         return None
#
#
# class ClusterTelemetryAgent(aiomas.Agent):
#     """
#     Agent that monitors hosts in clusters and emits a "problem" event when a
#     host reports issues.
#     """
#     # mock cluster ids...
#     __possible_clusters = ("ESX0001", "ESX0002", "ESX0003")
#
#     def __init__(self, container, num_hosts, monitor_agent):
#         super().__init__(container)
#         self.num_hosts = num_hosts
#         self.monitor = monitor_agent
#         # self.cluster_id = cluster_id
#         self.hosts = [
#             Host(
#                 uuid.uuid4(),
#                 random.sample(self.__class__.__possible_clusters, 1)[0]
#             ) for _ in range(self.num_hosts)
#         ]
#         LOG.info(
#             f"Started {repr(self)}: {self.num_hosts} hosts in {len(self.hosts)} clusters"
#         )
#
#     def __repr__(self):
#         return f"Cluster Telemetry Agent {self.addr}"
#
#     def run_cluster(self):
#         """
#         Simulates periodic telemetry collection and checks for anomalies.
#         When anomalies occur, a fix request is sent to the handling agents.
#         """
#         while True:
#             time.sleep(1)  # TODO switch to async clock to simulate this
#                            # this currently gives synchronization problems
#                            # with respect to the queue of the agents
#             # await self.container.clock.sleep(1)
#             for host in random.sample(self.hosts, self.num_hosts):
#                 problems = host.step()
#
#                 if problems:  # async call to monitor handler
#                     aiomas.run(self.call_problem_solve(host, problems))
#
#     async def call_problem_solve(self, host, problems):
#         LOG.info(f"{repr(self)} detected a problem: host={host.unique_id}")
#         LOG.info(
#             f"{repr(self)} is sending problem report to Monitor Agent {repr(self.monitor)}"
#         )
#         callee = await self.container.connect(self.monitor.addr)
#
#         # need to broadcast host id and cluster id in a serializable way
#         host_json = json.dumps(
#             {
#                 "host": str(host.unique_id),
#                 "cluster_id": str(host.cluster_id),
#                 "telemetry_agent_address": self.addr
#             }
#         )
#
#         result = await callee.got_problem(host_json, problems)
