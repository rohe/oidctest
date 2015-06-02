from oic.utils.http_util import Response

from aatest.check import ERROR
from aatest.check import OK
from aatest.check import WARNING

__author__ = 'roland'

INCOMPLETE = 4

TEST_RESULTS = {OK: "OK", ERROR: "ERROR", WARNING: "WARNING",
                INCOMPLETE: "INCOMPLETE"}

def get_profile_info(session, test_id=None):
    try:
        _conv = session["conv"]
    except KeyError:
        pass
    else:
        try:
            iss = _conv.client.provider_info["issuer"]
        except TypeError:
            iss = ""

        profile = to_profile(session, "dict")

        if test_id is None:
            try:
                test_id = session["testid"]
            except KeyError:
                return {}

        return {"Issuer": iss, "Profile": profile,
                "Test ID": test_id,
                "Test description": session["node"].desc,
                "Timestamp": in_a_while()}

    return {}

class Interface(object):
    def __init__(self, lookup, conf, test_flows, cache, test_profile,
                 profiles, test_class, check_factory, environ=None,
                 start_response=None):
        self.lookup = lookup
        self.conf = conf
        self.test_flows = test_flows
        self.cache = cache
        self.test_profile = test_profile
        self.profiles = profiles
        self.test_class = test_class
        self.check_factory = check_factory
        self.environ = environ
        self.start_response = start_response

    def store_test_info(self, session, profile_info=None):
        _info = {
            "trace": session["conv"].trace,
            "test_output": session["conv"].test_output,
            "index": session["index"],
            "seqlen": len(session["seq_info"]["sequence"]),
            "descr": session["node"].desc
        }

        try:
            _info["node"] = session["seq_info"]["node"]
        except KeyError:
            pass

        if profile_info:
            _info["profile_info"] = profile_info
        else:
            try:
                _info["profile_info"] = get_profile_info(session,
                                                         session["testid"])
            except KeyError:
                pass

        session["test_info"][session["testid"]] = _info

    def flow_list(self, session):
        resp = Response(mako_template="flowlist.mako",
                        template_lookup=self.lookup,
                        headers=[])

        try:
            _tid = session["testid"]
        except KeyError:
            _tid = None

        self.dump_log(session, _tid)

        argv = {
            "flows": session["tests"],
            "profile": session["profile"],
            "test_info": session["test_info"].keys(),
            "base": self.conf.BASE,
            "headlines": self.test_flows.DESC,
            "testresults": TEST_RESULTS
        }

        return resp(self.environ, self.start_response, **argv)
