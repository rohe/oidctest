#!/usr/bin/env python3

import json

ap = json.loads(open('assigned_ports.json').read())

inv = {}

for iss, port in ap.items():
    try:
        inv[port].append(iss)
    except KeyError:
        inv[port] = [iss]

for port, iss in inv.items():
    if len(iss) != 1:
        print(port, iss)