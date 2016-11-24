#!/usr/bin/env python
import logging

import argparse
from otest.utils import setup_logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    from beaker.middleware import SessionMiddleware
    from cherrypy import wsgiserver

    parser = argparse.ArgumentParser()
    parser.add_argument('-k', dest='insecure', action='store_true')
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

    setup_logging("conf.log", logger)

    app = Application(sessionhandler=SessionHandler, webio=WebIO,
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
