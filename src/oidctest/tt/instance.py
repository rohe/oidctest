import cherrypy
import logging
import os

from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from jwkest import as_bytes
from oic.utils.http_util import Response

from oidctest.tt import conv_response

logger = logging.getLogger(__name__)


class Instance(object):
    def __init__(self, rest, baseurl, tool_conf, entpath='entities', html=None):
        self.rest = rest
        self.baseurl = baseurl
        self.entpath = entpath
        self.tool_conf = tool_conf
        self.html = html

    @cherrypy.expose
    def new(self):
        return self.html['new_iss.html']

    @cherrypy.expose
    def index(self):
        return as_bytes(self.html['main.html'])

    def restart_instance(self, app, part):
        _iss = unquote_plus(part[0])
        _tag = unquote_plus(part[1])
        url = app.run_test_instance(quote_plus(_iss), quote_plus(_tag))

        if isinstance(url, Response):
            return conv_response(None, url)

        if url:
            args = {
                'title': "Action performed", 'base': self.baseurl,
                'note': 'Your test instance "{iss}:{tag}" has been '
                        'restarted as <a href="{url}">{url}</a>'.format(
                    iss=_iss, tag=_tag, url=url)}
        else:
            args = {
                'title': "Action Failed", 'base': self.baseurl,
                'note': 'Could not restart your test instance'}

        _msg = self.html['message'].format(**args)
        return as_bytes(_msg)
