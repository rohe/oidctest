#!/usr/bin/env python3

import os
import argparse
import logging

from oic.oic.message import factory as oic_message_factory

from otest.aus.app import WebApplication
from otest.aus.io import WebIO
from otest.conf_setup import construct_app_args
from otest.utils import SERVER_LOG_FOLDER
from otest.utils import setup_common_log

from oidctest.op import check
from oidctest.op import oper
from oidctest.op import func
from oidctest.op.profiles import PROFILEMAP
from oidctest.op.prof_util import ProfileHandler
from oidctest.op.tool import WebTester
from oidctest.op import profiles

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

    _path, app_args = construct_app_args(args, oper, func, profiles)
    _conf = app_args['conf']

    # Application arguments
    app_args.update(
        {"msg_factory": oic_message_factory, 'profile_map': PROFILEMAP,
         'profile_handler': ProfileHandler})

    WA = WebApplication(sessionhandler=SessionHandler, webio=WebIO,
                        webtester=WebTester, check=check, webenv=app_args,
                        pick_grp=pick_grp, path=_path)

    SRV = wsgiserver.CherryPyWSGIServer(
        ('0.0.0.0', _conf.PORT),
        SessionMiddleware(WA.application, session_opts))

    if args.tls:
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

        SRV.ssl_adapter = BuiltinSSLAdapter(_conf.SERVER_CERT, _conf.SERVER_KEY,
                                            _conf.CERT_CHAIN)
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "OP test server started, listening on port:%s%s" % (_conf.PORT, extra)
    logger.info(txt)
    print(app_args['client_info']['base_url'])
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
