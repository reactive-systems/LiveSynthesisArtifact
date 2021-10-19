import spot
import parser
import output
import obligationmonitor
import universalsynthesis
import subprocess
import univbenchmark


init_formula = None
update_formula = None
fin_trace = None
TS = None
args = None
ap_e = []
ap_s = []

def strip(f):
    if f._is(spot.op_G):
        return spot.formula.tt()
    if f._is(spot.op_ap):
        return f
    if f._is(spot.op_R):
        return spot.formula.tt()
    return f.map(strip)

def expand(f):
    if f._is(spot.op_ff) or f._is(spot.op_tt) or f._is(spot.op_ap) or f._is(spot.op_X):
        return f
    if f._is(spot.op_Not):
        return spot.formula.Not(expand(f[0]))
    if f._is(spot.op_F):
        g = expand(f[0])
        return spot.formula.Or([g, spot.formula.X(f)])
    if f._is(spot.op_G):
        g = expand(f[0])
        return spot.formula.And([g,spot.formula.X(f)])
    if f._is(spot.op_U):
        g1 = f[0]
        g2 = f[1]
        r1 = spot.formula.And([expand(g1), spot.formula.X(f)])
        return spot.formula.Or([r1, expand(g2)])
    if f._is(spot.op_W):
        g1 = f[0]
        g2 = f[1]
        r1 = spot.formula.And([expand(g1), spot.formula.X(f)])
        return spot.formula.Or([r1, expand(g2)])
    if f._is(spot.op_R):
        g1 = expand(f[0])
        g2 = expand(f[1])
        innerand = spot.formula.And([g1,g2])
        innerand2 = spot.formula.And([g2, spot.formula.X(f)])
        return spot.formula.Or([innerand, innerand2])
    if f._is(spot.op_M):
        g1 = expand(f[0])
        g2 = expand(f[1])
        innerand = spot.formula.And([g1, g2])
        innerand2 = spot.formula.And([g2, spot.formula.X(f)])
        return spot.formula.Or([innerand, innerand2])
    if f._is(spot.op_And):
        list = []
        for child in f:
            list.append(expand(child))
        return spot.formula.And(list)
    if f._is(spot.op_Or):
        list = []
        for child in f:
            list.append(expand(child))
        return spot.formula.Or(list)
    else:
        print('expansion failed')
        return f

def state_eval(nu, f):
    if f._is(spot.op_tt) or f._is(spot.op_ff):
        return f
    if f._is(spot.op_ap):
        if f.to_str() in nu:
            return spot.formula.tt()
        else:
            return spot.formula.ff()
    if f._is(spot.op_And):
        list = []
        for child in f:
            list.append(state_eval(nu, child))
        return spot.formula.And(list)
    if f._is(spot.op_Or):
        list = []
        for child in f:
            list.append(state_eval(nu, child))
        return spot.formula.Or(list)
    if f._is(spot.op_Not):
        return spot.formula.Not(state_eval(nu,f[0]))
    else:
        return f


def successor(f):
    if f._is(spot.op_And):
        list = []
        for child in f:
            list.append(successor(child))
        return spot.formula.And(list)
    if f._is(spot.op_Or):
        list = []
        for child in f:
            list.append(successor(child))
        return spot.formula.Or(list)
    if f._is(spot.op_X):
        return f[0]
    else:
        return f

def after(g, set):
    f = spot.simplify(spot.negative_normal_form(g))
    f = expand(f)
    f = state_eval(set, f)
    f = successor(f)
    f = spot.simplify(spot.negative_normal_form(f))
    return f

def trace_to_list(graph):
    nodes = graph.get_node_list()
    edges = graph.get_edges()
    ret_list = []
    for current in edges:
        current_set = set()
        (source, ) = graph.get_node(current.get_source())
        current_set.add(source.get_attributes()['label'])
        current_set.add(current.get_attributes()['label'])
        ret_list.append(current_set)
    formula_list = []
    for set1 in ret_list:
        current_set = set()
        for n in set1:
            current_set.add(spot.formula.ap(n))
        formula_list.append(current_set)
    return formula_list

def finite_trace_synthesis():
    ap_list = trace_to_list(TS)
    current_formula = init_formula
    for set in ap_list:
        current_formula = after(current_formula, set)
    stripf = strip(current_formula)
    return spot.formula.And([stripf, update_formula])

def call_bosy(formula):
    print(formula)
    print('TODO: send formula to bosy')
    output.dump_json(formula, ap_e, ap_s)
    subprocess.run(".bosy/bosybackend.sh --backend smt --target dot --synthesize bosyinput.json", shell=True)


def main():
    global init_formula
    global update_formula
    global ap_e
    global ap_s
    global TS
    args = parser.parse_inputs()
    if args.universalbenchmark:
        univbenchmark.run(args.input, args.tlsf)
        exit()

    filename = None
    aps = ap_e
    aps.extend(ap_s)
    TS = parser.TS_from_Dot(args.TS)
    init_formula, update_formula, ap_e, ap_s, filename = parser.parse_formulas(args)
    if args.runbosy:
        output.dump_json(init_formula, ap_e, ap_s)
        exit()
    if args.finitetrace:
        formula = finite_trace_synthesis()
        call_bosy(formula)
        exit()
    if args.universal:
        ts = parser.bosydot_to_ts(args.TS, obligationmonitor.list_of_2ap(ap_e))
        formula, univom = universalsynthesis.main(ts, init_formula, update_formula)
        call_bosy(formula)
        exit()
    if args.OM and args.TS:
        formula, univom = universalsynthesis.main(ts, init_formula, update_formula)
        output.dump_dot_graph(univom, 'obligationmonitorTS')
        exit()
    if args.OM:
        om = obligationmonitor.OM_from_formula(spot.simplify(spot.negative_normal_form(init_formula)), aps)
        output.dump_dot_graph(om, 'obligationmonitor')
        exit()
    else:
        print('Please specify inputs.')
        exit()

if __name__ == "__main__":
    main()