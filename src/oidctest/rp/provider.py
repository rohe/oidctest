import json
import logging
import time
import copy

from Cryptodome.PublicKey import RSA
from future.backports.urllib.parse import parse_qs

from jwkest.ecc import P256
from jwkest.jwk import RSAKey
from jwkest.jwk import ECKey
from jwkest.jwk import SYMKey

from oic import oic
from oic import rndstr
from oic.oauth2 import Message
from oic.oic import provider
from oic.oic.message import AccessTokenRequest
from oic.oic.message import ProviderConfigurationResponse
from oic.oic.message import RegistrationResponse
from oic.oic.message import RegistrationRequest
from oic.utils import keyio
from oic.utils.keyio import keyjar_init, key_summary

from otest.events import EV_HTTP_RESPONSE

__author__ = 'roland'

logger = logging.getLogger(__name__)


class TestError(Exception):
    pass


def sort_string(string):
    if string is None:
        return ""

    _l = list(string)
    _l.sort()
    return "".join(_l)


def response_type_cmp(allowed, offered):
    """

    :param allowed: A list of space separated lists of return types
    :param offered: A space separated list of return types
    :return:
    """

    if ' ' in offered:
        ort = set(offered.split(' '))
    else:
        try:
            ort = {offered}
        except TypeError:  # assume list
            ort = [set(o.split(' ')) for o in offered][0]

    for rt in allowed:
        if ' ' in rt:
            _rt = set(rt.split(' '))
        else:
            _rt = {rt}

        if _rt == ort:
            return True

    return False


class Server(oic.Server):
    def __init__(self, keyjar=None, ca_certs=None, verify_ssl=True):
        oic.Server.__init__(self, keyjar, ca_certs, verify_ssl)

        self.behavior_type = {}

    def make_id_token(self, session, loa="2", issuer="",
                      alg="RS256", code=None, access_token=None,
                      user_info=None, auth_time=0, exp=None, extra_claims=None):
        idt = oic.Server.make_id_token(self, session, loa, issuer, alg,
                                       code,
                                       access_token, user_info, auth_time,
                                       exp,
                                       extra_claims)

        if "ath" in self.behavior_type:  # modify the at_hash if available
            try:
                idt["at_hash"] = sort_string(idt["at_hash"])
            except KeyError:
                raise TestError("Missing at_hash in id_token")

        if "ch" in self.behavior_type:  # modify the c_hash if available
            try:
                idt["c_hash"] = sort_string(idt["c_hash"])
            except (KeyError, TypeError):
                pass

        if "issi" in self.behavior_type:  # mess with the iss value
            idt["iss"] = "https://example.org/"

        if "itsub" in self.behavior_type:  # missing sub claim
            del idt["sub"]

        if "aud" in self.behavior_type:  # invalid aud claim
            idt["aud"] = "https://example.com/"

        if "iat" in self.behavior_type:  # missing iat claim
            del idt["iat"]

        if "nonce" in self.behavior_type:  # invalid nonce if present
            try:
                idt["nonce"] = "012345678"
            except KeyError:
                pass

        return idt


class Provider(provider.Provider):
    def __init__(self, name, sdb, cdb, authn_broker, userinfo, authz,
                 client_authn, symkey, urlmap=None, ca_certs="", keyjar=None,
                 hostname="", template_lookup=None, template=None,
                 verify_ssl=True, capabilities=None, **kwargs):

        provider.Provider.__init__(
            self, name, sdb, cdb, authn_broker, userinfo, authz,
            client_authn,
            symkey, urlmap, ca_certs, keyjar, hostname, template_lookup,
            template, verify_ssl, capabilities)

        self.claims_type = ["normal"]
        self.behavior_type = []
        self.server = Server(keyjar=keyjar, ca_certs=ca_certs,
                             verify_ssl=verify_ssl)
        self.server.behavior_type = self.behavior_type
        self.claim_access_token = {}
        self.init_keys = []
        self.update_key_use = ""
        self.trace = None
        for param in ['jwks_name', 'jwks_uri']:
            try:
                setattr(self, param, kwargs[param])
            except KeyError:
                pass
        self.jwx_def = {}
        self.build_jwx_def()

    def build_jwx_def(self):
        self.jwx_def = {}

        for _typ in ["signing_alg", "encryption_alg", "encryption_enc"]:
            self.jwx_def[_typ] = {}
            for item in ["id_token", "userinfo"]:
                cap_param = '{}_{}_values_supported'.format(item, _typ)
                try:
                    self.jwx_def[_typ][item] = self.capabilities[cap_param][
                        0]
                except KeyError:
                    self.jwx_def[_typ][item] = ""

    def sign_encrypt_id_token(self, sinfo, client_info, areq, code=None,
                              access_token=None, user_info=None):
        # self._update_client_keys(client_info["client_id"])

        return provider.Provider.sign_encrypt_id_token(
            self, sinfo, client_info, areq, code, access_token, user_info)

    def no_kid_keys(self):
        keys = [copy.copy(k) for k in self.keyjar.get_signing_key()]
        for k in keys:
            k.kid = None
        return keys

    def id_token_as_signed_jwt(self, session, loa="2", alg="", code=None,
                               access_token=None, user_info=None, auth_time=0,
                               exp=None, extra_claims=None, **kwargs):

        kwargs = {}

        if "rotsig" in self.behavior_type:  # Rollover signing keys
            if alg == "RS256":
                key = RSAKey(kid="rotated_rsa_{}".format(time.time()),
                             use="sig").load_key(RSA.generate(2048))
            else:  # alg == "ES256"
                key = ECKey(kid="rotated_ec_{}".format(time.time()),
                            use="sig").load_key(P256)

            new_keys = {"keys": [key.serialize(private=True)]}
            self.trace.info("New signing keys: {}".format(new_keys))
            self.do_key_rollover(new_keys, "%d")
            self.trace.info("Rotated signing keys")

        if "nokid1jwks" in self.behavior_type:
            kwargs['keys'] = self.no_kid_keys()
            # found_key = None
            # for kb in self.keyjar.key_summary[""]:
            #     issuer_key = list(kb.keys())[0]
            #     if issuer_key.use == "sig" and \
            #             issuer_key.kty.startswith(
            #                 alg[:2]):
            #         issuer_key.kid = None
            #         found_key = key
            #         break
            # self.keyjar.key_summary[""] = [found_key]

        if "nokidmuljwks" in self.behavior_type:
            kwargs['keys'] = self.no_kid_keys()
            # for key in self.keyjar.key_summary[""]:
            #     for inner_key in list(key.keys()):
            #         inner_key.kid = None

        _jws = provider.Provider.id_token_as_signed_jwt(
            self, session, loa=loa, alg=alg, code=code,
            access_token=access_token, user_info=user_info,
            auth_time=auth_time,
            exp=exp, extra_claims=extra_claims, **kwargs)

        if "idts" in self.behavior_type:  # mess with the signature
            #
            p = _jws.split(".")
            p[2] = sort_string(p[2])
            _jws = ".".join(p)

        return _jws

    def _collect_user_info(self, session, userinfo_claims=None):
        ava = provider.Provider._collect_user_info(self, session,
                                                   userinfo_claims)

        _src = "src1"
        if "aggregated" in self.claims_type:  # add some aggregated claims
            extra = Message(eye_color="blue", shoe_size=8)
            _jwt = extra.to_jwt(algorithm="none")
            ava["_claim_names"] = Message(eye_color=_src,
                                          shoe_size=_src)
            a_claims = {_src: {"JWT": _jwt}}
            ava["_claim_sources"] = Message(**a_claims)
        elif "distributed" in self.claims_type:
            urlbase = self.name
            if urlbase[-1] != '/':
                urlbase += '/'

            _tok = rndstr()
            self.claim_access_token[_tok] = {"age": 30}
            ava["_claim_names"] = Message(age=_src)
            d_claims = {
                _src: {"endpoint": urlbase + "claim", "access_token": _tok}}
            ava["_claim_sources"] = Message(**d_claims)

        if "uisub" in self.behavior_type:
            ava["sub"] = "foobar"

        return ava

    def create_providerinfo(self, pcr_class=ProviderConfigurationResponse,
                            setup=None):
        _response = provider.Provider.create_providerinfo(self, pcr_class,
                                                          setup)

        if "isso" in self.behavior_type:
            _response["issuer"] = "https://example.com"

        return _response

    def registration_endpoint(self, request, authn=None, **kwargs):
        try:
            reg_req = RegistrationRequest().deserialize(request, "json")
        except ValueError:
            reg_req = RegistrationRequest().deserialize(request)

        try:
            f = response_type_cmp(kwargs['test_cnf']['response_type'],
                                  reg_req['response_types'])
        except KeyError:
            pass

        # Do initial verification that all endpoints from the client uses
        #  https
        for endp in ["redirect_uris", "jwks_uri", "initiate_login_uri"]:
            try:
                uris = reg_req[endp]
            except KeyError:
                continue

            if not isinstance(uris, list):
                uris = [uris]
            for uri in uris:
                if not uri.startswith("https://"):
                    return self._error(
                        error="invalid_configuration_parameter",
                        descr="Non-HTTPS endpoint in '{}'".format(endp))

        _response = provider.Provider.registration_endpoint(self, request,
                                                            authn, **kwargs)
        self.conv.events.store(EV_HTTP_RESPONSE, _response)
        self.init_keys = []
        if "jwks_uri" in reg_req:
            if _response.status == "200 OK":
                # find the client id
                req_resp = RegistrationResponse().from_json(
                    _response.message)
                for kb in self.keyjar[req_resp["client_id"]]:
                    if kb.imp_jwks:
                        self.trace.info(
                            "Client JWKS: {}".format(kb.imp_jwks))

        return _response

    def authorization_endpoint(self, request="", cookie=None, **kwargs):
        _req = parse_qs(request)

        try:
            _scope = _req["scope"]
        except KeyError:
            return self._error(
                error="incorrect_behavior",
                descr="No scope parameter"
            )
        else:
            # verify that openid is among the scopes
            _scopes = _scope[0].split(" ")
            if "openid" not in _scopes:
                return self._error(
                    error="incorrect_behavior",
                    descr="Scope does not contain 'openid'"
                )

        client_id = _req["client_id"][0]

        try:
            f = response_type_cmp(kwargs['test_cnf']['response_type'],
                                  _req['response_type'])
        except KeyError:
            pass
        else:
            self.trace.error('Wrong response type: {}'.format(
                _req['response_type']))
            if f is False:
                return self._error_response(error="incorrect_behavior",
                                            descr="Wrong response_type")

        _rtypes = []
        for rt in _req['response_type']:
            _rtypes.extend(rt.split(' '))

        if 'id_token' in _rtypes:
            try:
                self._update_client_keys(client_id)
            except TestError:
                return self._error(error="incorrect_behavior",
                                   descr="No change in client keys")

        _response = provider.Provider.authorization_endpoint(self, request,
                                                             cookie,
                                                             **kwargs)

        if "rotenc" in self.behavior_type:  # Rollover encryption keys
            rsa_key = RSAKey(kid="rotated_rsa_{}".format(time.time()),
                             use="enc").load_key(RSA.generate(2048))
            ec_key = ECKey(kid="rotated_ec_{}".format(time.time()),
                           use="enc").load_key(P256)

            keys = [rsa_key.serialize(private=True),
                    ec_key.serialize(private=True)]
            new_keys = {"keys": keys}
            self.trace.info("New encryption keys: {}".format(new_keys))
            self.do_key_rollover(new_keys, "%d")
            self.trace.info("Rotated encryption keys")
            logger.info(
                'Rotated OP enc keys, new set: {}'.format(
                    key_summary(self.keyjar, '')))

        # This is just for logging purposes
        try:
            _resp = self.server.http_request(_req["request_uri"][0])
        except KeyError:
            pass
        else:
            if _resp.status_code == 200:
                self.trace.info(
                    "Request from request_uri: {}".format(_resp.text))

        return _response

    def token_endpoint(self, request="", authn=None, dtype='urlencoded',
                       **kwargs):
        try:
            req = AccessTokenRequest().deserialize(request, dtype)
            client_id = self.client_authn(self, req, authn)
        except Exception as err:
            logger.error(err)
            self.trace.error("Failed to verify client due to: %s" % err)
            return self._error(error="incorrect_behavior",
                               descr="Failed to verify client")

        try:
            self._update_client_keys(client_id)
        except TestError:
            logger.error('No change in client keys')
            return self._error(error="incorrect_behavior",
                               descr="No change in client keys")

        _response = provider.Provider.token_endpoint(self, request,
                                                     authn, dtype, **kwargs)

        return _response

    def generate_jwks(self, mode):
        if "nokid1jwk" in self.behavior_type:
            alg = mode["sign_alg"]
            if not alg:
                alg = "RS256"
            keys = [k.to_dict() for kb in self.keyjar[""] for k in
                    list(kb.keys())]
            for key in keys:
                if key["use"] == "sig" and key["kty"].startswith(alg[:2]):
                    key.pop("kid", None)
                    jwk = dict(keys=[key])
                    return json.dumps(jwk)
            raise Exception(
                "Did not find sig {} key for nokid1jwk test ".format(alg))
        else:  # Return all keys
            keys = [k.to_dict() for kb in self.keyjar[""] for k in
                    list(kb.keys())]
            jwks = dict(keys=keys)
            return json.dumps(jwks)

    def _update_client_keys(self, client_id):
        if "updkeys" in self.behavior_type:
            if not self.init_keys:
                if "rp-enc-key" in self.baseurl:
                    self.update_key_use = "enc"
                else:
                    self.update_key_use = "sig"
                self.init_keys = []
                for kb in self.keyjar[client_id]:
                    for key in kb.available_keys():
                        if isinstance(key, SYMKey):
                            pass
                        elif key.use == self.update_key_use:
                            self.init_keys.append(key)
            else:
                for kb in self.keyjar[client_id]:
                    self.trace.info("Updating client keys")
                    kb.update()
                    if kb.imp_jwks:
                        self.trace.info(
                            "Client JWKS: {}".format(kb.imp_jwks))
                same = 0
                # Verify that the new keys are not the same
                for kb in self.keyjar[client_id]:
                    for key in kb.available_keys():
                        if isinstance(key, SYMKey):
                            pass
                        elif key.use == self.update_key_use:
                            if key in self.init_keys:
                                same += 1
                            else:
                                self.trace.info("New key: {}".format(key))
                if same == len(self.init_keys):  # no change
                    self.trace.info("No change in keys")
                    raise TestError("Keys unchanged")
                else:
                    self.trace.info(
                        "{} keys changed, {} keys the same".format(
                            len(self.init_keys) - same, same))

    def __setattr__(self, key, value):
        if key == "keys":
            # Update the keyjar instead of just storing the keys description
            keyjar_init(self, value)
        else:
            super(provider.Provider, self).__setattr__(key, value)

    def _get_keyjar(self):
        return self.server.keyjar

    def _set_keyjar(self, item):
        self.server.keyjar = item

    keyjar = property(_get_keyjar, _set_keyjar)
