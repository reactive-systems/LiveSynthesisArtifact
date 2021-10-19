import livesynthesis
import argparse
import spot
import pygraphviz as viz
import transitionsystems
import output
from pathlib import Path
import os
import re


def init_parse():
    p = argparse.ArgumentParser(description='Live synthesis implementation')
    #flags
    p.add_argument('--finitetrace', action='store_true', help='finite trace updates')
    p.add_argument('--universal', action='store_true', help='universal live updates')
    p.add_argument('-updatesensitive', action='store_true', help='update system is update-sensitive')
    #inputs
    p.add_argument('-initialformula',  help='The initial specification as LTL formula')
    p.add_argument('-updateformula', help='The update specification as LTL formula')
    p.add_argument('-TS', help='The transition system, a trace if --finitetrace is set')
    p.add_argument('-Eap', help='A comma seperated list of environment atomic propositions')
    p.add_argument('-Sap', help='A comma seperated list of system atomic propositions')
    p.add_argument('-OM', help='Generates the obligationmonitor for the input formula, utputs TS intersect OM if TS is given')
    p.add_argument('-runbosy', action='store_true', help='Runs the given input formula, Eap, and Sap with bosy')
    p.add_argument('-universalbenchmark', action='store_true', help='Benchmarks the input file')
    p.add_argument('-input', help='The input benchmark')
    p.add_argument('-tlsf', action='store_true' , help='Input of benchmark is in tslf or not ')
    args = p.parse_args()
    return args

def ap_from_argp(string):
    ap_list = string.split(",")
    return ap_list

def TS_from_Dot(filename):
    graph = viz.AGraph(filename)
    return graph



def parse_formulas(args):
    myfile = Path(args.initialformula)
    filename = None
    if myfile.is_file():
        with open(args.initialformula, 'r') as file:
            init_formula = spot.formula(file.read())
        filename = os.path.splitext(args.initialformula)[0]
    else:
        init_formula = spot.formula(args.initialformula)
    myfile = Path(args.Eap)
    if (myfile.is_file()):
        with open(args.Eap, 'r') as file:
            ap_e = ap_from_argp(file.readline().split()[1])
            ap_s = ap_from_argp(file.readline().split()[1])
    else:
        ap_e = ap_from_argp(args.Eap)
        ap_s = ap_from_argp(args.Sap)
    myfile = Path(args.updateformula)
    if myfile.is_file():
        with open(args.updateformula, 'r') as file:
            update_formula = spot.formula(file.read())
    else:
        update_formula = spot.formula(args.updateformula)
    return init_formula, update_formula, ap_e, ap_s, filename

def satisfy_transition_formula(formula, aps):
    if not formula:
        return True
    if len(formula) == 1:
        if ord(formula) == 8868:
            f = spot.formula('1')
        else:
            f = spot.formula(formula)
    else:
        formula = re.sub(r"\s+", "", formula, flags=re.UNICODE)
        formulas = formula.split('/')
        formulaslist = []
        for f in formulas:
            if f != "":
                formulaslist.append(spot.formula(f))
        f = spot.formula.And(formulaslist)
    f = livesynthesis.state_eval(aps, f)
    f = spot.simplify(f)
    return f._is(spot.op_tt)

def transform_sys_ap(node):
    list = node.attr['label'].split()
    ret_list = []
    for n in list:
        if n != node.get_name():
            ret_list.append(n)
    return ret_list

def bosydot_to_ts(args, list_ap_sets):
    setlist = list_ap_sets
    list_ap = []
    for x in list_ap_sets:
        list_ap.append(x)
    dotfile = TS_from_Dot(args)
    ts = transitionsystems.Transitionsystem()
    node_set = set()
    for node in dotfile.nodes():
        n = transitionsystems.Node(node.name, transform_sys_ap(node))
        ts.add_node(n)
        node_set.add(n)
    for edge in dotfile.edges():
        source, target = edge
        source = transitionsystems.Node(source.get_name(), dotfile.get_node(source).attr['label'])
        target = transitionsystems.Node(target.get_name(), dotfile.get_node(target).attr['label'])
        label = edge.attr['label']
        for ap in list_ap:
            if satisfy_transition_formula(label, ap):
                ts.create_edge(source, target, ap)
    return ts

def dot_to_transitionsystem(args):
    dotfile = TS_from_Dot(args)
    ts = transitionsystems.Transitionsystem()
    node_set = set()
    for node in dotfile.nodes():
        n = transitionsystems.Node(node.name, node.attr['label'])
        ts.add_node(n)
        node_set.add(n)
    for edge in dotfile.edges():
        source, target = edge
        source = transitionsystems.Node(source, dotfile.get_node(source).attr['label'])
        target = transitionsystems.Node(target, dotfile.get_node(target).attr['label'])
        label = edge.attr['label']
        ts.create_edge(source, target, label)
    output.dump_dot_graph(output.TS_to_dot(ts), 'inout')
    return ts

def parse_inputs():
    return init_parse()

