import cherrypy
import logging
import os

from urllib.parse import unquote_plus, quote_plus

from jwkest import as_bytes
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.utils.http_util import Response
from oidctest.tt import conv_response
from oidctest.tt import BUT
from otest.proc import kill_process

from src.oidctest.cp import init_events

logger = logging.getLogger(__name__)

HEADLINE = {
    'tool': "Test tool configuration",
    "registration_response": "",
    "provider_info": ""
}

ball = '<img src="/static/red-ball-16.png" alt="Red Ball">'


def do_line(grp, key, val, req=False):
    if req:
        _ball = ball
    else:
        _ball = ''

    if val is False or val is True:
        if val == "True":
            _choice = " ".join(
                ['True <input type="radio" name="{}:{}"',
                 'value="True" checked>'.format(grp, key),
                 'False <input type="radio" name="{}:{}" ',
                 'value="False">'.format(grp, key)])
        else:
            _choice = " ".join(
                ['True <input type="radio" name="{}:{}" ',
                 'value="True">'.format(grp, key),
                 'False <input type="radio" name="{}:{}" ',
                 'value="False" checked>'.format(grp, key)])

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
            'value="{}" class="str"></td><td>{}</td></tr>'.format(val, BUT)])


def display_form(head_line, grp, dic, state):
    lines = ['<h3>{}</h3>'.format(head_line), '<table>']
    keys = list(dic.keys())
    keys.sort()
    if grp in state:
        for param in state[grp]['immutable']:
            val = dic[param]
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
            val = dic[param]
            lines.append(do_line(grp, param, val, True))
            keys.remove(param)
    for key in keys:
        val = dic[key]
        lines.append(do_line(grp, key, val, False))
    lines.append('</table>')
    return lines


def display(base, iss, tag, dicts, state):
    lines = [
        '<form action="{}/run/{}/{}" method="post">'.format(base, iss, tag)]
    for grp, info in dicts.items():
        lines.append('<br>')
        lines.extend(display_form(HEADLINE[grp], grp, info, state))
    lines.append(
        '<button type="submit" value="configure" class="button">Save & '
        'Start</button>')
    lines.append(
        '<button type="submit" value="abort" class="abort">Abort</button>')
    lines.append('</form>')
    return "\n".join(lines)


TYPE2CLS = {'provider_info': ProviderConfigurationResponse,
            'registration_response': RegistrationResponse}


def update(typ, conf):
    cls = TYPE2CLS[typ]
    for param in cls.c_param:
        if param not in conf:
            conf[param] = ''
    return conf


class Action(object):
    def __init__(self, rest, tool_conf, html, entpath, app):
        self.rest = rest
        self.tool_conf = tool_conf
        self.html = html
        self.entpath = entpath
        self.baseurl = ''
        self.app = app

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
            cherrypy.request.params['iss'] = unquote_plus(vpath.pop(0))
            cherrypy.request.params['tag'] = unquote_plus(vpath.pop(0))
            cherrypy.request.params['ev'] = init_events(
                cherrypy.request.path_info)

            return self

    def update(self, iss, tag, ev):
        qp = [quote_plus(p) for p in [iss, tag]]
        _format, _conf = self.rest.read_conf(qp[0], qp[1])

        # provider_info and registration_response
        dicts = {'tool': _conf['tool']}
        for item in self.tool_conf:
            if item not in dicts['tool']:
                dicts['tool'][item] = ''

        for typ in ['provider_info', 'registration_response']:
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
        _msg = self.html['instance'].format(
            display=display('', qp[0], qp[1], dicts, state))

        return as_bytes(_msg)

    @cherrypy.expose
    def delete(self, iss, tag, ev, pid=0):
        qp = [quote_plus(p) for p in [iss, tag]]
        _key = '{}:{}'.format(*lp)

        if pid:
            kill_process(pid)
            del self.app.running_processes[_key]

        os.unlink(os.path.join(self.entpath, *qp))
        # Remove issuer if out of tags
        if not os.listdir(os.path.join(self.entpath, qp[0])):
            os.rmdir(os.path.join(self.entpath, qp[0]))

        del self.app.assigned_ports[_key]

        _msg = self.html['message'].format(
            title="Action performed",
            note='Your test tool instance <em>{}:{}</em> has been '
                 'removed'.format(iss, tag))

        return as_bytes(_msg)

    @cherrypy.expose
    def restart(self, iss, tag, ev):
        url = self.app.run_test_instance(quote_plus(iss), quote_plus(tag))

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

        _msg = self.html['message'].format(**args)
        return as_bytes(_msg)
