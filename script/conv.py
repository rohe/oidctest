#!/usr/bin/env python3
import importlib
import json
import os
import sys
from urllib.parse import quote_plus

from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse

from oidctest.app_conf import REST
from oidctest.ass_port import AssignedPorts


def convert(conf):
    ttc = importlib.import_module(conf)

    port = ttc.PORT
    _cli = ttc.CLIENT

    ttc_keys = list(_cli.keys())
    for k in ['keys', 'preferences', 'key_export_url', 'base_url',
              'client_info', 'behaviour', 'srv_discovery_url', 'instance_id',
              'client_registration', 'provider_info']:
        try:
            ttc_keys.remove(k)
        except ValueError:
            pass

    # print(ttc_keys)

    tool = {}
    for attr in ['ui_locales', 'acr_values', 'webfinger_url', 'login_hint',
                 'claims_locales', 'webfinger_email', 'ignore_check',
                 'contact_email', 'allow']:
        try:
            tool[attr] = _cli[attr]
        except KeyError:
            pass

    _prof = _cli['behaviour']['profile'].split('.')

    _profile = [_prof[0]]
    if 'webfinger_url' in tool or 'webfinger_email' in tool:
        _profile.append('T')
    else:
        _profile.append('F')

    _profile.extend(_prof[1:3])

    tool['profile'] = '.'.join(_profile)
    try:
        tool['tag'] = _cli['instance_id']
    except KeyError:
        tool['tag'] = 'default'
    while True:
        if _prof[-1] == '':
            _prof = _prof[:-1]
        else:
            break

    if len(_prof) > 3:
        for a, b in [('n', 'none'), ('s', 'sig'), ('e', 'enc')]:
            if a in _prof[3]:
                tool[b] = True
            else:
                tool[b] = False

    if _prof[-1] == '+':
        tool['extra'] = True
    else:
        tool['extra'] = False

    prov_info = {}
    cli_reg = {}

    if 'client_registration' in _cli:
        # profile[REGISTRATION] must be 'F'
        assert _profile[3] == 'F'
        for c in list(RegistrationResponse.c_param.keys()):
            try:
                cli_reg[c] = _cli['client_registration'][c]
            except KeyError:
                pass

    try:
        tool['issuer'] = _cli['srv_discovery_url']
    except KeyError:
        if 'provider_info' in _cli:
            # profile[REGISTRATION] must be 'F'
            assert _profile[2] == 'F'
            for c in list(ProviderConfigurationResponse.c_param.keys()):
                try:
                    prov_info[c] = _cli['provider_info'][c]
                except KeyError:
                    pass
        else:
            raise Exception('Missing provider_info')

    _keys = list(tool.keys())
    _keys.sort()

    # for key in _keys:
    #    print('{}: {}'.format(key, tool[key]))

    for k in ttc_keys:
        if k not in _keys:
            print('!! {}[{}]'.format(conf, k))

    res = {'tool': tool}
    if cli_reg:
        res["client"] = {"registration_response": cli_reg}
    if prov_info:
        try:
            res['client']['provider_info'] = prov_info
        except KeyError:
            res['client'] = {'provider_info': prov_info}

    return port, res


if __name__ == '__main__':
    sys.path.insert(0, '.')
    rest = REST('', '../entities')
    assigned_port = AssignedPorts('../aasigned_ports', 60000, 64000)
    for fil in sys.argv[1:]:
        if fil.endswith('.py'):
            print(fil)
            port, cnf = convert(fil[:-3])
            try:
                iss = cnf['tool']['issuer']
            except KeyError:
                iss = cnf['client']['provider_info']['issuer']
            qiss = quote_plus(iss.lower())

            if qiss.startswith('http'):
                qtag = quote_plus(cnf['tool']['tag'])
                fname = rest.entity_file_name(qiss, qtag)
                _key = '{}:{}'.format(qiss, qtag)
                if not os.path.isfile(fname):
                    rest.write(qiss, qtag, cnf)
                    try:
                        _p = assigned_port[_key]
                    except KeyError:
                        assigned_port[_key] = port
                    else:
                        _p = assigned_port.register_port(qiss, qtag)
                        print('{}/{} got other port {}->{}'.format(qiss, qtag,
                                                                   port, _p))
            else:
                print('skipped: {}'.format(fil))
