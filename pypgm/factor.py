'''
    Represents a factor - reflection from list of all possible assignments for
    a set of variables to a float number. This can be interpreted as a joint
    probability distribution, conditional probability distribution (cpd) or a
    unnormalized measure.
'''

import unittest
from pypgm.variable import Variable

class Factor(object):
    '''
    Syntax:

            E = Variable("Eartquake", ['still', 'shake']);
            B = Variable("Burglary",  ['safe', 'robbed']);
            A = Variable("Alarm", ['quiet', 'loud']);
            R = Variable("Radio", ['off', 'on'])

            F1 = Factor(name='E', var=[E],       cpd=[0.999, 0.001]);
            F2 = Factor(name='B', var=[B],       cpd=[0.99, 0.01]);
            F3 = Factor(name='R|E', var=[R,E],   cpd=[0.9, 0.2, 0.1, 0.8]);
            F4 = Factor(name='A|E,B', var=[A,E,B],
                        cpd=[1.0, 0.0, 0.01, 0.99, 0.02, 0.98, 0.0, 1.0]);

    Fields:
        name
            the name of the factor. This name is meant to be informal, for ex.
            "C|A,B" - means that the factor represents conditional probability
            distribution over variable C given variables A and B.
        var
            list of all variables included in the factor. Order of this list
            matters for assignment, cardinlity and factor's values computing.
            When creating a factor , variables are put in this list as they
            were listed by user, first conditioning variables, then listed
            using var argument, then induced variable if any (see
            Factor.__init__() for details).
        cpd
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

    def __init__(self, name='',
                        values=None,
                        cond=None,
                        cpd=None,
                        var=None):
        '''
        Syntax:
            It is possible to define factors in two ways: with or without
            defining variables.

            Explicit way to define variables and factors use this form:
                # first, we difine all variables in our model
                >>> C = Variable('Cancer', ['yes', 'no'])
                >>> T = Variable('Test', ['pos', 'neg'])

                # after that, we form factors using this variables
                >>> F11 = Factor(name='C', var=[C], cpd=[0.0001, 0.9999])
                >>> F12 = Factor(name='T', var=[C,T], cpd=[0.9, 0.1, 0.2, 0.8])
                >>> F11.var
                [Cancer]
                >>> F11.cpd
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
            define factors at the first place, since variables are never needed
            outside factors' definitions:
                >>> C = Factor(name='Cancer', values=["no", "yes"],
                ...             cpd=[0.99, 0.01])
                >>> T = Factor(name='Test', values=["pos", "neg"],
                ...             cond=[C], cpd=[0.2, 0.8, 0.9, 0.1])
                >>> C.name
                'Cancer'
                >>> C.card
                [2]
                >>> C.pcard
                [2, 1]
                >>> C.cond
                []
                >>> C.parents
                []
                >>> C.cpd
                [0.99, 0.01]
                >>> C.var
                [Cancer]
                >>> C.cons
                Cancer

                >>> T.name
                'Test'
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
                >>> T.cpd
                [0.2, 0.8, 0.9, 0.1]

            In this form, every factor's definition induces implicit variable,
            placed in var list of the factor.

        Arguments:
            name
                the name of the factor. This name is meant to be informal,
                for ex. "C|A,B" - means that the factro represents conditional
                probability distribution over variable C given variables
                A and B.
            values
                if factor introduces new variable, this would be it's value
                list.
            cond
                list of factors, conditioning this.
            cpd
                list of all fator's values. Length of this list should be equal
                to the product of all included variables' cardinalities.
                If not, generating exception.
            var
                list of all variables in the scope of the factor

        '''
        if not values: values = []
        if not cond: cond = []
        if not cpd: cpd = []
        if not var: var = []

        self.cpd = cpd              # условные вероятности
        self.name = name            # имя фактора
        self.cons = None            # основная факторная переменная (не в случае общей вероятности)
        self.pcard = []             # кумулятивная общая разрядность
        self.cond = []              # переменные-условия
        self.parents = []           # факторы-родители
        self.var = []               # переменные, входящие в фактор
        self.card = []              # вектор разрядности переменных
        self._uncond_cache = None

        for factor in cond:
            self.cond.append(factor.var[-1])
            self.parents.append(factor)

        if len(values) > 0:
            full = name
            self.cons = Variable(full, values)
            self.var = self.cond+var+[self.cons]
        else:
            self.var = self.cond+var

        for i in self.var:
            self.card.append(i.card)

        # counts cumulative cardinality
        for i in range(len(self.var)):
            self.pcard.append(reduce(lambda x, y: x*y, self.card[i:], 1))
        self.pcard.append(1)    # for compatibility

        if len(cpd) > 0:
            if len(cpd) != self.pcard[0]:
                string = "Cannot build conditioned factor: " + \
                        "cpd cardinality doesn't match"
                raise AttributeError(string)

    def _map(self, lst):
        '''
        bulds a map: hash table,
        where keys - indecies of THIS factor's assingment list
        and values - indecies of given var list assignment, corresponding to key

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> T._map(C.var)
            {0: 0}

        Arguments:
            lst
                list of variables to lookup in this var list

        '''
        res = {}
        for i in range(len(self.var)):
            for j in range(len(lst)):
                if self.var[i] == lst[j]:
                    res[i] = j
        return res

    def _ass(self, number, mapping):
        '''
        given number of assignment, computes
        this assignment of this factor
        and returns it rearranged according to map given

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> m = T._map(C.var)
            >>> T._ass(0, m)
            ['no']
            >>> T._ass(1, m)
            ['no']
            >>> T._ass(2, m)
            ['yes']
            >>> T._ass(3, m)
            ['yes']
            >>> T._ass(4, m)
            ['no']
            >>> T._ass(-1, m)
            ['yes']

        Arguments:
            number
                number of assignment. Should be within 0..n, where n -
                cardinality of a factor (Factor.pcard[0]-1). But if given out of
                boundaries - no exceptions, computing modulo.
            mapping

        '''
        ass = self._index2ass(number)
        res = []
        for i in range(len(mapping)):
            res.append(None)
        for i in range(len(ass)):
            if i in mapping.keys():
                mapping[i]
                ass[i]
                res[mapping[i]] = ass[i]
        return res

    def _ass2index(self, assignment):
        '''
        given a list of values of factor's vars
        in order according to factor.var
        computes a number of this asignment

        this number is always in range [0..Factor.pcard[0]-1]

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> C._ass2index(['no'])
            0
            >>> C._ass2index(['yes'])
            1
            >>> T._ass2index(['yes', 'pos'])
            2
            >>> T._ass2index(['yes', 'neg'])
            3
            >>> T._ass2index(['no', 'neg'])
            1
            >>> T._ass2index(['no', 'pos'])
            0

        Arguments:
            assingment
                list of values in order according to Factor.var list.

        '''
        j = 0
        res = 0
        for i in self.var:
            res += i.find_value(assignment[j])*self.pcard[j+1]
            j += 1
        return res

    def _index2ass(self, index):
        '''
        given a number computes an assignment -
        list of variables' values in order of factor.var

        if given index is greater than factor.pcard[0]-1
        it is equal to (index mod factor.pcard[0]).
        If assignment is not corect, raises an exception.

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> [{x: T._index2ass(x-1)} for x in range(6)][0]
            {0: ['yes', 'neg']}

        Arguments:
            index
                number of assignment. Shoul be within 0..n, where n -
                cardinality of a factor (Factor.pcard[0]-1). But if given out of
                boundaries - no exceptions, computing modulo.

        '''
        res = []
        for j in range(len(self.var)):
            res.append(self.var[-j-1].value[index % self.card[-j-1]])
            index = (index - (index % self.card[-j-1])) / self.card[-j-1]
        return res[::-1]

    def __mul__(self, other):
        '''
        computes product of factors
        F(A,C)*F(C,B) = F(A,B,C)

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> P = T*C
            >>> P.cpd
            [0.198, 0.792, 0.009000000000000001, 0.001]
            >>> P.var
            [Cancer, Test]
            >>> P.cpd[0]
            0.198
            >>> P.name
            'Product'
        '''
        if other == None:         # for compatibility
            return self
##        print "Product"
##        print self.var, self.cond
##        print other.var, other.cond
##        print (set(self.var) | set(other.var)) - set(other.cond)
        res = Factor(name='Product',
                    var=sorted(list((set(self.var) | set(other.var)) - set(other.cond)),
                            cmp=lambda x, y: cmp(x.name, y.name)),
                    cpd=[], cond=other.parents)
        map_s = res._map(self.var)
        map_o = res._map(other.var)
        res.cpd = []
        for i in range(res.pcard[0]):
            res.cpd.append(0)
        for i in range(res.pcard[0]):
            self_ind = self._ass2index(res._ass(i, map_s))
            other_ind = other._ass2index(res._ass(i, map_o))
            res.cpd[i] = (self.cpd[self_ind] * other.cpd[other_ind])
        return res

    def marginal(self, var=None):
        '''
        perfoms a factor marginalization
        F(A,B,C)-B = F(A,C)

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> M = T.marginal(C.var[-1])
            >>> M.name
            'Marginal factor'
            >>> M.var
            [Test]
            >>> M.cpd
            [1.1, 0.9]
            >>> M = T.marginal(T.var[-1])
            >>> M.name
            'Marginal factor'
            >>> M.var
            [Cancer]
            >>> M.cpd
            [1.0, 1.0]
        '''
        if not var in self.var:
            raise AttributeError("Unable to marginalize: variable is missing")

        res = Factor('Marginal factor',
                        var=sorted(list(set(self.var) - set([var])),
                                        cmp=lambda x, y: cmp(x.name, y.name)),
                        cpd=[])
        map_x = self._map(res.var)
        for i in range(res.pcard[0]):
            res.cpd.append(0)
        for i in range(len(self.cpd)):
            ind = res._ass2index(self._ass(i, map_x))
            res.cpd[ind] += self.cpd[i]
        return res

    def reduce(self, var=None, value=''):
        '''
        computes a factor reduction
        F(A,B)/F(B) = F(A)

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.reduce(var=C.var[-1], value='yes')
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.cpd
            [0.9, 0.1]
            >>> R = T.reduce(var=T.var[-1], value='pos')
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cpd
            [0.18181818181818182, 0.8181818181818181]
        '''
        return self._reduce2(var=var, value=value)._norm()

    def _reduce1(self, var=None, value=''):
        '''
        Syntax:

        Arguments:

        '''
        if not var in self.var:
            raise AttributeError()

        res = Factor(name='Reduced',
                        var=sorted(list(set(self.var) - set([var])),
                                        cmp=lambda x, y: cmp(x.name, y.name)),
                        cpd=[])
        map_x = self._map(res.var)
        map_y = self._map([var])
        for i in range(res.pcard[0]):
            res.cpd.append(0)
        for i in range(len(self.cpd)):
            ass_x = self._ass(i, map_x)
            ass_y = self._ass(i, map_y)
            ind = res._ass2index(ass_x)
            if ass_y[0] == value:
                res.cpd[ind] = self.cpd[i]
        return res

    def _reduce2(self, var=None, value=''):
        '''
        Syntax:

        Arguments:

        '''
        if not var in self.var:
            raise AttributeError()

        res = Factor(name='Reduced',
                        var=self.var,
                        cpd=[])
        map_x = self._map(res.var)
        map_y = self._map([var])
        for i in range(res.pcard[0]):
            res.cpd.append(0)
        for i in range(len(self.cpd)):
            ass_x = self._ass(i, map_x)
            ass_y = self._ass(i, map_y)
            ind = res._ass2index(ass_x)
            res.cpd[ind] = self.cpd[i] * var.equal(ass_y[0], value)
        return res.marginal(var)

    def __div__(self, other=None):
        '''
        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> D = (T*C)/C
            >>> D.name
            'Conditional'
            >>> D.var
            [Cancer, Test]
            >>> D.cond
            [Cancer]
            >>> D.cpd[0]
            0.2

        '''
        t = list(set(other.var) - set(other.cond))
        var = t[-1]
        if not var in self.var:
            raise AttributeError()

##        print "------------------------"
##        print self.var, t
##        print "Initial division"
##        print self

        res = Factor(name='Conditional',
                        var=list(set(self.var) - set(t)),
                        cond=list(set([other]) | set(self.parents)),
                        cpd=[])

        for i in range(res.pcard[0]):
            res.cpd.append(0)

        temp = Factor(var=t)
        for i in range(temp.pcard[0]):
            temp.cpd.append(0)

        map_to_temp = self._map(temp.var)

        for i in range(self.pcard[0]):
            temp_ass = self._ass(i, map_to_temp)
            temp_index = temp._ass2index(temp_ass)
            temp.cpd[temp_index] += self.cpd[i]

##        print "Temp factor"
##        print temp

        map_to_res = self._map(res.var)
        map_from_res = res._map(self.var)
##        print map_to_res, map_from_res

        for i in range(self.pcard[0]):
            temp_ass = self._ass(i, map_to_temp)
            temp_index = temp._ass2index(temp_ass)
            res_ass = self._ass(i, map_to_res)
            j = res._ass2index(res_ass)
            res.cpd[j] = self.cpd[i] / temp.cpd[temp_index]

##        print "------------------------"

        return res

    def __abs__(self):
        '''
        returns factor's cardinality: product of all variables' cardinalities

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

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
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> T.sum()
            2.0
            >>> C.sum()
            1.0
        '''
        return sum(self.cpd)

    def __str__(self):
        '''

        '''
        res = self.name+':\n'
        res += "\tScope:\n"
        for i in self.var:
            res += '\t\t'+i.name+'\n'
        if self.cons != None:
            res += "\tVariable:\n"
            res += '\t\t'+self.cons.name+'\n'
        res += "\tConditions:\n"
        for i in self.cond:
            res += '\t\t'+i.name+'\n'
        res += "\tcpd:\n"
        for j in range(len(self.cpd)):
            res += '\t\t'+str(j)+'->'
            for i in self._index2ass(j):
                res += str(i)+", "
            res += str(self.cpd[j])+'\n'
        res += str(self.sum())+'\n'
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
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.joint()
            >>> R.name
            'Product'
            >>> R.var
            [Cancer, Test]
            >>> R.cpd
            [0.198, 0.792, 0.009000000000000001, 0.001]
        '''
        res = self
        for parent in self.parents:
            res = res * parent.joint()
        return res

    def uncond(self, depth=-1):
        '''
        computes P(A,B) out of P(A,B|C,D)

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.uncond()
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.cpd
            [0.20700000000000002, 0.793]
        '''

        if self._uncond_cache:  return self._uncond_cache

##        print "Computing unconditioned of", self.name
##        res = self.joint()
##        for fact in self.parents:
##            res = res.marginal(fact.var[-1])
##        self._uncond_cache = res
##        return res

        res = self

        if depth == -1:
            for fact in self.parents:
                res = res * fact.uncond(depth=-1)
                res = res.marginal(fact.cons)
        elif depth == 0:
            for fact in self.parents:
                temp = Factor(name=fact.name+'_temp', var=[fact.cons])
                for i in xrange(temp.pcard[0]):
                    temp.cpd.append(1.0 / temp.pcard[0])
                res = res * temp
                res = res.marginal(fact.cons)
        else:
            for fact in self.parents:
                res = res * fact.uncond(depth=depth-1)
                res = res.marginal(fact.cons)

        if depth == -1:
            self._uncond_cache = res

        return res

    def _query1(self, query=None, evidence=None):

        if not query:  query = []
        if not evidence:  evidence = []

        res = self.joint()

        query_ = []
        for i in query:  query_.append(i.var[-1])
        evid = []
        for i in evidence:  evid.append(i.var[-1])
        hidden = set(res.var) - set(query_) - set(evid)

        for hid in hidden:  res = res.marginal(hid)
        for evid in evidence:  res = res / evid

        return res

    def _query2(self, query=None, evidence=None, depth=-1):

        if not query:  query = []
        if not evidence:  evidence = []

        res = self

##        print ">>>>>>>>>>>", self.name, self.parents
##        print query, evidence
        for fact in self.parents:
##            print fact.name
            if not fact in evidence:
##                print "Product"
                if fact._uncond_cache:
##                    print "From cache"
                    res = res * fact._uncond_cache
                else:
                    if depth == 0:
                        temp = Factor(name=fact.name+'_temp', var=[fact.cons])
                        for i in xrange(temp.pcard[0]):
                            temp.cpd.append(1.0 / temp.pcard[0])
                        res = res * temp
                    else:
                        res = res * fact._query2([fact], evidence, depth-1)
            if not fact in query:
                if fact in evidence:
                    res = res / fact
                else:
                    res = res.marginal(fact.cons)

##        print "After product:"
##        print res

        if not self in query:
            if self in evidence:
##                print self.name, "I'm from evidence, divide"
                res = res / self
            else:
##                print self.name, "I'm from hidden, margin"
                res = res.marginal(self.cons)
##        else:
##            print self.name, "I'm from query, skip"

##        print "After that:"
##        print res
##        print "<<<<<<<<<<<<<<<<<<<<<<<<"

        return res

    def query(self, query=None, evidence=None):
        '''
        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.query(query=[T], evidence={C: 'yes'})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.cond
            []
            >>> R.cpd
            [0.9, 0.09999999999999999]
            >>> R = T.query(query=[T], evidence={C: 'no'})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Test]
            >>> R.cond
            []
            >>> R.cpd
            [0.2, 0.8]
            >>> R = T.query(query=[C], evidence={T: 'pos'})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cond
            []
            >>> R.cpd
            [0.9565217391304348, 0.04347826086956522]
            >>> R = T.query(query=[C], evidence={})
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cond
            []
            >>> R.cpd
            [0.99, 0.010000000000000002]


            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> R = T.query(query=[T], evidence=[C])
            >>> R.name
            'Conditional'
            >>> R.var
            [Cancer, Test]
            >>> R.cpd[0]
            0.2
            >>> R.cond
            [Cancer]
            >>> R = T.query(query=[C], evidence=[T])
            >>> R.name
            'Conditional'
            >>> R.var
            [Test, Cancer]
            >>> R.cpd[0]
            0.9565217391304347
            >>> R.cond
            [Test]
            >>> R = T.query(query=[C], evidence=[])
            >>> R.name
            'Marginal factor'
            >>> R.var
            [Cancer]
            >>> R.cond
            []
            >>> R.cpd
            [0.99, 0.010000000000000002]
        '''

        if isinstance(evidence, dict):
            res = self._query2(query, evidence.keys())
            for (var, val) in evidence.iteritems():
                res = res.reduce(var=var.var[-1], value=val)
            return res
        elif isinstance(evidence, list):
            return self._query2(query, evidence)

    def _norm(self):
        '''
        normalizes values of the factorto make all valies sum to 1.0
        Warning: mutates the factor!
        If factor sums to 0, does nothing

        Syntax:
            >>> C = Factor(name='Cancer',
            ...             values=["no", "yes"],
            ...             cpd=[0.99, 0.01])
            >>> T = Factor(name='Test',
            ...             values=["pos", "neg"], cond=[C],
            ...             cpd=[0.2, 0.8, 0.9, 0.1])

            >>> C = C._norm()
            >>> C.cpd
            [0.99, 0.01]
            >>> T.cpd
            [0.2, 0.8, 0.9, 0.1]
            >>> T = T._norm()
            >>> T.cpd
            [0.1, 0.4, 0.45, 0.05]
            >>> A = Factor(name='null', values=[0,1], cpd=[0.0, 0.0])
            >>> A = A._norm()
            >>> A.cpd
            [0.0, 0.0]

        '''
        sum_ = self.sum()
        if sum_ != 0:
            for i in range(len(self.cpd)):
                self.cpd[i] = self.cpd[i] / sum_
        return self


class TestFactor(unittest.TestCase):

    def setUp(self):
        self.C = Factor(name='Cancer',
                        values=["no", "yes"],
                        cpd=[0.99, 0.01])
        self.T = Factor(name='Test',
                        values=["pos", "neg"], cond=[self.C],
                        cpd=[0.2, 0.8, 0.9, 0.1])

        self.m =  self.C._map(self.T.var)

    def tearDown(self):
        pass

    def test_var(self):
        self.assertEqual(1, len(self.C.var))
        self.assertEqual('Cancer', self.C.var[0].name)

        self.assertEqual(2, len(self.T.var))
        self.assertEqual('Cancer', self.T.var[0].name)
        self.assertEqual('Test', self.T.var[1].name)

    def test_card(self):
        self.assertEqual(2, len(self.C.pcard))
        self.assertEqual(2, self.C.pcard[0])

        self.assertEqual(3, len(self.T.pcard))
        self.assertEqual(4, self.T.pcard[0])

    def test_cpd(self):
        self.assertEqual(2, len(self.C.cpd))
        self.assertEqual(0.99, self.C.cpd[0])
        self.assertEqual(0.01, self.C.cpd[1])

        self.assertEqual(4, len(self.T.cpd))
        self.assertEqual(0.2, self.T.cpd[0])
        self.assertEqual(0.8, self.T.cpd[1])
        self.assertEqual(0.9, self.T.cpd[2])
        self.assertEqual(0.1, self.T.cpd[3])

    def test_map(self):
        self.assertEqual(1, len(self.m))
        self.assertEqual(0, self.m[0])

    def test_ass(self):
        self.assertEqual(['no'], self.T._ass(0, self.m))
        self.assertEqual(['no'], self.T._ass(1, self.m))
        self.assertEqual(['yes'], self.T._ass(2, self.m))
        self.assertEqual(['yes'], self.T._ass(-1, self.m))
        self.assertEqual(['no'], self.T._ass(4, self.m))

    def test_ass2index(self):
        self.assertEqual(self.C._ass2index(['no']), 0)
        self.assertEqual(self.C._ass2index(['yes']), 1)

        self.assertEqual(self.T._ass2index(['no', 'pos']), 0)
        self.assertEqual(self.T._ass2index(['no', 'neg']), 1)
        self.assertEqual(self.T._ass2index(['yes', 'pos']), 2)
        self.assertEqual(self.T._ass2index(['yes', 'neg']), 3)

    def test_index2ass(self):
        self.assertEqual(['no'], self.C._index2ass(0))
        self.assertEqual(['yes'], self.C._index2ass(1))

        self.assertEqual(['no', 'neg'], self.T._index2ass(1))
        self.assertEqual(['yes', 'neg'], self.T._index2ass(3))
        self.assertEqual(['no', 'pos'], self.T._index2ass(0))
        self.assertEqual(['yes', 'pos'], self.T._index2ass(2))

    def test__mul__(self):
        P = self.C * self.T
        self.assertEqual(4, len(P.cpd))
        self.assertAlmostEqual(0.198, P.cpd[0])
        self.assertAlmostEqual(0.001, P.cpd[3])
        self.assertEqual(2, len(P.var))
        self.assertEqual('Cancer', P.var[0].name)
        self.assertEqual('Test', P.var[1].name)

    def testmarginal(self):
        M = self.T.marginal(self.C.var[-1])
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(1.1, M.cpd[0])
        self.assertAlmostEqual(0.9, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Test', M.var[0].name)

        M = self.T.marginal(self.T.var[-1])
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(1.0, M.cpd[0])
        self.assertAlmostEqual(1.0, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Cancer', M.var[0].name)

    def testreduce(self):
        M = self.T.reduce(var=self.C.var[-1], value='yes')
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(0.9, M.cpd[0])
        self.assertAlmostEqual(0.1, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Test', M.var[0].name)

        M = self.T.reduce(var=self.C.var[-1], value='no')
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(0.2, M.cpd[0])
        self.assertAlmostEqual(0.8, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Test', M.var[0].name)

    def test__div__(self):
        M = (self.T*self.C)/self.C
        self.assertEqual(4, len(M.cpd))
        self.assertAlmostEqual(0.2, M.cpd[0])
        self.assertAlmostEqual(0.8, M.cpd[1])
        self.assertAlmostEqual(0.9, M.cpd[2])
        self.assertAlmostEqual(0.1, M.cpd[3])
        self.assertEqual(2, len(M.var))
        self.assertEqual('Cancer', M.var[0].name)
        self.assertEqual('Test', M.var[1].name)

    def test__abs__(self):
        self.assertEqual(2, abs(self.C))
        self.assertEqual(4, abs(self.T))

    def testsum(self):
        self.assertEqual(1.0, self.C.sum())
        self.assertEqual(2.0, self.T.sum())

    def testjoint(self):
        M = self.T.joint()
        self.assertEqual(4, len(M.cpd))
        self.assertAlmostEqual(0.198, M.cpd[0])
        self.assertAlmostEqual(0.792, M.cpd[1])
        self.assertAlmostEqual(0.009, M.cpd[2])
        self.assertAlmostEqual(0.001, M.cpd[3])
        self.assertEqual(2, len(M.var))
        self.assertEqual('Cancer', M.var[0].name)
        self.assertEqual('Test', M.var[1].name)

    def testuncond(self):
        M = self.T.uncond()
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(0.207, M.cpd[0])
        self.assertAlmostEqual(0.793, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Test', M.var[0].name)

    def testuncond_depth(self):
        A = Factor(name='A', values=[0, 1], cpd=[0.2, 0.8])
        B = Factor(name='B', values=[0, 1], cond=[A], cpd=[0.6, 0.4, 0.3, 0.7])
        C = Factor(name='C', values=[0, 1], cond=[B], cpd=[0.6, 0.4, 0.3, 0.7])
        D = Factor(name='D', values=[0, 1], cond=[C], cpd=[0.6, 0.4, 0.3, 0.7])
        E = Factor(name='E', values=[0, 1], cond=[D], cpd=[0.6, 0.4, 0.3, 0.7])
        F = Factor(name='F', values=[0, 1], cond=[E], cpd=[0.6, 0.4, 0.3, 0.7])
        G = Factor(name='G', values=[0, 1], cond=[F], cpd=[0.6, 0.4, 0.3, 0.7])
        M = G.uncond(depth=3)
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(0.42915, M.cpd[0])
        self.assertAlmostEqual(0.57085, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('G', M.var[0].name)

    def testquery(self):
        M = self.T.query(query=[self.C], evidence={self.T: 'pos'})
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(0.9565217391304348, M.cpd[0])
        self.assertAlmostEqual(0.04347826086956522, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Cancer', M.var[0].name)

        M = self.T.query(query=[self.C], evidence={self.T: 'neg'})
        self.assertEqual(2, len(M.cpd))
        self.assertAlmostEqual(0.9987389659520807, M.cpd[0])
        self.assertAlmostEqual(0.0012610340479192938, M.cpd[1])
        self.assertEqual(1, len(M.var))
        self.assertEqual('Cancer', M.var[0].name)

        M = self.T.query(query=[self.C], evidence=[self.T])
        self.assertEqual(4, len(M.cpd))
        self.assertAlmostEqual(0.9565217391304348, M.cpd[0])
        self.assertAlmostEqual(0.04347826086956522, M.cpd[1])
        self.assertAlmostEqual(0.9987389659520807, M.cpd[2])
        self.assertAlmostEqual(0.0012610340479192938, M.cpd[3])
        self.assertEqual(2, len(M.var))
        self.assertEqual('Test', M.var[0].name)
        self.assertEqual('Cancer', M.var[1].name)

    def test_norm(self):
        M = self.T._norm()
        self.assertEqual(4, len(M.cpd))
        self.assertAlmostEqual(0.1, M.cpd[0])
        self.assertAlmostEqual(0.4, M.cpd[1])
        self.assertAlmostEqual(0.45, M.cpd[2])
        self.assertAlmostEqual(0.05, M.cpd[3])
        self.assertEqual(2, len(M.var))
        self.assertEqual('Cancer', M.var[0].name)
        self.assertEqual('Test', M.var[1].name)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
##    doctest.testmod(verbose=True)
