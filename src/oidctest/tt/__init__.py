import os

import cherrypy
import time

import logging
from jwkest import as_bytes
from otest.events import EV_FAULT
from otest.events import EV_RESPONSE


logger = logging.getLogger(__name__)


BUT = '<button name="action" type="submit" value="{}" class="choice">{}</button>'


def conv_response(events, resp):
    _stat = int(resp._status.split(' ')[0])
    #  if self.mako_lookup and self.mako_template:
    #    argv["message"] = message
    #    mte = self.mako_lookup.get_template(self.mako_template)
    #    return [mte.render(**argv)]
    if _stat < 300:
        events.store(EV_RESPONSE, resp.message)
        for key, val in resp.headers:
            cherrypy.response.headers[key] = val
        return as_bytes(resp.message)
    elif 300 <= _stat < 400:
        events.store('Redirect', resp.message)
        raise cherrypy.HTTPRedirect(resp.message)
    else:
        events.store(EV_FAULT, resp.message)
        raise cherrypy.HTTPError(_stat, resp.message)


class FileSystem(object):
    def __init__(self, fdir):
        self.fdir = fdir
        self.fmtime = {}
        self.db = {}

    def __getitem__(self, item):
        if self.is_changed(item):
            fname = os.path.join(self.fdir, item)
            self.db[item] = self._read_info(fname)

        return self.db[item]

    def keys(self):
        return self.db.keys()

    @staticmethod
    def get_mtime(fname):
        try:
            mtime = os.stat(fname).st_mtime
        except OSError:
            # The file might be right in the middle of being written
            # so sleep
            time.sleep(1)
            mtime = os.stat(fname).st_mtime

        return mtime

    def is_changed(self, item):
        fname = os.path.join(self.fdir, item)
        if os.path.isfile(fname):
            mtime = self.get_mtime(fname)

            try:
                _ftime = self.fmtime[item]
            except KeyError: # Never been seen before
                self.fmtime[item] = mtime
                return True

            if mtime > _ftime:  # has changed
                self.fmtime[item] = mtime
                return True
            else:
                return False
        else:
            raise KeyError(item)

    @staticmethod
    def _read_info(fname):
        if os.path.isfile(fname):
            try:
                return open(fname, 'r').read()
            except Exception as err:
                logger.error(err)
                raise

        return None

    def get_files_from_dir(self):
        if not os.path.isdir(self.fdir):
            raise ValueError('No such directory: {}'.format(self.fdir))
        for f in os.listdir(self.fdir):
            fname = os.path.join(self.fdir, f)
            if f in self.fmtime:
                if self.is_changed(fname):
                    self.db[f] = self._read_info(fname)
            else:
                mtime = self.get_mtime(fname)
                self.db[f] = self._read_info(fname)
                self.fmtime[f] = mtime
