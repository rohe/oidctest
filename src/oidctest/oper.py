import logging
import os
from urlparse import urlparse
from aatest import END_TAG
from aatest.operation import Operation
import functools
from oic.exception import IssuerMismatch, PyoidcError

from oic.oauth2 import rndstr
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.oic import AccessTokenResponse
from oidctest.prof_util import WEBFINGER
from oidctest.prof_util import DISCOVER
from oidctest.prof_util import REGISTER
from oidctest.request import ErrorResponse, same_issuer
from oidctest.request import SyncGetRequest
from oidctest.request import AsyncGetRequest
from oidctest.request import SyncPostRequest

from jwkest import jws

__author__ = 'roland'

logger = logging.getLogger(__name__)

class SubjectMismatch(Exception):
    pass


def include(url, test_id):
    p = urlparse(url)
    if p.path[1:].startswith(test_id):
        if len(p.path[1:].split("/")) <= 1:
            return os.path.join(url, "_/_/_/normal")
        else:
            return url

    return "%s://%s/%s%s_/_/_/normal" % (p.scheme, p.netloc, test_id, p.path)



class Webfinger(Operation):
    def __init__(self, conv, profile, test_id, conf, funcs, chk_factory):
        Operation.__init__(self, conv, profile, test_id, conf, funcs,
                           chk_factory)
        self.resource = ""
        self.dynamic = self.profile[WEBFINGER] == "T"

    def run(self):
        if not self.dynamic:
            self.conv["issuer"] = self.conf.INFO["srv_discovery_url"]
        else:
            self.conv.trace.info(
                "Discovery of resource: {}".format(self.resource))
            issuer = self.conv.client.discover(self.resource)
            self.conv.trace.reply(issuer)
            self.conv.info["issuer"] = issuer

    def op_setup(self):
        # try:
        #     self.resource = self.op_args["resource"]
        # except KeyError:
        #     self.resource = self.conf.ISSUER+self.test_id
        pass


class Discovery(Operation):
    def __init__(self, conv, session, test_id, conf, funcs, chk_factory):
        Operation.__init__(self, conv, session, test_id, conf, funcs,
                           chk_factory)

        self.dynamic = self.profile[DISCOVER] == "T"

    def run(self):
        if self.dynamic:
            self.catch_exception(self.conv.client.provider_config,
                                 **self.op_args)
        else:
            self.conv.client.provider_info = ProviderConfigurationResponse(
                **self.conf.INFO["provider_info"]
            )

    def op_setup(self):
        # if self.dynamic:
        #     try:
        #         _issuer = include(self.op_args["issuer"], self.test_id)
        #     except KeyError:
        #         _issuer = include(self.conv.info["issuer"], self.test_id)
        #
        #     self.op_args["issuer"] = _issuer
        pass


class Registration(Operation):
    def __init__(self, conv, session, test_id, conf, funcs, chk_factory):
        Operation.__init__(self, conv, session, test_id, conf, funcs,
                           chk_factory)

        self.dynamic = self.profile[REGISTER] == "T"

    def run(self):
        if self.dynamic:
            self.catch_exception(self.conv.client.register, **self.req_args)
        else:
            self.conv.client.store_registration_info(
                RegistrationResponse(**self.conf.INFO["registered"]))

    def op_setup(self):
        if self.dynamic:
            self.req_args.update(self.conf.INFO["client"])
            self.req_args["url"] = self.conv.client.provider_info[
                "registration_endpoint"]


class SyncAuthn(SyncGetRequest):
    response_cls = "AuthorizationResponse"
    request_cls = "AuthorizationRequest"

    def __init__(self, conv, session, test_id, conf, funcs, chk_factory):
        super(SyncAuthn, self).__init__(conv, session, test_id, conf, funcs,
                                        chk_factory)
        self.op_args["endpoint"] = conv.client.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce
        # verify that I've got a valid access code
        self.tests["post"].append("valid_code")

        # Monkey-patch: make sure we use the same http session (preserving
        # cookies) when fetching keys from issuers 'jwks_uri' as for the
        # rest of the test sequence
        import oic.utils.keyio

        oic.utils.keyio.request = functools.partial(
            request_with_client_http_session, self)

    def op_setup(self):
        self.req_args["redirect_uri"] = self.conv.callback_uris[0]


class AsyncAuthn(AsyncGetRequest):
    response_cls = "AuthorizationResponse"
    request_cls = "AuthorizationRequest"

    def __init__(self, conv, session, test_id, conf, funcs, chk_factory):
        super(AsyncAuthn, self).__init__(conv, session, test_id, conf, funcs,
                                         chk_factory)
        self.op_args["endpoint"] = conv.client.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce

    def op_setup(self):
        self.req_args["redirect_uri"] = self.conv.callback_uris[0]


class AccessToken(SyncPostRequest):
    def __init__(self, conv, session, test_id, conf, funcs, chk_factory):
        Operation.__init__(self, conv, session, test_id, conf, funcs,
                           chk_factory)
        self.op_args["state"] = conv.state
        self.req_args["redirect_uri"] = conv.client.redirect_uris[0]

    def run(self):
        if self.skip:
            return

        self.conv.trace.info(
            "Access Token Request with op_args: {}, req_args: {}".format(
                self.op_args, self.req_args))
        atr = self.conv.client.do_access_token_request(
            request_args=self.req_args, **self.op_args)

        # Check the c_hash
        resp_hash = jws.left_hash(self.req_args["code"], atr["id_token"].jws_header["alg"])
        if atr["id_token"]["c_hash"] != resp_hash:
            raise ErrorResponse("c_hash mismatch {} != {}".format(atr["id_token"]["c_hash"], jws.left_hash(self.req_args["code"], "HS256")))

        if not "kid" in atr["id_token"].jws_header and not atr["id_token"].jws_header["alg"] == "HS256":
            for key, value in self.conv.client.keyjar.issuer_keys.iteritems():
                if not key == "" and (len(value) > 1 or len(value[0].keys()) > 1):
                    raise PyoidcError("No 'kid' in id_token header!")

        if not same_issuer(self.conv.info["issuer"], atr["id_token"]["iss"]):
            # if self.conv.info["issuer"] != atr["id_token"]["iss"]:
            raise IssuerMismatch(" {} != {}".format(self.conv.info["issuer"], atr["id_token"]["iss"]))

        self.conv.trace.response(atr)
        assert isinstance(atr, AccessTokenResponse)


class UserInfo(SyncGetRequest):
    def __init__(self, conv, session, test_id, conf, args, chk_factory):
        Operation.__init__(self, conv, session, test_id, conf, args,
                           chk_factory)
        self.op_args["state"] = conv.state

    def run(self):
        args = self.op_args.copy()
        args.update(self.req_args)

        user_info = self.conv.client.do_user_info_request(**args)
        assert user_info

        self.catch_exception(self._verify_subject_identifier,
                             client=self.conv.client,
                             user_info=user_info)

        if "_claim_sources" in user_info:
            user_info = self.conv.client.unpack_aggregated_claims(user_info)
            user_info = self.conv.client.fetch_distributed_claims(user_info)

        self.conv.client.userinfo = user_info
        self.conv.trace.response(user_info)

    @staticmethod
    def _verify_subject_identifier(client, user_info):
        if client.id_token:
            if user_info["sub"] != client.id_token["sub"]:
                msg = "user_info['sub'] != id_token['sub']: '{}!={}'".format(
                    user_info["sub"], client.id_token["sub"])
                raise SubjectMismatch(msg)
        return "Subject identifier ok!"


class DisplayUserInfo(Operation):
    pass


class Done(Operation):
    def run(self, *args, **kwargs):
        self.conv.trace.info(END_TAG)

class UpdateProviderKeys(Operation):
    def __call__(self, *args, **kwargs):
        # Monkey-patch: make sure we use the same http session (preserving
        # cookies) when fetching keys from issuers 'jwks_uri' as for the
        # rest of the test sequence
        import oic.utils.keyio

        oic.utils.keyio.request = functools.partial(
            request_with_client_http_session, self)

        issuer = self.conv.client.provider_info["issuer"]
        # Update all keys
        for keybundle in self.conv.client.keyjar.issuer_keys[issuer]:
            keybundle.update()


def request_with_client_http_session(instance, method, url, **kwargs):
    """Use the clients http session to make http request.
    Note: client.http_request function requires the parameters in reverse
    order (compared to the requests library): (method, url) vs (url, method)
    so we can't bind the instance method directly.
    """
    return instance.conv.client.http_request(url, method)

