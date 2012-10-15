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
class BinaryVariable(Variable):
    def __init__(self, name):
        self.name = name
        self.value=[0, 1]

class Factor:
    var=[]             # переменные, входящие в фактор
    cond=[]             # условия
    CPDs=[]
    card=[]
    pcard=[]
    def __init__(self, var=[], cond=[], CPDs=[]):
        self.var = var
        self.cond = cond
        self.CPDs = CPDs
        self.card=[]
        self.pcard=[]
        for i in self.var+self.cond:
            self.card.append(len(i.value))
        for i in range(len(self.card)):
            j=i
            p=1
            while j<len(self.card):
                p*=self.card[j]
                j+=1
            self.pcard.append(p)
        self.pcard.append(1)
        pass
    def __mul__(self, other):
        pass
    def ass2index(self, assignment):
        j=0
        res=0
        for v in self.var+self.cond:
##            print v.find_value(assignment[j]), self.pcard[j+1]
            res+=v.find_value(assignment[j])*self.pcard[j+1]
            j+=1
        return res

V1 = BinaryVariable("Variable 1");
V2 = BinaryVariable("Variable 2");
V3 = BinaryVariable("Variable 3");

F1 = Factor(var=[V1], cond=[],   CPDs=[0.11, 0.89]);
F2 = Factor(var=[V2], cond=[V1], CPDs=[0.59, 0.41, 0.22, 0.78]);
F3 = Factor(var=[V3], cond=[V2], CPDs=[0.39, 0.61, 0.06, 0.94]);

print F3.CPDs[F3.ass2index((1, 1))]


