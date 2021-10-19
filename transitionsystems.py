import spot
import livesynthesis

class Node:
    name = None
    label = None
    init = None
    id = None
    def __init__(self, name, label, init = False, id = '0'):
        self.name = name
        self.label = label
        self.init = init
        self.id = id

    def __eq__(self, other):
        return self.name == other.name and self.id == other.id
    def __hash__(self):
        return hash(self.name ) + hash(self.id)
    def get_name(self):
        return self.name
    def get_label(self):
        return self.label
    def get_init(self):
        return self.init
    def get_id(self):
        return self.id
class Edge:
    source = None
    target = None
    label = None

    def __init__(self, source, target, label):
        self.source = source
        self.target = target
        self.label = label
    def __eq__(self, other):
        return self.source == other.source and self.target == other.target and self.label == other.label
    def __hash__(self):
        return hash(self.source)+hash(self.target)
    def get_source(self):
        return self.source
    def get_target(self):
        return self.target
    def get_label(self):
        return self.label


class Transitionsystem:
    nodes = None
    edges = None

    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def create_node(self, name, label, init=False):
        self.nodes.add(Node(name, label, init))
    def add_node(self, node):
        self.nodes.add(node)
    def create_edge(self, source, target, label):
        self.edges.add(Edge(source,target,label))
    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def get_outgoing_edges(self, node):
        edgeset = set()
        for e in self.edges:
            if e.source == node:
                edgeset.add(e)
        return edgeset

    def get_node(self, string):
        for node in self.nodes:
            if node.name == string:
                return node

    def get_ingoing_edges(self, node):
        edgeset = set()
        for e in self.edges:
            if e.target == node:
                edgeset.add(e)
        return edgeset

    def get_init_node(self):
        for node in self.nodes:
            if node.get_name() == "s0":
                return node

