import logging
import os
import time
from urllib.parse import unquote_plus

import cherrypy
from jwkest import as_bytes
from otest.proc import find_test_instance
from otest.proc import isrunning

from oidctest.cp import init_events
from oidctest.ass_port import AssignedPorts
from oidctest.tt import unquote_quote

logger = logging.getLogger(__name__)


def iss_table(base, issuers):
    issuers.sort()
    line = ["<table class=\"table table-hover table-bordered\">"]
    for iss in issuers:
        _item = '<a href="{}/entity/{}">{}</a>'.format(base, iss,
                                                       unquote_plus(iss))
        line.append("<tr><td>{}</td></tr>".format(_item))

    line.append("</table>")
    return '\n'.join(line)


def item_table(qiss, items, active, assigned_ports, test_tool_base):
    line = ["<table class=\"table table-hover table-bordered\">", "<tr class=\"info\"><th>Tag</th><th>Status</th><th>Actions</th></tr>"]
    _del = '<button class="btn btn-default" name="action" type="submit" value="delete"><span class="glyphicon glyphicon-remove"></span>&nbsp;Delete</button>'
    _rst = '<button class="btn btn-default" name="action" type="submit" value="restart"><span class="glyphicon glyphicon-refresh"></span>&nbsp;Restart</button>'
    _cnf = '<button class="btn btn-default" name="action" type="submit" value="configure"><span class="glyphicon glyphicon-edit"></span>&nbsp;Reconfigure</button>'
    _stop = '<button class="btn btn-default" name="action" type="submit" value="stop"><span class="glyphicon glyphicon-stop"></span>&nbsp;&nbsp;Stop</button>'

    for item in items:
        
        eid = assigned_ports.make_key(qiss, item)
        _port = assigned_ports[eid]
        _instance = '{}:{}'.format(test_tool_base, _port)

        _url = "/action/{}/{}".format(qiss, item)
        _action = '\n'.join([
            '<form class="col-md-10" action="{}" method="get">'.format(_url), _rst, _stop,
            _cnf, _del])
        if active[item]:
            _ball = '<button type="button" class="btn btn-success" alt="Green"><span class="glyphicon glyphicon-ok-sign"></span></button>'
            inst = "<a href=\"{}\">{}</a>".format(_instance, item)
        else:
            _ball = '<button type="button" class="btn btn-danger" alt="Red"><span class="glyphicon glyphicon-minus-sign"></span></button>'
            inst = item;
        line.append("<tr><td style=\"vertical-align: middle;\">{}</td><td class=\"text-center\">{}</td><td>{}</td></tr>".format(
            inst, _ball, _action))
        line.append('</form>')

    line.append("</table>")
    return '\n'.join(line)


class Entity(object):
    def __init__(self, entpath, prehtml, rest, assigned_ports, test_tool_base, version, backuppath='backup'):
        self.entpath = entpath
        self.prehtml = prehtml
        self.rest = rest
        self.assigned_ports = assigned_ports
        self.test_tool_base = test_tool_base
        self.backup = backuppath
        self.version = version

    @cherrypy.expose
    def index(self):
        fils = os.listdir(self.entpath)

        # Remove examples
        try:
            fils.remove('https%3A%2F%2Fexample.com')
        except ValueError:
            pass

        _msg = self.prehtml['list_iss.html'].format(
            iss_table=iss_table('', fils),
            version=self.version
        )
        return as_bytes(_msg)

    @cherrypy.expose
    def list_tag(self, iiss):
        uqp, qp = unquote_quote(iiss)
        logger.info('List all tags for "{}"'.format(uqp[0]))
        iss = uqp[0]
        qiss = qp[0]
        try:
            fils = os.listdir(os.path.join(self.entpath, qiss))
        except FileNotFoundError:
            return b"No such Issuer exists"

        active = dict([(fil, isrunning(iss, fil)) for fil in fils])

        self.assigned_ports.load()
        _msg = self.prehtml['list_tag.html'].format(
            item_table=item_table(qiss, fils, active, self.assigned_ports, self.test_tool_base),
            iss=iss,
            version=self.version
        )
        return as_bytes(_msg)

    @cherrypy.expose
    def show_tag(self, iiss, itag):
        uqp, qp = unquote_quote(iiss, itag)
        logger.info('Show info on iss="{}", tag="{}"'.format(*uqp))

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

    @cherrypy.expose
    def backup(self, iiss, itag):
        uqp, qp = unquote_quote(iiss, itag)
        logger.info('Do backup of iss="{}", tag="{}"'.format(*uqp))

        info = open(os.path.join(self.entpath, *qp), 'r').read()
        bname = '{}.{}.{}'.format(qp[0], qp[1], time.time())
        fp = open(os.path.join(self.backup, bname), 'w')
        fp.write(info)
        fp.close()
        return ''

    @cherrypy.expose
    def restore(self, iiss, itag):
        uqp, qp = unquote_quote(iiss, itag)
        logger.info('Restore iss="{}", tag="{}"'.format(*uqp))
        bname = '{}.{}'.format(qp[0], qp[1])
        last = 0.0
        last_backup = None
        for item in os.listdir(self.backup):
            if item.startswith("."):
                continue
            if not itag.startswith(bname):
                continue

            # Should be 3 parts, only interested in the last
            p = item.split('.')[-1]
            if float(p) > last:
                last = float(p)
                last_backup = item

        if last_backup:
            fn = os.path.join(self.backup, last_backup)
            info = open(fn, 'r').read()
            return self.rest.store(qp[0], qp[1], info)
