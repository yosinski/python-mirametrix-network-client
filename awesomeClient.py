#! /usr/bin/env python

from socket import *
from time import sleep
import re, sys, random


from LoggedProcess import LoggedProcess
from helper import getLocalIP


'''

Research code. May work poorly.

'''


def simpleListenLoop(proc, tcpCliSock):
    # Eye-tracker API specific
    tcpCliSock.send(str.encode('<SET ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n"'))
    tcpCliSock.send(str.encode('<SET ID="ENABLE_SEND_DATA" STATE="1" />\r\n"'))

    # Loop forever
    RE_STRING = '<REC FPOGX="([-0-9\.]+)" FPOGY="([-0-9\.]+)" FPOGS="[0-9\.]+" FPOGD="[0-9\.]+" FPOGID="[0-9]+" FPOGV="([01])"/>'
    ii = 0
    while True:
        ii += 1
        data = tcpCliSock.recv(1024)
        st = bytes.decode(data)
        #print 'got something', st

        results = re.search(RE_STRING, st)

        if results is None:
            print 'Could not parse "%s", skipping' % st
            continue
        #print 'results is', results

        rawXX       = float(results.group(1))
        rawYY       = float(results.group(2))
        validEye = int(results.group(3))

        xx = rawXX
        yy = 1-rawYY

        idxY = int(yy * 3)
        xx = (xx-.1) * (1.0/.8)  # rescale hack....
        idxX = int(xx * 5)
        validIdx = idxY in [0, 1, 2] and idxX in [0, 1, 2, 3, 4]
        idx = idxY * 5 + idxX if validIdx else -1
        
#        print '%d (%.3f, %.3f) %d (%d, %d) %d' % (validEye, xx, yy, validIdx, idxX, idxY, idx)

        sendPositionEvery = 5
        if ii % sendPositionEvery == 0:
            # Send bin
            #proc.write('%d\n' % idx)
            # Send x, y (in real x, y order)
            proc.write('%f %f\n' % (rawXX, rawYY))
            print('%f %f\n' % (rawXX, rawYY))

        #print proc._quit, dir(proc._process)
        #print
        #print
        if(proc._quit):
            print 'QUITTING'
            break
    tcpCliSock.close()



def main():
    args = ('./yourProgramHere', '--arg1', '--arg2')
    
    proc = LoggedProcess(args         = args,
                         logStdOut    = 'stdout.log',
                         logStdErr    = 'stderr.log')

    print 'Started child process!'

    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    else:
        HOST = getLocalIP()

    if len(sys.argv) > 2:
        PORT = sys.argv[2]
    else:
        PORT = 4242

    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    print 'Attempting to connect to %s...' % repr(ADDR),
    sys.stdout.flush()
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    print 'connected!'

    print 'Starting loop'
    simpleListenLoop(proc, tcpCliSock)



if __name__ == '__main__':
    main()
