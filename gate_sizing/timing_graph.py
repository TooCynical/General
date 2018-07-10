# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 16:03:25 2018

@author: Lucas
"""

GATE = 0
STEINER_NODE = 1

class Indexer:
    def __init__(self):
        self.index = 0
        
    def __call__(self):
        self.index += 1
        return self.index - 1

class TimingGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_indexer = Indexer()
        self.edge_indexer = Indexer()

class Node:
    def __init__(self, type, x, y, index):
        self.type = type
        self.x = x
        self.y = y
        self.index = index

class Edge:
    def __init__(self, n1, n2, index):
        self.n1 = n1
        self.n2 = n2
        self.index = index