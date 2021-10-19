import spot
import json
import transitionsystems
import pygraphviz as viz


def dump_json(guarantees, inputs, outputs, filename = None, assumptions=[]):
    dict = {}
    dict["semantics"] = "moore"
    dict["inputs"] = inputs
    dict["outputs"] = outputs
    if assumptions:
        dict["assumptions"] = assumptions
    else:
        dict["assumptions"] = []
    dict["guarantees"] = [guarantees.to_str()]
    json_object = json.dumps(dict, indent=4)
    if filename:
        with open(f"{filename}.json", "w") as outfile:
            outfile.write(json_object)
    else:
        with open("bosyinput.json", "w") as outfile:
            outfile.write(json_object)

def dump_dot_graph(graph, filename):
    graph.write(f"{filename}.dot")

def TS_to_dot(ts):
    out_graph = viz.AGraph(directed=True, strict=False)
    for edge in ts.get_edges():
        out_graph.add_node(edge.get_source().get_name(), label=edge.get_source().get_label())
        out_graph.add_edge(edge.get_source().get_name(), edge.get_target().get_name(), label=edge.get_label())
    return out_graph

