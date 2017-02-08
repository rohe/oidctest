import cherrypy
import logging

from cherrypy import CherryPyException
from cherrypy import HTTPRedirect
from jwkest import as_bytes
from oidctest.tt import conv_response
from otest import exception_trace

logger = logging.getLogger(__name__)


class Main(object):
    def __init__(self, tester, flows, webenv, pick_grp, **kwargs):
        self.tester = tester
        self.sh = tester.sh
        self.info = tester.inut
        self.flows = flows
        self.webenv = webenv
        self.pick_grp = pick_grp
        self.kwargs = kwargs

    @cherrypy.expose
    def index(self):
        try:
            if self.sh.session_init():
                return as_bytes(self.info.flow_list())
            else:
                try:
                    _url = "{}opresult#{}".format(self.kwargs['base_url'],
                                                  self.sh["testid"][0])
                    cherrypy.HTTPRedirect(_url)
                except KeyError:
                    return as_bytes(self.info.flow_list())
        except Exception as err:
            exception_trace("display_test_list", err)
            cherrypy.HTTPError(message=err)

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if len(vpath) == 1:
            if vpath[0] in self.flows:
                cherrypy.request.params['test'] = vpath.pop(0)
                return self.run
        elif len(vpath) == 2:
            if vpath[0] == 'test_info':
                cherrypy.request.params['op_id'] = vpath[1]
                return self.test_info

    @cherrypy.expose
    def run(self, test):
        resp = self.tester.run(test, **self.webenv)
        self.sh['session_info'] = self.info.session

        if resp is False or resp is True:
            pass
        elif isinstance(resp, list):
            return conv_response(self.sh.events, resp)

        try:
            #  return info.flow_list()
            _url = "{}display#{}".format(
                    self.webenv['client_info']['base_url'],
                    self.pick_grp(self.sh['conv'].test_id))

            raise HTTPRedirect(_url, 303)
        except Exception as err:
            logger.error(err)
            raise CherryPyException(err)

    @cherrypy.expose
    def reset(self):
        self.sh.reset_session()
        return conv_response(self.sh.events, self.info.flow_list())

    @cherrypy.expose
    def pedit(self):
        try:
            return as_bytes(self.info.profile_edit())
        except Exception as err:
            return as_bytes(self.info.err_response("pedit", err))

    @cherrypy.expose
    def profile(self, **kwargs):
        return as_bytes(self.tester.set_profile(kwargs))

    @cherrypy.expose
    def test_info(self, op_id):
        try:
            return as_bytes(self.info.test_info(op_id))
        except KeyError:
            return as_bytes(self.info.not_found())

    @cherrypy.expose
    def next(self):
        resp = self.tester.cont(self.webenv)
        self.sh['session_info'] = self.info.session
        if resp:
            return conv_response(self.sh.events, resp)
        else:
            _url = "{}display#{}".format(self.webenv['base_url'],
                                         self.pick_grp(self.sh['conv'].test_id))
            HTTPRedirect(_url)

    def display(self):
        return as_bytes(self.info.flow_list())

    def opresult(self):
        _url = "{}display#{}".format(self.webenv['base_url'],
                                     self.pick_grp(self.sh['conv'].test_id))
        cherrypy.HTTPRedirect(_url)
