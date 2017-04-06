import json
import logging
import os
from urllib.parse import unquote_plus

import cherrypy
from jwkest import as_bytes
from oic.oauth2.message import list_serializer
from oic.utils.http_util import Response
from otest.proc import kill_process

from oidctest.app_conf import create_model
from oidctest.app_conf import TYPE2CLS
from oidctest.cp import init_events
from oidctest.prof_util import DISCOVER
from oidctest.prof_util import REGISTER
from oidctest.tt import conv_response
from oidctest.tt import unquote_quote

logger = logging.getLogger(__name__)

HEADLINE = {
    'tool': "Test tool configuration",
    "registration_response": "",
    "provider_info": ""
}

ball = '<img src="/static/Add_16x16.png" alt="Red Ball">'

_cline = '{} <input type="radio" name="{}:{}" value="{}" {}>'


def do_line(grp, key, val, req=False):
    if req:
        _ball = ball
    else:
        _ball = ''

    if val is False or val is True:
        if val == "True":
            _choice = " ".join(
                [_cline.format('True', grp, key, 'True', 'checked'),
                 _cline.format('False', grp, key, 'False', '')])
        else:
            _choice = " ".join(
                [_cline.format('True', grp, key, 'True', ''),
                 _cline.format('False', grp, key, 'False', 'checked')])

        return '<tr><th align="left">{}</th><td>{}</td><td>{}</td></tr>'.format(
            key, _choice, _ball)
    elif key in ['profile', 'issuer', 'tag']:
        l = [
            '<tr><th align="left">{}</th><td>{}</td><td>{}</td></tr>'.format(
                key, val, _ball),
            '<input type="hidden" name="{}:{}" value="{}"'.format(grp, key, val)
        ]
        return '\n'.join(l)
    else:
        return " ".join([
            '<tr><th align="left">{}</th><td><input'.format(key),
            'type="text" name="{}:{}"'.format(grp, key),
            'value="{}" class="str"></td><td>{}</td></tr>'.format(val, _ball)])


def comma_sep_list(key, val, multi):
    if key in multi:
        if isinstance(val, list):
            return ', '.join(val)
    return val


def display_form(head_line, grp, dic, state, multi):
    lines = ['<h3>{}</h3>'.format(head_line), '<table>']
    keys = list(dic.keys())
    keys.sort()
    if grp in state:
        for param in state[grp]['immutable']:
            val = comma_sep_list(param, dic[param], multi[grp])
            l = [
                '<tr><th align="left">{}</th>'.format(param),
                '<td>{}</td><td>{}</td></tr>'.format(val, ball),
                '<input type="hidden" name="{}:{}" value="{}"'.format(grp,
                                                                      param,
                                                                      val)
            ]
            lines.append(''.join(l))
            keys.remove(param)
        for param in state[grp]['required']:
            val = comma_sep_list(param, dic[param], multi[grp])
            lines.append(do_line(grp, param, val, True))
            keys.remove(param)
    for key in keys:
        val = comma_sep_list(key, dic[key], multi[grp])
        lines.append(do_line(grp, key, val, False))
    lines.append('</table>')
    return lines


def display(base, iss, tag, dicts, state, multi):
    lines = [
        '<form action="{}/run/{}/{}" method="post">'.format(base, iss, tag)]
    for grp, info in dicts.items():
        lines.append('<br>')
        lines.extend(display_form(HEADLINE[grp], grp, info, state, multi))
    lines.append(
        '<button type="submit" value="configure" class="button">Save & '
        'Start</button>')
    lines.append(
        '<button type="submit" value="abort" class="abort">Abort</button>')
    lines.append('</form>')
    return "\n".join(lines)


def update(typ, conf):
    cls = TYPE2CLS[typ]
    for param in cls.c_param:
        if param not in conf:
            conf[param] = ''
    return conf


def multi_value(typ):
    cls = TYPE2CLS[typ]
    res = []
    for param, spec in cls.c_param.items():
        if spec[2] == list_serializer:
            res.append(param)
    return res


class Action(object):
    def __init__(self, rest, tool_conf, html, entpath, ent_info_path,
                 tool_params, app):
        self.rest = rest
        self.tool_conf = tool_conf
        self.html = html
        self.entpath = entpath
        self.ent_info_path = ent_info_path
        self.baseurl = ''
        self.app = app
        self.tool_params = tool_params

    @cherrypy.expose
    def index(self, iss, tag, ev, action):
        if action == 'restart':
            return self.restart(iss, tag, ev)
        elif action == 'delete':
            return self.delete(iss, tag, ev)
        elif action == 'configure':
            return self.update(iss, tag, ev)

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if len(vpath):
            if len(vpath) == 2:
                cherrypy.request.params['iss'] = unquote_plus(vpath.pop(0))
                cherrypy.request.params['tag'] = unquote_plus(vpath.pop(0))
            cherrypy.request.params['ev'] = init_events(
                cherrypy.request.path_info)

            return self

    @cherrypy.expose
    def update(self, iss, tag, ev=None, **kwargs):
        logger.debug('update test tool configuration')
        uqp, qp = unquote_quote(iss, tag)
        _format, _conf = self.rest.read_conf(qp[0], qp[1])

        # provider_info and registration_response
        dicts = {'tool': _conf['tool']}
        for item in self.tool_params:
            if item not in dicts['tool']:
                dicts['tool'][item] = ''

        multi = {'tool': ['acr_values', 'claims_locales', 'ui_locales']}
        for typ in ['provider_info', 'registration_response']:
            multi[typ] = multi_value(typ)
            try:
                dicts[typ] = _conf['client'][typ]
            except KeyError:
                try:
                    dicts[typ] = update(typ, _conf[typ])
                except KeyError:
                    pass

        state = {'immutable': {}, 'required': {}}
        if 'registration_response' in dicts:
            state['registration_response'] = {
                'immutable': ['redirect_uris'],
                'required': ['client_id', 'client_secret']}

        if 'provider_info' in dicts:
            _req = ['authorization_endpoint', 'jwks_uri',
                    'response_types_supported', 'subject_types_supported',
                    'id_token_signing_alg_values_supported']

            state['provider_info'] = {'immutable': ['issuer']}

            if _conf['tool']['profile'].split('.')[0] not in ['I', 'IT']:
                _req.append('token_endpoint')

            state['provider_info']['required'] = _req
        _msg = self.html['instance.html'].format(
            display=display('', qp[0], qp[1], dicts, state, multi))

        return as_bytes(_msg)

    @cherrypy.expose
    def delete(self, iss, tag, ev, pid=0):
        logger.info('delete test tool configuration')
        uqp, qp = unquote_quote(iss, tag)
        _key = self.app.assigned_ports(*uqp)

        if pid:
            kill_process(pid)
            del self.app.running_processes[_key]

        os.unlink(os.path.join(self.entpath, *qp))
        # Remove issuer if out of tags
        if not os.listdir(os.path.join(self.entpath, qp[0])):
            os.rmdir(os.path.join(self.entpath, qp[0]))

        del self.app.assigned_ports[_key]

        _msg = self.html['message.html'].format(
            title="Action performed",
            note='Your test tool instance <em>{}:{}</em> has been '
                 'removed'.format(iss, tag))

        return as_bytes(_msg)

    @cherrypy.expose
    def restart(self, iss, tag, ev):
        logging.info('restart test tool')
        uqp, qp = unquote_quote(iss, tag)
        url = self.app.run_test_instance(*qp)

        if isinstance(url, Response):
            return conv_response(None, url)

        if url:
            args = {
                'title': "Action performed", 'base': self.baseurl,
                'note': 'Your test instance "{iss}:{tag}" has been '
                        'restarted as <a href="{url}">{url}</a>'.format(
                    iss=iss, tag=tag, url=url)}
        else:
            args = {
                'title': "Action Failed", 'base': self.baseurl,
                'note': 'Could not restart your test instance'}

        _msg = self.html['message.html'].format(**args)
        return as_bytes(_msg)

    @cherrypy.expose
    def create(self, **kwargs):
        logging.info('create test tool configuration')
        # construct profile
        ppiece = [kwargs['return_type']]
        for p in ['webfinger', 'discovery', 'registration']:
            if p in kwargs:
                ppiece.append('T')
            else:
                ppiece.append('F')

        profile = '.'.join(ppiece)
        _ent_conf = create_model(profile, ent_info_path=self.ent_info_path)
        state = {}

        if ppiece[DISCOVER] == 'F':
            _ent_conf['client']['provider_info']['issuer'] = kwargs['iss']

        if ppiece[REGISTER] == 'F':
            # need to create a redirect_uri, means I need to register a port
            _port = self.app.assigned_ports.register_port(kwargs['iss'],
                                                          kwargs['tag'])
            _ent_conf['client']['registration_response'][
                'redirect_uris'] = '{}:{}/authz_cb'.format(
                self.app.test_tool_base[:-1], _port)

        uqp, qp = unquote_quote(kwargs['iss'], kwargs['tag'])
        _ent_conf['tool']['issuer'] = uqp[0]
        _ent_conf['tool']['tag'] = uqp[1]
        _ent_conf['tool']['profile'] = profile

        logging.info("Test tool config: {}".format(_ent_conf))

        self.rest.write(qp[0], qp[1], _ent_conf)
        # Do a redirect
        raise cherrypy.HTTPRedirect(
            '/action/update?iss={}&tag={}'.format(qp[0], qp[1]))
