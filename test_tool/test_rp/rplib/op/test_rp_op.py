#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The OP used when testing RP libraries
"""
import json
import os
import re
import sys
import traceback
import logging

from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import urlparse
from oic.oauth2.message import Message

from oic.utils.client_management import CDB
from oic.utils.http_util import BadRequest
from oic.utils.http_util import Response
from oic.utils.http_util import NotFound
from oic.utils.http_util import ServiceError
from oic.utils.keyio import key_summary

from oidctest import UnknownTestID
from oidctest.endpoints import clear_log
from oidctest.endpoints import display_log
from oidctest.endpoints import make_tar
from oidctest.endpoints import static
from oidctest.endpoints import URLS
from oidctest.response_encoder import ResponseEncoder
from oidctest.rp.mode import extract_mode
from oidctest.rp.mode import init_keyjar
from oidctest.rp.mode import write_jwks_uri
from oidctest.rp.mode import setup_op

from otest.conversation import Conversation
from otest.events import Events
from otest.events import EV_EXCEPTION
from otest.events import EV_FAULT
from otest.events import EV_HTTP_REQUEST
from otest.events import EV_REQUEST
from otest.events import FailedOperation
from otest.events import HTTPRequest
from otest.events import Operation
from otest.jlog import JLog

try:
    from requests.packages import urllib3
except ImportError:
    pass
else:
    urllib3.disable_warnings()

__author__ = 'rohe0002'

from mako.lookup import TemplateLookup

LOGGER = logging.getLogger("")
LOGFILE_NAME = 'oc.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

CPC = ('%(asctime)s %(name)s:%(levelname)s '
       '[%(client)s,%(path)s,%(cid)s] %(message)s')
cpc_formatter = logging.Formatter(CPC)

hdlr.setFormatter(base_formatter)
LOGGER.addHandler(hdlr)
LOGGER.setLevel(logging.DEBUG)

NAME = "pyoic"

PASSWD = {
    "diana": "krall",
    "babs": "howes",
    "upper": "crust"
}

# ----------------------------------------------------------------------------

ROOT = './'

LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')

# ----------------------------------------------------------------------------

PAT = re.compile('\${([A-Z_0-9]*)}')

ABBR = {
    "code": 'C',
    "id_token": 'I',
    "id_token token": 'IT',
    "code id_token": 'CI',
    "code token": 'CT',
    "code id_token token": 'CIT',
    "dynamic": 'DYN',
    "configuration": 'CNF'
}

EXP = dict([(v, k) for k, v in ABBR.items()])


def replace_with_url(txt, links):
    for m in PAT.findall(txt):
        try:
            _url = links['URL'][m]
        except KeyError:
            pass
        else:
            txt = txt.replace('${%s}' % m, _url)

    return txt


def replace_with_link(txt, links):
    for m in PAT.findall(txt):
        try:
            _url, tag = links['LINK'][m]
        except KeyError:
            pass
        else:
            _li = replace_with_url(_url, links)
            _href = '<a href="{}">{}</a>'.format(_li, tag)
            txt = txt.replace('${%s}' % m, _href)
    return txt


def main_display(environ, start_response):
    resp = Response(mako_template="main.mako",
                    template_lookup=LOOKUP,
                    headers=[])

    args = {
        'profiles': ABBR
    }
    return resp(environ, start_response, **args)


def rp_test_list(environ, start_response, fdir, response_type, links):
    resp = Response(mako_template="list.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    mandatory = []
    optional = []

    for fn in os.listdir(fdir):
        if fn.startswith('rp-') and fn.endswith('.json'):
            fname = os.path.join(fdir, fn)
            fp = open(fname, 'r')
            try:
                _info = json.load(fp)
            except Exception:
                continue
            fp.close()
            if "MTI" in _info and response_type in _info['MTI']:
                _det_desc = replace_with_link(_info['detailed_description'],
                                              links)
                _exp_res = replace_with_link(_info['expected_result'],
                                             links)
                mandatory.append((fn[:-5], _det_desc, _exp_res))
            else:
                try:
                    rts = _info["capabilities"]["response_types_supported"]
                except KeyError:
                    pass
                else:
                    profs = [ABBR[x] for x in rts]
                    if response_type in profs:
                        _det_desc = replace_with_link(
                            _info['detailed_description'], links)
                        _exp_res = replace_with_link(_info['expected_result'],
                                                     links)
                        optional.append((fn[:-5], _det_desc, _exp_res))

    args = {
        'mandatory': mandatory,
        'optional': optional,
        'response_type': EXP[response_type]
    }
    return resp(environ, start_response, **args)


# ----------------------------------------------------------------------------


def get_client_address(environ):
    try:
        _addr = environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    except KeyError:
        _addr = environ['REMOTE_ADDR']
    # try:
    #     _port = environ['REMOTE_PORT']
    # except KeyError:
    #     _port = '?'
    # return "{}:{}".format(_addr, _port)
    return _addr


def rp_support_3rd_party_init_login(environ, start_response):
    resp = Response(mako_template="rp_support_3rd_party_init_login.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    return resp(environ, start_response)


def registration(environ, start_response):
    resp = Response(mako_template="registration.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    return resp(environ, start_response)


def generate_static_client_credentials(parameters):
    redirect_uris = parameters['redirect_uris']
    jwks_uri = str(parameters['jwks_uri'][0])
    _cdb = CDB(config.CLIENT_DB)
    static_client = _cdb.create(redirect_uris=redirect_uris,
                                # policy_uri="example.com",
                                # logo_uri="example.com",
                                jwks_uri=jwks_uri)
    return static_client['client_id'], static_client['client_secret']


def parse_path(path):
    # path should be <oper_id>/<test_id>/<endpoint> or just <endpoint>
    # if endpoint == '.well-known/webfinger'

    if path == '.well-known/webfinger':
        return {'endpoint': path}

    if path.startswith('/'):
        path = path[1:]

    p = path.split('/')
    if len(p) == 2:
        return {'oper_id': p[0], 'test_id': p[1].lower()}
    elif len(p) >= 3:
        return {'endpoint': '/'.join(p[2:]), 'oper_id': p[0],
                'test_id': p[1].lower()}
    else:
        raise ValueError('illegal path')


class TestConf(object):
    def __init__(self, conf_dir):
        self.conf_dir = conf_dir

    def __getitem__(self, item):
        fname = '{}/{}.json'.format(self.conf_dir, item)
        try:
            fp = open(fname, 'r')
        except Exception:
            return None
        else:
            try:
                return json.load(fp)
            except Exception:
                return None


class Application(object):
    def __init__(self, test_conf_dir, com_args, op_args, fdir, links):
        self.test_conf = TestConf(test_conf_dir)
        self.op = {}
        self.com_args = com_args
        self.op_args = op_args
        self.fdir = fdir
        fp = open(links, 'r')
        self.links = json.load(fp)
        fp.close()

    def op_setup(self, environ, mode, events, endpoint):
        addr = get_client_address(environ)
        path = '/'.join([mode['oper_id'], mode['test_id']])

        key = "{}:{}".format(addr, path)
        #  LOGGER.debug("OP key: {}".format(key))
        try:
            _op = self.op[key]
            _op.events = events
            if endpoint == '.well-known/openid-configuration':
                if mode["test_id"] == 'rp-id_token-kid-absent-multiple-jwks':
                    setattr(_op, 'keys', self.op_args['marg']['keys'])
                    _op_args = {
                        'baseurl': self.op_args['baseurl'],
                        'jwks': self.op_args['marg']['jwks']
                    }
                    write_jwks_uri(_op, _op_args)
                else:
                    init_keyjar(_op, self.op_args['keyjar'], self.com_args)
                    write_jwks_uri(_op, self.op_args)
        except KeyError:
            if mode["test_id"] in ['rp-id_token-kid-absent-multiple-jwks']:
                _op_args = {}
                for param in ['baseurl', 'cookie_name', 'cookie_ttl',
                              'endpoints']:
                    _op_args[param] = self.op_args[param]
                for param in ["jwks", "keys"]:
                    _op_args[param] = self.op_args["marg"][param]
                _op = setup_op(mode, self.com_args, _op_args,
                               self.test_conf, events)
            else:
                _op = setup_op(mode, self.com_args, self.op_args,
                               self.test_conf, events)
            _op.conv = Conversation(mode["test_id"], _op, None)
            _op.orig_keys = key_summary(_op.keyjar, '').split(', ')
            self.op[key] = _op

        return _op, path, key

    def application(self, environ, start_response):
        """
        :param environ: The HTTP application environment
        :param start_response: The application to run when the handling of the
            request is done
        :return: The response as a list of lines
        """

        path = environ.get('PATH_INFO', '').lstrip('/')
        response_encoder = ResponseEncoder(environ=environ,
                                           start_response=start_response)
        parameters = parse_qs(environ["QUERY_STRING"])

        session_info = {
            "addr": get_client_address(environ),
            'cookie': environ.get("HTTP_COOKIE", ''),
            'path': path,
            'parameters': parameters
        }

        jlog = JLog(LOGGER, session_info['addr'])
        jlog.info(session_info)

        if path == "robots.txt":
            return static(environ, start_response, "static/robots.txt")

        if path.startswith("static/"):
            return static(environ, start_response, path)
        elif path.startswith("tar/"):
            return static(environ, start_response, path)
        elif path.startswith("log"):
            return display_log(path, environ, start_response, lookup=LOOKUP)
        elif path.startswith('clear/'):
            return clear_log(path, environ, start_response, lookup=LOOKUP)
        elif path.startswith('mktar/'):
            return make_tar(path, environ, start_response, lookup=LOOKUP)
        elif path.startswith("_static/"):
            return static(environ, start_response, path)
        elif path.startswith("jwks.json"):
            try:
                mode, endpoint = extract_mode(self.op_args["baseurl"])
                events = Events()
                events.store('Init',
                             '===========================================')
                op, path, jlog.id = self.op_setup(environ, mode, events,
                                                  endpoint)
                jwks = op.generate_jwks(mode)
                resp = Response(jwks,
                                headers=[('Content-Type', 'application/json')])
                return resp(environ, start_response)
            except KeyError:
                # Try to load from static file
                return static(environ, start_response, "static/jwks.json")

        events = Events()
        events.store('Init', '===========================================')

        if path == '':
            return main_display(environ, start_response)
        elif path in EXP.keys():
            return rp_test_list(environ, start_response, self.fdir, path,
                                self.links)
        elif path == 'list':
            qs = parse_qs(environ.get('QUERY_STRING'))
            try:
                _prof = qs['profile'][0]
            except KeyError:
                return main_display(environ, start_response)
            else:
                return rp_test_list(environ, start_response, self.fdir, _prof,
                                    self.links)
        elif path == "generate_client_credentials":
            client_id, client_secret = generate_static_client_credentials(
                parameters)
            return response_encoder.return_json(
                json.dumps({"client_id": client_id,
                            "client_secret": client_secret}))
        elif path == "3rd_party_init_login":
            return rp_support_3rd_party_init_login(environ, start_response)

        # path should be <oper_id>/<test_id>/<endpoint>
        try:
            mode = parse_path(path)
        except ValueError:
            resp = BadRequest('Illegal path')
            return resp(environ, start_response)

        try:
            endpoint = mode['endpoint']
        except KeyError:
            _info = {'error': 'No endpoint', 'mode': mode}
            events.store(EV_FAULT, _info)
            jlog.error(_info)
            resp = BadRequest('Illegal path')
            return resp(environ, start_response)

        if endpoint == ".well-known/webfinger":
            session_info['endpoint'] = endpoint
            try:
                _p = urlparse(parameters["resource"][0])
            except KeyError:
                events.store(EV_FAULT,
                             FailedOperation('webfinger',
                                             'No resource defined'))
                jlog.error({'reason': 'No resource defined'})
                resp = ServiceError("No resource defined")
                return resp(environ, start_response)

            if _p.scheme in ["http", "https"]:
                events.store(EV_REQUEST,
                             Operation(name='webfinger', type='url',
                                       path=_p.path))
                mode = parse_path(_p.path)
            elif _p.scheme == "acct":
                _l, _ = _p.path.split('@')

                _a = _l.split('.')
                if len(_a) == 2:
                    _oper_id = _a[0]
                    _test_id = _a[1]
                elif len(_a) > 2:
                    _oper_id = ".".join(_a[:-1])
                    _test_id = _a[-1]
                else:
                    _oper_id = _a[0]
                    _test_id = 'default'

                mode.update({'oper_id': _oper_id, 'test_id': _test_id})
                events.store(EV_REQUEST,
                             Operation(name='webfinger', type='acct',
                                       oper_id=_oper_id, test_id=_test_id))
            else:
                _msg = "Unknown scheme: {}".format(_p.scheme)
                events.events(EV_FAULT, FailedOperation('webfinger', _msg))
                jlog.error({'reason': _msg})
                resp = ServiceError(_msg)
                return resp(environ, start_response)
        elif endpoint == "claim":
            authz = environ["HTTP_AUTHORIZATION"]
            _ev = Operation('claim')
            try:
                assert authz.startswith("Bearer")
            except AssertionError:
                resp = BadRequest()
            else:
                _ev.authz = authz
                events.store(EV_REQUEST, _ev)
                tok = authz[7:]
                # mode, endpoint = extract_mode(self.op_args["baseurl"])
                _op, _, sid = self.op_setup(environ, mode, events, endpoint)
                try:
                    _claims = _op.claim_access_token[tok]
                except KeyError:
                    resp = BadRequest()
                else:
                    del _op.claim_access_token[tok]
                    _info = Message(**_claims)
                    jwt_key = _op.keyjar.get_signing_key()
                    resp = Response(_info.to_jwt(key=jwt_key,
                                                 algorithm="RS256"),
                                    content='application/jwt')
            return resp(environ, start_response)

        if mode:
            session_info.update(mode)
            jlog.id = mode['oper_id']

        try:
            _op, path, jlog.id = self.op_setup(environ, mode, events, endpoint)
        except UnknownTestID as err:
            resp = BadRequest('Unknown test ID: {}'.format(err.args[0]))
            return resp(environ, start_response)

        session_info["op"] = _op
        session_info["path"] = path
        session_info['test_conf'] = self.test_conf[session_info['test_id']]

        for regex, callback in URLS:
            match = re.search(regex, endpoint)
            if match is not None:
                _op = HTTPRequest(endpoint=endpoint,
                                  method=environ["REQUEST_METHOD"])
                try:
                    _op.authz = environ["HTTP_AUTHORIZATION"]
                except KeyError:
                    pass
                events.store(EV_HTTP_REQUEST, _op)
                try:
                    environ['oic.url_args'] = match.groups()[0]
                except IndexError:
                    environ['oic.url_args'] = endpoint

                jlog.info({'callback': callback.__name__})
                try:
                    return callback(environ, start_response, session_info,
                                    events, op_arg=self.op_args, jlog=jlog)
                except Exception as err:
                    print("%s" % err)
                    message = traceback.format_exception(*sys.exc_info())
                    print(message)
                    events.store(EV_EXCEPTION, err)
                    LOGGER.exception("%s" % err)
                    resp = ServiceError("%s" % err)
                    return resp(environ, start_response)

        LOGGER.debug("unknown page: '{}'".format(endpoint))
        events.store(EV_FAULT, 'No such page: {}'.format(endpoint))
        resp = NotFound("Couldn't find the side you asked for!")
        return resp(environ, start_response)


# ----------------------------------------------------------------------------

if __name__ == '__main__':
    import argparse

    from cherrypy import wsgiserver
    from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

    from setup import main_setup

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('-f', dest='flowsdir')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _com_args, _op_arg, config = main_setup(args, LOOKUP)

    _app = Application(test_conf_dir=args.flowsdir, com_args=_com_args,
                       op_args=_op_arg, fdir=args.flowsdir, links='link.json')
    # Setup the web server
    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', args.port),
                                        _app.application)

    if _op_arg["baseurl"].startswith("https"):
        SRV.ssl_adapter = BuiltinSSLAdapter(config.SERVER_CERT,
                                            config.SERVER_KEY,
                                            config.CA_BUNDLE)
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "RP server starting listening on port:%s%s" % (args.port, extra)
    LOGGER.info(txt)
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
