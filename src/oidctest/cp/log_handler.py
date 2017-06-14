import gzip
import os
import shutil
import tarfile
import time

import cherrypy

PRE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenID Connect Provider Certification</title>
<link href="/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
<link href="/static/theme.css" rel="stylesheet">
<!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
</head>
<body>

    <div class="container" role="main">

        <div class="page-header">
            <div class="pull-left">
                <h2>OpenID Connect Relying Party Certification</h2>
            </div>
            <div class="pull-right">
                <a href="https://openid.net/certification"><img
                    class="img-responsive" src="/static/logo.png" /></a>
            </div>
            <div class="clearfix"></div>
        </div>

        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">Relying Party Certification Test Logs</h3>
            </div>
            <div class="panel-body">
"""

POST_HTML = """
            </div>
        </div>

        <div class="footer text-muted">
            <hr />
            <div class="pull-left">
                <ul class="list-inline">
                    <li>(C) 2017 - <a href="https://openid.net/foundation">OpenID
                            Foundation</a></li>
                    <li>E-mail: <a href="mailto:certification@openid.net">certification@openid.net</a></li>
                    <li>Issues: <a
                        href="https://github.com/openid-certification/oidctest/issues">Github</a>
                    <li>
                </ul>
            </div>
            <div class="pull-right">
                <ul class="list-inline">
                    <li>Version: {version}</li>
                </ul>
            </div>
        </div>

    </div>

    <script
        src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
</body>
</html>
"""


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


def create_rp_tar_archive(wd, bid, backup=False):
    """
    links all the logfiles in log/<tester_id>/<test_id> to
    tar/<tester_id>.<test_id> or backup/...

    :param wd: Base directory
    :param bid: tester id
    :param backup: Is this aa backup or not ?
    :return:
    """

    if backup:
        _dir = os.path.join(wd, "backup", bid)
        tname = "{}.{}.tar".format(bid, time.time())
    else:
        _dir = os.path.join(wd, "tar")
        tname = "{}.tar".format(bid)

    if not os.path.isdir(_dir):
        os.makedirs(_dir)

    _log = os.path.join(wd, 'log')
    if not os.path.isdir(_log):
        raise cherrypy.HTTPError(400, b'No such directory')

    # Must open the tar file in the tar/backup directory
    os.chdir(_dir)
    tar = tarfile.open(tname, "w")

    # back to the log directory
    os.chdir(os.path.join(wd, 'log'))
    for item in os.listdir(bid):
        if item.startswith("."):
            continue

        fn = os.path.join(bid, item)
        if os.path.isfile(fn):
            tar.add(fn)

    tar.close()

    # Back to the tar/backup directory
    os.chdir(_dir)
    with open(tname, 'rb') as f_in:
        with gzip.open('{}.gz'.format(tname), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    _zipped = open('{}.gz'.format(tname), 'rb').read()
    os.chdir(wd)

    # content='application/x-gzip'
    return _zipped


class Log(object):
    def __init__(self, root, version=''):
        self.root = root
        self.version = version

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
                '<p>A list of test results that are saved on disc:</p>',
                display_log(op_id, item)]

            response.append('<hr />')

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

            response.append(POST_HTML.format(version=self.version))

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
    def __init__(self, root, pre_html, version):
        self.root = root
        self.pre_html = pre_html
        self.version = version

    @cherrypy.expose
    def index(self, op_id='', tag='', profile='', test_id=''):
        prefix = ''
        if test_id:
            path = os.path.join(self.root, op_id, tag, profile, test_id)
        elif profile:
            path = os.path.join(self.root, op_id, tag, profile)
            prefix = '{}/{}/'.format(tag, profile)
        elif tag:
            path = os.path.join(self.root, op_id, tag)
            prefix = '{}/'.format(tag)
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
                    item = [(fn, '{}{}'.format(prefix,fn)) for fn in dirnames]
                    break
                if filenames:
                    item = [(fn, '{}{}'.format(prefix,fn)) for fn in filenames]
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
                    info = 'A list of test results that are saved on disc:',
                    list=display_log(op_id, item),
                    actions='\n'.join(_acts),
                    version=self.version
                )
            else:
                response = _pre_html.format(
                    info='A list of all testers registered on this server:',
                    list=display_testers(item),
                    actions='',
                    version=self.version
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
        self.root = root  # The directory where the log directory resides

    @cherrypy.expose
    def index(self, op_id=''):
        create_rp_tar_archive(self.root, op_id, True)
        _dir = os.path.join(self.root, 'log', op_id)
        shutil.rmtree(_dir)
        raise cherrypy.HTTPRedirect("/log", 303)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
            cherrypy.request.params['op_id'] = vpath.pop()
            return self
        return vpath


class Tar(object):
    def __init__(self, root):
        self.root = root  # The directory where the tar directory resides

    @cherrypy.expose
    def index(self, op_id=''):
        cherrypy.response.headers['Content-Type'] = 'application/x-gzip'
        return create_rp_tar_archive(self.root, op_id, False)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
            cherrypy.request.params['op_id'] = vpath.pop()
            return self
        return vpath


class OPTar(object):
    def __init__(self, root):
        self.root = root

    @cherrypy.expose
    def index(self, op_id, tag, profile):
        cherrypy.response.headers['Content-Type'] = 'application/x-gzip'
        return self.create_rp_tar_archive(op_id, tag, profile)

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
            _target_dir = os.path.join(self.root, 'backup', op_id)
            tname = "{}.{}.{}.tar".format(tag, profile, time.time())
        else:
            _target_dir = os.path.join(self.root, 'tar',op_id)
            tname = "{}.{}.tar".format(tag, profile)

        if not os.path.isdir(_target_dir):
            os.makedirs(_target_dir)

        os.chdir(_target_dir)
        # Start creating the tar file
        tar = tarfile.open(tname, "w")

        _src_dir = os.path.join(self.root, 'log', op_id, tag, profile)
        if not os.path.isdir(_src_dir):
            raise cherrypy.HTTPError(400, b'No such directory')

        for item in os.listdir(_src_dir):
            if item.startswith("."):
                continue

            fn = os.path.join(_src_dir, item)

            if os.path.isfile(fn):
                tar.add(fn)
        tar.close()

        os.chdir(_target_dir)
        # Now for gzipping the tar file
        with open(tname, 'rb') as f_in:
            with gzip.open('{}.gz'.format(tname), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        if backup:  # Don't keep the tar file
            os.unlink(tname)

        _zipped = open('{}.gz'.format(tname), 'rb').read()
        os.chdir(self.root)

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
