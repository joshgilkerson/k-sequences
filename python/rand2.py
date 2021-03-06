#!/usr/bin/env python

import sys
import utils
import random

if not len(sys.argv)==3:
    print "Usage: %s K N"%sys.argv[0]
    sys.exit()
    pass

K=int(sys.argv[1])
N=int(sys.argv[2])

driver=utils.k_seq(K,N)

failures=0
while not driver.finished():
    if driver.tryUse(random.randrange(0,N)): failures=0
    else: failures+=1
    if failures>=N*N:
        driver.use(random.randrange(0,N))
        failures=0
    pass


print "-----------------The Sequence-------------------"
driver.printSeq()
print "-----------------Occurences by Digit------------"
driver.printOccurences()
print "-----------------Occurences by Pair------------"
driver.printPairOccurences()
print "-----------------Minimal Distances--------------"
driver.printDistances()
