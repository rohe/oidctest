import cherrypy
import os

from urllib.parse import quote_plus
from urllib.parse import unquote_plus

import logging
from jwkest import as_bytes

from otest.proc import find_test_instance
from otest.proc import isrunning

from oidctest.tt import BUT
from oidctest.cp import init_events

logger = logging.getLogger(__name__)


def iss_table(base, issuers):
    issuers.sort()
    line = ["<table>"]
    for iss in issuers:
        _item = '<a href="{}/entity/{}">{}</a>'.format(base, iss,
                                                       unquote_plus(iss))
        line.append("<tr><td>{}</td></tr>".format(_item))

    line.append("</table>")
    return '\n'.join(line)


def item_table(qiss, items, active):
    line = ["<table>", "<tr><th>Tag</th><th>Status</th><th>Actions</th></tr>"]
    _del = BUT.format('delete', 'delete')
    _rst = BUT.format('restart', 'restart')
    _cnf = BUT.format('configure', 'reconfigure')

    for item in items:
        _url = "/action/{}/{}".format(qiss, item)
        _action = '\n'.join([
            '<form action="{}" method="get">'.format(_url), _del,
            _rst, _cnf])
        if active[item]:
            _ball = '<img src="/static/green-ball-32.png" alt="Green">'
        else:
            _ball = '<img src="/static/red-ball-32.png" alt="Red">'
        line.append("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            item, _ball, _action))

    line.append("</table>")
    return '\n'.join(line)


class Entity(object):
    def __init__(self, entpath, prehtml):
        self.entpath = entpath
        self.prehtml = prehtml

    @cherrypy.expose
    def index(self):
        fils = os.listdir(self.entpath)
        # Remove examples
        fils.remove('https%3A%2F%2Fexample.com')

        _msg = self.prehtml['list_iss.html'].format(
            iss_table=iss_table('', fils))
        return as_bytes(_msg)

    @cherrypy.expose
    def list_tag(self, iiss):
        iss = unquote_plus(iiss)
        qiss = quote_plus(iss)
        fils = os.listdir(os.path.join(self.entpath, qiss))

        active = dict([(fil, isrunning(iss, fil)) for fil in fils])

        _msg = self.prehtml['list_tag.html'].format(
            item_table=item_table(qiss, fils, active), iss=iss)
        return as_bytes(_msg)

    @cherrypy.expose
    def show_tag(self, iiss, itag):
        uqp = [unquote_plus(p) for p in [iiss, itag]]
        qp = [quote_plus(p) for p in uqp]

        if find_test_instance(*uqp):
            active = '<div class="active"> Running </div>'
        else:
            active = '<div class="inactive"> Inactive </div>'

        info = open(os.path.join(self.entpath, *qp), 'r').read()

        _msg = self.prehtml['action.html'].format(path=qp[-1], active=active,
                                                  display_info=info)
        return as_bytes(_msg)

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if len(vpath):
            cherrypy.request.params['iiss'] = vpath.pop(0)
            ev = init_events(cherrypy.request.path_info)

            if len(vpath):
                cherrypy.request.params['itag'] = vpath.pop(0)
                return self.show_tag
            else:
                return self.list_tag

