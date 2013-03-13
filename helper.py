import socket

def getLocalIP():
    '''Returns the local ip. Probably not 100% reliable'''

    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(("gmail.com",80))
    ip = ss.getsockname()[0]
    print 'Got local IP: %s' % ip
    return ip
