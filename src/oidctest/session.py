import copy
import logging
from aatest import session
from aatest.session import Done

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

    def session_setup(self, session=None, path="", index=0):
        logger.info("session_setup")
        if session is None:
            session = self.session
        _keys = list(session.keys())
        for key in _keys:
            if key.startswith("_"):
                continue
            elif key in ["tests", "flow_names", "response_type",
                         "test_info", "profile"]:  # don't touch !
                continue
            else:
                del session[key]

        session["testid"] = path
        for node in session["tests"]:
            if node.name == path:
                session["node"] = node
                break

        if "node" not in session:
            raise Exception("Unknown node name: {}".format(path))

        session["flow"] = self.test_flows[path]
        session["sequence"] = copy.deepcopy(session["flow"]["sequence"])
        session["sequence"].append(Done)
        session["index"] = index
        self.session = session

    def init_session(self, session, profile=None):
        if profile is None:
            profile = self.profile

        f_names = list(self.test_flows.keys())
        f_names.sort()
        session["flow_names"] = []
        for k in self.order:
            k += '-'
            l = [z for z in f_names if z.startswith(k)]
            session["flow_names"].extend(l)

        _tests =[]
        for k in session["flow_names"]:
            try:
                kwargs = {"mti": self.test_flows[k]["mti"]}
            except KeyError:
                kwargs = {}
            _tests.append(Node(k, self.test_flows[k]["desc"], **kwargs))

        session["tests"] = _tests
        session["test_info"] = {}
        session["profile"] = profile
        self.session = session
        return session

    def reset_session(self, session=None, profile=None):
        if not session:
            session = self.session

        _keys = list(session.keys())
        for key in _keys:
            if key.startswith("_"):
                continue
            else:
                del session[key]
        self.init_session(session, profile)

    def session_init(self, session=None):
        if not session:
            session = self.session

        if "tests" not in session:
            self.init_session(session)
            return True
        else:
            return False
