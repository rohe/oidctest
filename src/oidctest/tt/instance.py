import logging
from urllib.parse import unquote_plus

import cherrypy
from jwkest import as_bytes
from oic.oauth2.message import list_serializer
from oic.utils.http_util import Response

from oidctest.app_conf import TYPE2CLS
from oidctest.cp import init_events
from oidctest.tt import conv_response
from oidctest.tt import unquote_quote
from otest.prof_util import simplify_return_type, LABEL
from otest.prof_util import to_profile

logger = logging.getLogger(__name__)


def tool_conf_massage(tc):
    tc['return_type'] = simplify_return_type(tc['return_type'])
    tc['profile'] = to_profile(tc)
    _rm = LABEL[:]
    _rm.extend(['enc', 'sig', 'none'])
    for lab in _rm:
        try:
            del tc[lab]
        except KeyError:
            pass
    try:
        wemail = tc["webfinger_email"]
    except KeyError:
        pass
    else:
        if wemail.startswith('acct:'):
            pass
        else:
            tc["webfinger_email"] = "acct:{}".format(wemail)
    return tc


def is_multi_valued(item, typ):
    if typ in ['tool', '']:
        return item in ['acr_values', 'claims_locales', 'ui_locales']
    else:
        return TYPE2CLS[typ].c_param[item][2] == list_serializer


def collect_edit(**kwargs):
    _ent_conf = {}
    for key, val in kwargs.items():
        if val == '':
            continue

        grp, item = key.split(':')

        if val == 'False':
            val = False
        elif val == 'True':
            val = True
        elif is_multi_valued(item, grp):
            val = val.strip()
            val = val.strip("[]")
            _tmp = [v.strip() for v in val.split(',')]
            val = [v.strip("'\"") for v in _tmp]
        else:
            val = val.strip()
            val = val.strip("'\"")

        try:
            _ent_conf[grp][item] = val
        except KeyError:
            _ent_conf[grp] = {item: val}

    _ent_conf['tool'] = tool_conf_massage(_ent_conf['tool'])
    return _ent_conf


class Instance(object):
    def __init__(self, rest, baseurl, tool_conf, app, entpath='entities',
                 html=None):
        self.rest = rest
        self.baseurl = baseurl
        self.entpath = entpath
        self.tool_conf = tool_conf
        self.html = html
        self.app = app

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if vpath[0] == 'run':
            if len(vpath) == 2:
                cherrypy.request.params['iss'] = unquote_plus(vpath.pop(0))
                cherrypy.request.params['tag'] = unquote_plus(vpath.pop(0))
            cherrypy.request.params['ev'] = init_events(
                cherrypy.request.path_info)

            return self.run

    @cherrypy.expose
    def new(self):
        logger.info("New instance")
        return self.html['new_iss.html']

    @cherrypy.expose
    def index(self):
        return as_bytes(self.html['main.html'])

    def store_edit(self, qp, **kwargs):
        _ent_conf = collect_edit(**kwargs)
        self.rest.write(qp[0], qp[1], _ent_conf)

    @cherrypy.expose
    def run(self, iss='', tag='', ev=None, **kwargs):
        uqp, qp = unquote_quote(iss, tag)
        logger.info('Run iss="{}", tag="{}"'.format(*uqp))

        self.store_edit(qp, **kwargs)

        return self.restart_instance(iss, tag, 'start')

    def restart_instance(self, iss, tag, action='restart'):
        uqp, qp = unquote_quote(iss, tag)
        logger.info('{} iss="{}", tag="{}"'.format(action, uqp[0], uqp[1]))
        url = self.app.run_test_instance(qp[0], qp[1])

        if isinstance(url, Response):
            return conv_response(None, url)

        if url:
            args = {
                'title': "Action performed", 'base': self.baseurl,
                'note': 'Your test instance "{iss}:{tag}" has been '
                        '{act} as <a href="{url}">{url}</a>'.format(
                    iss=uqp[0], tag=uqp[1], url=url, act=action)}
        else:
            args = {
                'title': "Action Failed", 'base': self.baseurl,
                'note': 'Could not {} your test instance'.format(action)}

        _msg = self.html['message.html'].format(**args)
        return as_bytes(_msg)
