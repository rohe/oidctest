#!/usr/bin/env python3
import importlib
import os
import traceback

import argparse
import logging

import sys
from future.backports.urllib.parse import quote_plus
from oic.oic import Client
from oic.oic.message import factory as oic_message_factory

from otest.aus.app import WebApplication
from otest.aus.client import Factory
from otest.aus.handling import WebIh
from otest.conf_setup import construct_app_args
from otest.utils import SERVER_LOG_FOLDER
from otest.utils import setup_logging
from otest.utils import setup_common_log

from oidctest.app_conf import REST
from oidctest.op import check
from oidctest.op import oper
from oidctest.op import func
from oidctest.op import profiles
from oidctest.op.profiles import PROFILEMAP
from oidctest.prof_util import ProfileHandler
from oidctest.tool import WebTester

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
    parser.add_argument(
        '-k', dest='insecure', action='store_true',
        help="insecure mode for when you're expecting to talk HTTPS to "
             "servers that use self-signed certificates")
    parser.add_argument(
        '-i', dest='issuer',
        help="The issuer ID of the OP")
    parser.add_argument(
        '-f', dest='flows', action='append',
        help="A file that contains the flow definitions for all the tests")
    parser.add_argument('-p', dest='port', type=int,
                        help="Which port the server should listen on")
    # parser.add_argument('-P', dest='profile')
    parser.add_argument('-M', dest='makodir',
                        help="Root directory for the MAKO template files")
    parser.add_argument('-S', dest='staticdir',
                        help="Directory where static files are kept")
    parser.add_argument('-s', dest='tls', action='store_true',
                        help="Whether the server should support incoming HTTPS")
    parser.add_argument(
        '-t', dest='tag',
        help="An identifier used to distinguish between different "
             "configuration for the same OP instance")
    # parser.add_argument(
    #     '-x', dest='xport', action='store_true', help='ONLY for testing')
    parser.add_argument(
        '-m', dest='path2port',
        help="CSV file containing the path-to-port mapping that the reverse "
             "proxy (if used) is using")
    parser.add_argument(
        '-k', dest='insecure', action='store_true',
        help="insecure mode for when you're expecting to talk HTTPS to "
             "servers that use self-signed certificates")
    parser.add_argument(
        '-i', dest='issuer',
        help="The issuer ID of the OP")
    parser.add_argument(
        '-f', dest='flows', action='append',
        help="A file that contains the flow definitions for all the tests")
    parser.add_argument('-p', dest='port', type=int,
                        help="Which port the server should listen on")
    # parser.add_argument('-P', dest='profile')
    parser.add_argument('-M', dest='makodir',
                        help="Root directory for the MAKO template files")
    parser.add_argument('-S', dest='staticdir',
                        help="Directory where static files are kept")
    parser.add_argument('-s', dest='tls', action='store_true',
                        help="Whether the server should support incoming HTTPS")
    parser.add_argument(
        '-t', dest='tag',
        help="An identifier used to distinguish between different "
             "configuration for the same OP instance")
    # parser.add_argument(
    #     '-x', dest='xport', action='store_true', help='ONLY for testing')
    parser.add_argument(
        '-m', dest='path2port',
        help="CSV file containing the path-to-port mapping that the reverse "
             "proxy (if used) is using")
>>>>>>> Stashed changes
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

    rest = REST(None, CONF.ENT_PATH, CONF.ENT_INFO)
    if args.tag:
        qtag = quote_plus(args.tag)
    else:
        qtag = 'default'

    ent_conf = None
    try:
        ent_conf = rest.construct_config(quote_plus(args.issuer), qtag)
    except Exception as err:
        print('iss:{}, tag:{}'.format(quote_plus(args.issuer), qtag))
        for m in traceback.format_exception(*sys.exc_info()):
            print(m)
        exit()

    setup_logging("%s/rp_%s.log" % (SERVER_LOG_FOLDER, args.port), logger)
    logger.info('construct_app_args')

    _path, app_args = construct_app_args(args, CONF, oper, func, profiles,
                                         ent_conf)
    _conf = app_args['conf']

    # Application arguments
    app_args.update(
        {"msg_factory": oic_message_factory, 'profile_map': PROFILEMAP,
         'profile_handler': ProfileHandler,
         'client_factory': Factory(Client)})

    if args.insecure:
        app_args['client_info']['verify_ssl'] = False

    WA = WebApplication(sessionhandler=SessionHandler, webio=WebIh,
                        webtester=WebTester, check=check, webenv=app_args,
                        pick_grp=pick_grp, path=_path)

    SRV = wsgiserver.CherryPyWSGIServer(
        ('0.0.0.0', args.port),
        SessionMiddleware(WA.application, session_opts))

    if args.tls:
        _tls = args.tls
    else:
        _tls = CONF.TLS

    if _tls:
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

        SRV.ssl_adapter = BuiltinSSLAdapter(_conf.SERVER_CERT, _conf.SERVER_KEY,
                                            _conf.CERT_CHAIN)
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "OP test server started, listening on port:%s%s" % (args.port, extra)
    logger.info(txt)
    print('base_url: {}'.format(app_args['client_info']['base_url']))
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
