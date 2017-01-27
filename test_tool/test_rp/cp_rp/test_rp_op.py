#!/usr/bin/env python3

import argparse
import cherrypy

from oic.utils import webfinger

from oidctest.cp.op import Provider
from oidctest.cp.op import WebFinger
from oidctest.cp.op_handler import OPHandler
from oidctest.cp.setup import main_setup
from oidctest.rp import provider

from otest.flow import Flow
from otest.prof_util import SimpleProfileHandler

parser = argparse.ArgumentParser()
parser.add_argument('-d', dest='debug', action='store_true')
parser.add_argument('-f', dest='flowsdir', required=True)
parser.add_argument('-k', dest='insecure', action='store_true')
parser.add_argument('-p', dest='port', default=80, type=int)
parser.add_argument('-P', dest='path')
parser.add_argument('-t', dest='tls', action='store_true')
parser.add_argument('-v', dest='verbose', action='store_true')
parser.add_argument(dest="config")
args = parser.parse_args()

_com_args, _op_arg, config = main_setup(args)

_flows = Flow(args.flowsdir, profile_handler=SimpleProfileHandler)

cherrypy.tree.mount(WebFinger(webfinger.WebFinger()),
                    '/.well-known/webfinger')

op_args = com_args = test_conf = {}
op_handler = OPHandler(provider.Provider, _op_arg, _com_args, config)
cherrypy.tree.mount(Provider(op_handler), '/')

cherrypy.engine.start()
cherrypy.engine.block()
