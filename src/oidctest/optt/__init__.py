import logging

import cherrypy
from cherrypy import CherryPyException
from cherrypy import HTTPRedirect
from jwkest import as_bytes
from jwkest import as_unicode
from oic.oic import AuthorizationResponse
from otest import Break
from otest import OperationError
from otest import exception_trace
from otest.check import CRITICAL
from otest.check import OK
from otest.check import State
from otest.check import get_protocol_response
from otest.events import EV_CONDITION
from otest.events import EV_EXCEPTION
from otest.events import EV_FAULT
from otest.events import EV_HTTP_ARGS
from otest.events import EV_HTTP_REQUEST
from otest.events import EV_REQUEST
from otest.events import EV_RESPONSE
from otest.result import Result

from oidctest.tt import conv_response

logger = logging.getLogger(__name__)

BANNER = """
Something went wrong! If you know or suspect you know why, then try to
fix it. If you have no idea, then please tell us at certification@oidf.org
and we will help you figure it out.
"""

LOGOUT_MAP = {
    "FrontChannelLogout": "frontchannel_logout",
    "BackChannelLogout": "backchannel_logout",
    "PostLogout": "logout"
}


def expected_response_mode(conv):
    try:
        response_mode = conv.req.req_args["response_mode"]
    except KeyError:
        if conv.req.req_args["response_type"] == [''] or conv.req.req_args[
                "response_type"] == ['code']:
            response_mode = 'query'
        else:
            response_mode = 'fragment'
    else:
        if isinstance(response_mode, list):
            if len(response_mode):
                response_mode = response_mode[0]
            else:
                raise ValueError(
                    'Unknown response_mode value: {}'.format(response_mode))

    return response_mode


class Main(object):
    def __init__(self, tester, flows, webenv, pick_grp, **kwargs):
        self.tester = tester
        self.sh = tester.sh
        self.info = tester.inut
        self.flows = flows
        self.webenv = webenv
        self.pick_grp = pick_grp
        self.kwargs = kwargs
        self.session_checks = {'changed': 0, 'unchanged': 0}
        self.max_checks = self.info.conf.SESSION_MAX_CHECKS

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
        self.session_checks = {'changed': 0, 'unchanged': 0}
        try:
            resp = self.tester.run(test, **self.webenv)
        except HTTPRedirect:
            raise
        except Exception as err:
            # test_id = list(self.flows.complete.keys())[0]
            _trace = exception_trace('run', err, logger)
            self.tester.conv.events.store(EV_FAULT, _trace)
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
        try:
            #  return info.flow_list()
            _url = "{}display#{}".format(
                self.webenv['client_info']['base_url'],
                self.pick_grp(self.sh['conv'].test_id))

            raise HTTPRedirect(_url, 303)
        except KeyError as err:
            logger.error(err)
            raise CherryPyException(err)

    def process_error(self, msg, context):
        # test_id = list(self.flows.complete.keys())[0]
        self.tester.conv.events.store(EV_RESPONSE, msg)
        self.tester.conv.events.store(EV_FAULT, 'Error in {}'.format(context))
        # self.tester.conv.events.store(EV_CONDITION, State('Done', status=OK))
        res = Result(self.sh, self.flows.profile_handler)
        self.tester.store_result(res)
        logger.error('Encountered: {} in "{}"'.format(msg, context))
        self.opresult()

    def main_page(self):
        res = Result(self.sh, self.flows.profile_handler)
        self.tester.store_result(res)
        return self.display()

    @cherrypy.expose
    # @cherrypy.tools.allow(methods=["GET"])
    def authz_cb(self, **kwargs):
        if cherrypy.request.method != 'GET':
            # You should only get query/fragment here using GET
            return self.process_error(
                'Wrong HTTP method used expected GET got "{}". Could be that '
                'I got a form_post to the wrong redirect_uri'.format(
                    cherrypy.request.method), 'authz_cb')

        _conv = self.sh["conv"]
        try:
            _response_mode = expected_response_mode(_conv)
        except ValueError as err:
            return self.process_error(err, 'authz_cb')

        if _response_mode == "form_post":
            return self.process_error("Expected form_post, didn't get it",
                                      'authz_cb')
        elif _response_mode == 'fragment':
            try:
                kwargs = cherrypy.request.params
            except KeyError:
                pass
            else:
                _conv.events.store(EV_HTTP_ARGS, kwargs, ref='authz_cb')
                _conv.query_component = kwargs

            return self.info.opresult_fragment()

        if kwargs == {}:  # This should never be the case
            return self.process_error(
                'Got empty response could be I got something fragment '
                'encoded. Expected query response mode', 'authz_cb')

        _conv.events.store(EV_RESPONSE, 'Response URL with query part')

        try:
            resp = self.tester.async_response(self.webenv["conf"],
                                              response=kwargs)
        except cherrypy.HTTPRedirect:
            # self.tester.flows.store_test_info(self)
            raise
        except Break:
            resp = False
            self.tester.store_result()
        except Exception as err:
            _trace = exception_trace('authz_cb', err, logger)
            _conv.events.store(EV_FAULT, _trace)
            self.tester.store_result()
            return self.display_exception(exception_trace=_trace)

        if resp is False or resp is True:
            pass
        elif isinstance(resp, dict) and 'exception_trace' in resp:
            return self.display_exception(**resp)
        elif not isinstance(resp, int):
            return resp

        self.opresult()

    @cherrypy.expose
    # @cherrypy.tools.allow(methods=["POST"])
    def authz_post(self, **kwargs):
        if cherrypy.request.method != 'POST':
            return self.process_error(
                'Wrong HTTP method used expected POST got "{}"'.format(
                    cherrypy.request.method),
                'authz_post')

        _conv = self.sh["conv"]
        try:
            _response_mode = expected_response_mode(_conv)
        except ValueError as err:
            return self.process_error(err, 'authz_cb')

        # Can get here 2 ways, either directly if form_post is used or
        # indirectly if fragment encoding
        if _response_mode == 'query':  # should not be here at all
            if 'fragment' in kwargs:
                return self.process_error(
                    'Expected URL with query part got fragment', 'authz_post')
            else:
                return self.process_error(
                    'Expected URL with query part got form_post', 'authz_post')
        elif _response_mode == 'fragment':
            if 'fragment' in kwargs:  # everything OK
                self.tester.conv.events.store(EV_RESPONSE,
                                              'URL with fragment')
            else:
                return self.process_error(
                    'Expected URL with fragment part got form_post',
                    'authz_post')
        else:
            self.tester.conv.events.store(EV_RESPONSE, 'Form post')

        try:
            resp = self.tester.async_response(self.webenv["conf"],
                                              response=kwargs)
        except cherrypy.HTTPRedirect:
            raise
        except Exception as err:
            _trace = exception_trace('authz_post', err, logger)
            return self.display_exception(exception_trace=_trace)
            # return self.info.err_response("authz_cb", err)
        else:
            if resp is False or resp is True:
                pass
            elif not isinstance(resp, int):
                return resp

            self.opresult()

    def _endpoint(self, ref, request=None, **kwargs):
        _conv = self.sh['conv']

        # continue with next operation in the sequence
        self.sh["index"] += 1
        item = self.sh["sequence"][self.sh["index"]]
        if isinstance(item, tuple):
            cls, _ = item
        else:
            cls = item
        logger.debug('Next operation: %s (ref:%s)', cls.__name__, ref)
        if LOGOUT_MAP[cls.__name__] != ref:
            _conv.events.store(EV_FAULT, "Expected {} but got {}".format(cls.__name__, ref))
            self.tester.store_result()
            self.opresult()

        try:
            resp = self.tester.handle_request(request, **kwargs)
        except cherrypy.HTTPRedirect:
            self.tester.flows.store_test_info(self.tester)
            raise
        except (Break, OperationError) as err:
            resp = False
            _conv.events.store(EV_FAULT, err)
            self.tester.store_result()
        except Exception as err:
            _trace = exception_trace(ref, err, logger)
            _conv.events.store(EV_FAULT, _trace)
            self.tester.store_result()
            return self.display_exception(exception_trace=_trace)

        if resp is False or resp is True:
            pass
        elif resp in ["DONE", ""]:
            pass
        elif isinstance(resp, dict) and 'exception_trace' in resp:
            return self.display_exception(**resp)
        elif not isinstance(resp, int):
            return resp

        self.opresult()

    @cherrypy.expose
    def logout(self, **kwargs):  # post_logout_redirect_uri
        self.sh['conv'].events.store(EV_REQUEST, kwargs, receiver=self.tester.__class__.__name__)
        logger.debug('Post logout: {}'.format(kwargs))
        if kwargs:
            return self._endpoint(ref='logout', request_args=kwargs)
        else:
            return self._endpoint(ref='logout')

    @cherrypy.expose
    def backchannel_logout(self, **kwargs):
        logger.debug('Back channel logout: {}'.format(kwargs))
        self.sh['conv'].events.store(EV_HTTP_REQUEST, kwargs)
        if cherrypy.request.process_request_body is True:
            _request = as_unicode(cherrypy.request.body.read())
            if _request:
                logger.info('back_channel logout request: {}'.format(_request))
                if kwargs['entity_id'] != self.tester.conv.entity.entity_id:
                    self.sh['conv'].events.store(EV_FAULT, "Not for me!")
                    logger.debug('Not for me')
                    self.opresult()
                else:
                    return self._endpoint(ref='backchannel_logout',
                                          request=_request)
            else:
                _request_args = cherrypy.request.params
                if not _request_args:
                    raise cherrypy.HTTPError(
                        400, 'Missing Back channel Logout request body')

                logger.info('back_channel logout request_args: {}'.format(
                    _request_args))
                if kwargs['entity_id'] != self.tester.conv.entity.entity_id:
                    self.sh['conv'].events.store(EV_FAULT, "Not for me!")
                    logger.debug('Not for me')
                    self.opresult()
                else:
                    return self._endpoint(ref='backchannel_logout',
                                          request_args=_request_args)
        else:
            raise cherrypy.HTTPError(
                400, 'Missing Back channel Logout request body')

    @cherrypy.expose
    def frontchannel_logout(self, **kwargs):
        logger.debug('Front channel logout: {}'.format(kwargs))
        self.sh['conv'].events.store(EV_HTTP_REQUEST, kwargs)
        if kwargs['entity_id'] != self.tester.conv.entity.entity_id:
            logger.debug('Not for me')
            self.sh['conv'].events.store(EV_FAULT, "Not for me!")
            logger.debug('Not for me')
            self.opresult()
        else:
            _args = dict([(k, v) for k, v in kwargs.items()
                          if k not in ['entity_id', 'sid']])
            return self._endpoint(ref='frontchannel_logout', **_args)

    @cherrypy.expose
    def session_unchange(self, **kwargs):
        try:
            _state = kwargs['state']
        except KeyError:
            pass
        else:
            if _state == 'unchanged':
                self.tester.conv.events.store(
                    'SessionState', 'Session state verified unchanged')
                _index = self.tester.sh['index']
                _index += 1
                return self.tester.run_flow(self.tester.conv.test_id,
                                            index=_index)
            else:  # display session_verify.html again
                self.session_checks['unchanged'] += 1
                self.tester.conv.events.store(
                    'SessionState',
                    'Session check {} returned: {}'.format(
                        self.session_checks['unchanged'], _state))
                if self.session_checks['unchanged'] == self.max_checks:
                    self.tester.conv.events.store(EV_FAULT,
                                                  'Session state not unchanged')
                    return self.main_page()
                else:
                    _msg = self.tester.inut.pre_html['session_verify.html']
                    _csi = self.tester.conv.entity.provider_info['check_session_iframe']
                    _mod_msg = _msg.replace("{check_session_iframe}", _csi)
                    return as_bytes(_mod_msg)

    @cherrypy.expose
    def session_change(self, **kwargs):
        try:
            _state = kwargs['state']
        except KeyError:
            pass
        else:
            logger.debug('Session state: {}'.format(kwargs))
            self.tester.conv.events.store(
                'SessionState',
                'Session check returned: {}'.format(_state))

            if _state == 'changed':
                self.tester.conv.events.store(EV_CONDITION,
                                              State('Done', status=OK))
                self.tester.store_result()
                self.opresult()
            else:  # display after_logout.html again
                self.session_checks['changed'] += 1
                logger.debug('{} session check'.format(self.session_checks[
                                                           'changed']))
                self.tester.conv.events.store(
                    'SessionState',
                    'Session check {} returned: {}'.format(
                        self.session_checks['unchanged'], _state))

                if self.session_checks['changed'] >= self.max_checks:
                    self.tester.conv.events.store(EV_FAULT,
                                                  'Session state not changed')
                    return self.main_page()
                else:
                    _msg = self.tester.inut.pre_html['after_logout.html']
                    _csi = self.tester.conv.entity.provider_info[
                        'check_session_iframe']
                    _mod_msg = _msg.replace("{check_session_iframe}", _csi)
                    return as_bytes(_mod_msg)

    def rp_iframe(self, status, service_url):
        _conv = self.tester.conv
        _entity = _conv.entity

        _msg = self.tester.inut.pre_html['rp_session_iframe.html']
        # client_id
        _msg = _msg.replace("{client_id}", _entity.client_id)
        # session_state, get it from the Authorization response
        inst = get_protocol_response(_conv, AuthorizationResponse)
        _msg = _msg.replace("{session_state}", inst[0]['session_state'])
        # issuer
        _msg = _msg.replace("{issuer}", _entity.provider_info['issuer'])
        # session_change_url

        _msg = _msg.replace("{service_url}", service_url)
        _msg = _msg.replace('{status}', status)

        return as_bytes(_msg)

    @cherrypy.expose
    def session_iframe_unchanged(self):
        _entity = self.tester.conv.entity
        _service_url = self.info.conf.SESSION_UNCHANGE_URL.format(
            _entity.base_url)
        return self.rp_iframe('unchanged', _service_url)

    @cherrypy.expose
    def session_iframe_changed(self):
        _entity = self.tester.conv.entity
        _service_url = self.info.conf.SESSION_CHANGE_URL.format(
            _entity.base_url)
        return self.rp_iframe('changed', _service_url)
