import logging
import os
import time

logger = logging.getLogger(__name__)


class FileSystem(object):
    """
    FileSystem implements a simple file based database.
    It has a dictionary like interface.
    Each key maps one-to-one to a file on disc, where the content of the
    file is the value.
    """

    def __init__(self, fdir, key_conv=None, value_conv=None, c_size=0):
        """
        :param fdir: The root of the directory
        :param key_conv: Converts to/from the key displayed by this class to
        users of it to something that can be used as a file name.
        The value of key_conv is a dictionary with to keys ['to', 'from']
        where the value of 'to' is a function that can be used to convert
        the instance key value to the file name. The value of 'from' is a
        function that can be used to convert a file name to a key value.
        :type key_conv: Dictionary
        :param value_conv: As with key_conv you can convert/translate
        the value bound to a key in the database to something that can easily
        be stored in a file. Like with key_conv the value of this parameter
        is a dictionary with the keys ['to', 'from'].
        :type value_conv: dictionary
        """
        self.fdir = fdir
        self.fmtime = {}
        self.db = {}
        self.key_conv = key_conv or {}
        self.value_conv = value_conv or {}
        if not os.path.isdir(fdir):
            os.makedirs(fdir)

    def __getitem__(self, item):
        """
        Return the value bound to an identifier.

        :param item: The identifier.
        :return:
        """
        try:
            item = self.key_conv['to'](item)
        except KeyError:
            pass

        if self.is_changed(item):
            logger.info("File content change in {}".format(item))
            fname = os.path.join(self.fdir, item)
            self.db[item] = self._read_info(fname)

        return self.db[item]

    def __setitem__(self, key, value):
        """
        Binds a value to a specific key. If the file that the key maps to
        does not exist it will be created. The content of the file will be
        set to the value given.

        :param key: Identifier
        :param value: Value that should be bound to the identifier.
        :return:
        """

        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir, exist_ok=True)

        try:
            _key = self.key_conv['to'](key)
        except KeyError:
            _key = key

        fname = os.path.join(self.fdir, _key)
        fp = open(fname, 'w')
        try:
            fp.write(self.value_conv['to'](value))
        except KeyError:
            fp.write(value)
        fp.close()

        self.db[_key] = value
        self.fmtime[_key] = self.get_mtime(fname)

    def __delitem__(self, key):
        fname = os.path.join(self.fdir, key)
        if os.path.isfile(fname):
            os.unlink(fname)

        try:
            del self.db[key]
        except KeyError:
            pass

    def keys(self):
        """
        Implements the dict.keys() method
        """
        self.sync()
        for k in self.db.keys():
            try:
                yield self.key_conv['from'](k)
            except KeyError:
                yield k

    @staticmethod
    def get_mtime(fname):
        """
        Find the time this file was last modified.

        :param fname: File name
        :return: The last time the file was modified.
        """
        try:
            mtime = os.stat(fname).st_mtime_ns
        except OSError:
            # The file might be right in the middle of being written
            # so sleep
            time.sleep(1)
            mtime = os.stat(fname).st_mtime_ns

        return mtime

    def is_changed(self, item):
        """
        Find out if this item has been modified since last

        :param item: A key
        :return: True/False
        """
        fname = os.path.join(self.fdir, item)
        if os.path.isfile(fname):
            mtime = self.get_mtime(fname)

            try:
                _ftime = self.fmtime[item]
            except KeyError:  # Never been seen before
                self.fmtime[item] = mtime
                return True

            if mtime > _ftime:  # has changed
                self.fmtime[item] = mtime
                return True
            else:
                return False
        else:
            logger.error('Could not access {}'.format(fname))
            raise KeyError(item)

    def _read_info(self, fname):
        if os.path.isfile(fname):
            try:
                info = open(fname, 'r').read().strip()
                try:
                    info = self.value_conv['from'](info)
                except KeyError:
                    pass
                return info
            except Exception as err:
                logger.error(err)
                raise
        else:
            logger.error('No such file: {}'.format(fname))
        return None

    def sync(self):
        """
        Goes through the directory and builds a local cache based on
        the content of the directory.
        """
        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir)

        for f in os.listdir(self.fdir):
            fname = os.path.join(self.fdir, f)
            if not os.path.isfile(fname):
                continue
            if f in self.fmtime:
                if self.is_changed(f):
                    self.db[f] = self._read_info(fname)
            else:
                mtime = self.get_mtime(fname)
                self.db[f] = self._read_info(fname)
                self.fmtime[f] = mtime

    def items(self):
        """
        Implements the dict.items() method
        """
        self.sync()
        for k, v in self.db.items():
            try:
                yield self.key_conv['from'](k), v
            except KeyError:
                yield k, v

    def clear(self):
        """
        Completely resets the database. This means that all information in
        the local cache and on disc will be erased.
        """
        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir, exist_ok=True)
            return

        for f in os.listdir(self.fdir):
            del self[f]

    def update(self, ava):
        """
        Implements the dict.update() method
        """
        for key, val in ava.items():
            self[key] = val
