def serialise_states(states):
    result = []
    for state in states:
        items = []
        for (lhs, rhs, dot, la) in state:
            items.append({
                "lhs": lhs,
                "rhs": list(rhs),
                "dot": dot,
                "lookahead": la
            })
        result.append(items)
    return result


def serialise_table(action, goto_table):
    action_out = {}
    for (state, sym), val in action.items():
        action_out[f"{state},{sym}"] = list(val)

    goto_out = {}
    for (state, sym), j in goto_table.items():
        goto_out[f"{state},{sym}"] = j

    return action_out, goto_out