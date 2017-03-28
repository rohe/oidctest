import cherrypy
import logging

from cherrypy import CherryPyException
from cherrypy import HTTPRedirect
from jwkest import as_bytes
from oidctest.tt import conv_response

from otest import exception_trace
from otest.check import CRITICAL
from otest.events import EV_HTTP_ARGS, EV_EXCEPTION

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
        except cherrypy.HTTPRedirect:
            raise
        except Exception as err:
            exception_trace("display_test_list", err)
            cherrypy.HTTPError(message=str(err))

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if vpath[0] == 'continue':
            return self.next

        if len(vpath) == 1:
            if vpath[0] in self.flows:
                cherrypy.request.params['test'] = vpath.pop(0)
                return self.run
        elif len(vpath) == 2:
            if vpath[0] == 'test_info':
                cherrypy.request.params['test_id'] = vpath[1]
                return self.test_info

    @cherrypy.expose
    def run(self, test):
        resp = self.tester.run(test, **self.webenv)
        self.sh['session_info'] = self.info.session

        if resp is False or resp is True:
            pass
        elif isinstance(resp, list):
            return conv_response(self.sh.events, resp)
        elif isinstance(resp, bytes):
            return resp

        try:
            #  return info.flow_list()
            _url = "{}display#{}".format(
                self.webenv['client_info']['base_url'],
                self.pick_grp(self.sh['conv'].test_id))

            raise HTTPRedirect(_url, 303)
        except KeyError as err:
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
    def test_info(self, test_id):
        try:
            return as_bytes(self.info.test_info(test_id))
        except KeyError:
            raise cherrypy.HTTPError(404, test_id)

    @cherrypy.expose
    def next(self, **kwargs):
        resp = self.tester.cont(**kwargs)
        self.sh['session_info'] = self.info.session
        if resp:
            if isinstance(resp, int):
                if resp == CRITICAL:
                    exp = self.tester.conv.events.get_data(EV_EXCEPTION)
                    if exp:
                        raise cherrypy.HTTPError(message=exp[0])
            else:
                return conv_response(self.sh['conv'].events, resp)
        else:
            _url = "{}display#{}".format(self.webenv['base_url'],
                                         self.pick_grp(self.sh['conv'].test_id))
            HTTPRedirect(_url)

    @cherrypy.expose
    def display(self):
        return as_bytes(self.info.flow_list())

    def opresult(self):
        _url = "{}display#{}".format(self.webenv['base_url'],
                                     self.pick_grp(self.sh['conv'].test_id))
        cherrypy.HTTPRedirect(_url)

    @cherrypy.expose
    def authz_cb(self, **kwargs):
        _conv = self.sh["conv"]
        try:
            response_mode = _conv.req.req_args["response_mode"]
        except KeyError:
            response_mode = ""

        # Check if fragment encoded
        if response_mode == "form_post":
            pass
        else:
            try:
                response_type = _conv.req.req_args["response_type"]
            except KeyError:
                response_type = [""]

            if response_type == [""]:  # expect anything
                if cherrypy.request.params:
                    kwargs = cherrypy.request.params
                else:
                    return self.info.opresult_fragment()
            elif response_type != ["code"]:
                # but what if it's all returned as a query anyway ?
                try:
                    kwargs = cherrypy.request.params
                except KeyError:
                    pass
                else:
                    _conv.events.store(EV_HTTP_ARGS, kwargs)
                    _conv.query_component = kwargs

                return self.info.opresult_fragment()

        try:
            resp = self.tester.async_response(self.webenv["conf"],
                                              response=kwargs)
        except cherrypy.HTTPRedirect:
            raise
        except Exception as err:
            return self.info.err_response("authz_cb", err)
        else:
            if resp is False or resp is True:
                pass
            elif not isinstance(resp, int):
                return resp

            try:
                # return info.flow_list()
                url = "{}display#{}".format(
                    self.webenv['client_info']['base_url'],
                    self.pick_grp(_conv.test_id))
            except Exception as err:
                logger.error(err)
                raise cherrypy.HTTPError(message=str(err))
            else:
                raise cherrypy.HTTPRedirect(url)
