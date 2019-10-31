import copy
import json
import logging
import time

import requests
from Cryptodome.PublicKey import RSA
from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import splitquery
from future.backports.urllib.parse import urlencode
from jwkest.ecc import P256
from jwkest.jwk import ECKey
from jwkest.jwk import RSAKey
from jwkest.jwk import SYMKey
from oic import oic
from oic import rndstr
from oic.exception import InvalidRequest
from oic.oauth2 import Message
from oic.oauth2 import error_response
from oic.oic import provider
from oic.oic.message import AccessTokenRequest
from oic.oic.message import BACK_CHANNEL_LOGOUT_EVENT
from oic.oic.message import ProviderConfigurationResponse
from oic.oic.message import RegistrationRequest
from oic.oic.message import RegistrationResponse
from oic.oic.provider import FailedAuthentication
from oic.oic.provider import InvalidRedirectURIError
from oic.utils.http_util import Response
from oic.utils.jwt import JWT
from oic.utils.keyio import key_summary
from oic.utils.keyio import keyjar_init
from otest.events import EV_EXCEPTION
from otest.events import EV_FAULT
from otest.events import EV_HTTP_RESPONSE
from otest.events import EV_PROTOCOL_REQUEST
from otest.events import EV_REQUEST

__author__ = 'roland'

logger = logging.getLogger(__name__)

_jwks = {
    "keys": [
        {
            "kty": "RSA",
            "use": "sig",
            "kid": "cnFLaGVXb2E5WDF6b3dhN1QtdFFNRERMTFVGYWVBV0R1YldEWF9YM1dHTQ",
            "e": "AQAB",
            "n":
                "1duh4rXVoTxfJQutNcFR9GavPhWi2e3IqaVtIeWJ64Bdp6AxgmI5eAoaYHRMivpAfbynvB1b8G5Xoe59dfVBuhH5UScy8HFDPZknNMKTnTpyXbreOc7GmH7VPYYmK076w4oFUa76jx2V6Cm60o1enXlM9AbVrJ3llZA-eJYqvLaG2QNf63hVCpDr0a2WgSS2tk7Mu_o73SSu5tV_zLPN2efQF_e25iyMZqzEWZaMc0d4pJNXS9czXtpnumOHnxS5rps6933K50KRn2WJ9_jy65wo9w4dnmrxtxR7TaRxr2qYZUF8CKddfSOBueKjJZF_3DXWH9WhuCSyaaKtNKYFGQ",
            "d":
                "omkxEUZ8nf2GWFD80yUkw1I0ZhbyXUTrLoMWVTbIPlR3S7UpxFYqRNKPY48PDkCtN5BNZlx5lSeHX9AJ8co3h0LdL9dwJRAvO5mTH8thZXecoTgoSoiRZAB2m0nEtQE_Cb9I-NbFLGkQjocafYqlPzx-x5hlL7meQK6R8uxAOp2T3sl9joK5JfFr9cChZBwPjvN-8hk6NHjveHv5upQ11KVXrwoOgmCIiEFi9jyfc7mqdQlKng5CJ_uXwKdbnLyFPmx7q1Ny4WC13QRighsbKRapN-O5EAxV7mUx3LWPFOakccicl_qPxT2l4-98hqFyu15yT_0NWa25mGd0WlGSsQ",
            "p":
                "9_0BM2D5iJHQs1Qw23HEwEH3ayryaENdmaHIn8gQK38EqSdhPRDoyo0mOkmiNYItljpTPtSt0EOjA4mJRvHW2xnt7zI_DSLbcnFOBvurP0nnB4w1CXj8eiY7qqRnJsxobbkyZwFIjpbh_x2GDGU4wAJ3N5vUFDk0FbDqDn_9E4U",
            "q":
                "3MRZ9mO-B7zKw_T0H0nr8PIV6hllSzHxpsYPB3TA7gcdAVFezJnYmMjdsMzmaEYXt9KhP7WDM-2pQsRIIhJzZggQUwyy4wsfqo_C9ty7_l3W1v9fpluwWIk-fdmt5XgHbpHsmQkAA4OPJXkwJrv-z_yh54QTgdOWR5Wxe2AyrYU"
        },
        {
            "kty": "EC",
            "use": "sig",
            "kid": "VWwxRnNkU1RSZkVHVWNVdlBjYm91RmxHYmxMZFUzaTdHbEpaS01PM04tSQ",
            "crv": "P-256",
            "x": "Vea7gThpgaXoQ6_gPHAeixsIOuw6Bg3CHVhNFvzc8r4",
            "y": "Zgw4yPTZijqd1vpSWngiwE6HeX6l6btlsQHocqhmbPU",
            "d": "_I10xkdtyAHCaPIQL1dQ5TDyvPaflHCt57jxmwJ__Uk"
        },
        {
            "kty": "EC",
            "use": "sig",
            "kid": "STJCVHRHQzJJc3ExUDlzcF9RWktfTGlzb1JPSG5MX0VfTnBMbk8tVEhrOA",
            "crv": "P-384",
            "x":
                "j_6EIot-EyPqCo19iBDe6qQS8dHPFhElUnQh_ODxbi9TKkFTdNzeKgK2JXlgmSlA",
            "y": "ToI0SOGZgfhSO0DHPnNIguQlXIa54rP1fw-5UIcYOiKn4WgvIczf31UCG"
                 "-YN_snW",
            "d": "PX2PsP8ZVaoc-XcsFrFbnIs4eJzc6XwPq3GHNF-KCOL2EHxnYX066"
                 "-S1g9G_XM1Q"
        }
    ]
}


class TestError(Exception):
    pass


def unwrap_exception(err):
    while True:  # Exception wrapped in ..
        if not isinstance(err.args, tuple):
            err = err.args
            break
        elif isinstance(err.args[0], Exception):
            err = err.args[0]
        elif len(err.args) > 1 and isinstance(err.args[1], Exception):
            err = err.args[1]
        elif len(err.args) == 1:
            err = err.args[0]
            break
        else:
            err = '{}:{}'.format(*err.args)  # Is this a fair assumption ??
            break
    return err


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

        self.behavior_type = []

    def make_id_token(self, session, loa="2", issuer="",
                      alg="RS256", code=None, access_token=None,
                      user_info=None, auth_time=0, exp=None, extra_claims=None):
        idt = oic.Server.make_id_token(self, session, loa, issuer, alg, code,
                                       access_token, user_info, auth_time,
                                       exp, extra_claims)

        if "ath" in self.behavior_type:  # modify the at_hash if available
            try:
                idt["at_hash"] = sort_string(idt["at_hash"])
            except KeyError:
                raise TestError("Missing at_hash in id_token")

        if "math" in self.behavior_type:  # remove the at_hash if available
            if "at_hash" in idt:
                del idt['at_hash']

        if "ch" in self.behavior_type:  # modify the c_hash if available
            try:
                idt["c_hash"] = sort_string(idt["c_hash"])
            except (KeyError, TypeError):
                pass

        if "mch" in self.behavior_type:  # remove the c_hash if available
            if "c_hash" in idt:
                del idt['c_hash']

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
                 verify_ssl=True, capabilities=None, client_cert=None,
                 logout_path='', **kwargs):

        provider.Provider.__init__(
            self, name, sdb, cdb, authn_broker, userinfo, authz, client_authn,
            symkey=symkey, urlmap=urlmap, keyjar=keyjar, hostname=hostname,
            template_lookup=template_lookup, template=template,
            verify_ssl=verify_ssl, capabilities=capabilities,
            client_cert=client_cert, logout_path=logout_path)

        self.claims_type = ["normal"]
        self.behavior_type = []
        self.server = Server(keyjar=keyjar, ca_certs=ca_certs,
                             verify_ssl=verify_ssl)
        self.server.behavior_type = self.behavior_type
        self.claim_access_token = {}
        self.init_keys = []
        self.update_key_use = ""
        for param in ['jwks_name', 'jwks_uri', 'sso_ttl']:
            try:
                setattr(self, param, kwargs[param])
            except KeyError:
                pass
        self.jwx_def = {}
        self.build_jwx_def()
        self.other = 'https://example.com/op'
        self.keyjar.import_jwks(_jwks, self.other)

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
            self.events.store("New signing keys", new_keys)
            self.do_key_rollover(new_keys, "%d")
            self.events.store("Rotated signing keys", '')

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

    def create_providerinfo(self, setup=None):
        _response = provider.Provider.create_providerinfo(self, setup)

        if "isso" in self.behavior_type:
            _response["issuer"] = "https://example.com"

        return _response

    def _split_query(self, uri):
        base, query = splitquery(uri)
        if query:
            return base, parse_qs(query)
        else:
            return base, None

    def registration_endpoint(self, request, authn=None, **kwargs):
        try:
            reg_req = RegistrationRequest().deserialize(request, "json")
        except ValueError:
            reg_req = RegistrationRequest().deserialize(request)

        self.events.store(EV_PROTOCOL_REQUEST, reg_req)
        try:
            response_type_cmp(kwargs['test_cnf']['response_type'],
                              reg_req['response_types'])
        except KeyError:
            pass

        try:
            provider.Provider.verify_redirect_uris(reg_req)
        except InvalidRedirectURIError as err:
            return error_response(
                error="invalid_configuration_parameter",
                descr="Invalid redirect_uri: {}".format(err))

        if "initiate_login_uri" in self.behavior_type:
            if not "initiate_login_uri" in reg_req:
                return error_response(
                    error="invalid_configuration_parameter",
                    descr="No \"initiate_login_uri\" endpoint found in the "
                          "Client Registration Request\"")

        # Do initial verification that all endpoints from the client uses
        #  https
        for endp in ["jwks_uri", "initiate_login_uri"]:
            try:
                uris = reg_req[endp]
            except KeyError:
                continue

            if not isinstance(uris, list):
                uris = [uris]
            for uri in uris:
                if not uri.startswith("https://"):
                    return error_response(
                        error="invalid_configuration_parameter",
                        descr="Non-HTTPS endpoint in '{}'".format(endp))

        if not "contacts" in reg_req:
            return error_response(
                error="invalid_configuration_parameter",
                descr="No \"contacts\" claim provided in registration request.")
        elif not "@" in reg_req["contacts"][0]:
            return error_response(
                error="invalid_configuration_parameter",
                descr="First address in \"contacts\" value in registration "
                      "request is not a valid e-mail address.")

        _response = provider.Provider.registration_endpoint(self, request,
                                                            authn, **kwargs)
        self.events.store(EV_HTTP_RESPONSE, _response)
        self.init_keys = []
        if "jwks_uri" in reg_req:
            if _response.status_code == 200:
                # find the client id
                req_resp = RegistrationResponse().from_json(
                    _response.message)
                for kb in self.keyjar[req_resp["client_id"]]:
                    if kb.imp_jwks:
                        self.events.store("Client JWKS", kb.imp_jwks)

        return _response

    def response_mode(self, areq, fragment_enc, **kwargs):
        resp_mode = areq["response_mode"]
        if resp_mode == "form_post":
            context = {
                'action': kwargs['redirect_uri'],
                'inputs': kwargs['aresp'],
            }
            return Response(self.template_renderer('form_post', context),
                            headers=kwargs["headers"])
        elif resp_mode == 'fragment' and not fragment_enc:
            # Can't be done
            raise InvalidRequest("wrong response_mode")
        elif resp_mode == 'query' and fragment_enc:
            # Can't be done
            raise InvalidRequest("wrong response_mode")
        return None

    def authorization_endpoint(self, request="", cookie=None, **kwargs):
        if isinstance(request, dict):
            _req = request
        else:
            _req = {}
            for key, val in parse_qs(request).items():
                if len(val) == 1:
                    _req[key] = val[0]
                else:
                    _req[key] = val

        # self.events.store(EV_REQUEST, _req)

        try:
            _scope = _req["scope"]
        except KeyError:
            return error_response(
                error="incorrect_behavior",
                descr="No scope parameter"
            )
        else:
            # verify that openid is among the scopes
            _scopes = _scope.split(" ")
            if "openid" not in _scopes:
                return error_response(
                    error="incorrect_behavior",
                    descr="Scope does not contain 'openid'"
                )

        client_id = _req["client_id"]

        try:
            f = response_type_cmp(self.capabilities['response_types_supported'],
                                  _req['response_type'])
        except KeyError:
            pass
        else:
            if f is False:
                self.events.store(
                    EV_FAULT,
                    'Wrong response type: {}'.format(_req['response_type']))
                return error_response(error="incorrect_behavior",
                                      descr="Not supported response_type")

        _rtypes = _req['response_type'].split(' ')

        if 'id_token' in _rtypes:
            try:
                self._update_client_keys(client_id)
            except TestError:
                return error_response(error="incorrect_behavior",
                                      descr="No change in client keys")

        if isinstance(request, dict):
            request = urlencode(request)

        if "max_age" in _req and _req["max_age"] == "0" and "prompt" in _req \
                and \
                _req["prompt"] == "none":
            aresp = {
                "error": "login_required",
            }
            if "state" in _req:
                aresp['state'] = _req["state"]

            return self.response_mode(_req, False,
                                      aresp=aresp,
                                      redirect_uri=_req['redirect_uri'],
                                      headers={})
        else:
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
            self.events.store("New encryption keys", new_keys)
            self.do_key_rollover(new_keys, "%d")
            self.events.store("Rotated encryption keys", '')
            logger.info(
                'Rotated OP enc keys, new set: {}'.format(
                    key_summary(self.keyjar, '')))

        # This is just for logging purposes
        try:
            _resp = self.server.http_request(_req["request_uri"])
        except KeyError:
            pass
        except requests.ConnectionError as err:
            self.events.store(EV_EXCEPTION, err)
            err = unwrap_exception(err)
            return error_response(error="server_error", descr=err)
        else:
            if _resp.status_code == 200:
                self.events.store(EV_REQUEST,
                                  "Request from request_uri: {}".format(
                                      _resp.text))

        return _response

    def token_endpoint(self, request="", authn=None, dtype='urlencoded',
                       **kwargs):
        try:
            req = AccessTokenRequest().deserialize(request, dtype)
            client_id = self.client_authn(self, req, authn)
        except FailedAuthentication as err:
            logger.error(err)
            self.events.store(EV_EXCEPTION,
                              "Failed to verify client due to: {}".format(err))
            return error_response(error="invalid_client", descr=err.args[0])
        except Exception as err:
            logger.error(err)
            self.events.store(EV_EXCEPTION,
                              "Failed to verify client due to: %s" % err)
            return error_response(error="invalid_client",
                                  descr="Failed to verify client: {}".format(
                                      err))

        try:
            self._update_client_keys(client_id)
        except TestError:
            logger.error('No change in client keys')
            return error_response(error="incorrect_behavior",
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
                    self.events.store("Updating client keys")
                    kb.update()
                    if kb.imp_jwks:
                        self.events.store(
                            "Client JWKS", kb.imp_jwks)
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
                                self.events.store('Key change',
                                                  "New key: {}".format(key))
                if same == len(self.init_keys):  # no change
                    self.events.store("No change in keys")
                    raise TestError("Keys unchanged")
                else:
                    self.events.store('Key change',
                                      "{} changed, {} the same".format(
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

    def end_session_endpoint(self, request="", cookie=None, **kwargs):
        return provider.Provider.end_session_endpoint(self, request, cookie,
                                                      **kwargs)

    def do_back_channel_logout(self, cinfo, sub, sid):
        try:
            back_channel_logout_uri = cinfo['backchannel_logout_uri']
        except KeyError:
            return None

        # always include sub and sid so I don't check for
        # backchannel_logout_session_required

        payload = {
            'sub': sub, 'sid': sid,
        }

        if 'no_event' in self.behavior_type:
            pass
        elif 'wrong_event' in self.behavior_type:
            payload['events'] = {"http://schemas.openid.net/event/foobar": {}}
        else:
            payload['events'] = {BACK_CHANNEL_LOGOUT_EVENT: {}}

        if 'with_nonce' in self.behavior_type:
            payload['nonce'] = rndstr(16)

        try:
            alg = cinfo['id_token_signed_response_alg']
        except KeyError:
            alg = self.capabilities['id_token_signing_alg_values_supported'][0]

        if 'wrong_alg' in self.behavior_type:
            # figure out a alg I could use but that are not the one used
            # for ID Tokens. Pick one from id_token_signing_alg_values_supported
            if alg.startswith('RS'):
                alg = 'ES256'
            elif alg.startswith('ES'):
                alg = 'RS256'
            else:  # probably HS*
                alg = 'RS256'
        elif 'alg_none' in self.behavior_type:
            alg = 'none'

        if 'wrong_issuer' in self.behavior_type:
            iss = self.other
        else:
            iss = self.name

        if 'wrong_aud' in self.behavior_type:
            aud = self.other
        else:
            aud = cinfo["client_id"]

        _jws = JWT(self.keyjar, iss=iss, lifetime=86400, sign_alg=alg)

        if self.events:
            kw = {'iss': iss, 'sign_alg': alg, 'aud': aud}
            kw.update(payload)
            self.events.store('Logout token', '{}'.format(kw))

        _jws.with_jti = True
        sjwt = _jws.pack(aud=cinfo["client_id"], **payload)

        return back_channel_logout_uri, sjwt

    def do_front_channel_logout_iframe(self, c_info, iss, sid):
        if 'wrong_issuer' in self.behavior_type:
            iss = self.other
        if 'wrong_sid' in self.behavior_type:
            sid = 'another_sid'

        _iframe = provider.Provider.do_front_channel_logout_iframe(c_info, iss, sid)
        return _iframe

    def do_verified_logout(self, sid, client_id, alla = False, **kwargs):
        # Remove the logout uri that should not be used.
        if "back" in self.behavior_type:
            try:
                del self.cdb[client_id]["frontchannel_logout_uri"]
            except KeyError:
                pass
        elif "front" in self.behavior_type:
            try:
                del self.cdb[client_id]["backchannel_logout_uri"]
            except KeyError:
                pass

        return provider.Provider.do_verified_logout(self, sid, client_id, alla, **kwargs)
