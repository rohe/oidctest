from future.backports.urllib.parse import urlparse

import builtins
import inspect
import json
import logging
import os
import sys
import time

from Cryptodome.PublicKey import RSA
from jwkest.jwk import RSAKey
from oic import rndstr
from oic.exception import IssuerMismatch
from oic.exception import ParameterError
from oic.oauth2 import ErrorResponse
from oic.oauth2 import Message
from oic.oauth2.util import JSON_ENCODED
from oic.oic import OpenIDSchema
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.utils.keyio import KeyBundle
from oic.utils.keyio import dump_jwks
from oic.utils.keyio import ec_init
from oic.utils.keyio import rsa_init
from otest import RequirementsNotMet
from otest import Unknown
from otest.aus.operation import Operation
from otest.aus.request import AsyncGetRequest, display_jwx_headers
from otest.aus.request import SyncGetRequest
from otest.aus.request import SyncPostRequest
from otest.aus.request import same_issuer
from otest.check import get_id_tokens
from otest.events import EV_EXCEPTION
from otest.events import EV_NOOP
from otest.events import EV_PROTOCOL_RESPONSE
from otest.events import EV_REQUEST
from otest.events import EV_RESPONSE
from otest.events import OUTGOING
from otest.prof_util import RESPONSE

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
    def __init__(self, conv, inut, sh, **kwargs):
        Operation.__init__(self, conv, inut, sh, **kwargs)
        self.resource = ""
        self.dynamic = inut.profile_handler.webfinger(self.profile)

    def run(self):
        if self.dynamic:
            _conv = self.conv
            if self.resource:
                principal = self.resource
            else:
                principal = self.req_args['principal']

            _conv.entity.wf.events = _conv.entity.events
            self.catch_exception_and_error(_conv.entity.discover,
                                           principal=principal)

            if not _conv.events.get(EV_EXCEPTION):
                issuer = _conv.events.last_item(EV_RESPONSE)
                _conv.info["issuer"] = issuer
                _conv.events.store('issuer', issuer,
                                   sender=self.__class__.__name__)
        else:
            self.conv.events.store(EV_NOOP, "WebFinger")
            self.conv.info["issuer"] = self.conv.get_tool_attribute("issuer")

    def op_setup(self):
        # try:
        #     self.resource = self.op_args["resource"]
        # except KeyError:
        #     self.resource = self.conf.ISSUER+self.test_id
        pass


class Discovery(Operation):
    def __init__(self, conv, inut, sh, **kwargs):
        Operation.__init__(self, conv, inut, sh, **kwargs)
        self.dynamic = inut.profile_handler.discover(self.profile)

    def run(self):
        if self.dynamic:
            self.catch_exception_and_error(self.conv.entity.provider_config,
                                           **self.op_args)
        else:
            self.conv.events.store(EV_NOOP, "Dynamic discovery")
            self.conv.entity.provider_info = ProviderConfigurationResponse(
                **self.conv.entity_config["provider_info"]
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
    def __init__(self, conv, inut, sh, **kwargs):
        Operation.__init__(self, conv, inut, sh, **kwargs)
        self.dynamic = inut.profile_handler.register(self.profile)

    def run(self):
        if self.dynamic:
            self.catch_exception_and_error(self.conv.entity.register,
                                           **self.req_args)
        else:
            self.conv.events.store(EV_NOOP, "Dynamic registration")
            self.conv.entity.store_registration_info(
                RegistrationResponse(
                    **self.conv.entity_config["registration_response"]))

    def op_setup(self):
        if self.dynamic:
            self.req_args.update(self.conv.entity_config["registration_info"])
            self.req_args["url"] = self.conv.entity.provider_info[
                "registration_endpoint"]
            if self.conv.entity.jwks_uri:
                self.req_args['jwks_uri'] = self.conv.entity.jwks_uri

    def map_profile(self, profile_map):
        try:
            items = profile_map[self.__class__][self.profile[RESPONSE]].items()
        except KeyError:
            pass
        else:
            for func, arg in items:
                func(self, arg)


class SyncAuthn(SyncGetRequest):
    response_cls = "AuthorizationResponse"
    request_cls = "AuthorizationRequest"

    def __init__(self, conv, inut, sh, **kwargs):
        super(SyncAuthn, self).__init__(conv, inut, sh, **kwargs)
        self.op_args["endpoint"] = conv.entity.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce

        # defaults
        self.req_args['scope'] = ['openid']
        self.req_args['response_type'] = 'code'

        # verify that I've got a valid access code
        # self.tests["post"].append("valid_code")

    def op_setup(self):
        self.req_args["redirect_uri"] = self.conv.extra_args['callback_uris'][0]


class AsyncAuthn(AsyncGetRequest):
    response_cls = "AuthorizationResponse"
    request_cls = "AuthorizationRequest"

    def __init__(self, conv, inut, sh, **kwargs):
        super(AsyncAuthn, self).__init__(conv, inut, sh, **kwargs)
        self.op_args["endpoint"] = conv.entity.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce

    def op_setup(self):
        self.req_args["redirect_uri"] = self.conv.extra_args['callback_uris'][0]


class AccessToken(SyncPostRequest):
    def __init__(self, conv, inut, sh, **kwargs):
        super(AccessToken, self).__init__(conv, inut, sh, **kwargs)
        self.op_args["state"] = conv.state
        self.req_args["redirect_uri"] = conv.entity.redirect_uris[0]

    def run(self):
        res = self._run()
        if not isinstance(res, Message):
            return res

    def _run(self):
        if self.skip:
            return

        self.conv.events.store(
            EV_REQUEST,
            "op_args: {}, req_args: {}".format(self.op_args, self.req_args),
            direction=OUTGOING)

        atr = self.catch_exception_and_error(
            self.conv.entity.do_access_token_request,
            request_args=self.req_args, **self.op_args)

        if atr is None or isinstance(atr, ErrorResponse):
            return atr

        display_jwx_headers(atr, self.conv)

        try:
            _jws_alg = atr["id_token"].jws_header['alg']
        except (KeyError, AttributeError):
            pass
        else:
            if _jws_alg == "none":
                pass
            elif "kid" not in atr[
                    "id_token"].jws_header and _jws_alg != "HS256":
                keys = self.conv.entity.keyjar.keys_by_alg_and_usage(
                    self.conv.info["issuer"], _jws_alg, "ver")
                if len(keys) > 1:
                    raise ParameterError("No 'kid' in id_token header!")

        if not same_issuer(self.conv.info["issuer"], atr["id_token"]["iss"]):
            raise IssuerMismatch(" {} != {}".format(self.conv.info["issuer"],
                                                    atr["id_token"]["iss"]))

        # assert isinstance(atr, AccessTokenResponse)
        return atr


class RefreshToken(SyncPostRequest):
    def __init__(self, conv, inut, sh, **kwargs):
        super(RefreshToken, self).__init__(conv, inut, sh, **kwargs)
        self.op_args["state"] = conv.state
        # self.req_args["redirect_uri"] = conv.entity.redirect_uris[0]

    def run(self):
        res = self._run()
        if not isinstance(res, Message):
            return res

    def _run(self):
        if self.skip:
            return

        if 'authn_method' not in self.op_args:
            _ent = self.conv.entity
            try:
                self.op_args['authn_method'] = _ent.registration_response[
                    'token_endpoint_auth_method']
            except KeyError:
                for am in _ent.client_authn_method.keys():
                    if am in _ent.provider_info[
                            'token_endpoint_auth_methods_supported']:
                        self.op_args['authn_method'] = am
                        break

        self.conv.events.store(
            EV_REQUEST,
            "op_args: {}, req_args: {}".format(self.op_args, self.req_args),
            direction=OUTGOING)

        atr = self.catch_exception_and_error(
            self.conv.entity.do_access_token_refresh,
            request_args=self.req_args, **self.op_args)

        display_jwx_headers(atr, self.conv)

        try:
            _jws_alg = atr["id_token"].jws_header["alg"]
        except (KeyError, AttributeError):
            pass
        else:
            if _jws_alg == "none":
                pass
            elif "kid" not in atr[
                "id_token"].jws_header and not _jws_alg == "HS256":
                keys = self.conv.entity.keyjar.keys_by_alg_and_usage(
                    self.conv.info["issuer"], _jws_alg, "ver")
                if len(keys) > 1:
                    raise ParameterError("No 'kid' in id_token header!")

        return atr


class UserInfo(SyncGetRequest):
    def __init__(self, conv, inut, sh, **kwargs):
        super(UserInfo, self).__init__(conv, inut, sh, **kwargs)
        self.op_args["state"] = conv.state

    def do_user_info_request(self, **kwargs):
        res = self.conv.entity.do_user_info_request(**kwargs)
        if isinstance(res, OpenIDSchema):
            self._verify_subject_identifier(res)
        return res

    def run(self):
        args = self.op_args.copy()
        args.update(self.req_args)

        response = self.catch_exception_and_error(self.do_user_info_request,
                                                  **args)

        if response is None:
            pass
        elif "_claim_sources" in response:
            user_info = self.conv.entity.unpack_aggregated_claims(response)
            user_info = self.conv.entity.fetch_distributed_claims(user_info)
            self.conv.entity.userinfo = user_info
            self.conv.events.store(EV_PROTOCOL_RESPONSE, user_info)
        else:
            self.conv.entity.userinfo = response
            self.conv.events.store(EV_PROTOCOL_RESPONSE, response)
            # return response

    def _verify_subject_identifier(self, user_info):
        id_tokens = get_id_tokens(self.conv)
        if id_tokens:
            if user_info["sub"] != id_tokens[0]["sub"]:
                msg = "user_info['sub'] != id_token['sub']: '{}!={}'".format(
                    user_info["sub"], id_tokens[0]["sub"])
                raise SubjectMismatch(msg)
        return "Subject identifier ok!"


class DisplayUserInfo(Operation):
    pass


class UpdateProviderKeys(Operation):
    def __call__(self, *args, **kwargs):
        keyjar = self.conv.entity.keyjar
        self.conv.entity.original_keyjar = keyjar.copy()
        issuer = self.conv.entity.provider_info["issuer"]
        # Update all keys
        for keybundle in self.conv.entity.keyjar.issuer_keys[issuer]:
            keybundle.update()


class RotateKey(Operation):
    def __call__(self):
        keyjar = self.conv.entity.keyjar
        self.conv.entity.original_keyjar = keyjar.copy()

        # invalidate the old key
        old_key_spec = self.op_args["old_key"]
        old_key = keyjar.keys_by_alg_and_usage('', old_key_spec['alg'],
                                               old_key_spec['use'])[0]
        old_key.inactive_since = time.time()

        # setup new key
        key_spec = self.op_args["new_key"]
        typ = key_spec["type"].upper()
        if typ == "RSA":
            kb = KeyBundle(keytype=typ, keyusage=key_spec["use"])
            kb.append(RSAKey(use=key_spec["use"][0]).load_key(
                RSA.generate(key_spec["bits"])))
        elif typ == "EC":
            kb = ec_init(key_spec)
        else:
            raise Unknown('keytype: {}'.format(typ))

        # add new key to keyjar with
        list(kb.keys())[0].kid = self.op_args["new_kid"]
        keyjar.add_kb("", kb)

        # make jwks and update file
        keys = []
        for kb in keyjar[""]:
            keys.extend(
                [k.to_dict() for k in list(kb.keys()) if not k.inactive_since])
        jwks = dict(keys=keys)
        with open(self.op_args["jwks_path"], "w") as f:
            f.write(json.dumps(jwks))


class RestoreKeyJar(Operation):
    def __call__(self):
        self.conv.entity.keyjar = self.conv.entity.original_keyjar

        # make jwks and update file
        keys = []
        for kb in self.conv.entity.keyjar[""]:
            keys.extend([k.to_dict() for k in list(kb.keys())])
        jwks = dict(keys=keys)
        with open(self.op_args["jwks_path"], "w") as f:
            f.write(json.dumps(jwks))


class ReadRegistration(SyncGetRequest):
    response_cls = 'RegistrationResponse'
    content_type = JSON_ENCODED

    def op_setup(self):
        _client = self.conv.entity
        self.req_args["access_token"] = _client.registration_access_token
        self.op_args["authn_method"] = "bearer_header"
        self.op_args["endpoint"] = _client.registration_response[
            "registration_client_uri"]


class FetchKeys(Operation):
    def __call__(self):
        kb = KeyBundle(source=self.conv.entity.provider_info["jwks_uri"])
        kb.verify_ssl = False
        kb.update()

        try:
            self.conv.keybundle.append(kb)
        except AttributeError:
            self.conv.keybundle = [kb]


def _new_rsa_key(spec):
    if 'name' not in spec:
        if '/' in spec['key']:
            (head, tail) = os.path.split(spec['key'])
            spec['path'] = head
            spec['name'] = tail
        else:
            spec['name'] = spec['key']
    return rsa_init(spec)


class RotateKeys(Operation):
    def __init__(self, conv, inut, sh, **kwargs):
        Operation.__init__(self, conv, inut, sh, **kwargs)
        self.jwk_name = "export/jwk.json"
        self.new_key = {}
        self.kid_template = "_%d"
        self.key_usage = ""

    def __call__(self):
        # find the name of the file to which the JWKS should be written
        try:
            _uri = self.conv.entity.registration_response["jwks_uri"]
        except KeyError:
            raise RequirementsNotMet("No dynamic key handling")

        r = urlparse(_uri)
        # find the old key for this key usage and mark that as inactive
        for kb in self.conv.entity.keyjar.issuer_keys[""]:
            for key in list(kb.keys()):
                if key.use in self.new_key["use"]:
                    key.inactive = True

        kid = 0
        # only one key
        _nk = self.new_key
        _typ = _nk["type"].upper()

        if _typ == "RSA":
            error_to_catch = getattr(builtins, 'FileNotFoundError',
                                     getattr(builtins, 'IOError'))
            try:
                kb = KeyBundle(source="file://%s" % _nk["key"],
                               fileformat="der", keytype=_typ,
                               keyusage=_nk["use"])
            except error_to_catch:
                kb = _new_rsa_key(_nk)
        else:
            kb = {}

        for k in list(kb.keys()):
            k.serialize()
            k.add_kid()
            self.conv.entity.kid[k.use][k.kty] = k.kid
        self.conv.entity.keyjar.add_kb("", kb)

        dump_jwks(self.conv.entity.keyjar[""], r.path[1:])


class RotateSigKeys(RotateKeys):
    def __init__(self, conv, inut, sh, **kwargs):
        RotateKeys.__init__(self, conv, inut, sh, **kwargs)
        self.new_key = {
            "type": "RSA", "key": "./keys/second_sig.key",
            "use": ["sig"]
        }
        self.kid_template = "sig%d"


class RotateEncKeys(RotateKeys):
    def __init__(self, conv, inut, sh, **kwargs):
        RotateKeys.__init__(self, conv, inut, sh, **kwargs)
        self.new_key = {
            "type": "RSA", "key": "./keys/second_enc.key",
            "use": ["enc"]
        }
        self.kid_template = "enc%d"


class RefreshAccessToken(SyncPostRequest):
    request_cls = "RefreshAccessTokenRequest"
    response_cls = "AccessTokenResponse"


class Cache(Operation):
    pass


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if name == fname:
                return obj

    from otest.aus import operation
    obj = operation.factory(name)
    if not obj:
        raise Unknown("Couldn't find the operation: '{}'".format(name))
    return obj
