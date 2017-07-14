#!/usr/bin/env python3
import json
from urllib.parse import quote_plus

from oidctest.app_conf import REST
from oidctest.ass_port import AssignedPorts

old = REST('', entpath='entities')
old_info = old.items()
present = REST('', entpath='entities.present')
present_info = present.items()

assigned_port = AssignedPorts('./assigned_ports.json', 60001, 64000)
assigned_port.load()
pap = AssignedPorts('./assigned_ports.json.present', 60001, 64000)
pap.load()


def new_port(iss, tag, proposal=0):
    _k = pap.make_key(iss, tag)

    if proposal and proposal not in assigned_port.values():
        _p = proposal
    else:
        try:
            _p = pap[_k]
        except KeyError:
            _p = assigned_port.next_free_port()
            while _p in pap.values():
                _p = assigned_port.next_free_port(_p + 1)
        else:
            if _p in assigned_port.values():  # already there
                _p = assigned_port.next_free_port()
                while _p in pap.values():
                    _p = assigned_port.next_free_port(_p + 1)

    assigned_port[_k] = _p
    print(_k, _p)


def del_port(iss, tag):
    _k = pap.make_key(iss, tag)
    print(_k)
    try:
        del assigned_port[_k]
    except:
        pass


nport = []
rport = []

dc = 0
for iss, tags in present_info.items():
    if iss == 'https%3A%2F%2Fexample.com':
        continue

    try:
        otags = old_info[iss]
    except KeyError:
        for tag in tags:
            nport.append((iss, tag))
    else:
        st = set(tags)
        ot = set(otags)
        if st == ot:
            pass
        else:
            d = st.difference(ot)
            if d:
                for t in d:
                    nport.append((iss, t))
            d = ot.difference(st)
            if d:
                for t in d:
                    rport.append((iss, t))

for l in set(old_info.keys()).difference(set(present_info.keys())):
    for t in old_info[l]:
        rport.append((l, t))

print('-------')
for l in rport:
    del_port(*l)
print('+++++++')
for l in nport:
    # copy conf
    #qp = [quote_plus(x) for x in l]
    t, cnf = present.read_conf(*l)
    try:
        ruri = cnf['client']['registration_response']['redirect_uris']
    except:
        new_port(*l)
    else:
        if isinstance(ruri, list):
            ruri = ruri[0]
        else:
            cnf['client']['registration_response']['redirect_uris'] = [ruri]
        _p = ruri[:-9].split(':')[-1]
        new_port(l[0], l[1], _p)
    old.write(l[0], l[1], cnf)
