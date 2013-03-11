# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#--------------------------------------------
# Name:        PyPGM
# Author:      sejros
# Created:     15.10.2012
# Copyright:   (c) sejros 2012
# Licence:     GNU GPL
#--------------------------------------------

import networkx as nx
import matplotlib.pyplot as plt
try:
    import pygraphviz as pgv
except:
    pass

'''
Syntax:
    >>> D = Factor(name='D', values=[0,1], CPD=[0.6, 0.4], full="Difficulty")
    >>> I = Factor(name='I', values=[0,1], CPD=[0.7, 0.3], full="Intelligence")
    >>> G = Factor(name='G|I,D', values=[1, 2, 3], cond=[D,I], CPD=[0.3,  0.4,  0.3,
    ... 0.05, 0.25, 0.7,
    ... 0.9,  0.08, 0.02,
    ... 0.5,  0.3,  0.2],
    ... full="Grade")
    >>> S = Factor(name='S|I', values=[0, 1], cond=[I], CPD=[0.95, 0.05, 0.2, 0.8], full="SAT")
    >>> L = Factor(name='L|G', values=[0, 1], cond=[G], CPD=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01], full="Letter")
    >>> BN = Bayesian([D,I,S,G,L])
    >>> R = BN.joint().query2(query=[I], evidence={G:3, D:1})
    >>> R.CPDs
    [0.18918918918918917, 0.8108108108108109]


    >>> C = Variable('Cancer', ['yes', 'no'])
    >>> T = Variable('Test', ['pos', 'neg'])
    >>> F11 = Factor(name='C', var=[C], CPD=[0.0001, 0.9999])
    >>> F12 = Factor(name='T|C', var=[C,T], CPD=[0.9, 0.1, 0.2, 0.8])
    >>> F12.CPDs
    [0.9, 0.1, 0.2, 0.8]
    >>> F14 = (F12.marginal(C)) * F11
    >>> F14.CPDs
    [0.00011000000000000002, 9e-05, 1.09989, 0.89991]

'''

class Variable:
    '''
    Random variable is the basic building block fo Bayesian and Markov nets.
    Variable can be assigned to one of given set of values. This class
    represents discrete variable.

    Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake']);
            >>> B = Variable("Burglary",  [0, 1]);
            >>> A = Variable("Alarm", 3);
            >>> R = Variable("Radio", 2)

    Fields:
        name
            string representing the name of the variable. Assuming
            this is readble full name. This name is used for representing.
        value
            list of all possible values. Elements can be any type with defined
            equality operation
        card
            cardinality of the variable - number of all possible values

    '''
    name=""             # имя переменной
    value=[]            # значения переменной
    card = 0            # мощность переменной

    def __init__(self, name, a):
        '''
        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> print E.name
            Eartquake
            >>> E.card
            2
            >>> E.value
            ['still', 'shake']
            >>> E = Variable("Eartquake", 3)
            >>> E.value
            [0, 1, 2]
            >>> E.card
            3

        Arguments:
            name
                string representing the name of the variable. Assuming
                this is readble full name. This name is used for representing.
            a
                if list, represent full set of possible variable's values
                if int,  represent number of value (cardinality). Values in this
                case are integers from 0 to a-1.
        '''
        self.name = name
        self.value = []
        if  (type(a)==int):             # cardinality passed
            self.card = a
            for i in range(a):
                self.value.append(i)
        elif(type(a)==list):            # values list passed
            self.value = a
            self.card = len(a)

    def find_value(self, val):
        '''
        Given value finds its number among variable's values.
        If val is not in list of values, returns None

        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> E.find_value('still')
            0
            >>> E.find_value('shake')
            1
            >>> E = Variable("Eartquake", 3)
            >>> E.find_value(1)
            1
            >>> E.find_value(2)
            2

        Arguments:
            val
                one of the values of this variable
        '''
        for j in range(len(self.value)):
            if self.value[j]==val:
                return j

    def __abs__(self):
        '''
        Returns cardinality of the variable

        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> abs(E)
            2
            >>> E = Variable("Eartquake", 3)
            >>> abs(E)
            3
        '''
        return self.card

    def __repr__(self):
        '''
        Represent variable as a string (only name)

        Syntax:
            >>> E = Variable("Eartquake", ['still', 'shake'])
            >>> E
            Eartquake
            >>> E = Variable("Eartquake", 3)
            >>> E
            Eartquake
        '''
        return self.name

    def equal(self, term, value):
        '''
        Computes indicative equality function.
        Returns 0 if term!=value
        Returns 1 if term==value
        Returns None if term is not among self.value
        Syntax:
            >>> V = BinaryVariable("Sample")
            >>> V.equal(0, 0)
            1.0
            >>> V.equal(1, 0)
            0.0
            >>> V.equal(2, 0)
            >>> print V.equal(2, 0)
            None

        Arguments:
            term
                one of the values of this variable
            value
                value to be tested for equality with term
        '''
        if term in self.value:
            return float(term==value)
        return None

class BinaryVariable(Variable):
    '''
    Particular case of the variable with only two possible values: 0 and 1
    '''
    def __init__(self, name):
        '''
        Syntax:
            >>> E = BinaryVariable('coin flip')
            >>> E
            coin flip
            >>> abs(E)
            2
            >>> E.value
            [0, 1]
            >>> E.find_value(1)
            1

        Arguments:
            name
                string representing the name of the variable. Assuming
                this is readble full name. This name is used for representing.
        '''
        self.name = name
        self.value=[0, 1]
        self.card = 2

class Factor:
    '''
    Represents a factor - reflection from list of all possible assignments for
    a set of variables to a float number. This can be interpreted as a joint
    probability distribution, conditional probability distribution (CPD) or a
    unnormalized measure.

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

    Fields:
        name
            the name of the factor. This name is meant to be informal, for ex.
            "C|A,B" - means that the factro represents conditional probability
            distribution over variable C given variables A and B.
        var
            list of all variables included in the factor. Order of this list
            matters for assignment, cardinlity and factor's values computing.
            When creating a factor , variables are put in this list as they
            were listed by user, first conditioning variables, then listed
            using var argument, then induced variable if any (see
            Factor.__init__() for details).
        CPDs
            list of all fator's values. Length of this list should be equal
            to the product of all included variables' cardinalities.
        card
            list of included variable's cardinalities in order with respect
            to var list.
        pcard
            list of poduct-cumulative cardinalities computed out of card list.
        cons
            if factor introduces new variable (see Factor.__init__() for
            details), it is stored in this field
        cond
            list of all conditioning variables. This list is always duplicating
            some part of var list.
        parents
            list of all factors, that are meant to be conditioning this, or are
            parents to this according to bayesian net.
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
        '''

        Syntax:
            It is possible to define factors in two ways: with or without
            defining variables.

            Explicit way to define variables and factors use this form:
                # first, we difine all variables in our model
                >>> C = Variable('Cancer', ['yes', 'no'])
                >>> T = Variable('Test', ['pos', 'neg'])

                # after that, we form factors using this variables
                >>> F11 = Factor(name='C', var=[C], CPD=[0.0001, 0.9999])
                >>> F12 = Factor(name='T', var=[C,T], CPD=[0.9, 0.1, 0.2, 0.8])
                >>> F11.var
                [Cancer]
                >>> F11.CPDs
                [0.0001, 0.9999]
                >>> F11.card
                [2]
                >>> F11.pcard
                [2, 1]
                >>> F11.cond
                []
                >>> F11.name
                'C'

            Implicit way uses slightly different form of the constructor to
            define factors at the first place, scince variables are never needed
            outside factors' definitions:
                >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
                >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])
                >>> C.name
                'C'
                >>> C.card
                [2]
                >>> C.pcard
                [2, 1]
                >>> C.cond
                []
                >>> C.parents
                []
                >>> C.CPDs
                [0.99, 0.01]
                >>> C.var
                [Cancer]
                >>> C.cons
                Cancer

                >>> T.name
                'T'
                >>> T.card
                [2, 2]
                >>> T.pcard
                [4, 2, 1]
                >>> T.cond
                [Cancer]
                >>> T.cons
                Test
                >>> T.var
                [Cancer, Test]
                >>> T.CPDs
                [0.2, 0.8, 0.9, 0.1]

            In this form, every factor's definition induces implicit variable,
            placed in var list of the factor.

        Arguments:
            name
                the name of the factor. This name is meant to be informal, for ex.
                "C|A,B" - means that the factro represents conditional probability
                distribution over variable C given variables A and B.
            full
                if factor introduces new variable, this would be it's name. If
                empty, using name argument instead
            values
                if factor introduces new variable, this would be it's value
                list.
            cond
                list of factors, conditioning this.
            CPD
                list of all fator's values. Length of this list should be equal
                to the product of all included variables' cardinalities. If not,
                generating exception:
                    >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9])
                    Traceback (most recent call last):
                      File "<stdin>", line 1, in <module>
                      File "factors.py", line 253, in __init__
                        cond
                    AttributeError: Cannot build conditioned factor: CPD cardinality doesn't match

            var
                list of all variables in the scope of the factor

        '''
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

    def map(self, lst):
        '''
        bulds a map: hash table,
        where keys - indecies of THIS factor's assingment list
        and values - indecies of given var list assignment, corresponding to key

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> T.map(C.var)
            {0: 0}

        Arguments:
            lst
                list of variables to lookup in this var list

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

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> m = T.map(C.var)
            >>> T.ass(0, m)
            ['no']
            >>> T.ass(1, m)
            ['no']
            >>> T.ass(2, m)
            ['yes']
            >>> T.ass(3, m)
            ['yes']
            >>> T.ass(4, m)
            ['no']
            >>> T.ass(-1, m)
            ['yes']

        Arguments:
            n
                number of assignment. Shoul be within 0..n, where n -
                cardinality of a factor (Factor.pcard[0]-1). But if given out of
                boundaries - no exceptions, computing modulo.
            mp

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
        in order according to factor.var
        computes a number of this asignment

        this number is always in range [0..Factor.pcard[0]-1]

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> C.ass2index(['no'])
            0
            >>> C.ass2index(['yes'])
            1
            >>> T.ass2index(['yes', 'pos'])
            2
            >>> T.ass2index(['yes', 'neg'])
            3
            >>> T.ass2index(['no', 'neg'])
            1
            >>> T.ass2index(['no', 'pos'])
            0
            >>> T.ass2index(['n', 'pos'])
            Traceback (most recent call last):
              File "/usr/lib/python2.7/doctest.py", line 1289, in __run
                compileflags, 1) in test.globs
              File "<doctest __main__.Factor.ass2index[8]>", line 1, in <module>
                T.ass2index(['n', 'pos'])
              File "factors.py", line 448, in ass2index
                res+=v.find_value(assignment[j])*self.pcard[j+1]
            TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'

        Arguments:
            assingment
                list of values in order according to Factor.var list.

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
        it is equal to (index mod factor.pcard[0]).
        If assignment is not corect, raises an exception.

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> [{x: T.index2ass(x-1)} for x in range(6)]
            [{0: ['yes', 'neg']}, {1: ['no', 'pos']}, {2: ['no', 'neg']}, {3: ['yes', 'pos']}, {4: ['yes', 'neg']}, {5: ['no', 'pos']}]

        Arguments:
            index
                number of assignment. Shoul be within 0..n, where n -
                cardinality of a factor (Factor.pcard[0]-1). But if given out of
                boundaries - no exceptions, computing modulo.

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
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> P = T*C
            >>> P.CPDs
            [0.198, 0.792, 0.009000000000000001, 0.001]
            >>> P.var
            [Cancer, Test]
            >>> P.CPDs[0]
            0.198
            >>> P.name
            'Product'
        '''
        if other==None:         # for compatibility
            return self
        res=Factor(name='Product',
                    var=sorted(list(set(self.var) | set(other.var)), cmp=lambda x,y: cmp(x.name, y.name)),
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
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> M = T.marginal(C.var[-1])
            >>> M.name
            'Marginal factor'
            >>> M.var
            [Test]
            >>> M.CPDs
            [1.1, 0.9]
            >>> M = T.marginal(T.var[-1])
            >>> M.name
            'Marginal factor'
            >>> M.var
            [Cancer]
            >>> M.CPDs
            [1.0, 1.0]
        '''
        if not var in self.var:
            raise AttributeError("Unable to marginalize: variable is missing")

        res = Factor('Marginal factor',
                        var = sorted(list(set(self.var) - set([var])), cmp=lambda x,y: cmp(x.name, y.name)),
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
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.reduce(var=C.var[-1], value='yes')
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.CPDs
            [0.9, 0.1]
            >>> R = T.reduce(var=T.var[-1], value='pos')
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.CPDs
            [0.18181818181818182, 0.8181818181818181]
        '''
        return self._reduce2(var, value).norm()

    def _reduce1(self, var=None, value=''):
        if not var in self.var:
            raise AttributeError()

        res = Factor(name='Reduced',
                        var = sorted(list(set(self.var) - set([var])) , cmp=lambda x,y: cmp(x.name, y.name)),
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

    def _reduce2(self, var=None, value=''):
        if not var in self.var:
            raise AttributeError()

        res = Factor(name='Reduced',
                        var = self.var,
                        CPD=[])
        mapX = self.map(res.var)
        mapY = self.map([var])
        for i in range(res.pcard[0]):
            res.CPDs.append(0)
        for i in range(len(self.CPDs)):
            assX = self.ass(i, mapX)
            assY = self.ass(i, mapY)
            i1 = res.ass2index(assX)
            res.CPDs[i1] = self.CPDs[i] * var.equal(assY[0], value)
        return res.marginal(var)

    def __div__(self, other=None):
        '''
        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> D = (T*C)/C
            >>> D.name
            'Conditional'
            >>> D.var
            [Cancer, Test]
            >>> D.cond
            [Cancer]
            >>> D.CPDs
            [0.2, 0.8, 0.9000000000000001, 0.1]

        '''
        var = other.var[-1]
        if not var in self.var:
            raise AttributeError()

        res = Factor(name='Conditional',
                        var = sorted(list(set(self.var)-set(other.var)), cmp=lambda x,y: cmp(x.name, y.name)),
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
        '''
        returns factor's cardianlity: product of all variables' cardinalities

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> abs(C)
            2
            >>> abs(T)
            4
        '''
        return self.pcard[0]

    def sum(self):
        '''
        returns sum of all factor's values

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> T.sum()
            2.0
            >>> C.sum()
            1.0
        '''
        return sum(self.CPDs)

    def __str__(self):
        '''

        '''
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

    def __repr__(self):
        '''

        '''
        return self.name

    def joint(self):
        '''
        computes joint distribution out of the factor IF it has any conditions
        i. e. computes P(A,B,C) out of P(A,B|C)

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.joint()
            >>> R.name
            'Product'
            >>> R.var
            [Cancer, Test]
            >>> R.CPDs
            [0.198, 0.792, 0.009000000000000001, 0.001]
        '''
        res = self;
        for parent in self.parents:
            res = res * parent.joint()
        return res

    def uncond(self):
        '''
        computes P(A,B) out of P(A,B|C,D)

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.uncond()
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.CPDs
            [0.20700000000000002, 0.793]
        '''
        res = self.joint()
        for fact in self.parents:
            res = res.marginal(fact.uncond().var[-1])
        return res

    def query(self, query=[], evidence=[]):
        '''


        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.query(query=[T], evidence=[C])
            >>> R.name
            'Conditional'
            >>> R.var
            [Cancer, Test]
            >>> R.CPDs
            [0.2, 0.8, 0.9000000000000001, 0.1]
            >>> R.cond
            [Cancer]
            >>> R = T.query(query=[C], evidence=[T])
            >>> R.name
            'Conditional'
            >>> R.var
            [Test, Cancer]
            >>> R.CPDs
            [0.9565217391304347, 0.9987389659520807, 0.043478260869565216, 0.0012610340479192938]
            >>> R.cond
            [Test]
            >>> R = T.query(query=[C], evidence=[])
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cond
            []
            >>> R.CPDs
            [0.99, 0.010000000000000002]
        '''
        res = self.joint()
        q = []
        for qu in query:
            q.append(qu.var[-1])
        e = []
        for qu in evidence:
            e.append(qu.var[-1])
        hidden=set(res.var) - set(q) - set(e)
        for h in hidden:
            res = res.marginal(h)
        for e in evidence:
            res = res / e.uncond()
        return res

    def query2(self, query=[], evidence={}):
        '''


        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.query2(query=[T], evidence={C: 'yes'})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.cond
            []
            >>> R.CPDs
            [0.9, 0.09999999999999999]
            >>> R = T.query2(query=[T], evidence={C: 'no'})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.cond
            []
            >>> R.CPDs
            [0.2, 0.8]
            >>> R = T.query2(query=[C], evidence={T: 'pos'})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cond
            []
            >>> R.CPDs
            [0.9565217391304348, 0.04347826086956522]
            >>> R = T.query2(query=[C], evidence={})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cond
            []
            >>> R.CPDs
            [0.99, 0.010000000000000002]
        '''
        # TODO: furthermore: local inference
        res = self.joint()
        q = []
        for qu in query:
            q.append(qu.var[-1])
        e = {}
        for ev in evidence.keys():
            e[ev.var[-1]] = evidence[ev]
        hidden=set(res.var) - set(q) - set(e)
        for h in hidden:
            res = res.marginal(h)
        for ev in e.keys():
            res = res.reduce(var=ev, value=e[ev]).norm()
        return res

    def norm(self):
        '''
        normalizes values of the factorto make all valies sum to 1.0
        Warning: mutates the factor!
        If factor sums to 0, does nothing

        Syntax:
            >>> C = Factor(name='C', full="Cancer", values=["no", "yes"], CPD=[0.99, 0.01])
            >>> T = Factor(name='T', full="Test", values=["pos", "neg"], cond=[C], CPD=[0.2, 0.8, 0.9, 0.1])

            >>> C = C.norm()
            >>> C.CPDs
            [0.99, 0.01]
            >>> T.CPDs
            [0.2, 0.8, 0.9, 0.1]
            >>> T = T.norm()
            >>> T.CPDs
            [0.1, 0.4, 0.45, 0.05]
            >>> A = Factor(name='null', values=[0,1], CPD=[0.0, 0.0])
            >>> A = A.norm()
            >>> A.CPDs
            [0.0, 0.0]

        '''
        s = self.sum()
        if s != 0:
            for i in range(len(self.CPDs)):
                self.CPDs[i] = self.CPDs[i] / s
        return self

class Bayesian():
    '''


    Syntax:


    Fields:

    '''
    factors=[]

    def __init__(self, factors):
        '''


        Syntax:


        Arguments:

        '''
        self.graph = nx.DiGraph()
        self.factors = factors
        for f in self.factors:
            self.graph.add_node(f.var[-1])
            for p in f.parents:
                self.graph.add_edge(p.var[-1], f.var[-1])

    def joint(self):
        '''


        Syntax:


        Arguments:

        '''
        res = None
        for fact in self.factors:
            res = fact*res
        return res

    def draw(self):
        '''


        Syntax:


        Arguments:

        '''
        pos = nx.pygraphviz_layout(self.graph, prog='dot')
        nx.draw(self.graph, pos, node_shape='D')

# TODO: test on larger nets with operands of marginal, reduce, __mul__, __div__ including more than one cons var
# TODO: doctest everything

if __name__ == "__main__":
    import doctest
##    doctest.testmod(verbose=False)
    doctest.testmod(verbose=True)
