#------------------------------------------------------------------------------
# Name:        inrference
# Purpose:
#
# Author:      Admin
#
# Created:     05.03.2013
# Copyright:   (c) Admin 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------
#!/usr/bin/env python
'''
inference.py
'''

from pypgm import Factor, Bayesian


def cancer_example():
    '''
    Cancer example
    '''
    C = Factor(name='Cancer', values=["no", "yes"],
                cpd=[0.999, 0.001])
    T = Factor(name='Test', values=["pos", "neg"],
                cond=[C], cpd=[0.2, 0.8, 0.9, 0.1])
##    print C
##    print T
##    print T.joint()
##    print T.uncond()
##    R = T.query(query=[C], evidence={T:'pos'})
    print T._query2(query=[C], evidence={T:'pos'})
    print T._query1(query=[C], evidence=[T])
    print T._query3(query=[C], evidence={T:'pos'})

def student_example():
    '''
    bayesian_inference
    '''
    D = Factor(name='Difficulty', values=[0, 1], cpd=[0.6, 0.4])
    I = Factor(name='Intelligence', values=[0, 1], cpd=[0.7, 0.3])
    G = Factor(name='Grade|I,D', values=[1, 2, 3],
                cond=[D, I], cpd=[0.3, 0.4, 0.3,
                                0.05, 0.25, 0.7,
                                0.9, 0.08, 0.02,
                                0.5, 0.3, 0.2],)
    S = Factor(name='SAT|I', values=[0, 1], cond=[I],
                cpd=[0.95, 0.05, 0.2, 0.8])
    L = Factor(name='Letter|G', values=[0, 1], cond=[G],
                cpd=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01])

    BN = Bayesian([D, I, S, G, L])

    print  BN.joint().query(query=[I], evidence={G:3, D:1})

def bayesian_inference():
    '''
    bayesian_inference
    '''
    A = Factor(name='A',
                values=[0, 1],
                cpd=[0.6, 0.4])
    B = Factor(name='B',
                values=[0, 1],
                cpd=[0.7, 0.3])
    C = Factor(name='C',
                values=[0, 1],
                cond=[A, B],
                cpd=[0.7, 0.3, 0.9, 0.1, 0.8, 0.2, 0.6, 0.4])
    print C
    print C.joint().marginal(B.var[-1]).reduce(var=C.var[-1], value=0)._norm()
    print C.query([A], {C: 0})
    print C.query([A], [C])

def exact_bayesian():
    '''
    bayesian_inference
    '''
    A = Factor(name='A',
                values=[0, 1],
                cpd=[0.5, 0.5])
    B = Factor(name='B',
                values=[0, 1],
                cpd=[0.5, 0.5])
    C = Factor(name='C|A,B',
                values=[0, 1],
                cond=[A, B],
                cpd=[1, 0, 1, 0, 1, 0, 0, 1])
    print C.query(query=[A], evidence={C: 0, B: 0})


def local_inference():
    A = Factor(name='A', values=[0, 1], cpd=[0.2, 0.8])
    B = Factor(name='B', values=[0, 1], cond=[A], cpd=[0.6, 0.4, 0.3, 0.7])
    C = Factor(name='C', values=[0, 1], cond=[B], cpd=[0.6, 0.4, 0.3, 0.7])
    D = Factor(name='D', values=[0, 1], cond=[C], cpd=[0.6, 0.4, 0.3, 0.7])
    E = Factor(name='E', values=[0, 1], cond=[D], cpd=[0.6, 0.4, 0.3, 0.7])
    F = Factor(name='F', values=[0, 1], cond=[E], cpd=[0.6, 0.4, 0.3, 0.7])
    G = Factor(name='G', values=[0, 1], cond=[F], cpd=[0.6, 0.4, 0.3, 0.7])

    print D.query(query=[D], evidence={C:0})
    print D._query2(query=[D], evidence={C:0})
    print D._query3(query=[D], evidence={C:0})
##    P = D*C
##    print P
##    print P.reduce(var=C.var[-1], value=0)
##    print P.reduce(var=C.var[-1], value=0).marginal(var=B.var[-1])


##    A = Factor(name='A', values=[0, 1], cpd=[0.001, 0.999])
##    B = Factor(name='B', values=[0, 1], cond=[A], cpd=[0.96, 0.04, 0.93, 0.07])
##    C = Factor(name='C', values=[0, 1], cond=[B], cpd=[0.96, 0.04, 0.93, 0.07])
##    D = Factor(name='D', values=[0, 1], cond=[C], cpd=[0.96, 0.04, 0.93, 0.07])
##    E = Factor(name='E', values=[0, 1], cond=[D], cpd=[0.96, 0.04, 0.93, 0.07])
##    F = Factor(name='F', values=[0, 1], cond=[E], cpd=[0.96, 0.04, 0.93, 0.07])
##    G = Factor(name='G', values=[0, 1], cond=[F], cpd=[0.96, 0.04, 0.93, 0.07])

##    print G
##    print G.uncond()
##    print G.joint()
##    print G.query(query=[G], evidence={F: 0})
##    print G.query(query=[G], evidence={F: 1})


local_inference()

