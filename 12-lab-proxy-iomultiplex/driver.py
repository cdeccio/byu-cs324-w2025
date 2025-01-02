#!/usr/bin/python3
#

import argparse
import logging
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse

class PortWaitTimeout(Exception):
    pass

class MissingFile(Exception):
    pass

class MissingDirectory(Exception):
    pass

class FailedCommand(Exception):
    pass

CURRENT_DIR = '.'
SLOW_CLIENT = os.path.join(CURRENT_DIR, 'slow-client.py')
NOP_SERVER = os.path.join(CURRENT_DIR, 'nop-server.py')
PROXY = os.path.join(CURRENT_DIR, 'proxy')
WWW_DIR = os.path.join(CURRENT_DIR, 'www')
VALGRIND = 'valgrind'
VALGRIND_MEMCHECK_PATTERN = 'memcheck'

class ProxyTestSuite:
    def __init__(self, mode, test_classes, proxy_host='localhost',
            server_host='localhost',
            mem_mgmt=None, clean_shutdown=None, keep_files=False,
            server_output=False, proxy_output=False,
            verbose=False):
        self.mode = mode
        self.test_classes = test_classes
        self.proxy_host = proxy_host
        self.server_host = server_host
        self.mem_mgmt = mem_mgmt
        self.clean_shutdown = clean_shutdown
        self.keep_files = keep_files
        self.server_output = server_output
        self.proxy_output = proxy_output
        self.verbose = verbose
        self.use_valgrind = self.mem_mgmt is not None or self.clean_shutdown is not None

    def run(self):
        pts = 0
        possible_pts = 0
        mem_mgmt = 0
        possible_mem_mgmt = 0
        clean_shutdown = 0
        possible_clean_shutdown = 0
        for num, (classes, pts_for_group) in enumerate(self.test_classes):
            attempts = 0
            successes = 0
            possible_pts += pts_for_group
            num += 1
            print('TEST GROUP %d (%d points) ***' % (num, pts_for_group))
            for cls in classes:
                p = cls(proxy_host=self.proxy_host,
                        server_host=self.server_host,
                        use_valgrind=self.use_valgrind,
                        keep_files=self.keep_files,
                        server_output=self.server_output,
                        proxy_output=self.proxy_output,
                        verbose=self.verbose)
                print('    %s' % (p.DESCRIPTION))
                print('      %s' % (p.EXTENDED_DESCRIPTION))

                p.run()
                p.cleanup()
                attempts += p.attempts
                successes += p.successes
                possible_mem_mgmt += 1
                possible_clean_shutdown += 1

                mem_msg = ''
                if self.mem_mgmt is not None:
                    mem_msg += '; Mem Mgmt: '
                    if p.mem_mgmt:
                        mem_msg += 'success'
                        mem_mgmt += 1
                    else:
                        mem_msg += 'failure'
                if self.clean_shutdown is not None:
                    mem_msg += '; Clean Shutdown: '
                    if p.clean_shutdown:
                        mem_msg += 'success'
                        clean_shutdown += 1
                    else:
                        mem_msg += 'failure'

                mode_status = p.check_mode(self.mode)
                if mode_status is not None:
                    mem_msg += '; Concurrency model: '
                    if mode_status:
                        mem_msg += 'success'
                    else:
                        mem_msg += 'failure'

                print('      Result: %d/%d%s' % (p.successes, p.attempts, mem_msg))
            tot_pts = pts_for_group * (successes/attempts)
            pts += tot_pts
            print('    Subtotal: %d/%d' % (tot_pts, pts_for_group))

        if self.mem_mgmt is not None:
            possible_pts += self.mem_mgmt
            mem_mgmt = self.mem_mgmt * (mem_mgmt/possible_mem_mgmt)
            pts += mem_mgmt
            print('Mem Mgmt: %d/%d' % (mem_mgmt, self.mem_mgmt))
            
        if self.clean_shutdown is not None:
            possible_pts += self.clean_shutdown
            clean_shutdown = self.clean_shutdown * (clean_shutdown/possible_clean_shutdown)
            pts += clean_shutdown
            print('Clean Shutdown: %d/%d' % (clean_shutdown, self.mem_mgmt))

        if possible_pts > 0:
            percent = 100*pts/possible_pts
        else:
            percent = 0.0

        print('Total: %d/%d (%.02f%%)' % (pts, possible_pts, percent))

class ProxyTest:
    EXECUTABLES = \
            [SLOW_CLIENT, NOP_SERVER, PROXY]
    DESCRIPTION = 'Proxy Test'
    FILES = []

    def __init__(self, proxy_host='localhost', proxy_port=None,
            server_host='localhost', server_port=None,
            use_valgrind=True, keep_files=False,
            server_output=False, proxy_output=False,
            verbose=False):

        self.logger = logging.getLogger('.')

        self.server_host = server_host
        if server_port is None:
            server_port = self.find_free_port()
        self.server_port = server_port
        self.server_proc = None

        self.proxy_host = proxy_host
        if proxy_port is None:
            proxy_port = self.find_free_port()
        self.proxy_port = proxy_port
        self.proxy_proc = None
        self.proxy_url = 'http://%s:%d' % (self.proxy_host, proxy_port)

        self.nop_server_host = 'localhost'
        self.nop_server_port = self.find_free_port()
        self.nop_server_proc = None

        self.proxy_dir = tempfile.mkdtemp(prefix='proxy_', dir='.')
        self.logger.info('Created temporary directory for files downloaded from the proxy: %s.', self.proxy_dir)
        self.noproxy_dir = tempfile.mkdtemp(prefix='noproxy_', dir='.')
        self.logger.info('Created temporary directory for files downloaded directly from the server: %s.', self.noproxy_dir)
        fd, self.valgrind_log_file = tempfile.mkstemp(prefix='log_', dir='.')
        self.logger.info('Created temporary file for valgrind output: %s.', self.valgrind_log_file)
        os.close(fd)

        self.use_valgrind = use_valgrind
        self.keep_files = keep_files
        self.server_output = server_output
        self.proxy_output = proxy_output
        self.verbose = verbose

        # these are set by run()
        self.num_processes_pre = None
        self.num_processes_realtime = None
        self.num_threads_pre = None
        self.num_threads_realtime = None

        # these are set by run()
        self.attempts = None
        self.successes = None

        # these are set by cleanup()
        self.mem_mgmt = None
        self.mem_cleanup = None

        self.cleanup_processes_non_targetted()
        self._check_files()

        self.start_server()
        self.start_proxy()

        # Wait for threads to be initialized
        time.sleep(2)

        self.num_threads_pre = self.get_num_threads(self.proxy_proc.pid)
        self.num_processes_pre = self.get_num_processes(self.proxy_proc.pid)

    def __del__(self):
        self.cleanup_processes()
        if not self.keep_files:
            self.cleanup_files()

    @classmethod
    def get_num_processes(cls, pid):
        cmd = ['ps', '--no-headers', '-o', 'pid', '--pid', str(pid), '--ppid', str(pid)]
        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            return 0
        else:
            pids = set([int(p) for p in output.splitlines()])
            return len(pids)

    @classmethod
    def get_num_threads(cls, pid):
        cmd = ['ps', '--no-headers', '-L', '-o', 'lwp', '--pid', str(pid)]
        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            return 0
        else:
            lwpids = set([int(p) for p in output.splitlines()])
            return len(lwpids)

    @classmethod
    def port_in_use(cls, port):
        cmd = ['ss', '-n', '-l', '-t', '-p']
        output = subprocess.check_output(cmd)
        for row in output.splitlines()[1:]:
            row = row.decode('utf-8')
            cols = row.split()
            addr, nport = cols[3].rsplit(':', 1)
            nport = int(nport)
            if nport == port:
                return addr
        return None

    @classmethod
    def wait_for_port_use(cls, port, timeout):
        count = 0
        while cls.port_in_use(port) is None:
            time.sleep(1)
            count += 1
            if count > timeout:
                raise PortWaitTimeout

    @classmethod
    def find_free_port(cls):
        port = random.randint(1024, 65000)
        while port <= 65536:
            if not cls.port_in_use(port):
                return port
            port += 1
        return None

    def check_mode(self, mode):
        if self.num_processes_realtime is None or \
                self.num_processes_pre is None or \
                self.num_threads_realtime is None or \
                self.num_threads_pre is None:
            return None

        status = True
        if self.num_processes_realtime > self.num_processes_pre:
            if mode == 'multiprocess':
                level = logging.INFO
            else:
                level = logging.ERROR
                status = False
            self.logger.log(level, 'Processes are being forked on the fly: (%d > %d)' % (self.num_processes_realtime, self.num_processes_pre))
        if self.num_processes_pre > 1:
            if mode == 'processpool':
                level = logging.INFO
            else:
                level = logging.ERROR
                status = False
            self.logger.log(level, 'A pool of %d processes was created a program start.' % (self.num_threads_pre - 1))
        if self.num_threads_realtime > self.num_threads_pre:
            if mode == 'multithread':
                level = logging.INFO
            else:
                level = logging.ERROR
                status = False
            self.logger.log(level, 'Threads are being spawned on the fly: (%d > %d)' % (self.num_threads_realtime, self.num_threads_pre))
        if self.num_threads_pre > 2:
            if mode == 'threadpool':
                level = logging.INFO
            else:
                level = logging.ERROR
                status = False
            self.logger.log(level, 'A pool of %d threads was created a program start.' % (self.num_threads_pre - 2))
        return status

    def cleanup_processes_non_targetted(self):
        cmd = ['killall', '-INT'] + self.EXECUTABLES
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            pass

        cmd = ['pkill', '-INT', VALGRIND_MEMCHECK_PATTERN]
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            pass

    def _cleanup_processes(self, kill_proxy, kill_server, kill_nop):
        for sig in ('INT', 'TERM'):
            pids = []
            if kill_proxy and self.proxy_proc is not None and self.proxy_proc.poll() is None:
                pids.append(self.proxy_proc.pid)
            if kill_server and self.server_proc is not None and self.server_proc.poll() is None:
                pids.append(self.server_proc.pid)
            if kill_nop and self.nop_server_proc is not None and self.nop_server_proc.poll() is None:
                pids.append(self.nop_server_proc.pid)

            if not pids:
                break

            cmd = ['kill', '-%s' % (sig)] + [str(p) for p in pids]
            self.logger.debug(' '.join(cmd))
            try:
                subprocess.call(['kill', '-%s' % (sig)] + [str(p) for p in pids],
                     stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                pass

            time.sleep(1)

    def cleanup_processes(self):
        self.logger.info('Cleaning up all processes.')
        self._cleanup_processes(kill_server=True, kill_proxy=True, kill_nop=True)

    def kill_server(self):
        self.logger.info('Killing the server process.')
        self._cleanup_processes(kill_server=True, kill_proxy=False, kill_nop=False)

    def cleanup_files(self):
        self.logger.info('Removing temporary files: %s, %s, and %s' % (self.proxy_dir, self.noproxy_dir, self.valgrind_log_file))
        subprocess.call(['rm', '-r', '-f', self.proxy_dir, self.noproxy_dir,
            self.valgrind_log_file], stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def cleanup(self):
        self.cleanup_processes()
        if self.use_valgrind:
            self.check_valgrind()
        if self.keep_files:
            msg = 'Proxy Directory: %s\nNo Proxy Directory: %s' % \
                    (self.proxy_dir, self.noproxy_dir)
            if self.valgrind_log_file is not None:
                msg += '\nValgrind log file: %s' % (self.valgrind_log_file)
            self.logger.info(msg)
        else:
            self.cleanup_files()

    def _check_files(self):
        for f in self.FILES:
            if f.startswith('http://'):
                continue
            qs_index = f.find('?')
            if qs_index > -1:
                f = f[:qs_index]
            f = os.path.join(WWW_DIR, f)
            if not os.path.exists(f):
                raise MissingFile('File "%s" not found' % f)

        for f in self.EXECUTABLES:
            if not os.path.exists(f):
                raise MissingFile('File "%s" not found' % f)

        # Check for valgrind
        if subprocess.call([VALGRIND, '-h'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) != 0:
            raise FailedCommand('Unable to run valgrind.  Is it installed and in PATH?')

    def check_valgrind(self):
        with open(self.valgrind_log_file, 'r') as fh:
            valgrind_output = fh.read()

        status = {}
        for line in valgrind_output.splitlines():
            if re.search(r'definitely lost:', line):
                rows = line.split()
                status['definitely_lost'] = int(rows[3].replace(',', ''))
            elif re.search(r'indirectly lost:', line):
                rows = line.split()
                status['indirectly_lost'] = int(rows[3].replace(',', ''))
            elif re.search(r'possibly lost:', line):
                rows = line.split()
                status['possibly_lost'] = int(rows[3].replace(',', ''))
            elif re.search(r'still_reachable:', line):
                rows = line.split()
                status['still_reachable'] = int(rows[3].replace(',', ''))

        if status.get('definitely_lost', 0) > 0 or \
                status.get('indirectly_lost', 0) > 0:
            self.mem_mgmt = False
        else:
            self.mem_mgmt = True
        if status.get('still_reachable', 0) > 0:
            self.mem_cleanup = False
        else:
            self.mem_cleanup = True

        if not self.mem_mgmt:
            self.logger.warning('Memory directly or indirectly lost!')
        if not self.mem_cleanup:
            self.logger.warning('Memory still reachable at process end; shutdown not clean!')
        if not self.mem_mgmt or not self.mem_cleanup:
            self.logger.debug(valgrind_output)

    def start_server(self):
        self.logger.info('Starting server on port %d' % self.server_port)
        cmd = ['python3', '-m', 'http.server', '--cgi', str(self.server_port)]
        kwargs = {}
        if self.server_output:
            kwargs.update(stdout=self.server_output, stderr=subprocess.STDOUT)
        else:
            kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.logger.debug(' '.join(cmd))
        self.server_proc = subprocess.Popen(cmd, cwd=WWW_DIR, **kwargs)
        self.wait_for_port_use(self.server_port, 5)

    def start_proxy(self):
        self.logger.info('Starting proxy on port %d' % self.proxy_port)
        cmd = [PROXY, str(self.proxy_port)]
        if self.use_valgrind:
            cmd = ['valgrind', '--log-file=%s' % (self.valgrind_log_file), '--leak-check=full', '-v'] + cmd
        kwargs = {}
        if self.proxy_output:
            kwargs.update(stdout=self.proxy_output, stderr=subprocess.STDOUT)
        else:
            kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.logger.debug(' '.join(cmd))
        self.proxy_proc = subprocess.Popen(cmd, **kwargs)
        self.wait_for_port_use(self.proxy_port, 5)

    def start_nop_server(self):
        self.logger.info('Starting nop-server on port %d' % self.nop_server_port)
        cmd = [NOP_SERVER, str(self.nop_server_port)]
        kwargs = {}
        if not self.verbose:
            kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.logger.debug(' '.join(cmd))
        self.nop_server_proc = subprocess.Popen(cmd, **kwargs)
        self.wait_for_port_use(self.nop_server_port, 5)

    def _filesystem_safe(self, s):
        return ''.join([c for c in s if c.isalpha() or c.isdigit() or c == '-']).rstrip()

    def _download_proxy(self, url, output, timeout):
        self.logger.info('Fetching %s into %s - through proxy' % (url, output))
        # create an empty file
        open(output, 'w').close()
        cmd = ['curl', '--max-time', str(timeout), '--silent', '--proxy',
                self.proxy_url, '--output', output, url]
        self.logger.debug(' '.join(cmd))
        return subprocess.Popen(cmd)

    def _download_proxy_slow(self, url, output, timeout, sleep_between_send=1):
        self.logger.info('Fetching %s into %s - through proxy' % (url, output))
        # create an empty file
        open(output, 'w').close()
        cmd = [SLOW_CLIENT, '--max-time', str(timeout), '--sleep-between-send',
                str(sleep_between_send), '--proxy', self.proxy_url, '--output',
                output, url]
        self.logger.debug(' '.join(cmd))
        return subprocess.Popen(cmd)

    def download_proxy(self, url, output, timeout):
        raise NotImplemented

    def download_noproxy(self, url, output, timeout):
        self.logger.info('Fetching %s into %s - direct from server' % (url, output))
        # create an empty file
        open(output, 'w').close()
        cmd = ['curl', '--max-time', str(timeout), '--silent', '--output',
                output, url]
        self.logger.debug(' '.join(cmd))
        return subprocess.Popen(cmd)

    def _are_same(self, file1, file2):
        self.logger.info('Comparing %s and %s' % (file1, file2))
        try:
            subprocess.check_call(['diff', '-q', file1, file2])
        except subprocess.CalledProcessError as e:
            self.logger.error('Files %s and %s differ' % (file1, file2))
            try:
                output = subprocess.check_output(['diff', '-u', file1, file2])
            except subprocess.CalledProcessError as e:
                self.logger.debug(e.output.decode('utf-8'))
            return False
        else:
            self.logger.info('Files %s and %s are the same' % (file1, file2))
            return True

    def _is_newer_than(self, file1, file2):
        self.logger.info('Comparing timestamps of %s and %s' % (file1, file2))
        try:
            if os.path.getmtime(file1) > os.path.getmtime(file2):
                self.logger.info('%s was received before %s' % (file2, file1))
                return True
            else:
                self.logger.error('%s should have been received before %s' % (file2, file1))
                return False
        except OSError as e:
            self.logger.error(str(e))
            return False

    def run(self):
        raise NotImplemented


class BasicProxyTest(ProxyTest):
    FILES = ['foo.html', 'bar.txt', 'socket.jpg']
    DESCRIPTION = 'Basic Proxy Test'
    EXTENDED_DESCRIPTION = \
            'Requesting files of several types through proxy.' 

    download_proxy = ProxyTest._download_proxy

    def run(self):
        # Now do the test by fetching some text and binary files directly from
        # Tiny and via the proxy, and then comparing the results.
        tried = []
        for (i, filename) in enumerate(self.FILES):
            if filename.startswith('http://'):
                url = filename
                (scheme, netloc, path, params, query, fragment) = \
                        urllib.parse.urlparse(url)
                if query:
                    filename = '%s?%s' % (path, query)
                else:
                    filename = path
            else:
                url = 'http://%s:%d/%s' % \
                        (self.server_host, self.server_port, filename)
            dst_path_proxy = os.path.join(self.proxy_dir,
                    '%s-%d' % (self._filesystem_safe(filename), i))
            dst_path_noproxy = os.path.join(self.noproxy_dir,
                    '%s-%d' % (self._filesystem_safe(filename), i))

            proxy_proc = self.download_proxy(url, dst_path_proxy, 10)
            proxy_proc.wait()

            noproxy_proc = self.download_noproxy(url, dst_path_noproxy, 10)
            noproxy_proc.wait()

            tried.append((dst_path_proxy, dst_path_noproxy))

        successes = 0
        for (dst_path_proxy, dst_path_noproxy) in tried:
            if self._are_same(dst_path_noproxy, dst_path_proxy):
                successes += 1
        status = {}

        self.attempts = len(tried)
        self.successes = successes

class NonlocalProxyTest(BasicProxyTest):
    FILES = ['http://www-notls.imaal.byu.edu/index.html',
            'http://www-notls.imaal.byu.edu/images/imaal-80x80.png']
    DESCRIPTION = 'Non-local Proxy Test'
    EXTENDED_DESCRIPTION = \
            'Issuing a request to the proxy ' + \
            'for a non-local URL.'

class SlowRequestProxyTest(BasicProxyTest):
    FILES = ['foo.html']
    DESCRIPTION = 'Slow Request Test'
    EXTENDED_DESCRIPTION = \
            'Issuing a request to the proxy, iteratively, using several ' + \
            'calls to send().'

    download_proxy = ProxyTest._download_proxy_slow

class SlowResponseProxyTest(BasicProxyTest):
    FILES = ['cgi-bin/slow?sleep=1&size=4096']
    DESCRIPTION = 'Slow Response Test'
    EXTENDED_DESCRIPTION = \
            'Issuing a request to the proxy for a file that the server ' + \
            'sends iteratively, over several calls to send().'

class SlowRequestResponseProxyTest(BasicProxyTest):
    FILES = ['cgi-bin/slow?sleep=1&size=4096']
    DESCRIPTION = 'Slow Request/Response Test'
    EXTENDED_DESCRIPTION = \
            'Issuing a request to the proxy, iteratively, for a file that ' + \
            'the server also sends iteratively.'

    download_proxy = ProxyTest._download_proxy_slow

class DumbConcurrencyProxyTest(BasicProxyTest):
    FILES = ['foo.html']
    DESCRIPTION = 'Dumb Concurrency Test'
    EXTENDED_DESCRIPTION = \
            'Issuing a request to the proxy, while it is busy with ' + \
            'another request.' 

    def __init__(self, *args, **kwargs):
        super(BasicConcurrencyProxyTest, self).__init__(*args, **kwargs)
        self.start_nop_server()

    def run(self):
        url = 'http://%s:%d/' % (self.nop_server_host, self.nop_server_port)
        dst_path_proxy = os.path.join(self.proxy_dir, 'nop-server-request')
        nop_proc = self.download_proxy(url, dst_path_proxy, 10)

        return super(BasicConcurrencyProxyTest, self).run()

class CacheTest(ProxyTest):
    FILES = ['foo.html', 'bar.txt']
    DESCRIPTION = 'Cache Test'
    EXTENDED_DESCRIPTION = \
            'Requesting a file through the proxy after it has already ' + \
            'been requested.'

    download_proxy = ProxyTest._download_proxy

    def run(self):
        # Now do the test by fetching some text and binary files directly from
        # Tiny and via the proxy, and then comparing the results.
        tried = []
        for (i, filename) in enumerate(self.FILES):
            dst_path_proxy = os.path.join(self.proxy_dir,
                    '%s-%d' % (self._filesystem_safe(filename), i))
            dst_path_noproxy = os.path.join(self.noproxy_dir,
                    '%s-%d' % (self._filesystem_safe(filename), i))
            url = 'http://%s:%d/%s' % \
                    (self.server_host, self.server_port, filename)

            proxy_proc = self.download_proxy(url, dst_path_proxy, 10)
            proxy_proc.wait()

            noproxy_proc = self.download_noproxy(url, dst_path_noproxy, 10)
            noproxy_proc.wait()

        self.kill_server()

        for (i, filename) in enumerate(self.FILES):
            dst_path_proxy = os.path.join(self.proxy_dir,
                    '%s-%d' % (self._filesystem_safe(filename), i))
            dst_path_noproxy = os.path.join(self.noproxy_dir,
                    '%s-%d' % (self._filesystem_safe(filename), i))

            try:
                os.unlink(dst_path_proxy)
            except OSError as e:
                self.logger.warning('Error removing downloaded file "%s": %s' % \
                        (dst_path_proxy, str(e)))

            url = 'http://%s:%d/%s' % (self.server_host, self.server_port, filename)

            proxy_proc = self.download_proxy(url, dst_path_proxy, 10)
            proxy_proc.wait()

            tried.append((dst_path_proxy, dst_path_noproxy))

        successes = 0
        for (dst_path_proxy, dst_path_noproxy) in tried:
            if self._are_same(dst_path_noproxy, dst_path_proxy):
                successes += 1
        status = {}

        self.attempts = len(tried)
        self.successes = successes

class GenericConcurrencyProxyTest(ProxyTest):
    FILES = ['cgi-bin/slow?sleep=1&size=4096', 'foo.html']
    SLOW_FILE = 'cgi-bin/slow?sleep=1&size=4096'
    FAST_FILE = 'foo.html'
    DESCRIPTION = 'Extended Concurrency Test'
    EXTENDED_DESCRIPTION = \
            'Issuing 5 fast requests to the proxy, while it is busy ' + \
            'handling 5 slow requests that were issued first.'

    TIMES_TO_RUN = None
    TIMEOUT = 10

    download_proxy = ProxyTest._download_proxy
    download_proxy_slow = ProxyTest._download_proxy_slow

    def run(self):

        # Now do the test by fetching some text and binary files directly from
        # Tiny and via the proxy, and then comparing the results.
        tried_slow = []
        i = 0
        for i in range(i, self.TIMES_TO_RUN):
            dst_path_proxy = os.path.join(self.proxy_dir,
                    '%s-%d' % (self._filesystem_safe(self.SLOW_FILE), i))
            dst_path_noproxy = os.path.join(self.noproxy_dir,
                    '%s-%d' % (self._filesystem_safe(self.SLOW_FILE), i))
            url = 'http://%s:%d/%s&i=%d' % \
                    (self.server_host, self.server_port, self.SLOW_FILE, i)

            proxy_proc = self.download_proxy_slow(url, dst_path_proxy, self.TIMEOUT)
            noproxy_proc = self.download_noproxy(url, dst_path_noproxy, self.TIMEOUT)

            tried_slow.append((proxy_proc, noproxy_proc, dst_path_proxy, dst_path_noproxy))

        time.sleep(3)

        self.num_processes_realtime = self.get_num_processes(self.proxy_proc.pid)
        self.num_threads_realtime = self.get_num_threads(self.proxy_proc.pid)

        tried = []
        for i in range(self.TIMES_TO_RUN, self.TIMES_TO_RUN * 2):
            dst_path_proxy = os.path.join(self.proxy_dir,
                    '%s-%d' % (self._filesystem_safe(self.FAST_FILE), i))
            dst_path_noproxy = os.path.join(self.noproxy_dir,
                    '%s-%d' % (self._filesystem_safe(self.FAST_FILE), i))
            url = 'http://%s:%d/%s?i=%d' % \
                    (self.server_host, self.server_port, self.FAST_FILE, i)

            proxy_proc = self.download_proxy(url, dst_path_proxy, self.TIMEOUT)
            noproxy_proc = self.download_noproxy(url, dst_path_noproxy, self.TIMEOUT)

            tried.append((proxy_proc, noproxy_proc, dst_path_proxy, dst_path_noproxy))

        for (proxy_proc, noproxy_proc, dst_path_proxy, dst_path_noproxy) in \
                tried + tried_slow:
            proxy_proc.wait()
            noproxy_proc.wait()

        successes = 0
        for i in range(self.TIMES_TO_RUN):
            (proxy_proc_s, noproxy_proc_s, dst_path_proxy_s, dst_path_noproxy_s) = tried_slow[i]
            (proxy_proc, noproxy_proc, dst_path_proxy, dst_path_noproxy) = tried[i]
            same_s = self._are_same(dst_path_noproxy_s, dst_path_proxy_s)
            same = self._are_same(dst_path_noproxy, dst_path_proxy)
            fast_before_slow = self._is_newer_than(dst_path_proxy_s, dst_path_proxy)
            if same_s and same and fast_before_slow:
                successes += 1

        self.attempts = self.TIMES_TO_RUN
        self.successes = successes

class BasicConcurrencyProxyTest(GenericConcurrencyProxyTest):
    DESCRIPTION = 'Basic Concurrency Test'
    EXTENDED_DESCRIPTION = \
            'Issuing 1 fast request to the proxy, while it is busy ' + \
            'handling 1 slow request that was issued first.'

    TIMES_TO_RUN = 1

class ExtendedConcurrencyProxyTest(GenericConcurrencyProxyTest):
    DESCRIPTION = 'Extended Concurrency Test'
    EXTENDED_DESCRIPTION = \
            'Issuing 5 fast requests to the proxy, while it is busy ' + \
            'handling 5 slow requests that were issued first.'

    TIMES_TO_RUN = 5

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, action='store',
            choices=('multiprocess', 'processpool', 'multithread', 'threadpool', 'epoll'))
    parser.add_argument('-b', '--check-basic', type=int, action='store', metavar='<points>',
            help='Check proxy with basic HTTP tests')
    parser.add_argument('-c', '--check-concurrency', type=int, action='store', metavar='<points>',
            help='Check proxy for concurrent tests')
    parser.add_argument('-m', '--check-memory-mgmt', type=int, action='store', metavar='<points>',
            help='Check that proxy frees memory properly')
    parser.add_argument('-s', '--check-clean-shutdown', type=int, action='store', metavar='<points>',
            help='Check that proxy frees memory properly on shutdown')
    parser.add_argument('-e', '--check-cache', type=int, action='store', metavar='<points>',
            help='Check that proxy caches properly')
    #parser.add_argument('-l', '--check-logging', type=int, action='store', metavar='<points>',
    #        help='Check that proxy logs properly')
    parser.add_argument('-p', '--proxy-output', type=argparse.FileType('wb'),
            action='store', metavar='<file>',
            help='Send proxy-output to a file (Use "-" for stdout).')
    parser.add_argument('-t', '--server-output', type=argparse.FileType('wb'),
            action='store', metavar='<file>',
            help='Send server output to a file (Use "-" for stdout).')
    parser.add_argument('-k', '--keep-files', action='store_const', const=True, default=False,
            help='Don\'t delete files used for proxy/no-proxy downloads.')
    parser.add_argument('-v', '--verbose', action='count', default=0,
            help='Use more verbose output for debugging (use multiple times for more verbosity).')
    args = parser.parse_args(sys.argv[1:])

    if args.verbose > 1:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

    classes = []
    if args.check_basic is not None:
        classes.append((
            (BasicProxyTest,
                NonlocalProxyTest,
                SlowRequestProxyTest,
                SlowResponseProxyTest,
                SlowRequestResponseProxyTest),
            args.check_basic))
    if args.check_cache is not None:
        classes.append((
            (CacheTest, ),
            args.check_cache))
    if args.check_concurrency is not None:
        classes.append((
            (BasicConcurrencyProxyTest,
                ExtendedConcurrencyProxyTest),
            args.check_concurrency))

    p = ProxyTestSuite(args.mode, classes,
            mem_mgmt=args.check_memory_mgmt,
            clean_shutdown=args.check_clean_shutdown,
            keep_files=args.keep_files,
            server_output=args.server_output,
            proxy_output=args.proxy_output,
            verbose=args.verbose)
    p.run()

if __name__ == '__main__':
    main()
