# -*- coding: utf-8 -*-
"""
Created on Mon Apr 02 23:06:02 2018

@author: Lucas
"""

import random

def AM(x1, x2):
    ret = []
    for i in range(len(x1)):
        ret.append((x1[i] + x2[i]) / 2.0)
    return ret


class Monomial:
    MIN_POWER = -5
    MAX_POWER = 5
    
    def __init__(self, n, a=None, c=1):
        self.n = n            
        self.c = c        
        
        if a:
            self.a = a
        else:
            self.a = [random.randint(Monomial.MIN_POWER, Monomial.MAX_POWER) for d in xrange(n)]
        
    def __call__(self, x):
        ret = self.c
        for i in xrange(self.n):
            ret *= x[i] ** self.a[i]
        return ret
        
    def __repr__(self):
        return str(self.c) + str(self.a)


class Posynomial:
    def __init__(self, monomials):
        self.monomials = monomials
    
    def __call__(self, x):
        ret = 0
        for m in self.monomials:
            ret += m(x)
        return ret

    def __repr__(self):
        ret = ""
        for i in xrange(len(self.monomials)):
            ret += str(self.monomials[i])
            if i < len(self.monomials) - 1:
                ret += "+ "
        return ret

p = Posynomial([Monomial(4, c=4), Monomial(4, c=2), Monomial(4)])
print p
print p([2, 3, 4, 5])