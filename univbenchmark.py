import output
import parser
import subprocess
import json
import shlex
import universalsynthesis as uni
import obligationmonitor
import spot
import time

def parse_json(bosyfile):
    elements = json.loads(bosyfile)
    return elements
def formula_from_string(string):
    f = ''
    for sub in string:
        f += "("
        f += sub
        f += ") &&"
    return f[:-2]

def run(filename, tlsf):
    with open(filename, "r", encoding='utf-8') as file:
        initial_file, update_file = file.read().split("#")
    elements_init = parse_json(initial_file)
    elements_update = parse_json(update_file)
    initial_formula = formula_from_string(elements_init["guarantees"])
    initial_assumptions = formula_from_string(elements_init["assumptions"])
    init_formula = spot.formula(initial_formula)
    if initial_assumptions:
        init_formula = spot.formula.Implies(spot.formula(initial_assumptions), init_formula)
        print(init_formula.to_str())

    update_formula = formula_from_string(elements_update["guarantees"])

    ap_e = elements_update["inputs"]
    ap_e_init = elements_init["inputs"]
    ap_s = elements_update["outputs"]
    with open("results/tmpinput.json", "w") as file:
        file.write(initial_file)
    f = open(f"results/{filename}.dot", "w")
    print("Synthesizing a system for " + filename)
    subprocess.call(shlex.split(f'./bosybackend.sh --backend explicit --target dot --synthesize ../results/tmpinput.json'),
                    cwd='./bosy', stdout=f)
    f.close()
    print("Parsing result of bosy to obligation monitor")
    formula, univom = uni.main(parser.bosydot_to_ts(f"results/{filename}.dot", obligationmonitor.list_of_2ap(ap_e)),
                               init_formula, spot.formula(update_formula))
    elements_update["guarantees"] = []
    elements_update["guarantees"] = formula.to_str()
    output.dump_dot_graph(output.TS_to_dot(univom),f'results/{filename}_OM')
    #with open(f'results/{filename}_update.json',"w") as file:
    #    json.dump(elements_update,file)
    formula = spot.simplify(formula)
    output.dump_json(formula, ap_e, ap_s, f'results/{filename}_update', elements_update["assumptions"])
    f_result = open(f"results/{filename}_result.txt", "w")
    print("Synthesizing universal update")
    start = time.time()
    subprocess.call(shlex.split(f'./bosybackend.sh --backend explicit ../results/{filename}_update.json'),
                    cwd='./bosy')
    end = time.time()
    print("Time universal update:")
    duration = end - start
    print(duration)
    f_result.close()
    print("Synthesizing only the upate")
    start = time.time()
    output.dump_json(spot.simplify(update_formula), ap_e, ap_s, f'results/tmpupdate', elements_update["assumptions"])
    subprocess.call(
        shlex.split(f'./bosybackend.sh --backend explicit ../results/tmpupdate.json'),
        cwd='./bosy')
    end = time.time()
    duration = end - start
    print("Time onlye update system synthesis:")
    print(duration)
    size = len(univom.get_nodes())
    print("Size of obligation automaton: " + str(len(univom.get_nodes())))
    i = 1
    for n in univom.get_nodes():
        if not n.get_label() is "_init":
            formula = spot.formula.And([spot.formula(update_formula), spot.formula(n.get_label())])
            output.dump_json(formula, ap_e, ap_s, f'results/{filename}_update_{i}_{size}', elements_update["assumptions"])
            f_result = open(f"results/{filename}_result_{i}_{size}.txt", "w")
            print("Synthezising expl. update for obligation monitor state " + str(i))
            subprocess.call(shlex.split(f'./bosybackend.sh --synthesize ../results/{filename}_update_{i}_{size}.json'),
                            cwd='./bosy', stdout=f_result)
            print("... Done")
            f_result.close()
            i = i+1
