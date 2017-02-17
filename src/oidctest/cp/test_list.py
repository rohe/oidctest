import cherrypy
import json
import os
import re

import logging
from jwkest import as_bytes
from otest.flow import ABBR

PAT = re.compile('\${([A-Z_0-9]*)}')

EXP = dict([(v, k) for k, v in ABBR.items()])

logger = logging.getLogger(__name__)


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


def test_list(args, grps):
    """
    Creates list of test descriptions
    """
    line = [
        '<table>',
        '<tr><th>Test ID</th><th>Description</th><th>Info</th></tr>']

    for pgrp in grps:
        h = False
        for tid, desc, result, grp in args:
            if pgrp == grp:
                if h is False:
                    line.append(
                        '<tr style><td colspan="3" class="center"><b>{}</b></td></tr>'.format(grp))
                    h = True

                line.append(
                    '<tr><td style="white-space:nowrap">{}</td><td>{}</td><td>{}</td></tr>'.format(
                        tid, desc, result))
    line.append('</table>')
    return line


class TestList(object):
    def __init__(self, fdir, links_file, headline, grps):
        self.fdir = fdir
        fp = open(links_file, 'r')
        self.links = json.load(fp)
        fp.close()
        self.headline = headline
        self.grps = grps

    @cherrypy.expose
    def index(self, profile):
        mandatory = []
        optional = []

        for fn in os.listdir(self.fdir):
            if fn.startswith('rp-') and fn.endswith('.json'):
                fname = os.path.join(self.fdir, fn)
                fp = open(fname, 'r')
                try:
                    _info = json.load(fp)
                except Exception:
                    continue
                fp.close()
                if "MTI" in _info and profile in _info['MTI']:
                    _det_desc = replace_with_link(_info['detailed_description'],
                                                  self.links)
                    _exp_res = replace_with_link(_info['expected_result'],
                                                 self.links)
                    mandatory.append((fn[:-5], _det_desc, _exp_res,
                                      _info['group']))
                else:
                    try:
                        rts = _info["capabilities"]["response_types_supported"]
                    except KeyError:
                        pass
                    else:
                        profs = [ABBR[x] for x in rts]
                        if profile in profs:
                            _det_desc = replace_with_link(
                                _info['detailed_description'], self.links)
                            _exp_res = replace_with_link(
                                _info['expected_result'], self.links)
                            optional.append((fn[:-5], _det_desc, _exp_res,
                                             _info['group']))

        hl = self.headline.format(EXP[profile])

        response = [
            "<html><head>",
            '<link rel="stylesheet" type="text/css" href="/static/theme.css">',
            "<title>{}</title></head><body>".format(hl),
            '<h1>{}</h1>'.format(hl),
            '<h2>Mandatory to implement</h2>'
        ]

        response.extend(test_list(mandatory, self.grps))
        response.append('<h2>Optional</h2>')
        response.extend(test_list(optional, self.grps))
        response.append('</body></head>')

        return as_bytes('\n'.join(response))


# headline = 'List of OIDC RP library tests for profile: "<i>{}</i>"'

