# -*- coding: utf-8 -*-
"""
Created on Wed Aug 01 00:54:53 2018

@author: Lucas
"""

import random
import itertools
import copy
import numpy as np
import sys

MAX_INT = 10000000000

def monotone(L):
    return non_increasing(L) or non_decreasing(L)

def non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))

def count_shifts(L):
    shifts = 0
    
    def get_dir(i):
        if L[i] < L[i+1]:
            direction = 1
        elif L[i] > L[i+1]:
            direction = -1
        else:
            direction = 0
        return direction

    direction = get_dir(0)

    for i in xrange(1, len(L) - 1):
        new_direction = get_dir(i)
        if new_direction * direction == -1:
            shifts += 1
        if new_direction != 0:
            direction = new_direction
    return shifts

def delay(s, load=0.0):
    d = 0.0
    for i in range(len(s) - 1):
        d += float(s[i + 1]) / s[i]
    d += float(load) / s[-1]
    return d
    
def best_order(s, load=0.0, fixed_first=False):
    min_delay = MAX_INT
    best_order = copy.deepcopy(s)

    if fixed_first:
        for porder in itertools.permutations(s[1:]):
            order = [s[0]] + list(porder)
            cur_delay = delay(order, load)
            if cur_delay <= min_delay:
                min_delay = cur_delay
                best_order = copy.deepcopy(order)
    else:
        for order in itertools.permutations(s):
            cur_delay = delay(order, load)
            if cur_delay <= min_delay:
                min_delay = cur_delay
                best_order = copy.deepcopy(order)

    return best_order, min_delay
    
n = int(sys.argv[1])
s_max = 10
while(True):
    s = [random.randrange(1, s_max) for i in range(n)]
    load = random.randrange(s_max, 2 * s_max)
    L = best_order(s, load, True)[0]
    shifts = count_shifts(L)
    m = monotone(L)
    print L, load, shifts
    if shifts > 2:
        break