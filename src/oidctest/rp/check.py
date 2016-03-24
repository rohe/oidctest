import inspect
import json
import sys
import requests

from urllib.parse import urlparse

from aatest.check import Check
from aatest.check import ERROR
from aatest.check import WARNING
from aatest.events import EV_PROTOCOL_REQUEST

from oic.oic import AuthorizationRequest
from oic.oic import AccessTokenRequest
from oic.extension.client import RegistrationRequest

from otest.shannon_entropy import calculate

__author__ = 'roland'


class VerifyRegistrationOfflineAccess(Check):
    cid = 'verify-registration-offline-access'
    msg = "Check if offline access is requested"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          RegistrationRequest)

        # 'offline_access only allow if response_type == 'code'
        try:
            req_scope = request['scope']
        except KeyError:
            pass
        else:
            if 'offline_access' in req_scope:
                if request['response_type'] != 'code':
                    self._status = ERROR
                    self._message = 'Offline access not allowed for anything ' \
                                    'but code flow'

        return {}


class VerifyRegistrationResponseTypes(Check):
    cid = 'verify-registration-response_types'
    msg = "Only the allowed"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          RegistrationRequest)

        try:
            resp_types = request['response_types']
        except KeyError:
            pass
        else:
            for typ in resp_types:
                if typ not in self._kwargs:
                    self._status = ERROR
                    self._message = 'Not allowed response type: {}'.format(typ)

        return {}


# class VerifyRegistrationSoftwareStatement(Check):
#     cid = 'verify-registration-software-statement'
#     msg = "Verify that the correct claims appear in the Software statement"
#
#     def _func(self, conv):
#         request = conv.events.get_message(EV_PROTOCOL_REQUEST,
#                                           RegistrationRequest)
#
#         try:
#             _ss = request['software_statement']
#         except KeyError:
#             pass
#         else:
#             missing = []
#             for claim in ['redirect_uris', 'grant_types', 'client_name',
#                           'client_uri']:
#                 if claim not in _ss:
#                     missing.append(claim)
#             if 'jwks_uri' not in _ss and 'jwks' not in _ss:
#                 missing.append('jwks_uri/jwks')
#
#             if missing:
#                 self._status = WARNING
#                 self._message = 'Missing "{}" claims from Software ' \
#                                 'Statement'.format(missing)
#
#         return {}


class VerifyRegistrationRedirectUriScheme(Check):
    cid = 'verify-registration-redirect_uri-scheme'
    msg = "Only certain redirect_uri schemes are allowed"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          RegistrationRequest)

        try:
            ruris = request['redirect_uris']
        except KeyError:
            self._status = ERROR
            self._message = 'MUST register redirect_uris'
        else:
            for ruri in ruris:
                p = urlparse(ruri)
                if p.scheme == 'https':
                    continue
                elif p.scheme == 'http':
                    if 'localhost' != p.netloc.split('.'):
                        self._status = ERROR
                        self._message = 'Not allowed response type'
                        break
                else:  # How do I check for local schemes ?
                    pass

        return {}


class VerifyRegistrationPublicKeyRegistration(Check):
    cid = 'verify-registration-public_key-registration'
    msg = "Public key must be registered"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          RegistrationRequest)

        try:
            _uri = request['jwks_uri']
        except KeyError:
            try:
                jwks = request['jwks']
            except KeyError:
                self._status = ERROR
                self._message = 'Must register a public key'
            else:
                pub = 0
                for desc in jwks['keys']:
                    if desc['kty'] in ['RSA', 'EC']:
                        pub += 1
                if pub == 0:
                    self._status = ERROR
                    self._message = 'Must register a public key'
        else:
            resp = requests.request('GET', _uri, verify=False)
            if resp.status_code == 200:
                jwks = json.loads(resp.text)
                pub = 0
                for desc in jwks['keys']:
                    if desc['kty'] in ['RSA', 'EC']:
                        pub += 1
                if pub == 0:
                    self._status = ERROR
                    self._message = 'Must register a public key'
            else:
                self._status = ERROR
                self._message = 'Failed to access the RP keys at {}'.format(
                    _uri)

        return {}


# class VerifyRegistrationArguments(Check):
#     cid = 'verify-registration-arguments'
#     msg = "Verify registration parameters"
#
#     def _func(self, conv):
#         request = conv.events.get_message(EV_PROTOCOL_REQUEST,
#                                           RegistrationRequest)
#
#         for key, val in self._kwargs.items():
#             if val:
#
#             else:
#                 if key not in request:
#                     self._status = WARNING
#                     self._message = 'Missing "{}" argument in
# request'.format(missing)
#
#
#         return {}


class VerifyAuthorizationOfflineAccess(Check):
    cid = 'verify-authorization-offline-access'
    msg = "Check if offline access is requested"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          AuthorizationRequest)

        try:
            req_scopes = request['scope']
        except KeyError:
            pass
        else:
            if 'offline_access' in req_scopes:
                if request['response_type'] != ['code']:
                    self._status = ERROR
                    self._message = 'Offline access only when using "code" flow'

        return {}


class VerifyAuthorizationStateEntropy(Check):
    cid = 'verify-authorization-state-entropy'
    msg = "Check if offline access is requested"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          AuthorizationRequest)

        bits = calculate(request['state'])
        if bits < 128:
            self._status = WARNING
            self._message = 'Not enough entropy in string: {} < 128'.format(
                bits)
        return {}


class VerifyAuthorizationRedirectUri(Check):
    cid = 'verify-authorization-redirect_uri'
    msg = "Check if offline access is requested"

    def _func(self, conv):
        clireq_request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                                 RegistrationRequest)
        authz_request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                                AuthorizationRequest)

        if authz_request['redirect_uri'] not in clireq_request['redirect_uris']:
            self._status = ERROR
            self._message = 'Redirect_uri not registered'

        return {}


class VerifyTokenRequestClientAssertion(Check):
    cid = 'verify-token-request-client_assertion'
    msg = "Check that the client_assertion JWT contains expected claims"

    def _func(self, conv):
        request = conv.events.get_message(EV_PROTOCOL_REQUEST,
                                          AccessTokenRequest)

        ca = request['parsed_client_assertion']
        missing = []
        for claim in ["iss", "sub", "aud", "iat", "exp", "jti"]:
            if claim not in ca:
                missing.append(claim)

        if missing:
            self._status = ERROR
            self._message = 'Redirect_uri not registered'

        # verify jti entropy
        bits = calculate(ca['jti'])
        if bits < 128:
            self._status = WARNING
            self._message = 'Not enough entropy in string: {} < 128'.format(
                bits)

        return {}


def factory(cid):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Check):
            try:
                if obj.cid == cid:
                    return obj
            except AttributeError:
                pass

    return None
