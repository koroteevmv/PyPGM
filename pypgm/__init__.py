# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#--------------------------------------------
# Name:        PyPGM
# Author:      sejros
# Created:     15.10.2012
# Copyright:   (c) sejros 2012
# Licence:     GNU GPL
#--------------------------------------------

'''
Syntax:
    >>> D = Factor(name='D', values=[0,1], cpd=[0.6, 0.4])
    >>> I = Factor(name='I', values=[0,1], cpd=[0.7, 0.3])
    >>> G = Factor(name='G|I,D', values=[1, 2, 3], cond=[D,I],
    ... cpd=[0.3,  0.4,  0.3,
    ... 0.05, 0.25, 0.7,
    ... 0.9,  0.08, 0.02,
    ... 0.5,  0.3,  0.2])
    >>> S = Factor(name='S|I', values=[0, 1], cond=[I],
    ...             cpd=[0.95, 0.05, 0.2, 0.8])
    >>> L = Factor(name='L|G', values=[0, 1], cond=[G],
    ...             cpd=[0.1, 0.9, 0.4, 0.6, 0.99, 0.01])
    >>> BN = Bayesian([D,I,S,G,L])
    >>> R = BN.joint().query2(query=[I], evidence={G:3, D:1})
    >>> R.cpd
    [0.18918918918918917, 0.8108108108108109]


    >>> C = Variable('Cancer', ['yes', 'no'])
    >>> T = Variable('Test', ['pos', 'neg'])
    >>> F11 = Factor(name='C', var=[C], cpd=[0.0001, 0.9999])
    >>> F12 = Factor(name='T|C', var=[C,T], cpd=[0.9, 0.1, 0.2, 0.8])
    >>> F12.cpd
    [0.9, 0.1, 0.2, 0.8]
    >>> F14 = (F12.marginal(C)) * F11
    >>> F14.cpd
    [0.00011000000000000002, 9e-05, 1.09989, 0.89991]

'''

from .variable import Variable, BinaryVariable
from .factor import Factor
from .bayesian import Bayesian

# TODO: test on larger nets with operands of marginal, reduce,
# __mul__, __div__ including more than one cons var
# TODO: doctest everything
