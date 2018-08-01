# -*- coding: utf-8 -*-
"""
Created on Wed Aug 01 00:54:53 2018

@author: Lucas
"""

import random
import itertools
import copy
import numpy as np

def double_monotone(L):
    i = np.argmin(L)
    return monotone(L[:i]) and monotone(L[i:])

def monotone(L):
    return non_increasing(L) or non_decreasing(L)

def non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))

def delay(s, load=0.0):
    d = 0.0
    for i in range(len(s) - 1):
        d += float(s[i + 1]) / s[i]
    d += load / s[-1]
    return d
    
def best_order(s, load=0.0):
    min_delay = delay(s, load)
    best_order = copy.deepcopy(s)
    for order in itertools.permutations(s):
        cur_delay = delay(order, load)
        if cur_delay <= min_delay:
            min_delay = cur_delay
            best_order = copy.deepcopy(order)
    return best_order, min_delay
    
n = 10
while(True):
    s = [random.randrange(1, 100) for i in range(n)]
    load = random.randrange(1, 100)
    L = best_order(s, load)[0]
    dm = double_monotone(L)
    print L, load, dm
    if not dm:
        exit()