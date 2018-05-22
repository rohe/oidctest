import hashlib
import logging
import os

from jwkest import as_bytes
from oic import oic
from oic import rndstr
from oic.exception import PyoidcError
from oic.exception import RequestError
from oic.oauth2 import ErrorResponse
from oic.oauth2.exception import MissingRequiredAttribute
from oic.oic import OpenIDSchema
from oic.oic import UserInfoErrorResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

__author__ = 'roland'

logger = logging.getLogger(__name__)


class Client(oic.Client):
    def __init__(self, *args, **kwargs):
        oic.Client.__init__(self, *args, **kwargs)

    def generate_request_uris(self, request_dir):
        """
        Need to generate a path that is unique for the OP combo.
        This is before there is a client_id.

        :return: A list of uris
        """
        m = hashlib.sha256()
        m.update(as_bytes(self.provider_info['issuer']))
        m.update(as_bytes(self.base_url))
        frag = rndstr()
        return '{}{}/{}#{}'.format(self.base_url, request_dir, m.hexdigest(),
                                   frag)

    def filename_from_webname(self, webname):
        _filedir = self.requests_dir
        if not os.path.isdir(_filedir):
            os.makedirs(_filedir)

        assert webname.startswith(self.base_url)
        _name = webname.split('#')  # remove frag if there is one
        return _name[0][len(self.base_url):]

    def do_user_info_request(self, method="POST", state="", scope="openid",
                             request="openid", **kwargs):

        kwargs["request"] = request
        path, body, method, h_args = self.user_info_request(method, state,
                                                            scope, **kwargs)

        logger.debug(
            "[do_user_info_request] PATH:{} BODY:{} H_ARGS: {}".format(path,
                                                                       body,
                                                                       h_args))

        if self.events:
            self.events.store('Request', {'body': body})
            self.events.store('request_url', path)
            self.events.store('request_http_args', h_args)

        try:
            resp = self.http_request(path, method, data=body, **h_args)
        except MissingRequiredAttribute:
            raise

        if resp.status_code == 200:
            try:
                assert "application/json" in resp.headers["content-type"]
                sformat = "json"
            except AssertionError:
                assert "application/jwt" in resp.headers["content-type"]
                sformat = "jwt"
        elif resp.status_code == 500:
            raise PyoidcError("ERROR: Something went wrong: %s" % resp.text)
        elif 400 <= resp.status_code < 500:
            # the response text might be a OIDC message
            try:
                res = ErrorResponse().from_json(resp.text)
            except Exception:
                raise RequestError(resp.text)
            else:
                self.store_response(res, resp.text)
                return res
        else:
            raise PyoidcError("ERROR: Something went wrong [%s]: %s" % (
                resp.status_code, resp.text))

        try:
            _schema = kwargs["user_info_schema"]
        except KeyError:
            _schema = OpenIDSchema

        logger.debug("Reponse text: '{}'".format(resp.text))

        _txt = resp.text
        if sformat == "json":
            res = _schema().from_json(txt=_txt)
        else:
            verify = kwargs.get('verify', True)
            res = _schema().from_jwt(_txt, keyjar=self.keyjar,
                                     sender=self.provider_info["issuer"], verify=verify)

        if 'error' in res:  # Error response
            res = UserInfoErrorResponse(**res.to_dict())

        # TODO verify issuer:sub against what's returned in the ID Token

        self.store_response(res, _txt)

        return res


def make_client(**kw_args):
    """
    Have to get own copy of keyjar

    :param kw_args:
    :return:
    """
    c_keyjar = kw_args["keyjar"].copy()
    args = {'client_authn_method': CLIENT_AUTHN_METHOD, 'keyjar': c_keyjar}
    try:
        args['verify_ssl'] = kw_args['verify_ssl']
    except KeyError:
        pass

    _cli = Client(**args)

    c_info = {'keyjar': c_keyjar}
    for arg, val in list(kw_args.items()):
        if arg in ['keyjar']:
            continue
        setattr(_cli, arg, val)
        c_info[arg] = val

    return _cli, c_info
