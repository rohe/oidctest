import logging
import os
import subprocess
import time
import shlex
from urllib.parse import unquote_plus

from oic.utils.http_util import ServiceError
from otest.proc import isrunning
from otest.rp.setup import read_path2port_map

logger = logging.getLogger(__name__)


class Application(object):
    def __init__(self, test_script, flowdir, rest, assigned_ports,
                 test_tool_base, test_tool_conf, prehtml, path2port=None):
        self.assigned_ports = assigned_ports
        self.running_processes = self.assigned_ports.sync(test_script)
        self.test_script = test_script
        self.flowdir = flowdir
        self.path2port = path2port
        self.test_tool_base = test_tool_base
        self.test_tool_conf = test_tool_conf
        self.rest = rest
        self.prehtml = prehtml

    def key(self, iss, tag):
        return self.assigned_ports.make_key(iss, tag)

    def run_test_instance(self, iss, tag):
        _port = self.assigned_ports.register_port(iss, tag)
        
        args = [self.test_script]
        args.extend(["-i", shlex.quote(unquote_plus(iss))])
        args.extend(["-t", shlex.quote(unquote_plus(tag))])        
        args.extend(["-p", str(_port)])
        args.extend(["-f", self.flowdir])
        args.append("-s")
        
        if self.path2port:
            args.extend(["-m", self.path2port])
            ppmap = read_path2port_map(self.path2port)
            try:
                _path = ppmap[str(_port)]
            except KeyError:
                _errtxt = 'Port not in path2port map file {}'.format(
                    self.path2port)
                logger.error(_errtxt)
                return ServiceError(_errtxt)
            url = '{}{}'.format(self.test_tool_base, _path)
        else:
            url = '{}:{}'.format(self.test_tool_base, _port)

        typ, _econf = self.rest.read_conf(iss, tag)
        try:
            _insecure = _econf['tool']['insecure']
        except KeyError:
            pass
        else:
            if _insecure:
                args.append('-k')

        args.append(self.test_tool_conf)

        # If already running - kill
        try:
            pid = isrunning(unquote_plus(iss), unquote_plus(tag))
        except KeyError:
            pass
        else:
            if pid:
                logger.info('kill {}'.format(pid))
                subprocess.call(['kill', str(pid)])

        # Now get it running
        args.append('&')
        cmd = " ".join(args)
        logger.info("Test tool command: {}".format(cmd))

        # spawn independent process, leaping blindly here
        os.system(cmd)

        pid = 0
        for i in range(0, 10):
            time.sleep(1)
            pid = isrunning(unquote_plus(iss), unquote_plus(tag))
            if pid:
                break

        if pid:
            logger.info("{} {} - process id: {}".format(iss, tag, pid))
            self.running_processes['{}:{}'.format(iss, tag)] = pid
            return url
        else:
            logger.error('Failed to start the test tool')
            return None
