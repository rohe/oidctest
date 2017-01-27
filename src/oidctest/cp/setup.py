import logging
import os
import shelve
import importlib
import sys

from oic.utils.authn.authn_context import AuthnBroker
from oic.utils.authn.client import verify_client
from oic.utils.authz import AuthzHandling
from oic.utils.keyio import keyjar_init
from oic.utils.sdb import SessionDB
from oic.utils.userinfo import UserInfo

from oidctest.endpoints import add_endpoints
from oidctest.endpoints import ENDPOINTS
from oidctest.rp.provider import Provider

LOGGER = logging.getLogger(__name__)

__author__ = 'roland'


def main_setup(args, lookup=None):
    sys.path.insert(0, ".")
    config = importlib.import_module(args.config)
    if args.path:
        if config.baseurl.endswith('/'):
            config.issuer = '{}{}/'.format(config.baseurl, args.path)
        else:
            config.issuer = '{}/{}/'.format(config.baseurl, args.path)
    elif args.port:
        if config.baseurl.endswith('/'):
            config.issuer = '{}:{}/'.format(config.baseurl[:-1], args.port)
        else:
            config.issuer = '{}:{}/'.format(config.baseurl, args.port)

    _baseurl = config.issuer

    if not _baseurl.endswith("/"):
        _baseurl += "/"

    #config.issuer = config.issuer % args.port
    #config.SERVICE_URL = config.SERVICE_URL % args.port

    # Client data base
    cdb = shelve.open(config.CLIENT_DB, writeback=True)

    ac = AuthnBroker()

    for authkey, value in list(config.AUTHENTICATION.items()):
        authn = None
        # if "UserPassword" == authkey:
        #     from oic.utils.authn.user import UsernamePasswordMako
        #     authn = UsernamePasswordMako(None, "login.mako", LOOKUP, PASSWD,
        #                                  "authorization")

        if "NoAuthn" == authkey:
            from oic.utils.authn.user import NoAuthn

            authn = NoAuthn(None, user=config.AUTHENTICATION[authkey]["user"])

        if authn is not None:
            ac.add(config.AUTHENTICATION[authkey]["ACR"], authn,
                   config.AUTHENTICATION[authkey]["WEIGHT"])

    # dealing with authorization
    authz = AuthzHandling()

    if config.USERINFO == "SIMPLE":
        # User info is a simple dictionary in this case statically defined in
        # the configuration file
        userinfo = UserInfo(config.USERDB)
    else:
        userinfo = None

    com_args = {
        "name": config.issuer,
        "baseurl": _baseurl,
        "cdb": cdb,
        "authn_broker": ac,
        "userinfo": userinfo,
        "authz": authz,
        "client_authn": verify_client,
        "symkey": config.SYM_KEY,
        "template_lookup": lookup,
        "template": {"form_post": "form_response.mako"},
        "jwks_name": "./static/jwks_{}.json"
    }

    # Should I care about verifying the certificates used by other entities
    if args.insecure:
        com_args["verify_ssl"] = False
    else:
        com_args["verify_ssl"] = True

    try:
        assert os.path.isfile(config.SERVER_CERT)
        assert os.path.isfile(config.SERVER_KEY)
        com_args['client_cert'] = (config.SERVER_CERT, config.SERVER_KEY)
    except AttributeError:
        pass
    except AssertionError:
        print("Can't access client certificate and/or client secret")
        exit(-1)

    op_arg = {}

    try:
        op_arg["cookie_ttl"] = config.COOKIETTL
    except AttributeError:
        pass

    try:
        op_arg["cookie_name"] = config.COOKIENAME
    except AttributeError:
        pass

    # print URLS
    if args.debug:
        op_arg["debug"] = True

    # All endpoints the OpenID Connect Provider should answer on
    add_endpoints(ENDPOINTS)
    op_arg["endpoints"] = ENDPOINTS

    op_arg["baseurl"] = _baseurl

    # Add own keys for signing/encrypting JWTs
    try:
        # a throw-away OP used to do the initial key setup
        _op = Provider(sdb=SessionDB(com_args["baseurl"]), **com_args)
        jwks = keyjar_init(_op, config.keys)
    except KeyError:
        pass
    else:
        op_arg["jwks"] = jwks
        op_arg['keyjar'] = _op.keyjar
        #op_arg["keys"] = config.keys

    try:
        op_arg["marg"] = multi_keys(com_args, config.multi_keys)
    except AttributeError as err:
        pass

    return com_args, op_arg, config


def multi_keys(com_args, key_conf):
    # a throw-away OP used to do the initial key setup
    _op = Provider(sdb=SessionDB(com_args["baseurl"]), **com_args)
    jwks = keyjar_init(_op, key_conf, "m%d")

    return {"jwks": jwks, "keys": key_conf}
