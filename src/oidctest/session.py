import copy
import logging
import aatest

from oidctest.oper import Done

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


class SessionHandler(aatest.SessionHandler):
    def __init__(self, session, profiles, profile, flows, operation, orddesc,
                 **kwargs):
        super(SessionHandler, self).__init__(profiles, profile, flows,
                                             operation, orddesc)
        self.session = session

    def session_setup(self, test_index, session=None, path="", index=0):
        logger.info("session_setup")
        if session is None:
            session = self.session
        _keys = session.keys()
        for key in _keys:
            if key.startswith("_"):
                continue
            elif key in ["tests", "flow_names", "response_type",
                         "test_info", "profile"]:  # don't touch !
                continue
            else:
                del session[key]

        session["testid"] = path
        nodes_found = 0
        for node in session["tests"]:
            if node.name == path:
                if nodes_found == test_index:
                    session["node"] = node
                    break
                nodes_found += 1

        flow = self.test_flows[path]
        if isinstance(flow, list):
            flow = flow[test_index]

        session["flow"] = flow
        session["sequence"] = copy.deepcopy(session["flow"]["sequence"])
        session["sequence"].append(Done)
        session["index"] = index
        self.session = session

    def init_session(self, session, profile=None):
        if profile is None:
            profile = self.profile

        f_names = self.test_flows.keys()
        f_names.sort()
        session["flow_names"] = []
        for k in self.orddesc:
            k += '-'
            l = [z for z in f_names if z.startswith(k)]
            session["flow_names"].extend(l)

        _tests =[]
        for k in session["flow_names"]:

            flows = self.test_flows[k]
            if isinstance(flows, dict):
                flows = [flows]

            for test in flows:
                try:
                    kwargs = {"mti": test["mti"]}
                except KeyError:
                    kwargs = {}
                _tests.append(Node(k, test["desc"], **kwargs))

        session["tests"] = _tests
        session["test_info"] = {}
        session["profile"] = profile
        self.session = session
        return session

    def reset_session(self, session=None, profile=None):
        if not session:
            session = self.session

        _keys = session.keys()
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
