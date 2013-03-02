# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#--------------------------------------------
# Name:        PyPGM
# Author:      sejros
# Created:     15.10.2012
# Copyright:   (c) sejros 2012
# Licence:     GNU GPL
#--------------------------------------------

class Variable:
    '''
    Syntax:
            E = Variable("Eartquake", ['still', 'shake']);
            B = Variable("Burglary",  ['safe', 'robbed']);
            A = Variable("Alarm", ['quiet', 'loud']);
            R = Variable("Radio", ['off', 'on'])
    '''
    name=""             # имя переменной
    value=[]            # значения переменной
    factors=[]          # факторы, в которые входит данная переменная
    parents = []
    childs = []
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
    '''
    Syntax:
            E = Variable("Eartquake", ['still', 'shake']);
            B = Variable("Burglary",  ['safe', 'robbed']);
            A = Variable("Alarm", ['quiet', 'loud']);
            R = Variable("Radio", ['off', 'on'])

            F1 = Factor(name='E', var=[E],       CPDs=[0.999, 0.001]);
            F2 = Factor(name='B', var=[B],       CPDs=[0.99, 0.01]);
            F3 = Factor(name='R|E', var=[R,E],   CPDs=[0.9, 0.2, 0.1, 0.8]);
            F4 = Factor(name='A|E,B', var=[A,E,B],
                    CPDs=[1.0, 0.0, 0.01, 0.99, 0.02, 0.98, 0.0, 1.0]);
    '''
    var=[]              # переменные, входящие в фактор
    CPDs=[]             # условные вероятности
    card=[]             # вектор разрядности переменных
    pcard=[]            # кумулятивная общая разрядность
    name=''
    def __init__(self, name='', var=[], CPDs=[]):
        self.CPDs = CPDs    # TODO: validate CPD cardinality and sums
        self.pcard=[]
        self.name=name
        self.var=var
        self.card=[]
        for i in self.var:
            self.card.append(i.card)
##        for i in self.cons:
##            i.factors.append(self)              # adds self to each variable' factor list
##            self.card.append(i.card)            # builds factor's cardinality list from var's cardinalities
##        for i in self.cond:                     # in case of conditioning
##            self.card.append(i.card)            # continues factor'a cardinality list
##            i.factors.append(self)              # adds self to variables' factor list
##            for j in self.cons:                 # builds variables' hierarchy
##                i.childs.append(j)
##                j.parents.append(i)
        # counts cumulative cardinality
        for i in range(len(self.var)):
            self.pcard.append(
                reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)    # for compatibility
        # actually forgot how it workes. However, tested

    def __repr__(self):
        res=self.name+':\n'
        res+="\tScope:\n"
        for i in self.var:
            res+='\t\t'+i.name+'\n'
        res+="\tCPDs:\n"
        for j in range(len(self.CPDs)):
            res+='\t\t'+str(j)+'->'
            for i in self.index2ass(j):
                res+=str(i)+", "
            res+=str(self.CPDs[j])+'\n';
        return res

    def map(self, lst):
        '''
        bulds a map: hash table,
        where keys - indecies of THIS factor's assingment list
        and values - indecies of given var list assignment, corresponding to key
        '''
        m={}
        for i in range(len(self.var)):
            for j in range(len(lst)):
                if (self.var[i]==lst[j]):
                    m[i]=j
        return m
        
    def ass(self, n, mp):
        '''
        given number of assignment, computes
        this assignment of this factor
        and returns it rearranged according to map given
        '''
        ass = self.index2ass(n)
        res = []
        for i in range(len(mp)):
            res.append(None)
        for i in range(len(ass)):
            if i in mp.keys():
                res[mp[i]] = ass[i]
        return res
        
    def ass2index(self, assignment):
        '''
        given a list of values of factor's vars
        in order of factor.var
        computes a number of thiaa asignment

        this number is always in range [0..factor.pcard[0]-1]
        '''
        j=0
        res=0
        for v in self.var:
            res+=v.find_value(assignment[j])*self.pcard[j+1]
            j+=1
        return res
        
    def index2ass(self, index):
        '''
        given a number computes an assignment -
        list of variables' values in order of factor.var

        if given index is greater than factor.pcard[0]-1
        it is equal to (index mod factor.pcard[0])
        '''
        res=[]
        for j in range(len(self.var)):
            res.append(self.var[-j-1].value[index % self.card[-j-1]])
            index=(index - (index % self.card[-j-1])) / self.card[-j-1]
        return res[::-1]
        
    def __mul__(self, other):
        '''
        computes product of factors
        F(A,C)*F(C,B) = F(A,B,C)

        Syntax:
                A = Variable('A', [1, 2, 3])
                B = Variable('B', [1, 2])
                C = Variable('C', [1, 2])
                F1 = Factor(name='A,B', var=[A,B],
                            CPDs=[0.5, 0.8, 0.1, 0, 0.3, 0.9])
                F2 = Factor(name='B,C', var=[B,C],
                            CPDs=[0.5, 0.7, 0.1, 0.2])
                # factor product
                F3 = F1*F2
                F3.name = 'A,B,C'
                print F3
        '''
        res=Factor(name='Product',
                    var=list(set(self.var) | set(other.var)),
                    CPDs=[])
        mapS = res.map(self.var)
        mapO = res.map(other.var)
        res.CPDs = []
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        for n in range(res.pcard[0]):
            assS = res.ass(n, mapS)
            Si = self.ass2index(assS)
            assO = res.ass(n, mapO)
            Oi = other.ass2index(assO)
            res.CPDs[n] = (self.CPDs[Si] * other.CPDs[Oi])
        return res
        
    def marginal(self, var=None):
        '''
        perfoms a factor marginalization
        F(A,B,C)-B = F(A,C)

        Syntax:
                A = Variable('A', [1, 2, 3])
                B = Variable('B', [1, 2])
                C = Variable('C', [1, 2])
                F1 = Factor(name='A,B', var=[A,B],
                            CPDs=[0.5, 0.8, 0.1, 0, 0.3, 0.9])
                F2 = Factor(name='B,C', var=[B,C],
                            CPDs=[0.5, 0.7, 0.1, 0.2])
                # factor product
                F3 = F1*F2
                F3.name = 'A,B,C'
                print F3
                # factor marginalization
                F4 = F3.marginal(B)
                F4.name = 'A,C'
                print F4
        '''
        if not var in self.var:
            raise AttributeError()
            
        res = Factor('Marginal factor',
                        var = list(set(self.var) - set([var])),
                        CPDs=[])
        mapX = self.map(res.var)
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        for i in range(len(self.CPDs)):
            assX = self.ass(i, mapX)
            i1 = res.ass2index(assX)
            res.CPDs[i1] += self.CPDs[i]
        return res
        
    def reduce(self, var=None, value=''):
        '''
        computes a factor reduction
        F(A,B)/F(B) = F(A|B)

        Syntax:
                A = Variable('A', [1, 2, 3])
                B = Variable('B', [1, 2])
                C = Variable('C', [1, 2])
                F1 = Factor(name='A,B', var=[A,B],
                            CPDs=[0.5, 0.8, 0.1, 0, 0.3, 0.9])
                F2 = Factor(name='B,C', var=[B,C],
                            CPDs=[0.5, 0.7, 0.1, 0.2])        
                # factor product
                F3 = F1*F2
                F3.name = 'A,B,C'
                # factor reduction
                F4 = F3.reduce(var=C, value=1)
                F4.name = 'A,B'
                print F4
        '''
        if not var in self.var:
            raise AttributeError()
            
        res = Factor(name='Reduced',
                        var = list(set(self.var) - set([var])),
                        CPDs=[])
        mapX = self.map(res.var)
        mapY = self.map([var])
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        for i in range(len(self.CPDs)):
            assX = self.ass(i, mapX)
            assY = self.ass(i, mapY)
            i1 = res.ass2index(assX)
            if assY[0]==value:
                res.CPDs[i1] = self.CPDs[i]
        return res
        
"""
    def revert(self):
        '''
        given factor A,B|C,D computes C,D|A,B

        particular order of cons or cond may differ
        '''
        res = self
        for cond in self.cond:
            res = res - cond
            print '=>'
            print cond
            print cond.get_PD()
            f_cond = Factor(name='',
                            cons=[cond],
                            cond=[],
                            CPDs=cond.get_PD())
            res = res*f_cond
        for cons in self.cons:
            f_cons = Factor(name='',
                                cons=[cons],
                                cond=[],
                                CPDs=cons.get_PD())
            res = res/f_cons
        return res
"""

class CPD(Factor):
    """ Class doc """
    cons=[]
    cond=[]
        
    def __init__(self, name='', cons=[], cond=[], CPDs=[]):
        self.CPDs = CPDs    # TODO: validate CPD cardinality and sums
        self.pcard=[]
        self.name=name
        self.cons = cons
        self.cond = cond
        self.var = cons + cond
        self.card=[]
        for i in self.var:
            self.card.append(i.card)
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
        for i in range(len(self.var)):
            self.pcard.append(
                reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)    # for compatibility
        # actually forgot how it workes. However, tested

    def __repr__(self):
        res=self.name+':\n'
        res+="\tVariables:\n"
        for i in self.cons:
            res+='\t\t'+i.name+'\n'
        res+="\tConditions:\n"
        for i in self.cond:
            res+='\t\t'+i.name+'\n'
        res+="\tCPDs:\n"
        for j in range(len(self.CPDs)):
            res+='\t\t'+str(j)+'->'
            for i in self.index2ass(j):
                res+=str(i)+", "
            res+=str(self.CPDs[j])+'\n';
        return res

class PD(Factor):
    """ Class doc """
    
    def __init__ (self):
        """ Class initialiser """
        pass



E = Variable("Eartquake", ['still', 'shake']);
B = Variable("Burglary",  ['safe', 'robbed']);
A = Variable("Alarm", ['quiet', 'loud']);
R = Variable("Radio", ['off', 'on'])

F1 = Factor(name='E', var=[E],       CPDs=[0.999, 0.001]);
F2 = Factor(name='B', var=[B],       CPDs=[0.99, 0.01]);
F3 = Factor(name='R|E', var=[R,E],   CPDs=[0.9, 0.2, 0.1, 0.8]);
F4 = Factor(name='A|E,B', var=[A,E,B],
        CPDs=[1.0, 0.0, 0.01, 0.99, 0.02, 0.98, 0.0, 1.0]);

#~ print F1
#~ print F3
#~ print F3*F1
#~ print sum((F3*F1).CPDs)
#~ print (F3*F1).marginal(R)
#~ 
#~ print F4

##print F4
##print F1
##F6=F4-F2
##print F6
##print F6/F1

##F5 = F3 - E
##F5.name = 'R'
##print F5
##F6 = F5 * F1
##F6.name = 'R,E'
##print F6
##F7 = F6/F5
##F7.name = 'E|R'
##print F7

##print F3-E
##print F3.ass2index(F3.index2ass(3))
##for i in range(F3.pcard[0]):
##    print i, F3.index2ass(i), F3.ass2index(F3.index2ass(i))

##C = Variable('Cancer', ['yes', 'no'])
##T = Variable('Test', ['pos', 'neg'])
##
##F11 = Factor(name='C', cons=[C], CPDs=[0.0001, 0.9999])
##F12 = Factor(name='T|C', cons=[T], cond=[C], CPDs=[0.9, 0.1, 0.2, 0.8])
##F14 = (F12 - C) * F11
##F14.name='C,T'
##F15 = F14/(F12 - C)
##F15.name='C|T'
##print F15

A = Variable('A', [1, 2, 3])
B = Variable('B', [1, 2])
C = Variable('C', [1, 2])
F1 = Factor(name='A,B', var=[A,B],
            CPDs=[0.5, 0.8, 0.1, 0, 0.3, 0.9])
F2 = Factor(name='B,C', var=[B,C],
            CPDs=[0.5, 0.7, 0.1, 0.2])        
# factor product
F3 = F1*F2
F3.name = 'A,B,C'
# factor reduction
F4 = F3.reduce(var=C, value=1)
F4.name = 'A,B'
print F4
