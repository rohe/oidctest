import json
import logging
import os
import re

import cherrypy
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
    line = ['<table class="table table-hover table-bordered table-condensed">',
        '<tr><th>Test ID</th><th>Description</th><th>Info</th></tr>']

    for pgrp in grps:
        h = False
        for tid, desc, result, grp in args:
            if pgrp == grp:
                if h is False:
                    line.append(
                        '<tr style><td colspan="3" class="text-center info"><b>{}</b></td></tr>'.format(grp))
                    h = True

                line.append(
                    '<tr><tH style="white-space:nowrap">{}</tH><td>{}</td><td>{}</td></tr>'.format(
                        tid, desc, result))
    line.append('</table>')
    return line


HTML_PRE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenID Connect Relying Party Certification</title>
<link href="/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
<link href="/static/theme.css" rel="stylesheet">
<!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
</head>
<body>

    <div class="container" role="main">

        <div class="page-header">
            <div class="pull-left">
                <h2>OpenID Connect Relying Party Certification</h2>
            </div>
            <div class="pull-right">
                <a href="https://openid.net/certification"><img
                    class="img-responsive" src="/static/logo.png" /></a>
            </div>
            <div class="clearfix"></div>
        </div>
"""

HTML_POST = """
    </div>

    <script
        src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
</body>
</html>
"""

HTML_FOOTER = """
        <div id="footer" class="footer text-muted">
            <hr />
            <div class="pull-left">
                <ul class="list-inline">
                    <li>(C) 2017-2019- <a href="https://openid.net/foundation">OpenID
                            Foundation</a></li>
                    <li>E-mail: <a href="mailto:certification@oidf.org">certification@oidf.org</a></li>
                    <li>Issues: <a
                        href="https://github.com/openid-certification/oidctest/issues">Github</a>
                    <li>
                </ul>
            </div>
            <div class="pull-right">
                <ul class="list-inline">
                    <li>Version: {}</li>
                </ul>
            </div>
        </div>
"""

class TestList(object):
    def __init__(self, fdir, links_file, headline, grps, version=''):
        self.fdir = fdir
        fp = open(links_file, 'r')
        self.links = json.load(fp)
        fp.close()
        self.headline = headline
        self.grps = grps
        self.version = version

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
            HTML_PRE,            
            '<div class="panel panel-primary">',
            '  <div class="panel-heading">',
            '    <h3 class="panel-title">Mandatory</h3>',
            '  </div>',
            '  <div class="panel-body">'
        ]

        response.extend(test_list(mandatory, self.grps))
        response += [
            '  </div>',
            '</div>'
            '<div class="panel panel-primary">',
            '  <div class="panel-heading">',
            '    <h3 class="panel-title">Optional</h3>',
            '  </div>',
            '  <div class="panel-body">',
        ]
        
        response.extend(test_list(optional, self.grps))
        response += [
            '  </div>',
            '</div>',
            HTML_FOOTER.format(self.version),
            HTML_POST
        ]

        return as_bytes('\n'.join(response))


# headline = 'List of OIDC RP library tests for profile: "<i>{}</i>"'
