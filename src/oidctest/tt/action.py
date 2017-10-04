import logging
import os
from urllib.parse import unquote_plus

import cherrypy
from jwkest import as_bytes
from oic.oauth2.message import list_serializer
from oic.utils.http_util import Response
from otest.prof_util import abbr_return_type
from otest.prof_util import do_discovery
from otest.prof_util import do_registration
from otest.prof_util import from_profile
from otest.prof_util import return_type
from otest.prof_util import to_profile
from otest.proc import kill_process
from otest.proc import isrunning

from oidctest.app_conf import TYPE2CLS
from oidctest.app_conf import create_model
from oidctest.cp import init_events
from oidctest.tt import conv_response
from oidctest.tt import unquote_quote

logger = logging.getLogger(__name__)

HEADLINE = {
    'tool': "Test tool configuration",
    "registration_response": "",
    "provider_info": ""
}

ball = '<button type="button" class="btn btn-warning"><span class="glyphicon ' \
       'glyphicon-plus"></span></button>'

_cline = '{} <input type="radio" name="{}:{}" value="{}" {}>'


def do_line(grp, key, val, req=False):
    if req:
        _ball = ball
    else:
        _ball = ''

    if val is False or val is True:
        if val is True:
            _choice = " ".join(
                [_cline.format('True', grp, key, 'True', 'checked'),
                 _cline.format('False', grp, key, 'False', '')])
        else:
            _choice = " ".join(
                [_cline.format('True', grp, key, 'True', ''),
                 _cline.format('False', grp, key, 'False', 'checked')])

        return '<tr><th width="35%">{}</th><td>{}</td><td width="10%">{}</td></tr>'.format(
            key, _choice, _ball)
    else:
        return " ".join([
            '<tr><th width="35%">{}</th><td><input'.format(key),
            'type="text" name="{}:{}"'.format(grp, key),
            'value="{}" class="form-control"></td><td width="10%">{}</td></tr>'.format(
                val, _ball)])


def comma_sep_list(key, val, multi):
    if key in multi:
        if isinstance(val, list):
            return ', '.join(val)
    return val


def display_form(head_line, grp, dic, state, multi):
    lines = ['<table class="table table-hover table-bordered">']
    if head_line:
        lines.append(
            '<thead><tr><th colspan="3" class="text-center info"><h3>{}</h3></th></tr></thead>'.format(
                head_line))
    lines.append('<tbody>')
    keys = list(dic.keys())
    keys.sort()
    if grp in state:
        for param in state[grp]['immutable']:
            val = comma_sep_list(param, dic[param], multi[grp])
            l = [
                '<tr><th>{}</th>'.format(param),
                '<td>{}</td><td>{}</td></tr>'.format(val, ball),
                '<input type="hidden" name="{}:{}" value="{}"'.format(grp,
                                                                      param,
                                                                      val)
            ]
            lines.append(''.join(l))
            keys.remove(param)
        for param in state[grp]['required']:
            try:
                _val = dic[param]
            except KeyError:
                lines.append(
                      do_line(grp, param, '**MISSING REQUIRED VALUE**', True))
            else:
                val = comma_sep_list(param, _val, multi[grp])
                lines.append(do_line(grp, param, val, True))
                keys.remove(param)
    for key in keys:
        val = comma_sep_list(key, dic[key], multi[grp])
        lines.append(do_line(grp, key, val, False))
    lines.append('</tbody></table>')
    return lines


def display(dicts, state, multi, notes, action):
    lines = [
        '<form class="col-md-10" action="{}" method="post">'.format(action)]
    for grp, info in dicts.items():
        lines.append('<br>')
        lines.extend(display_form(HEADLINE[grp], grp, info, state, multi))
    lines.append('<p>{}</p>'.format(notes))
    lines.append(
        '<div class="btn-toolbar">'
        '<button type="submit" value="configure" class="btn btn-primary">Save '
        '& Start</button>')
    lines.append(
        '<button type="submit" value="abort" class="btn '
        'btn-default">Abort</button>'
        '</div>')
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


def update_config(conf, tool_params):
    # provider_info and registration_response
    dicts = {'tool': conf['tool']}
    _prof = conf['tool']['profile']
    _spec = from_profile(conf['tool']['profile'])
    _spec['return_type'] = abbr_return_type(_spec['return_type'])
    del dicts['tool']['profile']
    dicts['tool'].update(_spec)

    for item in tool_params:
        if item == 'profile':
            continue
        if item not in dicts['tool']:
            dicts['tool'][item] = ''

    multi = {'tool': ['acr_values', 'claims_locales', 'ui_locales']}
    for typ in ['provider_info', 'registration_response']:
        multi[typ] = multi_value(typ)
        try:
            dicts[typ] = conf['client'][typ]
        except KeyError:
            try:
                dicts[typ] = update(typ, conf[typ])
            except KeyError:
                pass

    state = {
        'tool': {'immutable': ['issuer', 'tag', 'register', 'discover',
                               'webfinger'],
                 'required': ['return_type']}}

    notes = ''
    if _spec['webfinger']:
        state['tool']['required'].extend(['webfinger_email',
                                          'webfinger_url'])
        notes = ("If <i>webfinger</i> is True then one of "
                 "<i>webfinger_email</i> and <i>webfinger_url</i> "
                 "<b>MUST</b> have a value.")

    if 'registration_response' in dicts:
        state['registration_response'] = {
            'immutable': ['redirect_uris'],
            'required': ['client_id', 'client_secret']}

    if 'provider_info' in dicts:
        _req = ['authorization_endpoint', 'jwks_uri',
                'response_types_supported', 'subject_types_supported',
                'id_token_signing_alg_values_supported']

        state['provider_info'] = {'immutable': ['issuer']}

        if return_type(_prof) not in ['I', 'IT']:
            _req.append('token_endpoint')

        state['provider_info']['required'] = _req

    return dicts, state, multi, notes


class Action(object):
    def __init__(self, rest, tool_conf, html, entpath, ent_info_path,
                 tool_params, app, version):
        self.rest = rest
        self.tool_conf = tool_conf
        self.html = html
        self.entpath = entpath
        self.ent_info_path = ent_info_path
        self.baseurl = ''
        self.app = app
        self.tool_params = tool_params
        self.version = version

    @cherrypy.expose
    def index(self, iss, tag, ev, action):
        if action == 'restart':
            return self.restart(iss, tag, ev)
        elif action == 'delete':
            return self.delete(iss, tag, ev)
        elif action == 'configure':
            return self.update(iss, tag, ev)
        elif action == 'stop':
            return self.stop(iss, tag, ev)

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
        """
        Displays interface for updating configuration
        
        :param iss: Issuer ID 
        :param tag: tag
        :param ev: Event instance
        :param kwargs: keyword arguments
        :return: 
        """
        logger.debug('update test tool configuration: {} {}'.format(iss, tag))
        uqp, qp = unquote_quote(iss, tag)

        try:
            _format, _conf = self.rest.read_conf(qp[0], qp[1])
        except TypeError:
            _msg = "No such test tool configuration"
            logger.info(_msg)
        else:
            logger.info('config: {}'.format(_conf))

            dicts, state, multi, notes = update_config(_conf, self.tool_params)

            action = "{}/run/{}/{}".format('', qp[0], qp[1])
            _msg = self.html['instance.html'].format(
                display=display(dicts, state, multi, notes, action),
                version=self.version
            )

        return as_bytes(_msg)

    def kill(self, iss, tag, ev):
        uqp, qp = unquote_quote(iss, tag)
        _key = self.app.assigned_ports.make_key(*uqp)
        
        try:
            pid = isrunning(unquote_plus(iss), unquote_plus(tag))
        except KeyError:
            pass
        else:
            if pid:
                # logger.info('kill {}'.format(pid))
                # subprocess.call(['kill', str(pid)])
                kill_process(pid)
                try:
                    del self.app.running_processes[_key]
                except KeyError:
                    pass
        
    @cherrypy.expose
    def stop(self, iss, tag, ev):
        logger.info('stop test tool: {} {}'.format(iss, tag))

        # If already running - kill
        self.kill(iss, tag, ev)
        
        uqp, qp = unquote_quote(iss, tag)

        # redirect back to entity page
        loc = '{}entity/{}'.format(self.rest.base_url, qp[0])
        raise cherrypy.HTTPRedirect(loc)

    @cherrypy.expose
    def delete(self, iss, tag, ev, pid=0):
        logger.info('delete test tool configuration: {} {}'.format(iss, tag))
        
        # If already running - kill
        self.kill(iss, tag, ev)
        
        uqp, qp = unquote_quote(iss, tag)
        _key = self.app.assigned_ports.make_key(*uqp)

        os.unlink(os.path.join(self.entpath, *qp))
        # Remove issuer if out of tags
        if not os.listdir(os.path.join(self.entpath, qp[0])):
            os.rmdir(os.path.join(self.entpath, qp[0]))

        try:
            del self.app.assigned_ports[_key]
        except KeyError:  # How could it already have gone ? Ah, well
            pass

        # redirect back to entity page
        loc = '{}entity'.format(self.rest.base_url)
        raise cherrypy.HTTPRedirect(loc)

    @cherrypy.expose
    def restart(self, iss, tag, ev):
        """
        Restart a test instance
        
        :param iss: 
        :param tag: 
        :param ev: 
        :return: 
        """
        logger.info('restart test tool: {} {}'.format(iss, tag))
        uqp, qp = unquote_quote(iss, tag)
        url = self.app.run_test_instance(*qp)

        if isinstance(url, Response):
            return conv_response(None, url)

        if url:
            # redirect back to entity page
            loc = '{}entity/{}'.format(self.rest.base_url, qp[0])
            raise cherrypy.HTTPRedirect(loc)
        else:
            args = {
                'title': "Action Failed", 'base': self.baseurl,
                'note': 'Could not restart your test instance'}

        _msg = self.html['message.html'].format(**args)
        return as_bytes(_msg)

    @cherrypy.expose
    def create(self, **kwargs):
        logger.info(
            'create test tool configuration: {} {}'.format(kwargs['iss'],
                                                           kwargs['tag']))
        # construct profile
        try:
            profile = to_profile(kwargs)
        except KeyError as err:
            logger.error(err)
            return as_bytes('Sorry failed to create: {}'.format(err))

        _ent_conf = create_model(profile, ent_info_path=self.ent_info_path)

        if not do_discovery(profile):
            _ent_conf['client']['provider_info']['issuer'] = kwargs['iss']

        if not do_registration(profile):
            # need to create a redirect_uri, means I need to register a port
            _port = self.app.assigned_ports.register_port(kwargs['iss'],
                                                          kwargs['tag'])
            if self.app.test_tool_base.endswith('/'):
                _base = self.app.test_tool_base[:-1]
            else:
                _base = self.app.test_tool_base
            _ent_conf['client']['registration_response'][
                'redirect_uris'] = '{}:{}/authz_cb'.format(_base, _port)

        uqp, qp = unquote_quote(kwargs['iss'], kwargs['tag'])
        _ent_conf['tool']['issuer'] = uqp[0]
        _ent_conf['tool']['tag'] = uqp[1]
        _ent_conf['tool']['profile'] = profile

        _ent_conf.update(from_profile(profile))
        logger.info("Test tool config: {}".format(_ent_conf))

        self.rest.write(qp[0], qp[1], _ent_conf)
        # Do a redirect
        raise cherrypy.HTTPRedirect(
            '/action/update?iss={}&tag={}'.format(qp[0], qp[1]))
