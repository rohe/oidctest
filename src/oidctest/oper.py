import json
import logging
import os
from urlparse import urlparse
from Crypto.PublicKey import RSA
from aatest import END_TAG
from aatest.operation import Operation
from jwkest.jwk import RSAKey

from oic.oauth2 import rndstr
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.oic import AccessTokenResponse
import time
from oic.utils.keyio import KeyBundle, ec_init
from oidctest.prof_util import WEBFINGER
from oidctest.prof_util import DISCOVER
from oidctest.prof_util import REGISTER
from oidctest.request import SyncGetRequest
from oidctest.request import AsyncGetRequest
from oidctest.request import SyncPostRequest

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
    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)
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
    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)

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
    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)

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

    def __init__(self, conv, io, sh, **kwargs):
        super(SyncAuthn, self).__init__(conv, io, sh, **kwargs)
        self.op_args["endpoint"] = conv.client.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce
        # verify that I've got a valid access code
        self.tests["post"].append("valid_code")

    def op_setup(self):
        self.req_args["redirect_uri"] = self.conv.callback_uris[0]


class AsyncAuthn(AsyncGetRequest):
    response_cls = "AuthorizationResponse"
    request_cls = "AuthorizationRequest"

    def __init__(self, conv, io, sh, **kwargs):
        super(AsyncAuthn, self).__init__(conv, io, sh, **kwargs)
        self.op_args["endpoint"] = conv.client.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce

    def op_setup(self):
        self.req_args["redirect_uri"] = self.conv.callback_uris[0]


class AccessToken(SyncPostRequest):
    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)
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
        self.conv.trace.response(atr)
        assert isinstance(atr, AccessTokenResponse)


class UserInfo(SyncGetRequest):
    def __init__(self, conv, io, sh, **kwargs):
        Operation.__init__(self, conv, io, sh, **kwargs)
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
        issuer = self.conv.client.provider_info["issuer"]
        # Update all keys
        for keybundle in self.conv.client.keyjar.issuer_keys[issuer]:
            keybundle.update()


class RotateKey(Operation):

    def __call__(self):
        keyjar = self.conv.client.keyjar
        self.conv.client.original_keyjar = keyjar.copy()

        # invalidate the old key
        old_kid = self.op_args["old_kid"]
        old_key = keyjar.get_key_by_kid(old_kid)
        old_key.inactive_since = time.time()

        # setup new key
        key_spec = self.op_args["new_key"]
        typ = key_spec["type"].upper()
        if typ == "RSA":
            kb = KeyBundle(keytype=typ, keyusage=key_spec["use"])
            kb.append(RSAKey(use=key_spec["use"]).load_key(
                RSA.generate(key_spec["bits"])))
        elif typ == "EC":
            kb = ec_init(key_spec)

        # add new key to keyjar with
        kb.keys()[0].kid = self.op_args["new_kid"]
        keyjar.add_kb("", kb)

        # make jwks and update file
        keys = []
        for kb in keyjar[""]:
            keys.extend([k.to_dict() for k in kb.keys() if not k.inactive_since])
        jwks = dict(keys=keys)
        with open(self.op_args["jwks_path"], "w") as f:
            f.write(json.dumps(jwks))


class RestoreKeyJar(Operation):

    def __call__(self):
        self.conv.client.keyjar = self.conv.client.original_keyjar

        # make jwks and update file
        keys = []
        for kb in self.conv.client.keyjar[""]:
            keys.extend([k.to_dict() for k in kb.keys()])
        jwks = dict(keys=keys)
        with open(self.op_args["jwks_path"], "w") as f:
            f.write(json.dumps(jwks))

class ReadRegistration(SyncGetRequest):
    def op_setup(self):
        _client = self.conv.client
        self.req_args["access_token"] = _client.registration_access_token
        self.op_args["authn_method"] = "bearer_header"
        self.op_args["endpoint"] = _client.registration_response[
            "registration_client_uri"]
