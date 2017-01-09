#!/usr/bin/env python
import json
import os
import sys
import yaml
from otest.prof_util import RT

export_dir = 'flows'
if not os.path.isdir(export_dir):
    os.makedirs(export_dir)

stream = open(sys.argv[1], 'r')
yc = yaml.safe_load(stream)
stream.close()
for tid, spec in yc['Flows'].items():
    _prof = spec['profile']
    del spec['profile']
    if _prof == '*':
        spec['usage'] = {'return_types': list(RT.keys())}
    else:
        spec['usage'] = {'return_types': _prof.split(',')}
    fp = open(os.path.join(export_dir, tid)+'.json', 'w')
    json.dump(spec, fp)
    fp.close()
