#!/usr/bin/env python3

import importlib
import json
import os
import argparse
import logging
import sys

from oic.utils.keyio import build_keyjar
from oic.oic.message import factory as oic_message_factory

from otest.aus.app import WebApplication
from otest.aus.io import WebIO
from otest.parse_cnf import parse_yaml_conf
from otest.rp.setup import read_path2port_map
from otest.utils import SERVER_LOG_FOLDER
from otest.utils import setup_common_log
from otest.utils import setup_logging

from oidctest.op import check
from oidctest.op import oper
from oidctest.op import func
from oidctest.op.profiles import PROFILEMAP
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
    parser.add_argument('-o', dest='operations')
    parser.add_argument('-f', dest='flows', action='append')
    parser.add_argument('-p', dest='profile')
    parser.add_argument('-P', dest='profiles')
    parser.add_argument('-M', dest='makodir')
    parser.add_argument('-S', dest='staticdir')
    parser.add_argument('-s', dest='tls', action='store_true')
    parser.add_argument(
        '-x', dest='xport', action='store_true', help='ONLY for testing')
    parser.add_argument('-m', dest='path2port')
    parser.add_argument(dest="config")
    args = parser.parse_args()

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

    # Add own keys for signing/encrypting JWTs
    jwks, keyjar, kidd = build_keyjar(CONF.KEYS)

    if args.staticdir:
        _sdir = args.staticdir
    else:
        _sdir = './static'

    # If this instance is behind a reverse proxy or on its own
    if CONF.BASE.endswith('/'):
        CONF.BASE = CONF.BASE[:-1]
    if args.path2port:
        ppmap = read_path2port_map(args.path2port)
        _path = ppmap[str(CONF.PORT)]
        if args.xport:
            _port = CONF.PORT
            _base = '{}:{}/{}/'.format(CONF.BASE, str(CONF.PORT), _path)
        else:
            _base = '{}/{}/'.format(CONF.BASE, _path)
            if args.tls:
                _port = 443
            else:
                _port = 80
    else:
        _port = CONF.PORT
        if _port not in [443, 80]:
            _base = '{}:{}'.format(CONF.BASE, _port)
        else:
            _base = CONF.BASE
        _path = ''

    # -------- JWKS ---------------
    _sdir = 'static'
    if args.path2port:
        jwks_uri = "{}{}/jwks_{}.json".format(_base, _sdir, _port)
        f = open('{}/jwks_{}.json'.format(_sdir, _port), "w")
    elif _port not in [443, 80]:
        jwks_uri = "{}:{}/{}/jwks_{}.json".format(CONF.BASE, _port, _sdir,
                                                  _port)
        f = open('{}/jwks_{}.json'.format(_sdir, _port), "w")
    else:
        jwks_uri = "{}/{}/jwks.json".format(CONF.BASE, _sdir)
        f = open('{}/jwks.json'.format(_sdir), "w")
    f.write(json.dumps(jwks))
    f.close()

    # -------- MAKO setup -----------
    if args.makodir:
        _dir = args.makodir
        if not _dir.endswith("/"):
            _dir += "/"
    else:
        _dir = "./"

    LOOKUP = TemplateLookup(directories=[_dir + 'templates', _dir + 'htdocs'],
                            module_directory=_dir + 'modules',
                            input_encoding='utf-8',
                            output_encoding='utf-8')

    _client_info = CONF.CLIENT

    try:
        ri = _client_info['registration_info']
    except KeyError:
        pass
    else:
        ri['redirect_uris'] = [r.format(_base) for r in ri['redirect_uris']]
        try:
            ri['post_logout_redirect_uris'] = [r.format(_base) for r in
                                               ri['post_logout_redirect_uris']]
        except KeyError:
            pass

    _base += '/'
    _client_info.update(
        {"base_url": _base, 'client_id': _base, "kid": kidd, "keyjar": keyjar,
         "jwks_uri": jwks_uri}
    )

    if args.profile:
        _profile = args.profile
    else:
        _profile = CONF.TOOL['profile']

    # Application arguments
    app_args = {"flows": fdef['Flows'], "conf": CONF,
                "client_info": _client_info, "order": fdef['Order'],
                "profiles": profiles, "operation": operations,
                "profile": _profile, "msg_factory": oic_message_factory,
                "lookup": LOOKUP, "desc": fdef['Desc'], "cache": {},
                'profile_map': PROFILEMAP, 'profile_handler': ProfileHandler}

    WA = WebApplication(sessionhandler=SessionHandler, webio=WebIO,
                        webtester=WebTester, check=check, webenv=app_args,
                        pick_grp=pick_grp, path=_path)

    SRV = wsgiserver.CherryPyWSGIServer(
        ('0.0.0.0', CONF.PORT),
        SessionMiddleware(WA.application, session_opts))

    if args.tls:
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

        SRV.ssl_adapter = BuiltinSSLAdapter(CONF.SERVER_CERT, CONF.SERVER_KEY,
                                            CONF.CERT_CHAIN)
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "OP test server started, listening on port:%s%s" % (CONF.PORT, extra)
    logger.info(txt)
    print(_base)
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
