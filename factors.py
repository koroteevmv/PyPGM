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
    card = 0            # мощность переменной

    def __init__(self, name, a):
        self.name = name
        self.childs=[]
        if  (type(a)==int):             # cardinality passed
            self.card = a
            for i in range(a):
                self.value.append(i)
        elif(type(a)==list):            # values list passed
            self.value = a
            self.card = len(a)

    def find_value(self, val):
        '''
        given value finds its number among variable's values
        '''
        for j in range(len(self.value)):
            if self.value[j]==val:
                return j
    def __abs__(self):
        return self.card

    def __repr__(self):
        return self.name

class BinaryVariable(Variable):
    def __init__(self, name):
        self.name = name
        self.value=[0, 1]
        self.card = 2

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
    cons=None           # переменная-следствие (не в случае общей вероятности)
    cond=[]             # переменные-условия
    parents=[]          # факторы-родители
    name=''             # имя фактора
    def __init__(self, name='', full='', values=[], cond=[], CPD=[], var=[]):
        self.CPDs = CPD
        self.pcard=[]
        self.name=name
        self.cond = []
        self.parents = []
        self.cons = None
        for factor in cond:
            self.cond.append(factor.var[-1])
            self.parents.append(factor)
        if len(values)>0:
            if full=="":
                full=name
            self.cons = Variable(full, values)
            self.var=self.cond+var+[self.cons]
        else:
            self.var=self.cond+var

        self.card=[]
        for i in self.var:
            self.card.append(i.card)
        # counts cumulative cardinality
        for i in range(len(self.var)):            # actually forgot how it workes. However, tested
            self.pcard.append(
                reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)    # for compatibility
        if len(CPD)>0:
            if len(CPD)!=self.pcard[0]:
                raise AttributeError("Cannot build conditioned factor: CPD cardinality doesn't match")
            tempf = self.marginal(self.var[-1])
            # TODO: maybe delete this check (for unnormalized factors)
            for i in tempf.CPDs:
                if i!=1.0:
                    raise AttributeError("Cannot build conditioned factor: CPD doesn't sum to 1")

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
        if other==None:         # for compatibility
            return self
        res=Factor(name='Product',
                    var=list(set(self.var) | set(other.var)),
                    CPD=[])
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
            raise AttributeError("Unable to marginalize: variable is missing")

        res = Factor('Marginal factor',
                        var = list(set(self.var) - set([var])),
                        CPD=[])
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
        F(A,B)/F(B) = F(A)

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
                        CPD=[])
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

    def __div__(self, other=None):
        '''
        '''
        var = other.var[-1]
        if not var in self.var:
            raise AttributeError()

        res = Factor(name='Conditional',
                        var = list(set(self.var)-set(other.var)),
                        cond = [other],
                        CPD=[])
        mapY = self.map([var])
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        for i in range(len(self.CPDs)):
            assY = self.ass(i, mapY)
            res.CPDs[i] = self.CPDs[i]/other.CPDs[other.ass2index(assY)]
        return res

    def __abs__(self):
        return self.pcard[0]

    def sum(self):
        return sum(self.CPDs)

    def __repr__(self):
        res=self.name+':\n'
        res+="\tScope:\n"
        for i in self.var:
            res+='\t\t'+i.name+'\n'
        if self.cons!=None:
            res+="\tVariable:\n"
            res+='\t\t'+self.cons.name+'\n'
        res+="\tConditions:\n"
        for i in self.cond:
            res+='\t\t'+i.name+'\n'
        res+="\tCPDs:\n"
        for j in range(len(self.CPDs)):
            res+='\t\t'+str(j)+'->'
            for i in self.index2ass(j):
                res+=str(i)+", "
            res+=str(self.CPDs[j])+'\n';
        res+=str(self.sum())+'\n'
        return res

    def joint(self):
        res = self;
        for parent in self.parents:
            res = res * parent.joint()
        return res

    def uncond(self):
        res = self.joint()
        for fact in self.parents:
            res = res.marginal(fact.uncond().var[-1])
        return res

    def query(self, query=[], evidence=[]):
        res = self.joint()
        q = []
        for qu in query:
            q.append(qu.var[-1])
        e = []
        for qu in evidence:
            q.append(qu.var[-1])
        hidden=set(res.var) - set(q) - set(e)
        for h in hidden:
            res = res.marginal(h)
        for e in evidence:
            res = res / e.uncond()
        return res

class Bayesian:
    # TODO: maybe delete this class
    '''
    '''
    factors=[]
    def __init__(self, factors):
        self.factors = factors
    def joint(self):
        res = None
        for fact in self.factors:
            res = fact*res
        return res
    def query(self, query=[], evidence=[]):
        res = self.joint()
        q = []
        for qu in query:
            q.append(qu.var[-1])
        e = []
        for qu in evidence:
            q.append(qu.var[-1])
        hidden=set(res.var) - set(q) - set(e)
        for h in hidden:
            res = res.marginal(h)
        for e in evidence:
            res = res / e.uncond()
        return res


# cancer example
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

C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])
print T
print T.joint()
print T.uncond()
print T.query(query=[C], evidence=[T])
print T.joint() / T.uncond()


# student example
D = BinaryVariable("Difficulty")
I = BinaryVariable("Intelligence")
G = Variable("Grade", [1, 2, 3])
S = BinaryVariable("SAT")
L = BinaryVariable("Letter")

F1 = Factor(name='D', var=[D], CPD=[0.6, 0.4])
F2 = Factor(name='I', var=[I], CPD=[0.7, 0.3])
F3 = Factor(name='G|I,D', var=[I, D, G], CPD=[ 0.3,  0.4,  0.3,
                                                0.05, 0.25, 0.7,
                                                0.9,  0.08, 0.02,
                                                0.5,  0.3,  0.2])
F4 = Factor(name='S|I', var=[I,S], CPD=[0.95, 0.05, 0.2, 0.8])
F5 = Factor(name='L|G', var=[G,L], CPD=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01])

D = Factor(name='D', values=[0,1], CPD=[0.6, 0.4], full="Difficulty")
I = Factor(name='I', values=[0,1], CPD=[0.7, 0.3], full="Intelligence")
G = Factor(name='G|I,D', values=[1, 2, 3], cond=[D,I], CPD=[0.3,  0.4,  0.3,
                                                        0.05, 0.25, 0.7,
                                                        0.9,  0.08, 0.02,
                                                        0.5,  0.3,  0.2],
                                                        full="Grade")
S = Factor(name='S|I', values=[0, 1], cond=[I], CPD=[0.95, 0.05, 0.2, 0.8], full="SAT")
L = Factor(name='L|G', values=[0, 1], cond=[G], CPD=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01], full="Letter")

BN = Bayesian([D,I,S,G,L])

##print G.query(query=[G], evidence=[D])
# TODO: test on larger nets with operands of marginal, reduce, __mul__, __div__ including more than one cons var
# TODO: doctest everything
# TODO: furthermore: local inference
