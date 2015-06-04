import logging

from aatest import get_node, make_node

from oidctest.prof_util import flows
from oidctest.oper import Done

__author__ = 'roland'

logger = logging.getLogger(__name__)

class SessionHandler(object):
    def __init__(self, profiles, profile, test_flows, test_class, **kwargs):
        self.profiles = profiles
        self.profile = profile
        self.test_flows = test_flows
        self.test_class = test_class

    def session_setup(self, session, path, index=0):
        logger.info("session_setup")
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
        session["node"] = get_node(session["tests"], path)
        sequence_info = {
            "sequence": self.profiles.get_sequence(
                path, session["profile"], self.test_flows.FLOWS,
                self.profiles.PROFILEMAP, self.test_class.PHASES),
            "mti": session["node"].mti,
            "tests": session["node"].tests}
        sequence_info["sequence"].append((Done, {}))
        session["seq_info"] = sequence_info
        session["index"] = index
        session["response_type"] = ""

        return sequence_info, index

    def init_session(self, session, profile=None):
        if profile is None:
            profile = self.profile

        f_names = self.test_flows.FLOWS.keys()
        f_names.sort()
        session["flow_names"] = []
        for k in self.test_flows.ORDDESC:
            k += '-'
            l = [z for z in f_names if z.startswith(k)]
            session["flow_names"].extend(l)

        session["tests"] = [make_node(x, self.test_flows.FLOWS[x]) for x in
                            flows(profile, session["flow_names"],
                                  self.test_flows.FLOWS)]

        session["response_type"] = []
        session["test_info"] = {}
        session["profile"] = profile

    def reset_session(self, session, profile=None):
        _keys = session.keys()
        for key in _keys:
            if key.startswith("_"):
                continue
            else:
                del session[key]
        self.init_session(session, profile)

    def session_init(self, session):
        if "tests" not in session:
            self.init_session(session)
            return True
        else:
            return False
