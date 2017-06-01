import os
from pyswip.easy import *
from pyswip.prolog import Prolog

from util.tools import get_logger
LOG = get_logger(__name__)


class SWIPInterface(object):
    __prolog = Prolog()
    __instance = None
    __knowledge = {
        "cpu": "agents/agent_logic/cpu.pl",
        "mem": "agents/agent_logic/mem.pl",
        "disk": "agents/agent_logic/disk.pl",
        "io": "agents/agent_logic/io.pl",
        "temp": "agents/agent_logic/temp.pl",
        "fan": "agents/agent_logic/fan.pl",
        "network": "agents/agent_logic/network.pl"
    }

    # singleton
    def __new__(cls):
        if cls.__instance is None:
            LOG.info("Instantiating interface layer for LOGIC")
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self._get_knowledge()

    def _get_knowledge(self):
        cwd = os.getcwd()
        for _, module_path in self.__knowledge.items():
            knowledge = os.path.join(cwd, module_path)
            LOG.info("Gaining knowledge from %s", knowledge)
            self.__prolog.consult(knowledge)

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