#!/usr/bin/env python

import sys
import utils

if not len(sys.argv)==3:
    print "Usage: %s K N"%sys.argv[0]
    sys.exit()
    pass

K=int(sys.argv[1])
N=int(sys.argv[2])

driver=utils.k_seq(K,N)

done=None
seq = range(0,N)

while not done:
    for i in seq:
        if done: break
        driver.use(i)
        if driver.finished():
            done=1
            break
        for j in seq:
            driver.tryUse(j)
            if driver.finished():
                done=1
                break
            pass
        pass
    pass


print "-----------------The Sequence-------------------"
driver.printSeq()
print "-----------------Occurences by Digit------------"
driver.printOccurences()
print "-----------------Occurences by Pair-------------"
driver.printPairOccurences()
print "-----------------Minimal Distances--------------"
driver.printDistances()
