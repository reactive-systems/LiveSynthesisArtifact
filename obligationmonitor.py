import livesynthesis
import pygraphviz as viz
from itertools import chain, combinations
import output
import spot
import transitionsystems

def list_of_2ap(set):
    s = list(set)
    return chain.from_iterable(combinations(s,r) for r in range(len(s)+1))


def OM_from_formula_dep(f, aps):
    powerset_ap = list_of_2ap(aps)
    list_ap = []
    for x in powerset_ap:
        list_ap.append(x)
    om = viz.AGraph(directed=True, strict=False)
    queue = []
    explored = set()
    om.add_node(f, label=livesynthesis.strip(f))
    om.add_edge('Initial',f)
    queue.append(f)
    while queue:
        current = queue.pop(0)
        explored.add(current)
        for current_ap in list_ap:
            g = livesynthesis.after(current, current_ap)
            if not g in explored:
                om.add_node(g, label=livesynthesis.strip(g))
                queue.append(g)
            om.add_edge(current, g, label=current_ap)
    output.dump_dot_graph(om, 'test')

def OM_from_formula(f, aps):
    powerset_ap = list_of_2ap(aps)
    list_ap = []
    for x in powerset_ap:
        list_ap.append(x)
    om = transitionsystems.Transitionsystem()
    queue = []
    explored = set()
    init_node = transitionsystems.Node(f, livesynthesis.strip(f), True)
    om.add_node(init_node)
    #om.add_edge('Initial',f)
    queue.append(init_node)
    while queue:
        current = queue.pop(0)
        explored.add(current)
        for current_ap in list_ap:
            g_prime = livesynthesis.after(current.get_name(), current_ap)
            g = transitionsystems.Node(g_prime, livesynthesis.strip(g_prime))
            if not g in explored:
                om.add_node(g)
                queue.append(g)
            om.create_edge(current, g, current_ap)
    output.dump_dot_graph(output.TS_to_dot(om), 'test')

