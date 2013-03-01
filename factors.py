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

class Variable:
    name=""             # имя переменной
    value=[]            # значения переменной
    factors=[]          # факторы, в которые входит данная переменная
    parents=[]
    childs=[]
    card = 0            # мощность переменной
    PD = None           # безусловная вероятность данной переменной

    def __init__(self, name, a):
        self.name = name
        self.factors=[]
        self.parents=[]
        self.childs=[]
        if  (type(a)==int):             # cardinality passed
            self.card = a
            for i in range(a):
                self.value.append(i)
        elif(type(a)==list):            # values list passed
            self.value = a
            self.card = len(a)
        self.PD=None

    def find_value(self, val):
        # given value finds its number among variable's values
        for j in range(len(self.value)):
            if self.value[j]==val:
                return j

    def __repr__(self):
        return self.name

    def get_PD(self):                                       # calculates probability distribution w/ no conditions
        if self.PD==None:                                   # find a factor contains this var as cons
            f = None
            for factor in self.factors:
                if factor.cons == [self]:
                    f = factor
            for v in list(set(f.var) - set([self])):        # marginalize all other vars from this factor
                f = f - v
            self.PD = f.CPDs                                # and extract PD from this reduced factor's CPD
        return self.PD

class BinaryVariable(Variable):
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
            i.factors.append(self)              # adds self to each variable' factor list
            self.card.append(i.card)            # builds factor's cardinality list from var's cardinalities
        for i in self.cond:                     # in case of conditioning
            self.card.append(i.card)            # continues factor'a cardinality list
            i.factors.append(self)              # adds self to variables' factor list
            for j in self.cons:                 # builds variables' hierarchy
                i.childs.append(j)
                j.parents.append(i)
        # counts cumulative cardinality
        for i in range(len(self.card)):
            self.pcard.append(
                reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)    # for compatibility
        # actually forgot how it workes. However, tested

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
            res+='\t\t'+str(j)+'->'
            for i in self.index2ass(j):
                res+=str(i)+", "
            res+=str(self.CPDs[j])+'\n';
        return res

    def map(self, lst):
        # bulds a map: hash table,
        # where keys - indecies of THIS factor's assingment list
        # and values - indecies of given var list assignment, corresponding to key
        m={}
        for i in range(len(self.var)):
            for j in range(len(lst)):
                if (self.var[i]==lst[j]):
                    m[i]=j
        return m
    def ass(self, n, mp):
        # given number of assignment, computes
        ass = self.index2ass(n)
        res = []
        for i in range(len(ass)):
            if i in mp.keys():
                res.append(ass[i])
        return res
    def __mul__(self, other):
        res=Factor(name='Product', cons=list(set(self.var) | set(other.var)),
                    cond=[],
                    CPDs=[])
        mapX=res.map(self.var)
        mapY=res.map(other.var)
        res.CPDs=[]
        for n in range(res.pcard[0]):
            assX = res.ass(n, mapX)
            assY = res.ass(n, mapY)
            res.CPDs.append(  self.CPDs[self.ass2index(assX)] *
                              other.CPDs[other.ass2index(assY)] )
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
            res.append(self.var[j].value[index % self.card[-(j+1)]])
            index=(index - (index % self.card[-(j+1)])) / self.card[-(j+1)]
        return res
    def __sub__(self, var):
##        print "Marginalizing factor", self.name, "wrt", var.name
        res = Factor('Reduced factor',
                        cons = self.cons,
                        cond = list(set(self.cond) - set([var])),
                        CPDs=[])
        mapX = self.map(res.var)
        mapY = self.map([var])
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        for i in range(len(self.CPDs)):
            assX = self.ass(i, mapX)
            assY = self.ass(i, mapY)[0]
            i1 = res.ass2index(assX)
##            print i, assX, assY, i1
##            print res.CPDs[i1], self.CPDs[i], var.get_PD()[var.find_value(assY)], self.CPDs[i]*var.get_PD()[var.find_value(assY)]
            res.CPDs[i1] += self.CPDs[i]*var.get_PD()[var.find_value(assY)]
##            print i, i1, res.CPDs[i1]
        return res
    def __div__(self, other):
        res = Factor(name='Division',
                        cons=list(set(self.cons) - set(other.cons)),
                        cond=list(set(self.cons) & set(other.cons)),
                        CPDs=[])
        mapX = self.map(res.var)
        mapY = self.map(res.cond)
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        print res.cons, res.cond
        print self.var, other.cons
        print mapX, mapY
        for i in range(len(self.CPDs)):
            assX = self.ass(i, mapX)
            assY = self.ass(i, mapY)
            print assX, assY
            print self.CPDs[self.ass2index(assX)],
            print other.CPDs[other.ass2index(assY)]
            res.CPDs[i] = self.CPDs[self.ass2index(assX)] / other.CPDs[other.ass2index(assY)]
        return res

E = Variable("Eartquake", ['still', 'shake']);
B = Variable("Burglary",  ['safe', 'robbed']);
A = Variable("Alarm", ['quiet', 'loud']);
R = Variable("Radio", ["off", "on"])

F1 = Factor(name='E', cons=[E],      CPDs=[0.999, 0.001]);
F2 = Factor(name='B', cons=[B],       CPDs=[0.99, 0.01]);
F3 = Factor(name='R|E', cons=[R], cond=[E],CPDs=[0.9, 0.1, 0.2, 0.8]);
F4 = Factor(name='A|E,B', cons=[A], cond=[E, B],
        CPDs=[1, 0, 0.01, 0.99, 0.02, 0.98, 0, 1]);

F6=F1*F2
print F1
print F6
print F6/F1

F5 = F3 - E
F5.name = 'R'
print F5
F6 = F5 * F1
F6.name = 'R,E'
print F6
F7 = F6/F5
F7.name = 'E|R'
print F7

##print F3-E
##print F3.ass2index(F3.index2ass(3))
##for i in range(F3.pcard[0]):
##    print i, F3.index2ass(i), F3.ass2index(F3.index2ass(i))

C = Variable('Cancer', ['yes', 'no'])
T = Variable('Test', ['pos', 'neg'])

F11 = Factor(name='C', cons=[C], CPDs=[0.0001, 0.9999])
F12 = Factor(name='T|C', cons=[T], cond=[C], CPDs=[0.9, 0.1, 0.2, 0.8])
F14 = (F12 - C) * F11
F14.name='C,T'
F15 = F14/(F12 - C)
F15.name='C|T'
print F15
