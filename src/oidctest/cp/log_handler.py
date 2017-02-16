import gzip
import os
import shutil
import tarfile

import cherrypy
import time

PRE_HTML = """<html>
  <head>
    <title>List of OIDC RP tests</title>
    <link rel="stylesheet" type="text/css" href="${base}/static/theme.css">
  </head>
  <body>"""

POST = """</body></html>"""


def display_log(opid, logs):
    el = ["<ul>"]
    for name, path in logs:
        el.append('<li><a href="/log/{}/{}">{}</a>'.format(opid, path, name))
    el.append("</ul>")
    return "\n".join(el)


def display_testers(logs):
    el = ["<ul>"]
    for name, path in logs:
        el.append('<li><a href="/log/{}">{}</a>'.format(path, name))
    el.append("</ul>")
    return "\n".join(el)


def create_rp_tar_archive(bid, backup=False):
    # links all the logfiles in log/<tester_id>/<test_id> to
    # tar/<tester_id>/<test_id>
    # mk_tardir('backup', userid)

    wd = os.getcwd()
    if backup:
        _dir = os.path.join(wd, "backup", bid)
        tname = "{}.{}.tar".format(bid, time.time())
    else:
        _dir = os.path.join(wd, "tar")
        tname = "{}.tar".format(bid)

    if not os.path.isdir(_dir):
        os.makedirs(_dir)

    os.chdir(_dir)

    # if not os.path.isdir(userid):
    #     return None

    tar = tarfile.open(tname, "w")

    os.chdir(os.path.join(wd, 'log'))
    for item in os.listdir(bid):
        if item.startswith("."):
            continue

        fn = os.path.join(bid, item)

        if os.path.isfile(fn):
            tar.add(fn)
    tar.close()

    os.chdir(_dir)
    with open(tname, 'rb') as f_in:
        with gzip.open('{}.gz'.format(tname), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    _zipped = open('{}.gz'.format(tname), 'rb').read()
    os.chdir(wd)

    # content='application/x-gzip'
    return _zipped


class Log(object):
    def __init__(self, root):
        self.root = root

    @cherrypy.expose
    def index(self, op_id='', test_id=''):
        if op_id and test_id:
            path = os.path.join(self.root, op_id, test_id)
        elif op_id:
            path = os.path.join(self.root, op_id)
        else:
            path = self.root

        if os.path.isfile(path):
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            return open(path).read()
        elif os.path.isdir(path):
            item = []
            for (dirpath, dirnames, filenames) in os.walk(path):
                if dirnames:
                    item = [(fn, fn) for fn in dirnames]
                    break
                if filenames:
                    item = [(fn, fn) for fn in filenames]
                    break

            item.sort()

            response = [
                PRE_HTML,
                '<h1>OpenID Certification OP Test logs</h1>',
                '<h3>A list of test results that are saved on disc:</h3>',
                display_log(op_id, item)]

            if op_id:
                cl_url = "/clear/{}".format(op_id)
                tar_url = "/mktar/{}".format(op_id)
                tar_file = "{}.tar.gz".format(op_id[1:])
                response.append(
                    '<p><a href="{}"><b>Clear all test logs</b></a></p>'.format(
                        cl_url))
                response.append(
                    '<p><a href="{}" download="{}"><b>Download gzipped tar '
                    'file</b></a></p>'.format(tar_url, tar_file))

            return '\n'.join(response)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
            cherrypy.request.params['op_id'] = vpath.pop()
            return self

        if len(vpath) == 2:
            cherrypy.request.params['op_id'] = vpath.pop(0)  # Oper ID
            cherrypy.request.params['test_id'] = vpath.pop(0)  # Test ID
            return self


class OPLog(object):
    def __init__(self, root, pre_html):
        self.root = root
        self.pre_html = pre_html

    @cherrypy.expose
    def index(self, op_id='', tag='', profile='', test_id=''):
        if test_id:
            path = os.path.join(self.root, op_id, tag, profile, test_id)
        elif profile:
            path = os.path.join(self.root, op_id, tag, profile)
        elif tag:
            path = os.path.join(self.root, op_id, tag)
        elif op_id:
            path = os.path.join(self.root, op_id)
        else:
            path = self.root

        if os.path.isfile(path):
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            return open(path).read()
        elif os.path.isdir(path):
            item = []
            for (dirpath, dirnames, filenames) in os.walk(path):
                if dirnames:
                    item = [(fn, fn) for fn in dirnames]
                    break
                if filenames:
                    item = [(fn, fn) for fn in filenames]
                    break

            item.sort()

            _pre_html = self.pre_html['logs.html']
            if op_id:
                # cl_url = "/clear/{}".format(op_id)
                # _acts = [
                #     '<p><a href="{}"><b>Clear all test logs</b></a></p>'.format(
                #         cl_url)]
                _acts = []
                if tag and profile:
                    tar_url = "/mktar/{}/{}/{}".format(op_id, tag, profile)
                    tar_file = "{}.{}.{}.tar.gz".format(op_id, tag, profile)
                    _acts.append(
                        '<p><a href="{}" download="{}"><b>Download gzipped tar '
                        'file</b></a></p>'.format(tar_url, tar_file))

                response = _pre_html.format(
                    info = '<h3>A list of test results that are saved on disc:</h3>',
                    list=display_log(op_id, item),
                    actions='\n'.join(_acts)
                )
            else:
                response = _pre_html.format(
                    info='<h3>A list of all testers registred on this server:</h3>',
                    list=display_testers(item),
                    actions=''
                )

            return response

    def _cp_dispatch(self, vpath):
        if vpath:
            cherrypy.request.params['op_id'] = vpath.pop(0)
        if vpath:
            cherrypy.request.params['tag'] = vpath.pop(0)  # Test ID
        if vpath:
            cherrypy.request.params['profile'] = vpath.pop(0)  # Test ID
        if vpath:
            cherrypy.request.params['test_id'] = vpath.pop(0)  # Test ID
        return self


class ClearLog(object):
    def __init__(self, root):
        self.root = root

    @cherrypy.expose
    def index(self, op_id=''):
        create_rp_tar_archive(op_id, True)
        _dir = os.path.join(self.root, op_id)
        shutil.rmtree(_dir)
        raise cherrypy.HTTPRedirect("/log", 303)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
            cherrypy.request.params['op_id'] = vpath.pop()
            return self
        return vpath


class Tar(object):
    def __init__(self, root):
        self.root = root

    @cherrypy.expose
    def index(self, op_id=''):
        cherrypy.response.headers['Content-Type'] = 'application/x-gzip'
        return create_rp_tar_archive(op_id, True)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
            cherrypy.request.params['op_id'] = vpath.pop()
            return self
        return vpath


class OPTar(object):
    def __init__(self, log_root, tar_root, backup_root):
        self.log_root = log_root
        self.tar_root = tar_root
        self.backup_root = backup_root

    @cherrypy.expose
    def index(self, op_id, tag, profile):
        cherrypy.response.headers['Content-Type'] = 'application/x-gzip'
        return self.create_rp_tar_archive(op_id, tag, profile, False)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 3:  # Must be op_is, tag and profile
            cherrypy.request.params['op_id'] = vpath.pop(0)
            cherrypy.request.params['tag'] = vpath.pop(0)
            cherrypy.request.params['profile'] = vpath.pop(0)

            if cherrypy.request.script_name == '/backup':
                return self.backup

            return self

        return vpath

    def create_rp_tar_archive(self, op_id, tag, profile, backup=False):
        # links all the logfiles in log_root/<tester_id>/<test_id> to
        # tar_root/<tester_id>/<test_id>
        # mk_tardir('backup', userid)

        if backup:
            _target_dir = os.path.join(self.backup_root, op_id)
            tname = "{}.{}.{}.tar".format(tag, profile, time.time())
        else:
            _target_dir = os.path.join(self.tar_root, op_id)
            tname = "{}.{}.tar".format(tag, profile)

        if not os.path.isdir(_target_dir):
            os.makedirs(_target_dir)

        wd = os.getcwd()
        os.chdir(_target_dir)

        # Start creating the tar file
        tar = tarfile.open(tname, "w")
        _src_dir = os.path.join(wd, self.log_root, op_id, tag, profile)
        for item in os.listdir(_src_dir):
            if item.startswith("."):
                continue

            fn = os.path.join(_src_dir, item)

            if os.path.isfile(fn):
                tar.add(fn)
        tar.close()

        # Now for gzipping the tar file
        with open(tname, 'rb') as f_in:
            with gzip.open('{}.gz'.format(tname), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        if backup:  # Don't keep the tar file
            os.unlink(tname)

        _zipped = open('{}.gz'.format(tname), 'rb').read()
        os.chdir(wd)
        return _zipped

    @cherrypy.expose
    def backup(self, op_id, tag, profile):
        self.create_rp_tar_archive(op_id, tag, profile, True)
        return ''


class Root(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"


if __name__ == "__main__":

    log_root = "/Users/roland/test_site/oidf/oidc_cp_rplib/log"

    cherrypy.tree.mount(Root(), '/')
    cherrypy.tree.mount(Log(log_root), '/log')
    cherrypy.tree.mount(ClearLog(log_root), '/clear')
    cherrypy.tree.mount(Tar(log_root), '/mktar')
    cherrypy.engine.start()
    cherrypy.engine.block()