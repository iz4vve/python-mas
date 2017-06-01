import sys
assert sys.version_info >= (3, 6), \
    "Python 3.6 (or above) is required to run the project"

import aiomas
import environment.Env as Env
from util.tools import get_logger

LOG = get_logger(__name__)
MONITOR = dict()


def main():
    global MONITOR
    cluster = Env.ClusterSimulator("ESX0001", MONITOR)
    cluster.add_host("host01")


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
