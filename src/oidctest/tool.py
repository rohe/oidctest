import logging

from aatest import exception_trace
from aatest import Break
from aatest.check import State, ERROR
from aatest.conversation import Conversation
from aatest.events import EV_CONDITION
from aatest.io import eval_state
from aatest.summation import store_test_state
from aatest.verify import Verify
from aatest.session import Done

from oic.utils.http_util import Redirect
from oic.utils.http_util import Response
from oic.utils.http_util import get_post

from oidctest import CRYPTSUPPORT
from oidctest.check.oidc_check import OK

#from oidctest.conversation import Conversation
from oidctest.common import make_client
from oidctest.common import Trace
from oidctest.prof_util import map_prof
from oidctest.utils import get_check

__author__ = 'roland'

logger = logging.getLogger(__name__)

def get_redirect_uris(cinfo):
    try:
        return cinfo["client"]["redirect_uris"]
    except KeyError:
        return cinfo["registered"]["redirect_uris"]


class Tester(object):
    def __init__(self, io, sh, profiles, profile, flows,
                 msg_factory=None, cache=None, **kwargs):
        self.io = io
        self.sh = sh
        self.profiles = profiles
        self.profile = profile
        self.flows = flows
        self.check_factory = get_check
        self.message_factory = msg_factory
        self.cache = cache
        self.kwargs = kwargs
        self.conv = None

    def match_profile(self, test_id):
        _spec = self.flows[test_id]
        return map_prof(self.profile.split("."), _spec["profile"].split("."))

    def run(self, test_id, cinfo, **kw_args):
        if not self.match_profile(test_id):
            logger.info("Test doesn't match the profile")
            return True

        redirs = get_redirect_uris(cinfo)

        self.sh.session_setup(path=test_id)
        _flow = self.flows[test_id]
        (_cli, _reg_info) = make_client(**kw_args)
        self.conv = Conversation(_flow, _cli,
                                 msg_factory=kw_args["msg_factory"],
                                 callback_uris=redirs, trace_cls=Trace)
        _cli.conv = self.conv
        self.conv.sequence = self.sh["sequence"]
        self.sh["conv"] = self.conv

        # noinspection PyTypeChecker
        try:
            return self.run_flow(test_id, kw_args["conf"])
        except Exception as err:
            exception_trace("", err, logger)
            self.io.print_info(test_id)
            return self.io.err_response("run", err)

    def handle_response(self, resp, index):
        return None

    def run_flow(self, test_id, conf=None, index=0):
        logger.info("<=<=<=<=< %s >=>=>=>=>" % test_id)
        _ss = self.sh
        _ss["node"].complete = False
        self.conv.test_id = test_id
        self.conv.conf = conf

        if index >= len(self.conv.sequence):
            return None

        _oper = None
        for item in self.conv.sequence[index:]:
            if isinstance(item, tuple):
                cls, funcs = item
            else:
                cls = item
                funcs = {}

            logger.info("<--<-- {} --- {} -->-->".format(index, cls))
            try:
                _oper = cls(conv=self.conv, inut=self.io, sh=self.sh,
                            profile=self.profile, test_id=test_id, conf=conf,
                            funcs=funcs, check_factory=self.check_factory,
                            cache=self.cache)
                self.conv.operation = _oper
                _oper.setup(self.profiles.PROFILEMAP)
                resp = _oper()
            except Exception as err:
                self.conv.events.store(
                    EV_CONDITION,
                    State(test_id=test_id, status=ERROR, message=err,
                          context=cls.__name__))
                exception_trace(cls.__name__, err, logger)
                self.sh["index"] = index
                return self.io.err_response("run_sequence", err)
            else:
                if resp:
                    resp = self.handle_response(resp, index)
                    if resp:
                        return self.io.respond(resp)

            index += 1

        try:
            if self.conv.flow["tests"]:
                _ver = Verify(self.check_factory, self.conv)
                _ver.test_sequence(self.conv.flow["tests"])
        except KeyError:
            pass
        except Exception as err:
            raise

        if isinstance(_oper, Done):
            self.conv.events.store(EV_CONDITION,
                                   State(test_id='Done', status=OK))

        store_test_state(_ss, _ss['conv'].events)

        if eval_state(self.conv.events) == OK:
            return True
        else:
            return False


class ClTester(Tester):
    pass


class WebTester(Tester):
    def display_test_list(self):
        try:
            if self.sh.session_init():
                return self.io.flow_list()
            else:
                try:
                    resp = Redirect("%sopresult#%s" % (
                        self.io.conf.BASE, self.sh["testid"][0]))
                except KeyError:
                    return self.io.flow_list()
                else:
                    return resp(self.io.environ, self.io.start_response)
        except Exception as err:
            exception_trace("display_test_list", err)
            return self.io.err_response("session_setup", err)

    def set_profile(self, environ):
        info = parse_qs(get_post(environ))
        try:
            cp = self.sh["profile"].split(".")
            cp[0] = info["rtype"][0]

            crsu = []
            for name, cs in list(CRYPTSUPPORT.items()):
                try:
                    if info[name] == ["on"]:
                        crsu.append(cs)
                except KeyError:
                    pass

            if len(cp) == 3:
                if len(crsu) == 3:
                    pass
                else:
                    cp.append("".join(crsu))
            else:  # len >= 4
                cp[3] = "".join(crsu)

            try:
                if info["extra"] == ['on']:
                    if len(cp) == 3:
                        cp.extend(["", "+"])
                    elif len(cp) == 4:
                        cp.append("+")
                    elif len(cp) == 5:
                        cp[4] = "+"
                else:
                    if len(cp) == 5:
                        cp = cp[:-1]
            except KeyError:
                if len(cp) == 5:
                    cp = cp[:-1]

            # reset all test flows
            self.sh.reset_session(profile=".".join(cp))
            return self.io.flow_list()
        except Exception as err:
            return self.io.err_response("profile", err)

    def _setup(self, test_id, cinfo, **kw_args):
        redirs = get_redirect_uris(cinfo)

        _flow = self.flows[test_id]
        _cli, _cli_conf = make_client(**kw_args)
        self.conv = Conversation(_flow, _cli, kw_args["msg_factory"],
                                 trace_cls=Trace, callback_uris=redirs)
        self.conv.entity_config = _cli_conf
        _cli.conv = self.conv
        self.sh.session_setup(path=test_id)
        self.sh["conv"] = self.conv
        self.conv.sequence = self.sh["sequence"]

    def run(self, test_id, cinfo, **kw_args):
        self._setup(test_id, cinfo, **kw_args)

        # noinspection PyTypeChecker
        try:
            return self.run_flow(test_id, kw_args["conf"])
        except Exception as err:
            exception_trace("", err, logger)
            #self.io.dump_log(self.sh, test_id)
            return self.io.err_response("run", err)

    def handle_response(self, resp, index):
        if resp:
            self.sh["index"] = index
            if isinstance(resp, Response):
                self.conv.events.store(EV_HTTP_RESPONSE, resp)
                return resp(self.io.environ, self.io.start_response)
            else:
                return resp
        else:
            return None

    def run_flow(self, test_id, conf=None, index=0):
        logger.info("<=<=<=<=< %s >=>=>=>=>" % test_id)
        _ss = self.sh
        _ss["node"].complete = False
        self.conv.test_id = test_id
        self.conv.conf = conf

        if index >= len(self.conv.sequence):
            return None

        _oper = None
        for item in self.conv.sequence[index:]:
            self.sh["index"] = index
            if isinstance(item, tuple):
                cls, funcs = item
            else:
                cls = item
                funcs = {}

            logger.info("<--<-- {} --- {} -->-->".format(index, cls))
            try:
                _oper = cls(conv=self.conv, io=self.io, sh=self.sh,
                            profile=self.profile,
                            test_id=test_id, conf=conf, funcs=funcs,
                            check_factory=self.check_factory, cache=self.cache)
                self.conv.operation = _oper
                _oper.setup(self.profiles.PROFILEMAP)
                resp = _oper()
            except Break:
                break
            except Exception as err:
                return self.io.err_response("run_sequence", err)
            else:
                rsp = self.handle_response(resp, index)
                if rsp:
                    return self.io.respond(rsp)

            index += 1

        try:
            if self.conv.flow["tests"]:
                print(">>", self.check_factory)
                _ver = Verify(self.check_factory, self.conv)
                _ver.test_sequence(self.conv.flow["tests"])
        except KeyError:
            pass
        except Exception as err:
            raise

        if isinstance(_oper, Done):
            self.conv.events.store(EV_CONDITION,
                                   State(test_id='done', status=OK))

        self.sh['node'].complete = True
        self.sh['node'].state = eval_state(self.conv.events)

    def cont(self, environ, ENV):
        query = parse_qs(environ["QUERY_STRING"])
        path = query["path"][0]
        index = int(query["index"][0])

        try:
            index = self.sh["index"]
        except KeyError:  # Cookie delete broke session
            self._setup(path, **ENV)
        except Exception as err:
            return self.io.err_response("session_setup", err)
        else:
            self.conv = self.sh["conv"]

        index += 1

        try:
            return self.run_flow(path, ENV["conf"], index)
        except Exception as err:
            exception_trace("", err, logger)
            self.io.print_info(path)
            return self.io.err_response("run", err)

    def async_response(self, conf):
        index = self.sh["index"]
        item = self.sh["sequence"][index]
        self.conv = self.sh["conv"]

        if isinstance(item, tuple):
            cls, funcs = item
        else:
            cls = item

        logger.info("<--<-- {} --- {}".format(index, cls))
        resp = self.conv.operation.parse_response(self.sh["testid"],
                                                  self.io, self.message_factory)
        if resp:
            return resp

        index += 1

        return self.run_flow(self.sh["testid"], index=index)