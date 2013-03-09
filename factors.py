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
import pygraphviz as pgv

'''

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
    Represents a factor - 
    
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
            
        var
            
        CPDs
            
        card
            
        pcard
            
        cons
            
        cond
            
        parents
            
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
            

        Arguments:
            
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
            

        Arguments:
            
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
            

        Arguments:
            
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
        
        Syntax:
            

        Arguments:
            
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
        
        Syntax:
            

        Arguments:
            
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
        
        Syntax:
            

        Arguments:
            
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
        
        Syntax:
            

        Arguments:
            
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
        
        Syntax:
            

        Arguments:
            
        '''
        return self._reduce2(var, value).norm()

    def _reduce1(self, var=None, value=''):
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

    def _reduce2(self, var=None, value=''):
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
            res.CPDs[i1] = self.CPDs[i] * float(assY[0]==value)
        return res.marginal(var)

    def __div__(self, other=None):
        '''
        
        
        Syntax:
            

        Arguments:
            
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
        '''
        returns factor's cardianlity: product of all variables' cardinalities
        
        Syntax:
            

        Arguments:
            
        '''
        return self.pcard[0]

    def sum(self):
        '''
        returns sum of all factor's values
        
        Syntax:
            

        Arguments:
            
        '''
        return sum(self.CPDs)

    def __str__(self):
        '''
        
        
        Syntax:
            

        Arguments:
            
        '''
        return self.name

    def __repr__(self):
        '''
        
        
        Syntax:
            

        Arguments:
            
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

    def joint(self):
        '''
        computes joint distribution out of the factor IF it has any conditions
        i. e. computes P(A,B,C) out of P(A,B|C)
        
        Syntax:
            

        Arguments:
            
        '''
        res = self;
        for parent in self.parents:
            res = res * parent.joint()
        return res

    def uncond(self):
        '''
        computes P(A,B) out of P(A,B|C,D)
        
        Syntax:
            

        Arguments:
            
        '''
        res = self.joint()
        for fact in self.parents:
            res = res.marginal(fact.uncond().var[-1])
        return res

    def query(self, query=[], evidence=[]):
        '''
        
        
        Syntax:
            

        Arguments:
            
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
            

        Arguments:
            
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
        
        Syntax:
            

        Arguments:
            
        '''
        s = self.sum()
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
#    doctest.testmod(verbose=False)
    doctest.testmod(verbose=True)
