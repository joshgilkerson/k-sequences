#!/usr/bin/env python

import sys
import math

if not len(sys.argv)==3:
    print "Usage: %s k n"%sys.argv[0]
    sys.exit()
    pass

K=float(int(sys.argv[1]))
N=float(int(sys.argv[2]))

val=math.ceil((N-1.0)/2.0/K)*N
for j in range(1,int(K+1)):
    val+=math.ceil((N+K-j)/2.0/K)
    val-=math.ceil((N-1.0)/2.0/K)
print val

