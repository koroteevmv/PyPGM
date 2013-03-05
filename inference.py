#-------------------------------------------------------------------------------
# Name:        модуль1
# Purpose:
#
# Author:      Admin
#
# Created:     05.03.2013
# Copyright:   (c) Admin 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import factors

class Factor(factors.Factor):
    def reduce(self, var=None, value=''):
        print "AAAAAAAA"
        if not var in self.var:
            raise AttributeError()

        res = self.__class__(name='Reduced',
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
        pass

def bayesian_inference():
    A = Factor(name='A',
                values=[0, 1],
                CPD=[0.6, 0.4])
    B = Factor(name='B',
                values=[0, 1],
                CPD=[0.7, 0.3])
    C = Factor(name='C|A,B', full='C',
                values=[0, 1],
                cond=[A, B],
                CPD=[0.7, 0.3, 0.9, 0.1, 0.8, 0.2, 0.6, 0.4])
    print C.joint().marginal(B.var[-1]).reduce(var=C.var[-1], value=0).norm()

def exact_bayesian():
    A = Factor(name='A',
                values=[0, 1],
                CPD=[0.5, 0.5])
    B = Factor(name='B',
                values=[0, 1],
                CPD=[0.5, 0.5])
    C = Factor(name='C|A,B', full='C',
                values=[0, 1],
                cond=[A, B],
                CPD=[1, 0, 1, 0, 1, 0, 0, 1])
    print C.reduce(var=C.var[-1], value=0)

def main():
    exact_bayesian()
    pass

if __name__ == '__main__':
    main()
