#!/usr/bin/env python


import importlib
import json
import os
import argparse
import logging
import sys

from future.backports.urllib.parse import urlparse

from oic.utils.keyio import build_keyjar
from oic.oic.message import factory as oic_message_factory

from aatest.parse_cnf import parse_yaml_conf
from aatest.utils import SERVER_LOG_FOLDER
from aatest.utils import setup_common_log
from aatest.utils import setup_logging
from oidctest.op.profiles import PROFILEMAP

from otest.aus.app import WebApplication
from otest.aus.io import WebIO

from oidctest.op import check
from oidctest.op import oper
from oidctest.op import func
from oidctest.op.prof_util import ProfileHandler
from oidctest.op.tool import WebTester

from requests.packages import urllib3

urllib3.disable_warnings()

if not os.path.isdir(SERVER_LOG_FOLDER):
    os.makedirs(SERVER_LOG_FOLDER)

common_logger = setup_common_log()
logger = logging.getLogger("")

try:
    from mako.lookup import TemplateLookup
    from oic.oic.message import factory as message_factory
    from oic.oauth2 import ResponseError
    from oic.utils import exception_trace
    from oic.utils.http_util import Redirect
    from oic.utils.http_util import get_post
    from oic.utils.http_util import BadRequest
    from oidctest.session import SessionHandler
except Exception as ex:
    common_logger.exception(ex)
    raise ex


def pick_args(args, kwargs):
    return dict([(k, kwargs[k]) for k in args])


def pick_grp(name):
    return name.split('-')[1]


if __name__ == '__main__':
    from beaker.middleware import SessionMiddleware
    from cherrypy import wsgiserver

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', dest='mailaddr')
    parser.add_argument('-o', dest='operations')
    parser.add_argument('-f', dest='flows', action='append')
    parser.add_argument('-d', dest='directory')
    parser.add_argument('-p', dest='profile')
    parser.add_argument('-P', dest='profiles')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    # global ACR_VALUES
    # ACR_VALUES = CONF.ACR_VALUES

    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': True,
        'session.auto': True,
        'session.timeout': 900
    }

    sys.path.insert(0, ".")
    CONF = importlib.import_module(args.config)

    setup_logging("%s/rp_%s.log" % (SERVER_LOG_FOLDER, CONF.PORT), logger)

    fdef = {'Flows': {}, 'Order': [], 'Desc': {}}
    cls_factories = {'': oper.factory}
    func_factory = func.factory

    for flow_def in args.flows:
        spec = parse_yaml_conf(flow_def, cls_factories, func_factory)
        fdef['Flows'].update(spec['Flows'])
        fdef['Desc'].update(spec['Desc'])
        fdef['Order'].extend(spec['Order'])

    if args.profiles:
        profiles = importlib.import_module(args.profiles)
    else:
        from oidctest.op import profiles

    if args.operations:
        operations = importlib.import_module(args.operations)
    else:
        from oidctest.op import oper as operations

    if args.directory:
        _dir = args.directory
        if not _dir.endswith("/"):
            _dir += "/"
    else:
        _dir = "./"

    if args.profile:
        TEST_PROFILE = args.profile
    else:
        TEST_PROFILE = "C.T.T.ns"

    # Add own keys for signing/encrypting JWTs
    jwks, keyjar, kidd = build_keyjar(CONF.keys)

    # export JWKS
    p = urlparse(CONF.KEY_EXPORT_URL)
    f = open("." + p.path, "w")
    f.write(json.dumps(jwks))
    f.close()
    jwks_uri = p.geturl()

    LOOKUP = TemplateLookup(directories=[_dir + 'templates', _dir + 'htdocs'],
                            module_directory=_dir + 'modules',
                            input_encoding='utf-8',
                            output_encoding='utf-8')

    app_args = {"base_url": CONF.BASE, "kidd": kidd, "keyjar": keyjar,
                "jwks_uri": jwks_uri, "flows": fdef['Flows'], "conf": CONF,
                "cinfo": CONF.INFO, "order": fdef['Order'],
                "profiles": profiles, "operation": operations,
                "profile": args.profile, "msg_factory": oic_message_factory,
                "lookup": LOOKUP, "desc": fdef['Desc'], "cache": {},
                'map_prof': PROFILEMAP, 'profile_handler': ProfileHandler}

    WA = WebApplication(sessionhandler=SessionHandler, webio=WebIO,
                        webtester=WebTester, check=check, webenv=app_args,
                        pick_grp=pick_grp)

    SRV = wsgiserver.CherryPyWSGIServer(
        ('0.0.0.0', CONF.PORT), SessionMiddleware(WA.application, session_opts))

    if CONF.BASE.startswith("https"):
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

        SRV.ssl_adapter = BuiltinSSLAdapter(CONF.SERVER_CERT, CONF.SERVER_KEY,
                                            CONF.CERT_CHAIN)
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "RP server starting listening on port:%s%s" % (CONF.PORT, extra)
    logger.info(txt)
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
