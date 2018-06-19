import cherrypy
import logging

from cherrypy import CherryPyException
from cherrypy import HTTPRedirect
from jwkest import as_bytes
from otest.result import Result

from oidctest.tt import conv_response

from otest import Break
from otest import exception_trace
from otest.check import CRITICAL
from otest.check import ERROR
from otest.check import State
from otest.events import EV_CONDITION
from otest.events import EV_EXCEPTION
from otest.events import EV_FAULT
from otest.events import EV_HTTP_ARGS
from otest.events import EV_RESPONSE

logger = logging.getLogger(__name__)

BANNER = "Something went seriously wrong, please tell us at " \
         "certification@oidf.org"


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

    def display_exception(self, exception_trace=''):
        """
        So far only one known special response type

        :param exception_trace:
        :return: Bytes
        """
        txt = [80 * '*', '\n', BANNER, '\n', 80 * '*', '\n', '\n', '\n']
        txt.extend(exception_trace)
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return as_bytes(txt)

    @cherrypy.expose
    def run(self, test):
        try:
            resp = self.tester.run(test, **self.webenv)
        except HTTPRedirect:
            raise
        except Exception as err:
            test_id = list(self.flows.complete.keys())[0]
            self.tester.conv.events.store(
                EV_CONDITION,
                State(test_id=test_id, status=ERROR, message=err,
                      context='run'))
            _trace = exception_trace('run', err, logger)
            return self.display_exception(exception_trace=_trace)

        self.sh['session_info'] = self.info.session

        if isinstance(resp, dict):
            return self.display_exception(**resp)
        elif resp is False or resp is True:
            pass
        elif isinstance(resp, list):
            return conv_response(self.sh.events, resp)
        elif isinstance(resp, bytes):
            return resp

        self.opresult()

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
                    self.opresult()
            else:
                return conv_response(self.sh['conv'].events, resp)
        else:
            self.opresult()

    @cherrypy.expose
    def display(self):
        return as_bytes(self.info.flow_list())

    def opresult(self):
        # _url = "{}display#{}".format(self.webenv['base_url'],
        #                              self.pick_grp(self.sh['conv'].test_id))
        # cherrypy.HTTPRedirect(_url)
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
    def authz_cb(self, **kwargs):
        _conv = self.sh["conv"]

        if cherrypy.request.method == 'POST':
            # You should only get query/fragment here
            self.process_error('Wrong HTTP method. No POST to this endpoint',
                             'authz_cb')

        try:
            response_mode = _conv.req.req_args["response_mode"]
        except KeyError:
            response_mode = ""

        # Check if fragment encoded
        if response_mode == ["form_post"]:
            self.process_error("Expected form_post, didn't get it", 'authz_cb')
        else:
            if _conv.req.req_args["response_type"] != ["code"]:
                try:
                    kwargs = cherrypy.request.params
                except KeyError:
                    pass
                else:
                    _conv.events.store(EV_HTTP_ARGS, kwargs, ref='authz_cb')
                    _conv.query_component = kwargs

                return self.info.opresult_fragment()

        _conv.events.store(EV_RESPONSE, 'Response URL with query part')

        try:
            resp = self.tester.async_response(self.webenv["conf"],
                                              response=kwargs)
        except cherrypy.HTTPRedirect:
            raise
        except Break:
            resp = False
            self.tester.store_result()
        except Exception as err:
            _conv.events.store(EV_FAULT, err)
            self.tester.store_result()
            resp = False

        if resp is False or resp is True:
            pass
        elif not isinstance(resp, int):
            return resp

        self.opresult()

    def process_error(self, msg, context):
        test_id = list(self.flows.complete.keys())[0]
        self.tester.conv.events.store(
            EV_CONDITION,
            State(test_id=test_id, status=ERROR, message=msg,
                  context=context))
        res = Result(self.sh, self.flows.profile_handler)
        self.tester.store_result(res)
        self.opresult()

    @cherrypy.expose
    def authz_post(self, **kwargs):
        _conv = self.sh["conv"]

        if cherrypy.request.method != 'POST':
            return self.process_error('Wrong HTTP method used', 'authz_post')

        # Can get here 2 ways, either directly if form_post is used or
        # indirectly if fragment encoding
        try:
            response_mode = _conv.req.req_args["response_mode"]
        except KeyError:
            response_mode = ''

        if response_mode != ['form_post']: # MUST be fragment
            response_type = _conv.req.req_args["response_type"]
            if response_type != ["code"]:
                if 'fragment' in kwargs:  # everything OK
                    self.tester.conv.events.store(EV_RESPONSE,
                                                  'URL with fragment')
                else:
                    return self.process_error('Expected URL with fragment part',
                                            'authz_post')
            else:
                return self.process_error('Expected URL with query part',
                                        'authz_post')
        else:
            self.tester.conv.events.store(EV_RESPONSE, 'Form post')

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

            self.opresult()
