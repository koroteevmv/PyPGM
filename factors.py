# -*- coding: UTF-8 -*-
#--------------------------------------------
# Name:        модуль1
# Purpose:
#
# Author:      Admin
#
# Created:     15.10.2012
# Copyright:   (c) Admin 2012
# Licence:     <your licence>
#--------------------------------------------
#!/usr/bin/env python

class consiable:
    name=""             # имя переменной
    value=[]            # значения переменной
    factors=[]          # факторы, в которые входит данная переменная
    parents=[]
    childs=[]
    card = 0            # мощность переменной
    PD = None
    def __init__(self, name, a):
        self.name = name
        self.factors=[]
        self.parents=[]
        self.childs=[]
        if  (type(a)==int):
            self.card = a
            for i in range(a):
                self.value.append(i)
        elif(type(a)==list):
            self.value = a
            self.card = len(a)
        self.PD=[]

    def find_value(self, val):
        for j in range(len(self.value)):
            if self.value[j]==val:
                return j
    def __repr__(self):
        return self.name
    def get_PD(self):     # TODO: implement
        if self.PD==None:
            f = None
            for factor in self.factors:
                if factor.cons == [self]:
                    f = factor
            for v in list(set(f.var) - set([self])):
                f = f - v
            self.PD = f.CPDs
        return self.PD

class Binaryconsiable(consiable):
    def __init__(self, name):
        self.name = name
        self.value=[0, 1]
        self.card = 2
        self.factors = []
        self.parents=[]
        self.childs=[]
        self.PD = None

class Factor:
    cons=[]             # переменная-результат
    cond=[]             # переменные-условия
    var=[]              # переменные, входящие в фактор
    CPDs=[]             # условные вероятности
    card=[]             # вектор разрядности переменных
    pcard=[]            # кумулятивная общая разрядность
    name=''
    def __init__(self, name='', cons=[], cond=[], CPDs=[]):
        self.cons = cons
        self.CPDs = CPDs    # TODO: validate CPD cardinality and sums
        self.card=[]
        self.pcard=[]
        self.name=name
        self.cond=cond
        self.var=self.cons + self.cond

        for i in self.cons:
            i.factors.append(self)
            self.card.append(i.card)
        for i in self.cond:
            self.card.append(i.card)
            i.factors.append(self)
            for j in self.cons:
                i.childs.append(j)
                j.parents.append(i)

        for i in range(len(self.card)):
            self.pcard.append(
                reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)
    def __repr__(self):
        res=self.name+':\n'
        res+="\tVariables:\n"
        for i in self.cons:
            res+='\t\t'+i.name+'\n'
        res+="\tConditioned on:\n"
        for j in self.cond:
            res+='\t\t'+j.name+'\n'
        res+="\tCPDs:\n"
        for j in range(len(self.CPDs)):
            res+='\t\t'
            for i in self.index2ass(j):
                res+=str(i)+", "
            res+=str(self.CPDs[j])+'\n';
        return res
    def __mul__(self, other):
        res=Factor(cons=list(set(self.var) | set(other.var)))
        res.name = 'Product'
        N = res.pcard[0]
        mapX={}
        mapY={}
        for i in range(len(res.var)):
            for j in range(len(self.var)):
                if (res.var[i].name==self.var[j].name):
                    mapX[i]=j
            for j in range(len(other.var)):
                if (res.var[i].name==other.var[j].name):
                    mapY[i]=j
        print mapX
        print mapY
        res.CPDs=[]
        for n in range(N):
            ass = res.index2ass(n)
            assX=[]
            assY=[]
            for j in range(len(ass)):
                if j in mapX.keys():
                    assX.append(ass[j])
                if j in mapY.keys():
                    assY.append(ass[j])
            print ass, assX, assY
            res.CPDs.append(  self.CPDs[self.ass2index(assX)] *
                              other.CPDs[other.ass2index(assY)] )
            print self.CPDs[self.ass2index(assX)] * other.CPDs[other.ass2index(assY)],
            print self.CPDs[self.ass2index(assX)],
            print other.CPDs[other.ass2index(assY)]
        return res
    def ass2index(self, assignment):
        j=0
        res=0
        for v in self.var:
            res+=v.find_value(assignment[j])*self.pcard[j+1]
            j+=1
        return res
    def index2ass(self, index):
        res=[]
        for j in range(len(self.card)):
            res.append(index % self.card[-(j+1)])
            index=(index - (index % self.card[-(j+1)])) / self.card[-(j+1)]
        return res[::-1]
    def __sub__(self, var):
        m=0
        for i in range(len(self.var)):
            if (self.var[i]==var): m=i
        res = Factor('Reduced factor',
                        cons = self.cons,
                        cond=list(set(self.cond) - set([var])))
        mapX={}
        mapY={}
        for i in range(len(self.var)):
            for j in range(len(res.var)):
                if (res.var[j].name==self.var[i].name):
                    mapX[i]=j
            if (self.var[i].name==var.name):
                    mapY[i]=j
##        print mapX
##        print mapY
        for i in range(len(res.pcard)):
            res.CPDs.append(0)
        for i in range(len(self.CPDs)):
            ass = self.index2ass(i)
            assX=[]
            assY=[]
            for j in range(len(ass)):
                if j in mapX.keys():
                    assX.append(ass[j])
                if j in mapY.keys():
                    assY.append(ass[j])
##            print ass, assX, assY
##            print self.CPDs[i], var.get_PD()[assY[0]]
            i1 = res.ass2index(assX)
            res.CPDs[i1] += self.CPDs[i]*var.get_PD()[assY[0]]
        return res

E = Binaryconsiable("Eartquake");
B = Binaryconsiable("Burglary");
A = Binaryconsiable("Alarm");
R = Binaryconsiable("Radio");

F1 = Factor(name='EarthQake', cons=[E],      CPDs=[0.99, 0.01]);
F2 = Factor(name='Burglary', cons=[B],       CPDs=[0.99, 0.01]);
F3 = Factor(name='Radio', cons=[R], cond=[E],CPDs=[0.99, 0.01, 0.01, 0.99]);
F4 = Factor(name='Alarm', cons=[A], cond=[E, B],CPDs=[0.99, 0.01, 0.01, 0.99]);

##print F3-E
##print F3.ass2index(F3.index2ass(3))
##for i in range(F3.pcard[0]):
##    print i, F3.index2ass(i), F3.ass2index(F3.index2ass(i))

print E.get_PD()
print F3 - E
print R.get_PD()