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
        for i in range(len(self.var)):            # actually forgot how it workes. However, tested
            self.pcard.append(
                reduce(lambda x, y: x*y, self.card[i:], 1) )
        self.pcard.append(1)    # for compatibility

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
        res+=str(self.sum())+'\n'
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

    def sum(self):
        return sum(self.CPDs)

"""
    def revert(self):

        given factor A,B|C,D computes C,D|A,B

        particular order of cons or cond may differ

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

class PD(Factor):
    """
    Class doc
    """
    var = None

    def __init__ (self, name='', full="", values=[], CPD=[]):
        """ Class initialiser """
        if full=="":
            full=name
        self.name = name
        if sum(CPD)!=1.0:
            raise AttributeError("Cannot build unconditioned factor: PD doesn't sum to 1")
        self.CPDs = CPD
        self.var = [Variable(full, values)]
        Factor.__init__(self, name=self.name, var=self.var, CPDs=self.CPDs)

class CPD(Factor):
    """ Class doc """
    cons=[]
    cond=[]

    def __init__(self, name='', full='', values=[], cond=[], CPD=[]):
        '''
        '''
        if full=="":
            full=name
        self.cons = Variable(full, values)
        self.cond = []
        for factor in cond:
            self.cond.append(factor.var[-1])
        Factor.__init__(self, name=name, var=self.cond+[self.cons], CPDs=CPD)
        if len(CPD)!=self.pcard[0]:
            raise AttributeError("Cannot build conditioned factor: CPD cardinality doesn't match")
        tempf = self.marginal(self.var[-1])
        for i in tempf.CPDs:
            if i!=1.0:
                raise AttributeError("Cannot build conditioned factor: CPD doesn't sum to 1")

    def __repr__(self):
        res=self.name+':\n'
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


# student example
D = BinaryVariable("Difficulty")
I = BinaryVariable("Intelligence")
G = Variable("Grade", [1, 2, 3])
S = BinaryVariable("SAT")
L = BinaryVariable("Letter")

F1 = Factor(name='D', var=[D], CPDs=[0.6, 0.4])
F2 = Factor(name='I', var=[I], CPDs=[0.7, 0.3])
F3 = Factor(name='G|I,D', var=[I, D, G], CPDs=[ 0.3,  0.4,  0.3,
                                                0.05, 0.25, 0.7,
                                                0.9,  0.08, 0.02,
                                                0.5,  0.3,  0.2])
F4 = Factor(name='S|I', var=[I,S], CPDs=[0.95, 0.05, 0.2, 0.8])
F5 = Factor(name='L|G', var=[G,L], CPDs=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01])

#~ print F3
#~ print F1*F2*F3*F4*F5

D = PD(name='D', values=[0,1], CPD=[0.6, 0.4], full="Difficulty")
I = PD(name='I', values=[0,1], CPD=[0.7, 0.3], full="Intelligence")
S =CPD(name='S|I', values=[0, 1], cond=[I], CPD=[0.95, 0.05, 0.2, 0.8], full="SAT")
G =CPD(name='G|I,D', values=[1, 2, 3], cond=[D,I], CPD=[0.3,  0.4,  0.3,
                                                        0.05, 0.25, 0.7,
                                                        0.9,  0.08, 0.02,
                                                        0.5,  0.3,  0.2],
                                                        full="Grade")
L =CPD(name='L|G', values=[0, 1], cond=[G], CPD=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01], full="Letter")
print D*I*S*G*L
