import logging
from oic.exception import IssuerMismatch, PyoidcError
import requests
import copy
from urlparse import parse_qs
from bs4 import BeautifulSoup

from requests.models import Response
from oic.oauth2.util import URL_ENCODED
from oic.oauth2 import ResponseError
from oic.utils.http_util import Redirect
from oic.utils.http_util import get_post
from oic.utils.time_util import utc_time_sans_frac
#from oictest.check import CheckEndpoint

from oidctest.oper import Operation
from oidctest.log import Log

__author__ = 'rolandh'

logger = logging.getLogger(__name__)

DUMMY_URL = "https://remove.this.url/"


class ErrorResponse(Exception):
    pass


class SyncRequest(Operation):
    request_cls = None
    method = ""
    module = ""
    content_type = URL_ENCODED
    response_cls = None
    response_where = "url"
    response_type = "urlencoded"
    accept = None
    _tests = {"post": [], "pre": []}

    def __init__(self, conv, session, test_id, conf, funcs, chk_factory):
        Operation.__init__(self, conv, session, test_id, conf, funcs,
                           chk_factory)
        self.conv.req = self
        self.tests = copy.deepcopy(self._tests)
        self.request = self.conv.msg_factory(self.request_cls)
        self.response = self.conv.msg_factory(self.response_cls)

    def do_request(self, client, url, body, ht_args):
        _trace = self.conv.trace
        response = client.http_request(url, method=self.method, data=body,
                                       **ht_args)

        _trace.reply("RESPONSE: %s" % response)
        _trace.reply("CONTENT: %s" % response.text)
        try:
            _trace.reply("REASON: %s" % response.reason)
        except AttributeError:
            pass
        if response.status_code in [301, 302]:
            _trace.reply("LOCATION: %s" % response.headers["location"])
        try:
            _trace.reply("COOKIES: %s" % requests.utils.dict_from_cookiejar(
                response.cookies))
        except AttributeError:
            _trace.reply("COOKIES: %s" % response.cookies)

        return response

    def handle_response(self, r, csi):
        r = self.conv.intermit(r)
        if 300 < r.status_code < 400:
            resp = self.conv.parse_request_response(
                r, self.response, body_type=self.response_type,
                state=self.conv.state, keyjar=self.conv.client.keyjar)
        elif r.status_code == 200:
            resp = self.response()
            if "response_mode" in csi and csi["response_mode"] == "form_post":
                forms = BeautifulSoup(r.content).findAll('form')
                for inp in forms[0].find_all("input"):
                    resp[inp.attrs["name"]] = inp.attrs["value"]
            else:
                r = self.conv.intermit(r)

            resp.verify(keyjar=self.conv.client.keyjar)
        else:
            resp = r

        if not isinstance(resp, Response):

            try:
                if not "kid" in resp["id_token"].jws_header and not resp["id_token"].jws_header["alg"] == "HS256":
                    for key, value in self.conv.client.keyjar.issuer_keys.iteritems():
                        if not key == "" and (len(value) > 1 or len(value[0].keys()) > 1):
                            raise PyoidcError("No 'kid' in id_token header!")

                if self.req_args['nonce'] != resp["id_token"]['nonce']:
                    raise ErrorResponse("invalid nonce! {} != {}".format(self.req_args['nonce'], resp["id_token"]['nonce']))
            except KeyError:
                pass

            try:
                if not same_issuer(self.conv.info["issuer"], resp["id_token"]["iss"]):
                    raise IssuerMismatch(" {} != {}".format(self.conv.info["issuer"], resp["id_token"]["iss"]))
                self.conv.client.id_token = resp["id_token"]
            except KeyError:
                pass

        return resp

    def run(self):
        _client = self.conv.client

        url, body, ht_args, csi = _client.request_info(
            self.request, method=self.method, request_args=self.req_args,
            target=_client.provider_info["issuer"],
            **self.op_args)

        try:
            http_args = self.op_args["http_args"]
        except KeyError:
            http_args = ht_args
        else:
            http_args.update(ht_args)

        self.conv.trace.info(20*"="+" "+self.__class__.__name__+" "+20*"=")
        self.conv.trace.request("URL: {}".format(url))
        if body:
            self.conv.trace.request("BODY: {}".format(body))
        response_msg = self.do_request(_client, url, body, http_args)

        response = self.handle_response(response_msg, csi)
        self.conv.trace.response(response)
        self.sequence.append((response, response_msg.text))

        return response


class AsyncRequest(Operation):
    request_cls = None
    method = ""
    module = ""
    content_type = URL_ENCODED
    response_cls = ""
    response_where = "url"
    response_type = "urlencoded"
    accept = None
    _tests = {"post": [], "pre": []}

    def __init__(self, conv, session, test_id, conf, funcs, chk_factory,
                 comcls=None):
        Operation.__init__(self, conv, session, test_id, conf, funcs,
                           chk_factory)
        self.conv.req = self
        self.trace = conv.trace
        self.tests = copy.deepcopy(self._tests)
        self.csi = None
        self.request = self.conv.msg_factory(self.request_cls)
        self.response = self.conv.msg_factory(self.response_cls)
        if comcls:
            self.com = comcls()
        else:
            self.com = Log

    def run(self):
        _client = self.conv.client
        _trace = self.conv.trace

        url, body, ht_args, csi = _client.request_info(
            self.request, method=self.method, request_args=self.req_args,
            **self.op_args)

        self.csi = csi

        _trace.info("redirect.url: %s" % url)
        _trace.info("redirect.header: %s" % ht_args)
        self.conv.timestamp.append((url, utc_time_sans_frac()))
        return Redirect(str(url))

    def parse_response(self, path, io, message_factory):
        _ctype = self.response_type
        _conv = self.conv

        if self.csi is None:
            url, body, ht_args, csi = _conv.client.request_info(
                self.request, method=self.method, request_args=self.req_args,
                **self.op_args)

            self.csi = csi

        try:
            response_mode = self.csi["response_mode"]
        except KeyError:
            response_mode = None

        # parse the response
        if response_mode == "form_post":
            info = parse_qs(get_post(io.environ))
            _ctype = "dict"
        elif self.response_where == "url":
            info = io.environ["QUERY_STRING"]
            _ctype = "urlencoded"
        else:  # resp_c.where == "body"
            info = get_post(io.environ)

        logger.info("Response: %s" % info)
        _conv.trace.reply(info)
        resp_cls = message_factory(self.response_cls)
        algs = _conv.client.sign_enc_algs("id_token")
        try:
            response = _conv.client.parse_response(
                resp_cls, info, _ctype,
                self.csi["state"],
                keyjar=_conv.client.keyjar, algs=algs)
        except ResponseError as err:
            return io.err_response(_conv, "run_sequence", err)
        except Exception as err:
            return io.err_response(_conv, "run_sequence", err)

        logger.info("Parsed response: %s" % response.to_dict())
        _conv.protocol_response.append((response, info))
        _conv.trace.response(response)


def same_issuer(issuer_A, issuer_B):
    if not issuer_A.endswith("/"):
        issuer_A += "/"
    if not issuer_B.endswith("/"):
        issuer_B += "/"
    return issuer_A == issuer_B


class SyncGetRequest(SyncRequest):
    method = "GET"


class AsyncGetRequest(AsyncRequest):
    method = "GET"


class SyncPostRequest(SyncRequest):
    method = "POST"


class SyncPutRequest(SyncRequest):
    method = "PUT"


class SyncDeleteRequest(SyncRequest):
    method = "DELETE"
