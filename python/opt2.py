#!/usr/bin/env python

import sys

if not len(sys.argv)==2:
    print "Usage: %s n"%sys.argv[0]
    sys.exit()
    pass

N=int(sys.argv[1])

import math

val=N*(N-1)/4
if N%4==0:val+=N/4+1
elif N%4==1:val+=2
elif N%4==2:val+=N*3/4
else: val+=N/2

print val

    
