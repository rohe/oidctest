from aatest.events import EV_SEND
from aatest.events import EV_REDIRECT_URL
from aatest.events import EV_HTTP_RESPONSE
from aatest.operation import Operation
from aatest.verify import Verify
from oic.utils import http_util

__author__ = 'roland'


class Response(Operation):
    endpoint = ''

    def __init__(self, conv, inut, sh, **kwargs):
        Operation.__init__(self, conv, inut, sh, **kwargs)
        self.expect_error = {}
        self.req_args = {}
        self.op_args = {}
        self.csi = None
        self.entity = self.conv.entity
        self.trace = self.conv.trace
        self.relay_state = ''
        self.request_id = ''
        self.response_args = {}
        self.request_inst = None

    def construct_message(self):
        return {}

    def handle_request(self, *args):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        if self.skip:
            return
        else:
            cls_name = self.__class__.__name__
            if self.tests["pre"] or self.tests["post"]:
                _ver = Verify(self.check_factory, self.conv, cls_name=cls_name)
                _ver.test_sequence(self.tests["pre"])

            self.conv.trace.info("Running '{}'".format(cls_name))

            res = self.run(*args, **kwargs)

            if res:
                return res

    def run(self, *args, **kwargs):
        #self.handle_request()
        send_args = self.construct_message()
        if isinstance(send_args, http_util.Response):
            return send_args

        self.conv.events.store(EV_SEND, send_args)
        self.conv.events.store(EV_REDIRECT_URL, send_args['url'])
        res = self.entity.send(**send_args)
        self.conv.events.store(EV_HTTP_RESPONSE, res)
        self.trace.info("Got a {} response".format(res.status_code))
        self.trace.info("Received HTML: {}".format(res.text))
        return res


class RedirectResponse(Response):
    _class = None
    _args = {}
    _method = 'GET'

    def run(self):
        self.handle_request()
        send_args = self.construct_message()
        if isinstance(send_args, Response):
            return send_args

        self.conv.events.store(EV_SEND, send_args)
        self.conv.events.store(EV_REDIRECT_URL, send_args['url'])
        res = self.entity.send(**send_args)
        self.conv.events.store(EV_HTTP_RESPONSE, res)
        self.trace.info("Got a {} response".format(res.status_code))
        self.trace.info("Received HTML: {}".format(res.text))
        return res
