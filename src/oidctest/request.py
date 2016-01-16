import logging
from aatest import Break
import requests
import copy
from six.moves.urllib.parse import parse_qs
# from urllib.parse import parse_qs
from bs4 import BeautifulSoup

from oic.exception import IssuerMismatch
from oic.exception import PyoidcError
from requests.models import Response
from oic.oauth2 import ErrorResponse
from oic.oauth2 import ResponseError
from oic.oauth2.util import URL_ENCODED
from oic.utils.http_util import Redirect
from oic.utils.http_util import get_post
from oic.utils.time_util import utc_time_sans_frac
# from oictest.check import CheckEndpoint

from oidctest.oper import Operation
from oidctest.log import Log

__author__ = 'rolandh'

logger = logging.getLogger(__name__)

DUMMY_URL = "https://remove.this.url/"


class ParameterError(Exception):
    pass


class Request(Operation):
    def expected_error_response(self, response):
        if isinstance(response, Response):  # requests response
            # don't want bytes
            _txt = response.content.decode('utf8')
            response = ErrorResponse().from_json(_txt)

        if isinstance(response, ErrorResponse):
            self.conv.events.store("protocol_response", response)
            if response["error"] not in self.expect_error["error"]:
                raise Break("Wrong error, got {} expected {}".format(
                    response["error"], self.expect_error["error"]))
            try:
                if self.expect_error["stop"]:
                    raise Break("Stop requested after received expected error")
            except KeyError:
                pass
        else:
            self.conv.trace.error("Expected error, didn't get it")
            raise Break("Did not receive expected error")

        return response


class SyncRequest(Request):
    request_cls = None
    method = ""
    module = ""
    content_type = URL_ENCODED
    response_cls = None
    response_where = "url"
    response_type = "urlencoded"
    accept = None
    _tests = {"post": [], "pre": []}

    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)
        self.conv.req = self
        self.tests = copy.deepcopy(self._tests)
        self.request = self.conv.msg_factory(self.request_cls)
        self.response = self.conv.msg_factory(self.response_cls)

    def do_request(self, client, url, body, ht_args):
        _trace = self.conv.trace
        response = client.http_request(url, method=self.method, data=body,
                                       **ht_args)

        self.conv.events.store("http_response", response)
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
                state=self.conv.state, keyjar=self.conv.entity.keyjar)
        elif r.status_code == 200:
            resp = self.response()
            if "response_mode" in csi and csi["response_mode"] == "form_post":
                forms = BeautifulSoup(r.content).findAll('form')
                for inp in forms[0].find_all("input"):
                    resp[inp.attrs["name"]] = inp.attrs["value"]
            else:
                r = self.conv.intermit(r)

            resp.verify(keyjar=self.conv.entity.keyjar)
        else:
            resp = r

        if not isinstance(resp, Response):  # Not a HTTP response
            try:
                try:
                    _id_token = resp["id_token"]
                except KeyError:
                    pass
                else:
                    if "kid" not in _id_token.jws_header and not \
                                    _id_token.jws_header["alg"] == "HS256":
                        for key, value in \
                                self.conv.entity.keyjar.issuer_keys.items():
                            if not key == "" and (len(value) > 1 or len(
                                    list(value[0].keys())) > 1):
                                raise PyoidcError(
                                    "No 'kid' in id_token header!")

                    if self.req_args['nonce'] != _id_token['nonce']:
                        raise PyoidcError(
                            "invalid nonce! {} != {}".format(
                                self.req_args['nonce'], _id_token['nonce']))

                    if not same_issuer(self.conv.info["issuer"],
                                       _id_token["iss"]):
                        raise IssuerMismatch(
                            " {} != {}".format(self.conv.info["issuer"],
                                               _id_token["iss"]))
                    self.conv.entity.id_token = _id_token
            except KeyError:
                pass

        return resp

    def run(self):
        _client = self.conv.entity

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

        self.conv.events.store('request', csi)
        self.conv.trace.info(
            20 * "=" + " " + self.__class__.__name__ + " " + 20 * "=")
        self.conv.trace.request("URL: {}".format(url))
        if body:
            self.conv.trace.request("BODY: {}".format(body))
        http_response = self.do_request(_client, url, body, http_args)

        response = self.catch_exception(self.handle_response, r=http_response,
                                        csi=csi)
        self.conv.trace.response(response)
        self.conv.events.store('response', response)
        #self.sequence.append((response, http_response.text))

        if self.expect_error:
            response = self.expected_error_response(response)
        else:
            if isinstance(response, ErrorResponse):
                raise Break("Unexpected error response")

        return response


class AsyncRequest(Request):
    request_cls = None
    method = ""
    module = ""
    content_type = URL_ENCODED
    response_cls = ""
    response_where = "url"  # if code otherwise 'body'
    response_type = "urlencoded"
    accept = None
    _tests = {"post": [], "pre": []}

    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)
        self.conv.req = self
        self.trace = conv.trace
        self.tests = copy.deepcopy(self._tests)
        self.csi = None
        self.request = self.conv.msg_factory(self.request_cls)
        self.response = self.conv.msg_factory(self.response_cls)
        if "comcls" in kwargs:
            self.com = kwargs["comcls"]()
        else:
            self.com = Log

    def run(self):
        _client = self.conv.entity
        _trace = self.conv.trace

        url, body, ht_args, csi = _client.request_info(
            self.request, method=self.method, request_args=self.req_args,
            lax=True, **self.op_args)

        self.csi = csi

        _trace.info("redirect.url: %s" % url)
        _trace.info("redirect.header: %s" % ht_args)
        self.conv.events.store('url', url)
        return Redirect(str(url))

    def parse_response(self, path, io, message_factory):
        _ctype = self.response_type
        _conv = self.conv

        if self.csi is None:
            url, body, ht_args, csi = _conv.entity.request_info(
                self.request, method=self.method, request_args=self.req_args,
                **self.op_args)

            self.csi = csi

        try:
            response_mode = self.csi["response_mode"]
        except KeyError:
            response_mode = None

        if self.request_cls == "AuthorizationRequest":
            try:
                _rt = self.csi["response_type"]
            except KeyError:
                response_where = ""
            else:
                if _rt == ["code"]:
                    response_where = "url"
                elif _rt == [""]:
                    response_where = ""
                else:
                    response_where = "fragment"
        else:
            response_where = self.response_where

        # parse the response
        if response_mode == "form_post":
            info = parse_qs(get_post(io.environ))
            _ctype = "dict"
        elif response_where == "url":
            info = io.environ["QUERY_STRING"]
            _ctype = "urlencoded"
        elif response_where == "fragment":
            query = parse_qs(get_post(io.environ))
            try:
                info = query["fragment"][0]
            except KeyError:
                return io.sorry_response(io.conf.BASE, "missing fragment ?!")
        elif response_where == "":
            info = io.environ["QUERY_STRING"]
            _ctype = "urlencoded"
        else:  # resp_c.where == "body"
            info = get_post(io.environ)

        logger.info("Response: %s" % info)

        _conv.trace.reply(info)
        ev_index = _conv.events.store('reply', info)

        resp_cls = message_factory(self.response_cls)
        algs = _conv.entity.sign_enc_algs("id_token")
        try:
            response = _conv.entity.parse_response(
                resp_cls, info, _ctype,
                self.csi["state"],
                keyjar=_conv.entity.keyjar, algs=algs)
        except ResponseError as err:
            return io.err_response(self.sh.session, "run_sequence", err)
        except Exception as err:
            return io.err_response(self.sh.session, "run_sequence", err)

        logger.info("Parsed response: %s" % response.to_dict())

        _conv.trace.response(response)
        _conv.events.store('response', response, ref=ev_index)

        if self.expect_error:
            self.expected_error_response(response)
        else:
            if isinstance(response, ErrorResponse):
                raise Break("Unexpected error response")


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
