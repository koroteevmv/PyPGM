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
import operator
class Variable:
    name=""             # имя переменной
    value=[]            # значения переменной
    def __init__(self, name, a):
        self.name = name
        if  (type(a)==int):
            for i in range(a):
                self.value.append(i)
        elif(type(a)==list):
            self.value = a
    def find_value(self, val):
        for j in range(len(self.value)):
            if self.value[j]==val:
                return j
    def __repr__(self):
        return self.name
class BinaryVariable(Variable):
    def __init__(self, name):
        self.name = name
        self.value=[0, 1]

class Factor:
    var=[]              # переменные, входящие в фактор
    cond=[]             # условия
    CPDs=[]             # условные вероятности
    card=[]             # вектор разрядности переменных
    pcard=[]            # кумулятивная общая разрядность
    name=''
    def __init__(self, name='', var=[], cond=[], CPDs=[]):
        self.var = var
        self.cond = cond
        self.CPDs = CPDs
        self.card=[]
        self.pcard=[]
        self.name=name
        for i in self.var+self.cond:
            self.card.append(len(i.value))
        for i in range(len(self.card)):
            self.pcard.append( reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)
    def __repr__(self):
        res=self.name+':\n'
        for j in self.var+self.cond:
            res+='\t'+j.name+'\n'
        return
    def __mul__(self, other):
        pass
    def ass2index(self, assignment):
        j=0
        res=0
        for v in self.var+self.cond:
            res+=v.find_value(assignment[j])*self.pcard[j+1]
            j+=1
        return res
    def index2ass(self, index):
        res=[]
        for j in range(len(self.var+self.cond)):
            res.append(index % self.card[-(j+1)])
            index=(index - (index % self.card[-(j+1)])) / self.card[-(j+1)]
        return res[::-1]

V1 = BinaryVariable("Variable 1");
V2 = BinaryVariable("Variable 2");
V3 = BinaryVariable("Variable 3");

F1 = Factor(name='Factor 1', var=[V1], cond=[],   CPDs=[0.11, 0.89]);
F2 = Factor(name='Factor 2', var=[V2], cond=[V1], CPDs=[0.59, 0.41, 0.22, 0.78]);
F3 = Factor(name='Factor 3', var=[V3], cond=[V2], CPDs=[0.39, 0.61, 0.06, 0.94]);

for j in range(F3.pcard[0]):
    print j, F3.index2ass(j), F3.ass2index(F3.index2ass(j))


