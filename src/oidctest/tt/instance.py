import cherrypy
import logging

from urllib.parse import unquote_plus

from jwkest import as_bytes
from oic.utils.http_util import Response
from oidctest.cp import init_events

from oidctest.tt import conv_response, unquote_quote

logger = logging.getLogger(__name__)


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

    @cherrypy.expose
    def run(self, iss='', tag='', ev=None, **kwargs):
        uqp, qp = unquote_quote(iss, tag)
        logger.info('Run iss="{}", tag="{}"'.format(*uqp))
        _ent_conf = {}
        for key, val in kwargs.items():
            if val == '':
                continue

            grp, item = key.split(':')

            if val == 'False':
                val = False
            elif val == 'True':
                val = True

            try:
                _ent_conf[grp][item] = val
            except KeyError:
                _ent_conf[grp] = {item: val}

        self.rest.write(qp[0], qp[1], _ent_conf)
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
