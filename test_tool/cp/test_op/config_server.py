#!/usr/bin/env python3
import importlib
import logging
import os

import cherrypy
from fedoidc.file_system import FileSystem

from oidctest.cp import dump_log
from oidctest.cp.log_handler import OPLog
from oidctest.cp.log_handler import OPTar
from oidctest.tt.action import Action
from oidctest.tt.app import Application
from oidctest.tt.entity import Entity
from oidctest.tt.instance import Instance
from oidctest.tt.rest import REST
from oidctest.ass_port import AssignedPorts

logger = logging.getLogger("")
LOGFILE_NAME = 'conf_srv.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

tool_params = ['acr_values', 'claims_locales', 'issuer',
               'login_hint', 'profile', 'ui_locales', 'webfinger_email',
               'webfinger_url', 'insecure', 'tag']

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='test_tool_conf')
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-P', dest='path')
    parser.add_argument('-H', dest='htmldir')
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _conf = importlib.import_module(args.config)
    _ttc = importlib.import_module(args.test_tool_conf)

    folder = os.path.abspath(os.curdir)

    _html = FileSystem(args.htmldir)
    _html.sync()

    cherrypy.tools.dumplog = cherrypy.Tool('before_finalize', dump_log)

    cherrypy.config.update(
        {'environment': 'production',
         'log.error_file': 'site.log',
         'tools.trailing_slash.on': False,
         'log.screen': True,
         'tools.sessions.on': True,
         'tools.encode.on': True,
         'tools.encode.encoding': 'utf-8',
         'tools.dumplog.on': True,
         'server.socket_host': '0.0.0.0',  # listen on all interfaces
         'server.socket_port': args.port
         })

    provider_config = {
        '/': {
            'root_path': 'localhost',
            'log.screen': True,
        },
        '/static': {
            'tools.staticdir.dir': os.path.join(folder, 'static'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True
        }}

    if args.path:
        if _conf.baseurl.endswith('/'):
            _base_url = '{}{}/'.format(_conf.baseurl, args.path)
        else:
            _base_url = '{}/{}/'.format(_conf.BASE_URL, args.path)
    elif args.port:
        if _conf.BASE_URL.endswith('/'):
            _base_url = '{}:{}/'.format(_conf.BASE_URL[:-1], args.port)
        else:
            _base_url = '{}:{}/'.format(_conf.BASE_URL, args.port)
    else:
        _base_url = _conf.BASE_URL

    rest = REST(_base_url)

    _assigned_ports = AssignedPorts('assigned_ports.json', _conf.PORT_MIN, _conf.PORT_MAX)
    _assigned_ports.load()

    cherrypy.tree.mount(
        Entity(_conf.ENT_PATH, _html, rest, _assigned_ports, _ttc.BASE), '/entity')
    _app = Application(_conf.TEST_SCRIPT, _conf.FLOWDIR, rest,
                       _assigned_ports, _ttc.BASE, args.test_tool_conf,
                       args.htmldir)
    cherrypy.tree.mount(
        Action(rest, _ttc, _html, _conf.ENT_PATH, _conf.ENT_INFO, tool_params,
               _app),
        '/action')

    log_root = os.path.join(folder, 'log')
    _tar = OPTar(log_root)
    cherrypy.tree.mount(_tar, '/mktar')
    cherrypy.tree.mount(_tar, '/backup')
    cherrypy.tree.mount(OPLog(log_root, _html), '/log')

    # Main
    test_tool_conf = args.test_tool_conf
    cherrypy.tree.mount(
        Instance(rest, _base_url, test_tool_conf, _app, html=_html), '/',
        provider_config)

    # If HTTPS
    if args.tls:
        cherrypy.server.ssl_certificate = _conf.SERVER_CERT
        cherrypy.server.ssl_private_key = _conf.SERVER_KEY
        if _conf.CA_BUNDLE:
            cherrypy.server.ssl_certificate_chain = _conf.CA_BUNDLE

    cherrypy.engine.start()
    cherrypy.engine.block()
