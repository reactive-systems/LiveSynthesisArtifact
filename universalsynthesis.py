import transitionsystems
import output
import parser
import obligationmonitor
import livesynthesis
import spot

def main(ts, initial_formula, update_formula):
    explored = set()
    om_ts = transitionsystems.Transitionsystem()
    init_node = transitionsystems.Node(initial_formula, livesynthesis.strip(initial_formula), True, ts.get_init_node().get_name())
    om_ts.add_node(init_node)
    output.dump_dot_graph(output.TS_to_dot(ts),'correction')
    queue = []
    queue.append(init_node)
    while queue:
        current = queue.pop(0)
        for current_edge in ts.get_outgoing_edges(ts.get_node(current.get_id())):
            aps = set()
            aps.update(ts.get_node(current.get_id()).get_label())
            aps.update(current_edge.get_label())
            new_formula = livesynthesis.after(current.get_name(), aps)
            new_node = transitionsystems.Node(new_formula, livesynthesis.strip(new_formula), False, current_edge.get_target().get_name())
            if new_node in explored:
                om_ts.create_edge(current, new_node, aps)
            else:
                queue.append(new_node)
                om_ts.add_node(new_node)
                om_ts.create_edge(current, new_node, aps)
        explored.add(current)
    formula_list = []
    for node in om_ts.get_nodes():
        formula_list.append(spot.formula(node.get_label()))
    formula_list.append(update_formula)
    return spot.formula.And(formula_list), om_ts
