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

while not driver.finished():
    best=-1
    possibles=[]
    for i in range(0,N):
        temp=driver.goodnessCount(i)
        if temp>best:
            possibles=[i]
            best=temp
            pass
        elif temp==best: possibles.append(i)
        pass
    possibles2=[]
    best2=-1
    for i in possibles:
        temp=driver.unmatchedCount(i)
        if temp>best2:
            possibles2=[i]
            best2=temp
            pass
        elif temp==best2: possibles2.append(i)
        pass
    driver.use(possibles2[0])
    pass


print "-----------------The Sequence-------------------"
driver.printSeq()
print "-----------------Occurences by Digit------------"
driver.printOccurences()
print "-----------------Occurences by Pair------------"
driver.printPairOccurences()
print "-----------------Minimal Distances--------------"
driver.printDistances()
