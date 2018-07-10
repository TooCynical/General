# -*- coding: utf-8 -*-
"""
Created on Sun Apr 01 21:09:49 2018

@author: Lucas
"""

import networkx as nx
import matplotlib.pyplot as plt
import pylab


GATE_SIZE_CAP_FACTOR = 1.0
WIRE_LENGTH_CAP_FACTOR = 1.0

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

    def compute_downcaps(self):
        for node in reversed(self.nodes):
            downcap = 0.0            
            for child in node.children:
                downcap += child.cap()
                downcap += dist(node, child) * WIRE_LENGTH_CAP_FACTOR
            node.set_downcap(downcap)

    def draw(self):
        G = nx.DiGraph()
        node_pos = [[node.x, node.y] for node in self.nodes]
        label_pos = [[node.x, node.y] for node in self.nodes]
        
        colors = ['gray' if node.gate else 'black' for node in self.nodes]
        sizes = [node.gate.size * 500 if node.gate else 50 for node in self.nodes]
        labeldict = {}
        for node in self.nodes:
            G.add_node(node.idx)
            
            for child in node.children:
                G.add_edge(node.idx, child.idx)     

            if node.gate:
                labeldict[node.idx] = node.delay()            
            else:
                labeldict[node.idx] = ""

        nx.draw(G, node_pos, node_color = colors, node_size = sizes, alpha=0.3)
        nx.draw_networkx_labels(G, label_pos, labeldict, font_color='r')
        
    def print_nodes(self):
        for node in self.nodes:
            print node
        
class Node:
    def __init__(self, idx, x, y, parents):
        self.idx = idx
        self.x = float(x)
        self.y = float(y)
        self.parents = parents
        self.children = []
        self.downcap = -1
        
        for p in parents:
            p.add_child(self)
            
    def cap(self):
        if self.gate:
            return self.gate.size * self.gate.rho
        else:
            return self.downcap
            
    def delay(self):
        if self.gate:
            return self.downcap / self.gate.size
        else:
            return 0.0

    def set_downcap(self, downcap):
        self.downcap = downcap
        
    def set_gate(self, gate):
        self.gate = gate
    
    def add_child(self, child):
        self.children.append(child)
        
    def __repr__(self):
        return "Node: " + str([p.idx for p in self.parents]) + "->" + str(self.idx) + \
               "->" + str([c.idx for c in self.children]) + " @" + str((self.x, self.y)) + "\n" + \
               "gate: " + str(self.gate) + "\n" + \
               "delay: " + str(self.delay()) + "\n" + \
               "downcap: " + str(self.downcap) +  "\n" + \
               "incap: " + str(self.cap())

def dist(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

class Edge:
    def __init__(self, head_idx, tail_idx):
        self.head_idx = head_idx
        self.tail_idx = tail_idx

class Gate:
    def __init__(self, size=1.0, rho=1.0):
        self.size = size        
        self.rho = rho
    
    def __repr__(self):
        return str(self.size)


G = TimingGraph()
n1 = G.add_node(gate=Gate(4))
n2 = G.add_node(1.0, 1, [n1], gate=Gate(1))
n3 = G.add_node(1.0, -1, [n1], gate=Gate(2))
n4 = G.add_node(2.0, 0.0, [n2, n3], gate=Gate())
n5 = G.add_node(2.5, 0.0, [n4])
n6 = G.add_node(3.0, 0.0, [n5], gate=Gate())
n7 = G.add_node(3.0, 1.0, [n5], gate=Gate())

G.compute_downcaps()
G.print_nodes()

G.draw()
pylab.show()


