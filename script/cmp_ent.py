#!/usr/bin/env python3
import json

from oidctest.app_conf import REST

r = REST('',entpath='entities')
old = r.items()
f = open('entlist1.json', 'w')
f.write(json.dumps(old))
f.close()
new = REST('',entpath='entities.old').items()
f = open('entlist2.json', 'w')
f.write(json.dumps(new))
f.close()

dc = 0
for iss, tags in new.items():
    try:
        otags = old[iss]
    except KeyError:
        print('+ {}: {}'.format(iss, tags))
        dc += len(tags)
    else:
        st = set(tags)
        ot = set(otags)
        if st == ot:
            pass
        else:
            d = st.difference(ot)
            if d:
                dc += len(d)
                print('(+) {}: {}'.format(iss, d))
            d = ot.difference(st)
            if d:
                dc += len(d)
                print('(-) {}: {}'.format(iss, d))

for l in set(old.keys()).difference(set(new.keys())):
    dc += len(old[l])
    print("- {}".format(l))

print('Sum changes: {}'.format(dc))