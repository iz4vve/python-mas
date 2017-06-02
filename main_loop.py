import sys
assert sys.version_info >= (3, 6), \
    "Python 3.6 (or above) is required to run the project"
import random
import threading
import time

import aiomas

import environment.Env as Env
import agents.Agents as agents
from util.tools import get_logger

LOG = get_logger(__name__)


class Monitor(dict):  # let's make dict thread-safe

    def __setitem__(self, key, value):
        with threading.Lock():
            super().__setitem__(key, value)

MONITOR = Monitor()


def run_cluster():
    global MONITOR
    ticker = 0
    while True:
        for _id, cluster in random.sample(MONITOR.items(), len(MONITOR)):
            ticker += 1
            time.sleep(.5)
            print("tick")
            cluster.step_cluster()
            if not ticker % 10:
                print("PING")
                cluster.ping_all()
            if not ticker % 30:
                print("SSH")
                cluster.test_ssh()


def main():
    global MONITOR

    # containers
    agents_container = aiomas.Container.create(("localhost", 5555))

    # cluster
    cluster = Env.ClusterSimulator("ESX0001", MONITOR, agents_container)
    cluster.add_host("host01")

    # agents instantiation
    gatekeeper = agents.Gatekeeper(agents_container, MONITOR)
    cpu_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)
    mem_fixer = agents.MemFixer(agents_container, gatekeeper.addr, MONITOR)
    disk_fixer = agents.DiskFixer(agents_container, gatekeeper.addr, MONITOR)
    io_fixer = agents.IOFixer(agents_container, gatekeeper.addr, MONITOR)
    temp_fixer = agents.TempFixer(agents_container, gatekeeper.addr, MONITOR)
    fan_fixer = agents.FanFixer(agents_container, gatekeeper.addr, MONITOR)
    connection_fixer = agents.ConnectionFixer(
        agents_container,
        gatekeeper.addr,
        MONITOR
    )

    # register agents to cluster
    cluster.register_fixer("cpu", cpu_fixer.addr)
    cluster.register_fixer("mem", mem_fixer.addr)
    cluster.register_fixer("disk", disk_fixer.addr)
    cluster.register_fixer("io", io_fixer.addr)
    cluster.register_fixer("temp", temp_fixer.addr)
    cluster.register_fixer("fan", fan_fixer.addr)
    cluster.register_fixer("connection", connection_fixer.addr)

    MONITOR[cluster.unique_id] = cluster

    try:
        aiomas.run(until=run_cluster())
    except KeyboardInterrupt:
        LOG.info("Received SIGKILL, shutting down...")


if __name__ == '__main__':
    import datetime
    start = datetime.datetime.now()
    LOG.info("Starting main event loop")
    main()
    LOG.info(
        "Main event loop terminated after: %s", datetime.datetime.now() - start
    )

###############################################################################
