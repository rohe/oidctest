# CheeryPy dependent stuff
import os
import cherrypy
import logging

from otest.events import Events
from otest.events import EV_HTTP_REQUEST
from otest.events import HTTPRequest
from otest.events import layout

logger = logging.getLogger(__name__)


def write_events(events, oper_id, test_id):
    _dir = os.path.join("log", oper_id)
    file_name = os.path.join(_dir, test_id + '.txt')

    try:
        fp = open(file_name, "a+")
    except IOError:
        try:
            os.makedirs(_dir)
        except OSError:
            pass

        try:
            fp = open(file_name, "w")
        except Exception as err:
            logger.error(
                "Couldn't dump to log file {} reason: {}".format(
                    file_name, err))
            raise

    _elem = [layout(0, ev) for ev in events]
    fp.write("\n".join(_elem))
    fp.write("\n\n")
    fp.close()


def dump_log():
    try:
        op = cherrypy.request.params['op']
    except KeyError:
        pass
    else:
        write_events(op.events, op.oper_id, op.test_id)


def init_events(path, msg=''):
    ev = Events()
    if msg:
        ev.store('Init', '{} {} {}'.format(10 * '=', msg, 10 * '='))
    else:
        ev.store('Init', 40 * '=')
    req = HTTPRequest(path, method=cherrypy.request.method)
    try:
        req.authz = cherrypy.request.headers['Authorization']
    except KeyError:
        pass
    ev.store(EV_HTTP_REQUEST, req)
    return ev
