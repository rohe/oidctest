#!/usr/bin/env python3
import argparse
import json
import os
from urllib.parse import quote_plus, unquote_plus

from oidctest.ass_port import AssignedPorts


def print_conf(c):
    iss, tag = c.split('][', 2)
    fname= os.path.join('entities', quote_plus(unquote_plus(iss)), quote_plus(unquote_plus(tag)))
    cnf = json.loads(open(fname,'r').read())
    print(">>>", fname)
    print(json.dumps(cnf, sort_keys=True, indent=2,
                     separators=(',', ': ')))


ap = AssignedPorts('assigned_ports.json',0,0)

#info = open('assigned_ports.json').read()
#ap = json.loads(info)

inv_ap = dict([(v, k) for k, v in ap.items()])

parser = argparse.ArgumentParser()
parser.add_argument('-d', dest='delete')
parser.add_argument('-p', dest='port', type=int)
parser.add_argument('-l', dest='list', action='store_true')
parser.add_argument('-m', dest='match')
parser.add_argument('-o', dest='open', action="store_true")
args = parser.parse_args()

if args.delete:
    del ap[args.delete]

if args.list:
    kl = list(inv_ap.keys())
    kl.sort()
    for k in kl:
        print(k, inv_ap[k])

if args.match:
    for k in ap.keys():
        if args.match in k:
            print(k, ap[k])
            if args.open:
                print_conf(k)

if args.port:
    print(inv_ap[args.port])
    if args.open:
        print_conf(inv_ap[args.port])

