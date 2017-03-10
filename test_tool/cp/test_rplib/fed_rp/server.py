#!/usr/bin/env python3
import importlib

import cherrypy
import logging
import os

import sys
from fedoidc import test_utils
from oic.utils import webfinger

from oidctest.cp import dump_log
from oidctest.cp.log_handler import ClearLog
from oidctest.cp.log_handler import Log
from oidctest.cp.log_handler import Tar
from oidctest.cp.op import Provider
from oidctest.cp.op import WebFinger
from oidctest.cp.op_handler import OPHandler
from oidctest.cp.setup import cb_setup
from oidctest.cp.test_list import TestList
from oidctest.tt.fed import FoKeys
from oidctest.tt.fed import named_kc
from oidctest.tt.fed import Sign
from oidctest.tt.fed import Who

from otest.flow import Flow
from otest.prof_util import SimpleProfileHandler

logger = logging.getLogger("")
LOGFILE_NAME = 'rp_test.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    import argparse
    from oidctest.fed import provider

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('-f', dest='flowsdir', required=True)
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-P', dest='path')
    parser.add_argument('-t', dest='tls', action='store_true')
    # federation extras
    parser.add_argument('-i', dest='iss', required=True)
    parser.add_argument('-F', dest='fed_conf')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _com_args, _op_arg, config = cb_setup(args)

    sys.path.insert(0, ".")
    fed_conf = importlib.import_module(args.fed_conf)

    liss = list(fed_conf.FO.values())
    liss.extend(list(fed_conf.OA.values()))
    liss.extend(list(fed_conf.EO.values()))

    signer, keybundle = test_utils.setup(fed_conf.KEYDEFS, fed_conf.TOOL_ISS,
                                         liss, fed_conf.SMS_DEF, fed_conf.OA,
                                         'ms_dir')

    folder = os.path.abspath(os.curdir)
    _flows = Flow(args.flowsdir, profile_handler=SimpleProfileHandler)
    op_handler = OPHandler(provider.Provider, _op_arg, _com_args, _flows)

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
        }}

    # WebFinger
    webfinger_config = {
        '/': {'base_url': _op_arg['baseurl']}}
    cherrypy.tree.mount(WebFinger(webfinger.WebFinger()),
                        '/.well-known/webfinger', webfinger_config)

    # test list
    cherrypy.tree.mount(
        TestList('flows', 'links.json',
                 'List of OIDC RP library tests for profile: "<i>{}</i>"',
                 config.GRPS),
        '/list')

    log_root = folder + '/log'

    cherrypy.tree.mount(Log(log_root), '/log')
    cherrypy.tree.mount(ClearLog(log_root), '/clear')
    cherrypy.tree.mount(Tar(log_root), '/mktar')

    # OIDC Providers
    cherrypy.tree.mount(Provider(op_handler, _flows), '/', provider_config)

    #  ================= Federation specific stuff =========================

    cherrypy.tree.mount(Sign(signer), '/sign')
    cherrypy.tree.mount(FoKeys(keybundle), '/bundle')
    cherrypy.tree.mount(Who(fed_conf.FO), '/who')

    # ======================================================================

    # HTTPS support
    if args.tls:
        cherrypy.server.ssl_certificate = config.SERVER_CERT
        cherrypy.server.ssl_private_key = config.SERVER_KEY
        if config.CA_BUNDLE:
            cherrypy.server.ssl_certificate_chain = config.CA_BUNDLE

    cherrypy.engine.start()
    cherrypy.engine.block()
