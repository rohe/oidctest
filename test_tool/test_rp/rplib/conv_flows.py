#!/usr/bin/env python
import json
import os
import sys
import yaml

export_dir = 'flows'
if not os.path.isdir(export_dir):
    os.makedirs(export_dir)

stream = open(sys.argv[1], 'r')
yc = yaml.safe_load(stream)
stream.close()
for tid, spec in yc['Flows'].items():
    spec['usage'] = {'return_types': spec['profile'].split(',')}
    del spec['profile']
    fp = open(os.path.join(export_dir, tid)+'.json', 'w')
    json.dump(spec, fp)
    fp.close()
