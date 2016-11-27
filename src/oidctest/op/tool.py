import logging

from oic.utils.http_util import Response

from otest import exception_trace
from otest import Trace
from otest.aus import tool
from otest.conversation import Conversation
from otest.aus.client import Factory

from oidctest.op import prof_util

__author__ = 'roland'

logger = logging.getLogger(__name__)


def get_redirect_uris(cinfo):
    """
    Used before there is a Conversation instance
    :param cinfo: Client Configuration Information
    :return: list of redirect_uris
    """
    try:
        return cinfo["registration_info"]["redirect_uris"]
    except KeyError:
        return cinfo["registration_response"]["redirect_uris"]


class Tester(tool.Tester):
    def __init__(self, io, sh, profiles, profile, flows=None,
                 msg_factory=None, cache=None, **kwargs):
        tool.Tester.__init__(self, io, sh, profiles, profile, flows,
                             msg_factory=msg_factory, cache=cache,
                             **kwargs)
        # self.chk_factory = get_check
        self.map_prof = prof_util.map_prof


class ClTester(tool.Tester):
    def __init__(self, io, sh, profiles, profile, flows=None,
                 msg_factory=None, cache=None, **kwargs):
        tool.Tester.__init__(self, io, sh, profiles, profile, flows,
                             msg_factory=msg_factory, cache=cache,
                             **kwargs)
        # self.chk_factory = get_check
        self.map_prof = prof_util.map_prof

    def match_profile(self, test_id):
        _spec = self.flows[test_id]
        return self.map_prof(self.profile, _spec["profile"])

    def run(self, test_id, **kw_args):
        if not self.match_profile(test_id):
            logger.info("Test doesn't match the profile")
            return True

        redirs = get_redirect_uris(kw_args['client_info'])

        self.sh.session_setup(path=test_id)
        _flow = self.flows[test_id]
        _cli, _c_info = kw_args['client_factory'].make_client(
            **kw_args['client_info'])
        self.conv = Conversation(_flow, _cli,
                                 msg_factory=kw_args["msg_factory"],
                                 callback_uris=redirs, trace_cls=Trace,
                                 opid=kw_args['opid'])
        _cli.conv = self.conv
        _cli.event_store = self.conv.events
        self.conv.entity_config = _c_info
        self.conv.sequence = self.sh["sequence"]
        self.conv.tool_config = kw_args['tool_conf']
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
                 msg_factory=None, cache=None, map_prof=None,
                 client_factory=None, **kwargs):
        tool.WebTester.__init__(self, io, sh, profiles=profiles,
                                profile=profile, flows=flows,
                                msg_factory=msg_factory, cache=cache, **kwargs)
        self.check_factory = check_factory
        self.client_factory = client_factory
        self.map_prof = map_prof or prof_util.map_prof

    def setup(self, test_id, **kw_args):
        redirs = get_redirect_uris(kw_args["client_info"])

        _flow = self.flows[test_id]
        _cli, _c_info = self.client_factory.make_client(
            **kw_args['client_info'])
        self.conv = Conversation(_flow, _cli, kw_args["msg_factory"],
                                 trace_cls=Trace, callback_uris=redirs)
        self.conv.entity_config = _c_info
        self.conv.tool_config = kw_args['tool_conf']
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
