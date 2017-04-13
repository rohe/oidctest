import logging

from otest import session


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
    def __init__(self, iss='', tag='', profile='', flows=None, order=None,
                 **kwargs):
        session.SessionHandler.__init__(self, profile=profile, flows=flows,
                                        order=order, **kwargs)
        self.iss = iss
        self.tag = tag

    def session_setup(self, path="", flow=None, index=0):
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
        if not flow:
            flow = self.test_flows.expanded_conf(path)

        self['flow'] = flow
        self["sequence"] = flow["sequence"]
        self["index"] = index

    def init_session(self, profile=None):
        if not profile:
            profile = self.profile
        else:
            self.profile = profile

        self["tests"] = self.test_flows.matches_profile(profile)
                                                        #self.extra['tool_conf'])
        self["profile"] = profile
        return session
