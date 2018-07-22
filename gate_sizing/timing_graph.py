import networkx as nx
import matplotlib.pyplot as plt
import pylab

PRIMARY_IN = 1
PRIMARY_OUT = 2
GATE = 3
STEINER_NODE = 4


class Indexer:
    def __init__(self):
        self.idx = 0

        
    def __call__(self):
        self.idx += 1
        return self.idx - 1


class TimingGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_idxer = Indexer()
        self.edge_idxer = Indexer()


    def add_node(self, tp, pred = []):
        new_node = Node(tp, self.node_idxer())
        
        for p in pred:
            new_edge = Edge(p, new_node, self.edge_idxer())
            p.add_post(new_node)
            new_node.add_pred(p)
            self.edges.append(new_edge)

        self.nodes.append(new_node)
        
        return new_node


    def print_graph(self):
        for node in self.nodes:
            print [p.idx for p in node.pred], node, [p.idx for p in node.post]


    def draw(self):
        G = nx.Graph()
        node_pos = [[node.x(), node.y()] for node in self.nodes]
        label_pos = [[node.x(), node.y()] for node in self.nodes]

        colors = []
        for node in self.nodes:
            if node.tp.type == GATE:
                colors.append('red')
            elif node.tp.type == PRIMARY_IN:
                colors.append('blue')
            elif node.tp.type == PRIMARY_OUT:
                colors.append('green')
            elif node.tp.type == STEINER_NODE:
                colors.append('gray')
            else:
                colors.append('yellow')

        sizes = [50 for node in self.nodes]
        labeldict = {}
        for node in self.nodes:
            G.add_node(node.idx)
            
            for p in node.post:
                G.add_edge(node.idx, p.idx)     

            if node.tp.type == GATE:
                labeldict[node.idx] = ""           
            else:
                labeldict[node.idx] = ""

        nx.draw(G, node_pos, node_color = colors, node_size = sizes, alpha=1.)
        nx.draw_networkx_labels(G, label_pos, labeldict, font_color='r')


class Node:
    def __init__(self, tp, idx):
        self.tp = tp
        
        self.pred = []
        self.post = []

        self.idx = idx


    def add_post(self, node):
        self.post.append(node)


    def add_pred(self, node):
        self.pred.append(node)


    def x(self):
        return self.tp.x


    def y(self):
        return self.tp.y


    def __repr__(self):
        return "Node " + str(self.idx) + " (" + str(self.tp) +  ")" + " @ " + str(self.x()) + ", " + str(self.y()) 


class Edge:
    def __init__(self, n1, n2, idx):
        self.n1 = n1
        self.n2 = n2
        self.idx = idx


    def length(self):
        return abs(self.n1.x() - self.n2.x()) + abs(self.n1.y() - self.n2.y())


    def __repr__(self):
        return "(" + str(self.n1.idx) + ", " + str(self.n2.idx) + ")"


class TimingPoint:
    def __init__(self, type, x, y, rat=-1):
        self.type = type
        self.force_fixed = False

        self.x = x
        self.y = y

        self.rat = rat

    def __repr__(self):
        if self.type == PRIMARY_IN:
            return "PI"
        if self.type == PRIMARY_OUT:
            return "PO"
        if self.type == GATE:
            return "GA"
        if self.type == STEINER_NODE:
            return "SN"


t0 = TimingPoint(PRIMARY_IN, 0, 1)
t1 = TimingPoint(PRIMARY_IN, 0, 0)
t2 = TimingPoint(GATE, 1, 0)
t3 = TimingPoint(STEINER_NODE, 2, 0)
t4 = TimingPoint(PRIMARY_OUT, 2, 1)
t5 = TimingPoint(PRIMARY_OUT, 2, -1)

G = TimingGraph()
n0 = G.add_node(t0)
n1 = G.add_node(t1)
n2 = G.add_node(t2, [n0, n1])
n3 = G.add_node(t3, [n2])
n4 = G.add_node(t4, [n3])
n5 = G.add_node(t5, [n3])

G.print_graph()
G.draw()

pylab.show()
