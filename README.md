# MAS for ESX cluster monitoring and maintenance
###### ©2017 Pietro Mascolo - Released under licence GPLv3.

Simulation of a reactive monitoring system in a server cluster environment using asynchronous agents.

The package `environment` contains a simplistic simulation of telemetry collection 
from a mock `Host` class.  
Telemetry is collected by an agent defined in the module (`ClusterTelemetryAgent`).

When the agent detects and anomaly it emits a signal to a monitoring agent in the
package `agents`: `MonitorAgent`. The monitoring agent dispatches the collected messages to a 
`FixerAgent` that contains the logic to solve the problem detected in the host.
If the Fixer can find a solution, it submits it to a `Gatekeeper` - the only entity 
that should be able to send signals back into the cluster - which evaluates the feasibility
of the proposed solution. If the solution is deemed acceptable, it is invoked by the `Gatekeeper`.

Example basic usage:
```python
import aiomas
import environment.Env as Env
from agents.Agents import MonitorAgent, FixerAgent, GateKeeper

# instantiates containers and agents
cluster_container = aiomas.Container.create(("localhost", 5554))
agents_container = aiomas.Container.create(('localhost', 5555))

gatekeeper = GateKeeper(agents_container)
fixer = FixerAgent(agents_container, gatekeeper.addr)
monitor = MonitorAgent(agents_container, fixer.addr)

# instantiates mock telemetry agent
cluster = Env.ClusterTelemetryAgent(cluster_container, 10, monitor)

aiomas.run(until=cluster.run_cluster())

```

NOTE:  
The `pyswip` version available on pip has some incompatibility issues with Python 3.
[A different version][2] has been used in the project: instructions on how to install it can be found [here][1].



[1]: https://github.com/yuce/pyswip/blob/master/INSTALL.md
[2]: https://github.com/yuce/pyswip
