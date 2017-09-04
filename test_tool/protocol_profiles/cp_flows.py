#!/usr/bin/env python3
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='fro')
parser.add_argument('-t', dest='to')
parser.add_argument('-o', dest='old')
parser.add_argument('-n', dest='new')
parser.add_argument('-m', dest='mods')
args = parser.parse_args()


def dict_mod(d0, d1):
    for key, vals in d1.items():
        if key not in d0:
            d0[key] = vals
        else:
            if isinstance(d0[key], dict) and isinstance(vals, dict):
                d0[key] = dict_mod(d0[key], vals)
            else:
                d0[key] = vals

    return d0


def apply_mods(inp, mods):

    _seq = inp['sequence'][:]

    for i in range(0,len(inp['sequence'])):
        inp_seq = inp['sequence'][i]
        try:
            mod_seq = mods['sequence'][i]
        except IndexError:
            break

        if isinstance(mod_seq, str):
            continue

        if isinstance(inp_seq, str):
            _seq[i] = mod_seq
        else:
            _seq[i] = dict_mod(inp_seq, mod_seq)

    inp['sequence'] = _seq
    return inp


if not os.path.isdir(args.fro):
    print('No directory to copy from')
    exit(1)

if not os.path.isdir(args.to):
    os.makedirs(args.to)

_mods = json.loads(open(args.mods).read())

n = 0
for f in os.listdir(args.fro):
    if f.endswith('.json'):  # Only copy json files
        fname = os.path.join(args.fro, f)
        data = open(fname).read()
        nf = f.replace(args.old, args.new, 1)
        try:
            mod_data = apply_mods(json.loads(data), _mods)
        except Exception as err:
            print(err)
            exit(1)
        else:
            fname = os.path.join(args.to, nf)
            fs = open(fname, 'w')
            fs.write(json.dumps(mod_data))
            fs.close()
            n += 1

print('{} files copied'.format(n))