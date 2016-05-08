import copy
import logging

from aatest import session
from aatest.session import Done

from oidctest.op.prof_util import map_prof

__author__ = 'roland'

logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self, name, desc, mti=None):
        self.name = name
        self.desc = desc
        self.mti = mti
        self.state = 0
        self.info = ""
        self.rmc = False
        self.experr = False
        self.complete = False


class SessionHandler(session.SessionHandler):
    def session_setup(self, path="", index=0):
        logger.info("session_setup")

        _keys = list(self.keys())
        for key in _keys:
            if key.startswith("_"):
                continue
            elif key in ["tests", "flow_names", "response_type",
                         "test_info", "profile"]:  # don't touch !
                continue
            else:
                del self[key]

        self["testid"] = path
        for node in self["tests"]:
            if node.name == path:
                self["node"] = node
                break

        if "node" not in self:
            raise Exception("Unknown node name: {}".format(path))

        self["flow"] = self.test_flows[path]
        self["sequence"] = copy.deepcopy(self["flow"]["sequence"])
        self["sequence"].append(Done)
        self["index"] = index
        self.session = session

    def init_session(self, profile=None):
        if not profile:
            profile = self.profile

        f_names = list(self.test_flows.keys())
        f_names.sort()
        self["flow_names"] = []
        for k in self.order:
            k += '-'
            l = [z for z in f_names if z.startswith(k)]
            self["flow_names"].extend(l)

        _tests = []
        _sprof = profile.split(".")
        for k in self["flow_names"]:
            _test = self.test_flows[k]
            if map_prof(_sprof, _test["profile"].split(".")):
                try:
                    kwargs = {"mti": _test["mti"]}
                except KeyError:
                    kwargs = {}
                _tests.append(Node(k, _test["desc"], **kwargs))

        self["tests"] = _tests
        self["test_info"] = {}
        self["profile"] = profile
        self.session = session
        return session
