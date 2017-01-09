import copy
import logging

from otest import Done
from otest import session
from otest.flow import match_usage
from otest.prof_util import prof2usage

from oidctest.prof_util import map_prof

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

        self["flow"] = self.test_flows.expanded_conf(path)
        self["sequence"] = self["flow"]["sequence"]
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
        for k in self["flow_names"]:
            _test = self.test_flows[k]
            if match_usage(_test["usage"], **prof2usage(profile[0])):
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
