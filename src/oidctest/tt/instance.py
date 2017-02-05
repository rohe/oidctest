import logging
import os
from urllib.parse import unquote_plus, quote_plus

import cherrypy
from jwkest import as_bytes
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.utils.http_util import Response
from otest.proc import kill_process, isrunning, find_test_instance

from oidctest.tt import conv_response

logger = logging.getLogger(__name__)

TYPE2CLS = {'provider_info': ProviderConfigurationResponse,
            'registration_response': RegistrationResponse}


def update(typ, conf):
    cls = TYPE2CLS[typ]
    for param in cls.c_param:
        if param not in conf:
            conf[param] = ''
    return conf


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
            'value="{}" class="str"></td><td>{}</td></tr>'.format(val, _b)])


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


HEADLINE = {
    'tool': "Test tool configuration",
    "registration_response": "",
    "provider_info": ""
}


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


def iss_table(base, issuers):
    issuers.sort()
    line = ["<table>"]
    for iss in issuers:
        _item = '<a href="{}/entity/{}">{}</a>'.format(base, iss,
                                                       unquote_plus(iss))
        line.append("<tr><td>{}</td></tr>".format(_item))

    line.append("</table>")
    return '\n'.join(line)


_b = '<button name="action" type="submit" value="{}" class="choice">{}</button>'


def item_table(qiss, items, active):
    line = ["<table>", "<tr><th>Tag</th><th>Status</th><th>Actions</th></tr>"]
    _del = _b.format('delete', 'delete')
    _rst = _b.format('restart', 'restart')
    _cnf = _b.format('configure', 'reconfigure')

    for item in items:
        _url = "/entity/{}/{}".format(qiss, item)
        _action = '\n'.join(['<form action="{}/action" method="get">'.format(
            _url), _del, _rst, _cnf])
        if active[item]:
            _ball = '<img src="/static/green-ball-32.png" alt="Green">'
        else:
            _ball = '<img src="/static/red-ball-32.png" alt="Red">'
        line.append("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            item, _ball, _action))

    line.append("</table>")
    return '\n'.join(line)


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
    def update(self, qiss, qtag):
        lp = [unquote_plus(p) for p in [qiss, qtag]]
        qp = [quote_plus(p) for p in lp]
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
    def delete(self, qiss, qtag, pid=0, app=None):
        lp = [unquote_plus(p) for p in [qiss, qtag]]
        qp = [quote_plus(p) for p in lp]
        _key = '{}:{}'.format(*lp)

        if pid:
            kill_process(pid)
            del app.running_processes[_key]

        os.unlink(os.path.join(self.entpath, *qp))
        # Remove issuer if out of tags
        if not os.listdir(os.path.join(self.entpath, qp[0])):
            os.rmdir(os.path.join(self.entpath, qp[0]))

        del app.assigned_ports[_key]

        _msg = self.html['message'].format(
            title="Action performed",
            note='Your test tool instance <em>{}:{}</em> has been '
                 'removed'.format(*lp))

        return as_bytes(_msg)

    @cherrypy.expose
    def index(self):
        return as_bytes(self.html['main.html'])

    @cherrypy.expose
    def list(self):
        fils = os.listdir(self.entpath)
        # Remove examples
        fils.remove('https%3A%2F%2Fexample.com')

        _msg = self.html['list_iss'].format(issuers=fils)
        return as_bytes(_msg)

    def list_tag(self, iss):
        _iss = unquote_plus(iss)
        qiss = quote_plus(_iss)
        fils = os.listdir(os.path.join(self.entpath, qiss))

        active = dict([(fil, isrunning(_iss, fil)) for fil in fils])

        _msg = self.html['list_tag'].format(
            item_tabel=item_table(qiss, fils, active), iss=_iss)
        return as_bytes(_msg)

    def show_tag(self, qiss, qtag):
        lp = [unquote_plus(p) for p in [qiss, qtag]]

        if find_test_instance(*lp):
            active = '<div class="active"> Running </div>'
        else:
            active = '<div class="inactive"> Inactive </div>'

        qp = [quote_plus(p) for p in lp]
        info = open(os.path.join(self.entpath, *qp), 'r').read()

        _msg = self.html['action'].format(path=qp[-1], active=active,
                                          display_info=info)
        return as_bytes(_msg)

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
