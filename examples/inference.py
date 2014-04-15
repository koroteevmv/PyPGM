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
    print C
    print T
    print T.joint()
    print T.uncond()
    R = T.joint().query2(query=[C], evidence={T:'pos'})
    R.name = "Tested once"
    print R
##    print T.joint() / T.uncond()

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
                                0.5, 0.3, 0.2],
                full="Grade")
    S = Factor(name='SAT|I', values=[0, 1], cond=[I],
                cpd=[0.95, 0.05, 0.2, 0.8])
    L = Factor(name='Letter|G', values=[0, 1], cond=[G],
                cpd=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01])

    BN = Bayesian([D, I, S, G, L])

    print  BN.joint().query2(query=[I], evidence={G:3, D:1})

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
    C = Factor(name='C|A,B', full='C',
                values=[0, 1],
                cond=[A, B],
                cpd=[0.7, 0.3, 0.9, 0.1, 0.8, 0.2, 0.6, 0.4])
    print C.joint().marginal(B.var[-1]).reduce(var=C.var[-1], value=0).norm()

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
    C = Factor(name='C|A,B', full='C',
                values=[0, 1],
                cond=[A, B],
                cpd=[1, 0, 1, 0, 1, 0, 0, 1])
    print C.query2(query=[A], evidence={C: 0, B:0})



cancer_example()

