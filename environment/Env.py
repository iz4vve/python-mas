"""
This module simulates the behaviour of a ESX host.
A random component has been added to simulate random breaks in the machine.

Author: Pietro Mascolo
Email: pietro_mascolo@optum.com
"""
import json
import random
import time
import uuid

import aiomas

from util.tools import get_logger

LOG = get_logger(__name__)


class Host(object):
    """
    Simulates a host behaviour by random changes in the tracked metrics
    This is just for show: it does NOT aim to be a realistic simulation of a
    server.
    """
    def __init__(self, unique_id, cluster_id):
        self._unique_id = unique_id
        self.cluster_id = cluster_id
        self.__threshold = 99
        self.__min_threshold = 5

        self.cpu = 0.0
        self.mem = 0.0
        self.disk = 0.0
        self.fan = 0.0
        self.io = 0.0
        self.pingable = True
        self.sshable = True

        # properties to be checked
        self.checks = ("cpu", "mem", "disk", "fan", "io")
        self.bools = ("pingable", "sshable")

    def __str__(self):
        _repr = ", ".join(f"{i}={getattr(self, i)}" for i in self.checks)
        _repr_bools = ", ".join(f"{i}={getattr(self, i)}" for i in self.bools)
        return f"Host {self.unique_id}: {', '.join([_repr, _repr_bools])}"

    @property
    def unique_id(self):
        return self._unique_id

    def update_stats(self):
        """
        Random shifts in the host status
        """
        new_stats = [random.randint(0, 100) for i in range(len(self.checks))]
        for attr, value in zip(self.checks, new_stats):
            setattr(self, attr, value)

        new_bools = [random.random() < 0.9999 for _ in self.bools]
        for attr, value in zip(self.bools, new_bools):
            setattr(self, attr, value)

    def check_stats(self):
        """
        Checks if any value is an outlier wrt to host's thresholds
        :return: outliers wrt host's thresholds
        :rtype: list((metric_name, value))
        """
        values = [getattr(self, i) for i in self.checks]
        bool_values = [getattr(self, i) for i in self.bools]

        problems = [
            (name, value) for name, value in zip(self.checks, values)
            if value > self.__threshold or value < self.__min_threshold
        ] + [
            (name, value) for name, value in zip(self.bools, bool_values)
            if not value
        ]

        return problems

    def step(self):
        """
        Updates status of the host
        :return: outliers wrt host's thresholds
        :rtype: list((metric_name, value))
        """
        self.update_stats()  # this would be telemetry collection in reality...
        check = self.check_stats()

        if check:
            return check
        return None


class ClusterTelemetryAgent(aiomas.Agent):
    """
    Agent that monitors hosts in clusters and emits a "problem" event when a
    host reports issues.
    """
    # mock cluster ids...
    __possible_clusters = ("ESX0001", "ESX0002", "ESX0003")

    def __init__(self, container, num_hosts, monitor_agent):
        super().__init__(container)
        self.num_hosts = num_hosts
        self.monitor = monitor_agent
        # self.cluster_id = cluster_id
        self.hosts = [
            Host(
                uuid.uuid4(),
                random.sample(self.__class__.__possible_clusters, 1)
            ) for _ in range(self.num_hosts)
        ]

    def __repr__(self):
        return f"Cluster Agent {self.cluster_id}@{self.addr}"

    def run_cluster(self):
        while True:
            time.sleep(1)  # TODO switch to async clock to simulate this
                           # this currently gives synchronization problems
                           # with respect to the queue of the agents
            # await self.container.clock.sleep(1)
            for host in random.sample(self.hosts, self.num_hosts):
                problems = host.step()

                if problems:  # async call to monitor handler
                    aiomas.run(self.call_problem_solve(host, problems))

    async def call_problem_solve(self, host, problems):
        LOG.info(f"{repr(self)} detected a problem: host={host.unique_id}")
        LOG.info(
            f"{repr(self)} is sending problem report to Monitor Agent {repr(self.monitor)}"
        )
        callee = await self.container.connect(self.monitor.addr)

        # need to broadcast host id and cluster id in a serializable way
        host_json = json.dumps(
            {
                "host": str(host.unique_id),
                "cluster_id": str(host.cluster_id),
                "cluster_address": self.addr
            }
        )

        result = await callee.got_problem(host_json, problems)
