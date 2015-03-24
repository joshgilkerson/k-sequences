#!/usr/bin/env python

import sys
import math
import string

trans=string.letters[26:]+string.digits+string.letters[:26]+string.punctuation

LATEX_TABLES=1

def printUpper(array,dim):
    if LATEX_TABLES:
        sys.stdout.write("\\begin{tabular}[t]{|"+("c|"*(dim+1))+"}\n\hline ")
        f_str="&%s"
        sys.stdout.write(trans[0])
    else:
        i=int(math.log10(max(array)))+2
        f_str='%-'+str(int(i))+'s'
        sys.stdout.write(f_str%trans[0])
        pass
    for i in range(1,dim): sys.stdout.write(f_str%trans[i])
    if LATEX_TABLES: sys.stdout.write("&\\ \\\\")
    sys.stdout.write('\n')
    for i in range(0,dim):
        if not LATEX_TABLES: sys.stdout.write(f_str%'')
        else: sys.stdout.write("\\hline ")
        for j in range(1,i+1): sys.stdout.write(f_str%'')
        for j in range(i+1,dim):
            sys.stdout.write(f_str%str(array[i*dim+j]))
            pass
        sys.stdout.write(f_str%trans[i])
        if LATEX_TABLES: print "\\\\"
        else: sys.stdout.write('\n')
        pass
    if LATEX_TABLES: print "\\hline\n\\end{tabular}" #"\\hline\n\\end{tabular}"
    return

class k_seq:
    def __init__(self,k,n):
        if len(trans)<n:
            raise ValueError, "n(%d) is > %d, the max."%(n,len(trans))
        self.n=n
        self.k=k
        self.graph=[0]*n*n
        self.minDist=[k+1]*n*n
        self.sequence=[]
        return

    def goodnessCount(self,x):
        count=0
        for i in self.sequence[0-self.k:]:
            if not self.graph[i*self.n+x]:count+=1
            pass
        return count        

    def unmatchedCount(self,x):
        count=0
        for i in range(0,self.n):
            if not self.graph[i*self.n+x]:count+=1
            pass
        return count

    def use(self,x):
        self.sequence.append(x)
        t_seq=self.sequence[0-self.k-1:]
        for i in range(1,len(t_seq)+1):
            self.graph[t_seq[-i]*self.n+x]+=1
            if not t_seq[-i]==x: self.graph[x*self.n+t_seq[-i]]+=1
            self.minDist[t_seq[-i]*self.n+x]= min(
                self.minDist[t_seq[-i]*self.n+x],i-1)
            self.minDist[self.n*x+t_seq[-i]]=min(
                self.minDist[self.n*x+t_seq[-i]],i-1)
            pass
        return

    def tryUse(self,x):
        use=None
        if len(self.sequence)==0 or self.goodnessCount(x)>0:
            self.use(x)
            return 1
        return None

    def finished(self):
        for i in self.graph:
            if not i: return None
            pass
        return 1

    def printSeq(self):
        for i in self.sequence: sys.stdout.write(trans[i])
        print
        #print [trans[i] for i in self.sequence]
        print "Length: %d"%len(self.sequence)
        return

    def printOccurences(self):
        for i in range(0,self.n):
            print '%s : %d'%(trans[i],self.graph[i*self.n+i])
            pass
        return
    
    def printPairOccurences(self):
        printUpper(self.graph,self.n)
##         for i in range(0,self.n*self.n,self.n):
##             for j in self.graph[i:i+self.n]:
##                 if j==0: sys.stdout.write(' ')
##                 elif j==1: sys.stdout.write('.')
##                 elif j==2: sys.stdout.write('+')
##                 else: sys.stdout.write('*')
##                 pass
##             sys.stdout.write('\n')
##             pass
        return

    def printDistances(self):
        summary=[0]*(self.k+1)
        printUpper(self.minDist,self.n)
        for i in self.minDist:
            summary[i]+=1
            pass
        for i in range(1,self.k+1):
            print "%-5d : %d / %d"%(i,summary[i]/2,self.n*(self.n-1)/2)
            pass
        return
    
    pass
