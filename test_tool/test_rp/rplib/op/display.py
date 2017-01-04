#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import re

from future.backports.urllib.parse import parse_qs
from mako.lookup import TemplateLookup
from oic.utils.http_util import Response, BadRequest

ROOT = './'

LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')

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


class Application(object):
    def __init__(self, fdir, links):
        self.fdir = fdir
        fp = open(links, 'r')
        self.links = json.load(fp)
        fp.close()

    def application(self, environ, start_response):
        """
        :param environ: The HTTP application environment
        :param start_response: The application to run when the handling of the
            request is done
        :return: The response as a list of lines
        """

        path = environ.get('PATH_INFO', '').lstrip('/')

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
                resp = BadRequest('Missing query parameter')
                return resp(environ, start_response)
            else:
                return rp_test_list(environ, start_response, self.fdir, _prof,
                                    self.links)
        else:
            resp = BadRequest('Unknown page')
            return resp(environ, start_response)


if __name__ == '__main__':
    from cherrypy import wsgiserver

    _app = Application(fdir='flows', links='link.json')
    # Setup the web server
    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8081),
                                        _app.application)

    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
