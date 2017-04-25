import os

depth = 9
rlist = list(range(depth))

ren = {}
for i in rlist:
    ren[i] = {}

for f in os.listdir('.'):
    if '.log.' in f:
        p = f.split('.')
        ip = int(p[-1])
        if 1 <= ip < depth:
            ren[ip][f] = '{}.log.{}'.format(p[0], ip+1)
    elif f.endswith('.log'):
        ren[0][f] = '{}.1'.format(f)

print(ren)

for i in reversed(rlist):
    for old, new in ren[i].items():
        os.rename(old, new)