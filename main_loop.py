import sys
assert sys.version_info >= (3, 6), \
    "Python 3.6 (or above) is required to run the project"
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
    for cluster in MONITOR:
        time.sleep(1)
        cluster.step_cluster()


def main():
    global MONITOR
    cluster = Env.ClusterSimulator("ESX0001", MONITOR)
    cluster.add_host("host01")

    # containers
    agents_container = aiomas.Container.create(("localhost", 5555))

    # agents instantiation
    gatekeeper = agents.Gatekeeper(agents_container)
    cpu_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)
    mem_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)
    disk_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)
    io_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)
    temp_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)
    fan_fixer = agents.CpuFixer(agents_container, gatekeeper.addr, MONITOR)

    # register agents to cluster
    cluster.register_fixer("cpu", cpu_fixer.addr)
    cluster.register_fixer("mem", mem_fixer.addr)
    cluster.register_fixer("disk", disk_fixer.addr)
    cluster.register_fixer("io", io_fixer.addr)
    cluster.register_fixer("temp", temp_fixer.addr)
    cluster.register_fixer("fan", fan_fixer.addr)






# def main():
#     num_hosts = 10000
#
#     cluster_container = aiomas.Container.create(("localhost", 5554))
#     agents_container = aiomas.Container.create(('localhost', 5555))
#
#     gatekeeper = GateKeeper(agents_container)
#     fixer = FixerAgent(agents_container, gatekeeper.addr)
#     monitor = MonitorAgent(agents_container, fixer.addr)
#
#     callbacks = {
#         "cpu": callback.cpu,
#         "mem": callback.mem,
#         "disk": callback.disk,
#         "fan": callback.cpu,
#         "io": callback.io,
#         "pingable": callback.not_pingable,
#         "sshable": callback.not_sshable
#     }
#     fixer.batch_register(callbacks)
#
#     cluster = Env.ClusterTelemetryAgent(cluster_container, num_hosts, monitor)
#
#     try:
#         LOG.info("Spawning agents")
#         LOG.info(f"Starting Telemetry Agent: {repr(cluster)}")
#         aiomas.run(until=cluster.run_cluster())
#     except KeyboardInterrupt:
#         LOG.info("Received SIGKILL, shutting down gently...")


###############################################################################
if __name__ == '__main__':
    main()
