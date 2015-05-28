import logging
import os
from urlparse import urlparse
from aatest.operation import Operation

from oic.oauth2 import rndstr
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.oic import AccessTokenResponse
from oidctest.prof_util import WEBFINGER
from oidctest.prof_util import DISCOVER
from oidctest.prof_util import REGISTER
from oidctest.request import SyncGetRequest, SyncPostRequest
from oidctest.request import SyncRequest

__author__ = 'roland'

logger = logging.getLogger(__name__)


def include(url, test_id):
    p = urlparse(url)
    if p.path[1:].startswith(test_id):
        if len(p.path[1:].split("/")) <= 1:
            return os.path.join(url, "_/_/_/normal")
        else:
            return url

    return "%s://%s/%s%s_/_/_/normal" % (p.scheme, p.netloc, test_id, p.path)



class Webfinger(Operation):
    def __init__(self, conv, profile, test_id, conf, funcs):
        Operation.__init__(self, conv, profile, test_id, conf, funcs)
        self.resource = ""
        self.dynamic = self.profile[WEBFINGER] == "T"

    def __call__(self):
        if not self.dynamic:
            self.conv["issuer"] = self.conf.INFO["srv_discovery_url"]
        else:
            self.conv.trace.info(
                "Discovery of resource: {}".format(self.resource))
            issuer = self.conv.client.discover(self.resource)
            self.conv.trace.reply(issuer)
            self.conv.info["issuer"] = issuer

    def setup(self, profile_map):
        self.map_profile(profile_map)
        self._setup()

        try:
            self.resource = self.op_args["resource"]
        except KeyError:
            self.resource = self.conf.ISSUER+self.test_id


class Discovery(Operation):
    def __init__(self, conv, session, test_id, conf, funcs):
        Operation.__init__(self, conv, session, test_id, conf, funcs)

        self.dynamic = self.profile[DISCOVER] == "T"

    def __call__(self):
        if self.dynamic:
            self.catch_exception(self.conv.client.provider_config,
                                 **self.op_args)
        else:
            self.conv.client.provider_info = ProviderConfigurationResponse(
                **self.conf.INFO["provider_info"]
            )

    def setup(self, profile_map):
        self.map_profile(profile_map)
        self._setup()

        if self.dynamic:
            try:
                _issuer = include(self.op_args["issuer"], self.test_id)
            except KeyError:
                _issuer = include(self.conv.info["issuer"], self.test_id)

            self.op_args["issuer"] = _issuer


class Registration(Operation):
    def __init__(self, conv, session, test_id, conf, funcs):
        Operation.__init__(self, conv, session, test_id, conf, funcs)

        self.dynamic = self.profile[REGISTER] == "T"

    def __call__(self):
        if self.dynamic:
            self.catch_exception(self.conv.client.register, **self.req_args)
        else:
            self.conv.client.store_registration_info(
                RegistrationResponse(**self.conf.INFO["registered"]))

    def setup(self, profile_map):
        self.map_profile(profile_map)
        self._setup()

        if self.dynamic:
            self.req_args.update(self.conf.INFO["client"])
            self.req_args["url"] = self.conv.client.provider_info[
                "registration_endpoint"]


class SyncAuthn(SyncGetRequest):
    response_cls = "AuthorizationResponse"
    request_cls = "AuthorizationRequest"

    def __init__(self, conv, session, test_id, conf, funcs):
        SyncGetRequest.__init__(self, conv, session, test_id, conf, funcs)
        self.op_args["endpoint"] = conv.client.provider_info[
            "authorization_endpoint"]

        conv.state = rndstr()
        self.req_args["state"] = conv.state
        conv.nonce = rndstr()
        self.req_args["nonce"] = conv.nonce

    def setup(self, profile_map):
        self.map_profile(profile_map)
        self._setup()

        self.req_args["redirect_uri"] = self.conv.callback_uris[0]


class AccessToken(SyncPostRequest):
    def __init__(self, conv, session, test_id, conf, funcs):
        Operation.__init__(self, conv, session, test_id, conf, funcs)
        self.op_args["state"] = conv.state
        self.req_args["redirect_uri"] = conv.client.redirect_uris[0]

    def __call__(self):
        self.conv.trace.info(
            "Access Token Request with op_args: {}, req_args: {}".format(
                self.op_args, self.req_args))
        atr = self.conv.client.do_access_token_request(
            request_args=self.req_args, **self.op_args)
        self.conv.trace.response(atr)
        assert isinstance(atr, AccessTokenResponse)


class UserInfo(SyncGetRequest):
    def __init__(self, conv, session, test_id, conf, args):
        Operation.__init__(self, conv, session, test_id, conf, args)
        self.op_args["state"] = conv.state

    def __call__(self):
        user_info = self.conv.client.do_user_info_request(**self.op_args)
        assert user_info
        self.conv.client.userinfo = user_info


class DisplayUserInfo(Operation):
    pass
