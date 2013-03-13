#! /usr/bin/env python

import os
import sys
import time
import threading
import subprocess

from asyncproc import Process



class LoggedProcess(Process):
    '''Like asyncproc.Process, but allows logging of stdout/stderr to files.'''

    def __init__(self, *params, **kwparams):
        '''Takes an extra two keyword args, all are optional:
        
        logStdOut = "<filename>"     (default: None)
        logStdErr = "<filename>"     (default: None)
        warnOverflow = True/False    (default: True)
        
        Both log* arguemnts default to None.  If no file is used,
        stdout/stderr are kept in memory and must be read manually.
        If either is None, LoggedProcess issues a warning that memory
        overflow may occur if no one else reads the threads.
        '''

        self._logStdOut    = kwparams.setdefault('logStdOut',    None)
        self._logStdErr    = kwparams.setdefault('logStdErr',    None)
        self._warnOverflow = kwparams.setdefault('warnOverflow', True)

        del kwparams['logStdOut']
        del kwparams['logStdErr']
        del kwparams['warnOverflow']

        if self._logStdOut is None and self._warnOverflow:
            print >> sys.stderr, ('WARNING: LoggedProcess created without specifying logStdOut ' +
                                  'file.  stdout will be kept in memory unless it is read manually')
        if self._logStdErr is None and self._warnOverflow:
            print >> sys.stderr, ('WARNING: LoggedProcess created without specifying logStdErr ' +
                                  'file.  stderr will be kept in memory unless it is read manually')
        
        self._mod_init(*params, **kwparams)


    def _mod_init(self, *params, **kwparams):
        '''Modified version of deault Process.__init__.  Handles _reader creation differently'''
        if len(params) <= 3:
            kwparams.setdefault('stdin', subprocess.PIPE)
        if len(params) <= 4:
            kwparams.setdefault('stdout', subprocess.PIPE)
        if len(params) <= 5:
            kwparams.setdefault('stderr', subprocess.PIPE)
        self._pending_input = []
        self._collected_outdata = []
        self._collected_errdata = []
        self._exitstatus = None
        self._lock = threading.Lock()
        self._inputsem = threading.Semaphore(0)
        # Flag telling feeder threads to quit
        self._quit = False

        self._process = subprocess.Popen(*params, **kwparams)

        if self._process.stdin:
            self._stdin_thread = threading.Thread(
                name="stdin-thread",
                target=self._feeder, args=(self._pending_input,
                                            self._process.stdin))
            self._stdin_thread.setDaemon(True)
            self._stdin_thread.start()

        if self._process.stdout:
            self._stdout_thread = threading.Thread(
                name="stdout-thread",
                target=self._reader, args=(self._collected_outdata,
                                            self._process.stdout,
                                            self._logStdOut))
            self._stdout_thread.setDaemon(True)
            self._stdout_thread.start()

        if self._process.stderr:
            self._stderr_thread = threading.Thread(
                name="stderr-thread",
                target=self._reader, args=(self._collected_errdata,
                                            self._process.stderr,
                                            self._logStdErr))
            self._stderr_thread.setDaemon(True)
            self._stderr_thread.start()


    def _reader(self, collector, source, outfile = None):
        ''' Overridden version of _reader that logs to file if self. '''
        
        while True:
            #print 'trying to read', source
            data = os.read(source.fileno(), 65536)
            #print 'got data', data
            sys.stdout.flush()
            if outfile is None:
                self._lock.acquire()
                collector.append(data)
                self._lock.release()
            else:
                ff = open(outfile, 'a')
                ff.write(data)
                ff.close()
                if len(data) < 1000:
                    time.sleep(.5)  # sleep a little to give our disk a break
            if data == "":
                source.close()
                break
        return


    def read(self, *args, **kwargs):
        '''Overridden version of read that warns if read is attempted on a process that is logging.'''
        if self._logStdOut is not None:
            print >> sys.stderr, ('WARNING: This LoggedProcess is logging to %s, so calling' % self._logStdOut +
                                  'LoggedProcess.read() will never return anything.')
        return super(LoggedProcess, self).read(*args, **kwargs)


    def readerr(self, *args, **kwargs):
        '''Overridden version of readerr that warns if readerr is attempted on a process that is logging.'''
        if self._logStdOut is not None:
            print >> sys.stderr, ('WARNING: This LoggedProcess is logging to %s, so calling' % self._logStdErr +
                                  'LoggedProcess.readerr() will never return anything.')
        return super(LoggedProcess, self).readerr(*args, **kwargs)



def test():
    '''Tests LoggedProcess'''

    print 'Starting process, should be logged to stdout.log and stderr.log'
    proc = LoggedProcess(('./sleeper.py',),
                         logStdOut = 'stdout.log',
                         logStdErr = 'stderr.log')

    while True:
        time.sleep(1)



if __name__ == '__main__':
    test()
