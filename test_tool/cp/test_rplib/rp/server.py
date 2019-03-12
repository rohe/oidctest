#!/usr/bin/env python3
import importlib
import logging
import os

import cherrypy
import sys

from oic.utils import webfinger
from otest.flow import Flow
from otest.prof_util import SimpleProfileHandler

from oidctest.cp import dump_log
from oidctest.cp.log_handler import ClearLog
from oidctest.cp.log_handler import Log
from oidctest.cp.log_handler import Tar
from oidctest.cp.op import Provider
from oidctest.cp.op import WebFinger
from oidctest.cp.op import RelyingParty
from oidctest.cp.op_handler import OPHandler
from oidctest.cp.setup import cb_setup
from oidctest.cp.test_list import TestList

logger = logging.getLogger("")
LOGFILE_NAME = 'rp_test.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def get_version():
    sys.path.insert(0, ".")
    vers = importlib.import_module('version')
    return vers.VERSION


if __name__ == '__main__':
    import argparse
    from oidctest.rp import provider

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('-f', dest='flowsdir', required=True)
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-P', dest='path')
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _version = get_version()
    _com_args, _op_arg, config = cb_setup(args)

    folder = os.path.abspath(os.curdir)
    _flowsdir = os.path.normpath(os.path.join(folder, args.flowsdir))
    _flows = Flow(_flowsdir, profile_handler=SimpleProfileHandler)
    op_handler = OPHandler(provider.Provider, _op_arg, _com_args, _flows,
                           folder)

    cherrypy.tools.dumplog = cherrypy.Tool('before_finalize', dump_log)

    cherrypy.config.update(
        {'environment': 'production',
         'log.error_file': 'site.log',
         'tools.trailing_slash.on': False,
         'server.socket_host': '0.0.0.0',
         'log.screen': True,
         'tools.sessions.on': True,
         'tools.encode.on': True,
         'tools.encode.encoding': 'utf-8',
         'tools.dumplog.on': True,
         'server.socket_port': args.port
         })

    provider_config = {
        '/': {
            'root_path': 'localhost',
            'log.screen': True
        },
        '/static': {
            'tools.staticdir.dir': os.path.join(folder, 'static'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True,
            'cors.expose_public.on': True
        },
        '/favicon.ico':
        {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(folder,
                                                      'static/favicon.ico')
        },
        '/robots.txt':
        {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(folder,
                                                      'static/robots.txt')
        }
    }

    # WebFinger
    webfinger_config = {'/': {'base_url': _op_arg['baseurl']}}
    cherrypy.tree.mount(WebFinger(webfinger.WebFinger(), version=_version),
                        '/.well-known/webfinger', webfinger_config)

    # test list
    cherrypy.tree.mount(
        TestList(_flowsdir, 'links.json',
                 'List of OIDC RP library tests for profile: "<i>{}</i>"',
                 config.GRPS, version=_version),
        '/list')

    log_root = folder + '/log'

    cherrypy.tree.mount(Log(log_root, version=_version), '/log')
    cherrypy.tree.mount(ClearLog(folder), '/clear')
    cherrypy.tree.mount(Tar(folder), '/mktar')

    cherrypy.tree.mount(RelyingParty(op_handler, version=_version), '/rp')

    # OIDC Providers
    cherrypy.tree.mount(Provider(op_handler, _flows, version=_version),
                        '/', provider_config)

    # If HTTPS
    if args.tls:
        cherrypy.server.ssl_certificate = config.SERVER_CERT
        cherrypy.server.ssl_private_key = config.SERVER_KEY
        if config.CA_BUNDLE:
            cherrypy.server.ssl_certificate_chain = config.CA_BUNDLE

    cherrypy.engine.start()
    cherrypy.engine.block()
