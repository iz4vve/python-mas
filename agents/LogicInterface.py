from pyswip.easy import *
from pyswip.prolog import Prolog


class SWIPInterface(object):
    __prolog = Prolog()
    __instance = None
    __knowledge = {
        "cpu": "agent_logic/cpu.pl",
        "mem": "agent_logic/mem.pl",
        "disk": "agent_logic/disk.pl",
        "io": "agent_logic/io.pl",
        "temp": "agent_logic/temp.pl",
        "fan": "agent_logic/fan.pl",
        "network": "agent_logic/network.pl"
    }

    # singleton
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self._get_knowledge()

    def _get_knowledge(self):
        for _, module_path in self.__knowledge.items():
            self.__prolog.consult(module_path)

"""
from pyswip.prolog import Prolog
# from pyswip.easy import registerForeign
from pyswip import newModule, Query
from pyswip.easy import *

# def requires_ping():
#     pass

prolog = Prolog()
module = newModule("/home/pmascolo/Projects/personal/python-mas/agents/agent_logic/cpu.pl")
prolog.consult("/home/pmascolo/Projects/personal/python-mas/agents/agent_logic/cpu.pl")
print("Query")
assertz = Functor("assertz")
underused = Functor("underused")
cpu = Functor("cpu", 2)
call(assertz(cpu("host1", 90)))
X = Variable()

q = Query(underused("host1"))
print(q.nextSolution())

"""