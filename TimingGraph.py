# -*- coding: utf-8 -*-
"""
Created on Sun Apr 01 21:09:49 2018

@author: Lucas
"""

import networkx as nx
import matplotlib.pyplot as plt
import pylab


class TimingGraph:
    def __init__(self):
        self.nodes = []
        self.gates = []
        self.idx_count = 0
        
    def add_node(self, x=0.0, y=0.0, parents=[], gate=None):
        node = Node(self.idx_count, x, y, parents)
        self.idx_count += 1        

        self.nodes.append(node)
        node.set_gate(gate)
        if gate:        
            self.gates.append(node)            
            
        return node

    def draw(self):
        G = nx.DiGraph()
        pos = [[node.x, node.y] for node in self.nodes]
        colors = ['blue' if node.gate else 'black' for node in self.nodes]
        sizes = [node.gate.size * 300 if node.gate else 50 for node in self.nodes]
        for node in self.nodes:
            G.add_node(node.idx)
            for child in node.children:
                G.add_edge(node.idx, child.idx)                

        nx.draw(G, pos, node_color = colors, node_size = sizes)

        
class Node:
    def __init__(self, idx, x, y, parents):
        self.idx = idx
        self.x = float(x)
        self.y = float(y)
        self.parents = parents
        self.children = []
        
        for p in parents:
            p.add_child(self)
        
    def set_gate(self, gate):
        self.gate = gate
    
    def add_child(self, child):
        self.children.append(child)
        
    def __repr__(self):
        return "Node: " + str([p.idx for p in self.parents]) + "->" + str(self.idx) + \
               "->" + str([c.idx for c in self.children]) + " @" + str((self.x, self.y)) + "\n" + \
               "gate: " + str(self.gate)


class Gate:
    def __init__(self, size=1.0, rho=1.0):
        self.size = size        
        self.rho = rho
    
    def __repr__(self):
        return str(self.size)


G = TimingGraph()
n1 = G.add_node(gate=Gate(4))
n2 = G.add_node(1.0, 1, [n1], gate=Gate(0.5))
n3 = G.add_node(1.0, -1, [n1], gate=Gate(2))
n4 = G.add_node(2.0, 0.0, [n2, n3])
n5 = G.add_node(2.5, 0.0, [n4])
n6 = G.add_node(3.0, 0.0, [n5], gate=Gate())
n7 = G.add_node(3.0, 1.0, [n5], gate=Gate())

G.draw()
pylab.show()


