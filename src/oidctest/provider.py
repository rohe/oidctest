import json
from oic import oic
import time
import urlparse

from Crypto.PublicKey import RSA
from jwkest.ecc import P256
from jwkest.jwk import RSAKey, ECKey
from oic.oauth2 import Message, rndstr
from oic.oic import provider, ProviderConfigurationResponse
from oic.oic.message import RegistrationRequest
from oic.utils.keyio import keyjar_init


__author__ = 'roland'

class TestError(Exception):
    pass


def sort_string(string):
    if string is None:
        return ""

    _l = list(string)
    _l.sort()
    return "".join(_l)


class Server(oic.Server):
    def __init__(self, keyjar=None, ca_certs=None, verify_ssl=True):
        oic.Server.__init__(self, keyjar, ca_certs, verify_ssl)

        self.behavior_type = {}

    def make_id_token(self, session, loa="2", issuer="",
                      alg="RS256", code=None, access_token=None,
                      user_info=None, auth_time=0, exp=None, extra_claims=None):
        idt = oic.Server.make_id_token(self, session, loa, issuer, alg, code,
                                       access_token, user_info, auth_time, exp,
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
                raise TestError("Missing c_hash in id_token")

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
            self, name, sdb, cdb, authn_broker, userinfo, authz, client_authn,
            symkey, urlmap, ca_certs, keyjar, hostname, template_lookup,
            template, verify_ssl, capabilities)

        self.claims_type = ["normal"]
        self.behavior_type = []
        self.server = Server(ca_certs=ca_certs, verify_ssl=verify_ssl)
        self.server.behavior_type = self.behavior_type
        self.claim_access_token = {}

    def sign_encrypt_id_token(self, sinfo, client_info, areq, code=None,
                              access_token=None, user_info=None):
        self._update_client_keys(client_info["client_id"])

        return provider.Provider.sign_encrypt_id_token(self, sinfo, client_info, areq, code,
                              access_token, user_info)

    def id_token_as_signed_jwt(self, session, loa="2", alg="", code=None,
                               access_token=None, user_info=None, auth_time=0,
                               exp=None, extra_claims=None):

        if "rotsig" in self.behavior_type:  # Rollover signing keys
            if alg == "RS256":
                key = RSAKey(kid="rotated_rsa_{}".format(time.time()),
                             use="sig").load_key(RSA.generate(2048))
            elif alg == "ES256":
                key = ECKey(kid="rotated_ec_{}".format(time.time()),
                            use="sig").load_key(P256)

            new_key = {"keys": [key.serialize(private=True)]}
            self.do_key_rollover(new_key, "%d")

        if "nokid1jwk" in self.behavior_type:
            if not alg == "HS256":
                found_key = None
                for key in self.keyjar.issuer_keys[""]:
                    issuer_key = key.keys()[0]
                    if issuer_key.use == "sig" and issuer_key.kty.startswith(alg[:2]):
                        issuer_key.kid = None
                        found_key = key
                        break
                self.keyjar.issuer_keys[""] = [found_key]

        if "nokidmuljwks" in self.behavior_type:
            for key in self.keyjar.issuer_keys[""]:
                for inner_key in key.keys():
                    inner_key.kid = None

        _jws = provider.Provider.id_token_as_signed_jwt(
            self, session, loa=loa, alg=alg, code=code,
            access_token=access_token, user_info=user_info, auth_time=auth_time,
            exp=exp, extra_claims=extra_claims)

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
            _tok = rndstr()
            self.claim_access_token[_tok] = {"age": 30}
            ava["_claim_names"] = Message(age=_src)
            d_claims = {_src: {"endpoint": urlbase + "claim", "access_token": _tok}}
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

        # Do initial verification that all endpoints from the client uses https
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

        return provider.Provider.registration_endpoint(self, request, authn,
                                                       **kwargs)

    def authorization_endpoint(self, request="", cookie=None, **kwargs):
        _req = urlparse.parse_qs(request)

        if "openid" in self.behavior_type:
            # verify that openid is among the scopes
            if "openid" not in _req["scope"]:
                return self._error(
                    error="invalid_request",
                    descr="Scope does not contain 'openid'"
                )
        client_id = _req["client_id"][0]
        self._update_client_keys(client_id)

        return provider.Provider.authorization_endpoint(self, request, cookie,
                                                        **kwargs)

    def generate_jwks(self, mode):
        if "rotenc" in self.behavior_type:  # Rollover encryption keys
            rsa_key = RSAKey(kid="rotated_rsa_{}".format(time.time()),
                             use="enc").load_key(RSA.generate(2048))
            ec_key = ECKey(kid="rotated_ec_{}".format(time.time()),
                           use="enc").load_key(P256)

            keys = [rsa_key.serialize(private=True),
                    ec_key.serialize(private=True)]
            new_keys = {"keys": keys}
            self.do_key_rollover(new_keys, "%d")

            signing_keys = [k.to_dict() for k in self.keyjar.get_signing_key()]
            new_keys["keys"].extend(signing_keys)
            return json.dumps(new_keys)
        elif "nokid1jwk" in self.behavior_type:
            alg = mode["sign_alg"]
            if not alg:
                alg = "RS256"
            keys = [k.to_dict() for kb in self.keyjar[""] for k in kb.keys()]
            for key in keys:
                if key["use"] == "sig" and key["kty"].startswith(alg[:2]):
                    key.pop("kid", None)
                    jwk = dict(keys=[key])
                    return json.dumps(jwk)
            raise Exception("Did not find sig {} key for nokid1jwk test ".format(alg))
        else:  # Return all keys
            keys = [k.to_dict() for kb in self.keyjar[""] for k in kb.keys()]
            jwks = dict(keys=keys)
            return json.dumps(jwks)

    def _update_client_keys(self, client_id):
        if "updkeys" in self.behavior_type:
            for kb in self.keyjar[client_id]:
                kb.update()


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