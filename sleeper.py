#! /usr/bin/env python

from time import sleep
from datetime import datetime, timedelta
import random
import sys
import pdb

def sleeper():
    if len(sys.argv) > 1:
        maxTime = float(sys.argv[1])
    else:
        maxTime = 9999
        
    time0 = datetime.now()
    while True:
        sleep(random.uniform(0, .5))
        diff = datetime.now()-time0
        diffSeconds = diff.seconds + diff.microseconds/1000000.0
        print diffSeconds
        #print >> sys.stderr, 'errText'
        sys.stdout.flush()
        sys.stderr.flush()
        if diffSeconds > maxTime:
            break

sleeper()
