#!/usr/bin/env python
import importlib
import logging

import argparse

from mako.lookup import TemplateLookup
from otest.utils import setup_logging

from oidctest.app_conf import Application

logger = logging.getLogger('')

if __name__ == '__main__':
    from beaker.middleware import SessionMiddleware
    from cherrypy import wsgiserver

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', dest='base_url')
    parser.add_argument('-c', dest='test_tool_conf')
    parser.add_argument('-f', dest='flows', action='append')
    parser.add_argument('-m', dest='path2port')
    parser.add_argument('-p', dest='port', default=80)
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument('-M', dest='makodir')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': True,
        'session.auto': True,
        'session.timeout': 900
    }

    setup_logging("conf.log", logger)

    _conf = importlib.import_module(args.config)

    if args.makodir:
        _dir = args.makodir
    else:
        _dir = _conf.MAKO_DIR
    if not _dir.endswith('/'):
        _dir += '/'

    if args.base_url:
        _base_url = args.base_url
    else:
        if args.port != 80:
            if _conf.BASE_URL.endswith('/'):
                _base_url = '{}:{}/'.format(_conf.BASE_URL[:-1], args.port)
            else:
                _base_url = '{}:{}/'.format(_conf.BASE_URL, args.port)
        else:
            if not _conf.BASE_URL.endswith('/'):
                _base_url = '{}/'.format(_conf.BASE_URL)
            else:
                _base_url = _conf.BASE_URL

    if args.path2port:
        _p2p = args.path2port
    else:
        _p2p = _conf.PATH2PORT
    if _p2p:
        port_min = _conf.PORT_MIN
        port_max = _conf.PORT_MAX
    else:
        port_min = port_max = 0

    if args.flows:
        _flows = args.flows
    else:
        _flows = _conf.FLOWS

    mako_lookup = TemplateLookup(
        directories=[_dir + 'templates', _dir + 'htdocs'],
        module_directory=_dir + 'modules', input_encoding='utf-8',
        output_encoding='utf-8')

    app = Application(_base_url, mako_lookup, test_script='optest.py',
                      ent_path=_conf.ENT_PATH, ent_info=_conf.ENT_INFO,
                      flows=_flows, path2port=_p2p, mako_dir=_dir,
                      port_min=port_min, port_max=port_max,
                      test_tool_conf=args.test_tool_conf)

    SRV = wsgiserver.CherryPyWSGIServer(
        ('0.0.0.0', int(args.port)),
        SessionMiddleware(app.application, session_opts))

    if args.tls:
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

        SRV.ssl_adapter = BuiltinSSLAdapter(_conf.SERVER_CERT, _conf.SERVER_KEY,
                                            _conf.CERT_CHAIN)
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "Configuration server started, listening on port:%s%s" % (
        args.port, extra)
    logger.info(txt)
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
