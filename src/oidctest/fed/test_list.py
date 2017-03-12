import cherrypy
import json
import os
import re

import logging

import sys
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


def get_mandatory(file_dir, links):
    mandatory = []
    # optional = []

    for fn in os.listdir(file_dir):
        if fn.startswith('rp-') and fn.endswith('.json'):
            fname = os.path.join(file_dir, fn)
            fp = open(fname, 'r')
            try:
                _info = json.load(fp)
            except Exception:
                continue
            fp.close()

            _det_desc = replace_with_link(_info['detailed_description'], links)
            _exp_res = replace_with_link(_info['expected_result'], links)
            mandatory.append((fn[:-5], _det_desc, _exp_res, _info['group']))
    return mandatory


class TestList(object):
    def __init__(self, fdir, links_file, headline, grps):
        self.fdir = fdir
        fp = open(links_file, 'r')
        self.links = json.load(fp)
        fp.close()
        self.headline = headline
        self.grps = grps

    @cherrypy.expose
    def index(self, profile=''):
        mandatory = get_mandatory(self.fdir, self.links)

        hl = 'Federation functionality tests'

        response = [
            "<html><head>",
            '<link rel="stylesheet" type="text/css" href="/static/theme.css">',
            "<title>{}</title></head><body>".format(hl),
            '<h1>{}</h1>'.format(hl),
            '<h2>Mandatory to implement</h2>'
        ]

        response.extend(test_list(mandatory, self.grps))
        # response.append('<h2>Optional</h2>')
        # response.extend(test_list(optional, self.grps))
        response.append('</body></head>')

        return as_bytes('\n'.join(response))


# headline = 'List of OIDC RP library tests for profile: "<i>{}</i>"'

if __name__ == "__main__":
    file_dir = sys.argv[1]

    fp = open(sys.argv[2], 'r')
    links = json.load(fp)
    fp.close()

    grps = sys.argv[3:]
    mandatory = get_mandatory(file_dir, links)
    print("\n".join(test_list(mandatory, grps)))
