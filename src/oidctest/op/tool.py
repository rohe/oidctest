import logging

from oic.utils.http_util import Response

from aatest import exception_trace
from aatest.conversation import Conversation

from oidctest.op import prof_util
from oidctest.op.client import make_client

from otest import Trace
from otest.aus import tool

__author__ = 'roland'

logger = logging.getLogger(__name__)


def get_redirect_uris(cinfo):
    try:
        return cinfo["client"]["redirect_uris"]
    except KeyError:
        return cinfo["registered"]["redirect_uris"]


class Tester(tool.Tester):
    def __init__(self, io, sh, profiles, profile, flows=None,
                 msg_factory=None, cache=None, **kwargs):
        tool.Tester.__init__(self, io, sh, profiles, profile, flows,
                             msg_factory=msg_factory, cache=cache,
                             **kwargs)
        # self.chk_factory = get_check
        self.map_prof = prof_util.map_prof


class ClTester(Tester):
    def run(self, test_id, **kw_args):
        if not self.match_profile(test_id):
            logger.info("Test doesn't match the profile")
            return True

        redirs = get_redirect_uris(kw_args['cinfo'])

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
            return self.run_flow(test_id, conf=kw_args["conf"])
        except Exception as err:
            exception_trace("", err, logger)
            # res = Result(self.sh, self.kwargs['profile_handler'])
            # res.print_info(test_id)
            return self.inut.err_response("run", err)


class WebTester(tool.WebTester):
    def __init__(self, io, sh, profiles, profile, flows, check_factory=None,
                 msg_factory=None, cache=None, map_prof=None, **kwargs):
        tool.WebTester.__init__(self, io, sh, profiles=profiles,
                                profile=profile, flows=flows,
                                msg_factory=msg_factory, cache=cache, **kwargs)
        self.check_factory = check_factory
        self.map_prof = map_prof or prof_util.map_prof

    def setup(self, test_id, cinfo, **kw_args):
        redirs = get_redirect_uris(cinfo)

        _flow = self.flows[test_id]
        _cli, _cli_conf = make_client(**kw_args)
        self.conv = Conversation(_flow, _cli, kw_args["msg_factory"],
                                 trace_cls=Trace, callback_uris=redirs)
        self.conv.entity_config = _cli_conf
        _cli.conv = self.conv
        _cli.event_store = self.conv.events
        self.sh.session_setup(path=test_id)
        self.sh["conv"] = self.conv
        self.conv.sequence = self.sh["sequence"]

    def run(self, test_id, **kw_args):
        self.setup(test_id, **kw_args)

        # noinspection PyTypeChecker
        try:
            return self.run_flow(test_id, conf=kw_args["conf"])
        except Exception as err:
            exception_trace("", err, logger)
            # self.inut.dump_log(self.sh, test_id)
            return self.inut.err_response("run", err)

    def handle_response(self, resp, index, oper=None):
        if resp:
            self.sh["index"] = index
            if isinstance(resp, Response):
                # self.conv.events.store(EV_HTTP_RESPONSE,
                #                        {'headers': resp.headers,
                #                         'status_code': resp.status})
                return resp(self.inut.environ, self.inut.start_response)
            else:
                return resp
        else:
            return None
