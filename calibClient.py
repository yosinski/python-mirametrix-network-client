#! /usr/bin/env python

import sys
from socket import *
from time import sleep

from helper import getLocalIP


'''

Research code... may not work

'''

def main():
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    else:
        HOST = getLocalIP()

    PORT = 4242
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    print 'Attempting to connect to %s...' % repr(ADDR),
    sys.stdout.flush()
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    print 'connected!'

    # Eye-tracker API specific
    tcpCliSock.sendall(str.encode('<SET ID="CALIBRATE_SHOW" STATE="0" />\r\n"'))
    sleep(1)
    tcpCliSock.sendall(str.encode('<SET ID="CALIBRATE_SHOW" STATE="1" />\r\n"'))
    sleep(1)
    tcpCliSock.sendall(str.encode('<SET ID="CALIBRATE_START" STATE="1" />\r\n"'))


    #tcpCliSock.sendall(str.encode('\r\n"'))
    #tcpCliSock.sendall(str.encode('\r\n"'))
    #
    #import pdb; pdb.set_trace()
    #tcpCliSock.sendall(str.encode('<SET ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n"'))
    #tcpCliSock.sendall(str.encode('<SET ID="ENABLE_SEND_DATA" STATE="1" />\r\n"'))

    # Loop forever
    while True:
        data = tcpCliSock.recv(1024)
        foo = bytes.decode(data)
        print 'got something', foo

    tcpCliSock.close()



if __name__ == '__main__':
    main()

