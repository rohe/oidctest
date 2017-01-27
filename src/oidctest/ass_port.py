import json

from future.backports.urllib.parse import unquote_plus

from otest.proc import find_test_instances


class OutOfRange(Exception):
    pass


class AssignedPorts(object):
    def __init__(self, filename, min, max):
        self.filename = filename
        self.min = min
        self.max = max
        self._db = {}

    def __setitem__(self, key, value):
        if '%' in key:
            key = unquote_plus(key)

        self._db[key] = value
        self.dump()

    def __getitem__(self, item):
        if "%" in item:
            item = unquote_plus(item)

        return self._db[item]

    def __delitem__(self, key):
        if '%' in key:
            key = unquote_plus(key)

        del self._db[key]
        self.dump()

    def keys(self):
        return self._db.keys()

    def values(self):
        return self._db.values()

    def __contains__(self, item):
        if "%" in item:
            item = unquote_plus(item)
        return item in self._db

    def dump(self):
        fp = open(self.filename, 'w')
        fp.write(json.dumps(self._db))
        fp.close()

    def sync(self, test_script):
        running_processes = {}

        update = False
        inst = find_test_instances(test_script)
        if inst:
            for pid, info in inst.items():
                key = '{}:{}'.format(info["iss"], info["tag"])
                if key not in self._db:
                    self[key] = info["port"]
                    update = True
                running_processes[key] = pid

        if update:
            self.dump()

        return running_processes

    def load(self):
        try:
            _ass = open(self.filename, 'r').read()
        except FileNotFoundError:
            pass
        else:
            if _ass:
                for key, val in json.loads(_ass).items():
                    self._db[key] = val

    def register_port(self, eid):
        """
        Get an assigned port. If no one is assigned, find the next available.
        :param key: entity identifier
        :return: Integer
        """
        try:
            # already registered ?
            _port = self._db[eid]
        except KeyError:
            if self._db == {}:
                _port = self.min
                self._db[eid] = _port
            else:
                pl = list(self._db.values())
                pl.sort()
                if not pl:
                    _port = self.min
                    self._db[eid] = _port
                elif pl[0] != self.min:
                    _port = self.min
                    self._db[eid] = _port
                else:
                    _port = self.min
                    for p in pl:
                        if p == _port:
                            _port += 1
                            continue
                        else:
                            break
                    if _port > self.max:
                        raise OutOfRange('Out of ports')
                    self._db[eid] = _port
            self.dump()
        return _port
