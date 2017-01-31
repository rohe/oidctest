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


def create_rp_tar_archive(userid, backup=False):
    # links all the logfiles in log/<tester_id>/<test_id> to
    # tar/<tester_id>/<test_id>
    # mk_tardir('backup', userid)

    wd = os.getcwd()
    if backup:
        _dir = os.path.join(wd, "backup", userid)
        tname = "{}.{}.tar".format(userid, time.time())
    else:
        _dir = os.path.join(wd, "tar")
        tname = "{}.tar".format(userid)

    if not os.path.isdir(_dir):
        os.makedirs(_dir)

    os.chdir(_dir)

    # if not os.path.isdir(userid):
    #     return None

    tar = tarfile.open(tname, "w")

    os.chdir(os.path.join(wd, 'log'))
    for item in os.listdir(userid):
        if item.startswith("."):
            continue

        fn = os.path.join(userid, item)

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

        return vpath


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