from flask import Flask, request, jsonify, send_from_directory
from collections import defaultdict, deque
import os

app = Flask(__name__)


def get_terminals(grammar):
    terminals = set()
    for prods in grammar.values():
        for prod in prods:
            for symbol in prod:
                if symbol not in grammar:
                    terminals.add(symbol)
    terminals.add("$")
    return list(terminals)


def compute_first(grammar, terminals):
    first = defaultdict(set)
    for t in terminals:
        first[t].add(t)
    changed = True
    while changed:
        changed = False
        for nt in grammar:
            for prod in grammar[nt]:
                for symbol in prod:
                    before = len(first[nt])
                    first[nt] |= first[symbol]
                    if len(first[nt]) > before:
                        changed = True
                    break
    return first


def first_of_string(symbols, first):
    result = set()
    for symbol in symbols:
        result |= first[symbol]
        break
    return result


def closure(items, grammar, first):
    closure_set = set(items)
    while True:
        new_items = set()
        for (lhs, rhs, dot, lookahead) in closure_set:
            if dot < len(rhs):
                B = rhs[dot]
                if B in grammar:
                    beta = rhs[dot + 1:]
                    beta_lookahead = list(beta) + [lookahead]
                    first_beta = first_of_string(beta_lookahead, first)
                    for prod in grammar[B]:
                        for b in first_beta:
                            new_items.add((B, tuple(prod), 0, b))
        if new_items.issubset(closure_set):
            break
        closure_set |= new_items
    return frozenset(closure_set)


def goto(items, symbol, grammar, first):
    moved = set()
    for (lhs, rhs, dot, lookahead) in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((lhs, rhs, dot + 1, lookahead))
    return closure(moved, grammar, first)


def build_canonical_collection(grammar, start_symbol, terminals, non_terminals, first):
    augmented_start = start_symbol + "'"
    grammar[augmented_start] = [[start_symbol]]
    non_terminals = [augmented_start] + non_terminals

    start_item = (augmented_start, tuple([start_symbol]), 0, "$")
    start_state = closure([start_item], grammar, first)

    states = [start_state]
    queue = deque([start_state])

    while queue:
        state = queue.popleft()
        for symbol in terminals + non_terminals:
            next_state = goto(state, symbol, grammar, first)
            if next_state and next_state not in states:
                states.append(next_state)
                queue.append(next_state)

    return states, augmented_start


def build_parsing_table(states, grammar, terminals, non_terminals, augmented_start):
    action = {}
    goto_table = {}
    conflicts = []

    for i, state in enumerate(states):
        for (lhs, rhs, dot, lookahead) in state:
            if dot < len(rhs):
                symbol = rhs[dot]
                moved_items = set()
                for (l2, r2, d2, la2) in state:
                    if d2 < len(r2) and r2[d2] == symbol:
                        moved_items.add((l2, r2, d2 + 1, la2))
                j = None
                for idx, s in enumerate(states):
                    if moved_items and all(item in s for item in moved_items):
                        j = idx
                        break
                if j is None:
                    continue
                if symbol in terminals:
                    entry = ("shift", j)
                    if (i, symbol) in action and action[(i, symbol)] != entry:
                        conflicts.append((i, symbol))
                    action[(i, symbol)] = entry
                elif symbol in grammar:
                    goto_table[(i, symbol)] = j
            else:
                if lhs == augmented_start:
                    action[(i, "$")] = ("accept",)
                else:
                    entry = ("reduce", lhs, rhs)
                    if (i, lookahead) in action and action[(i, lookahead)] != entry:
                        conflicts.append((i, lookahead))
                    action[(i, lookahead)] = entry

    return action, goto_table, conflicts


def parse(tokens, action, goto_table):
    stack = [0]
    tokens = list(tokens) + ["$"]
    pointer = 0
    steps = []

    while True:
        state = stack[-1]
        token = tokens[pointer]
        step = {
            "stack": list(stack),
            "input": tokens[pointer:],
            "action": None,
            "status": "running"
        }

        if (state, token) not in action:
            step["action"] = f"Error — no action for state {state}, token '{token}'"
            step["status"] = "error"
            steps.append(step)
            return False, steps

        act = action[(state, token)]

        if act[0] == "shift":
            step["action"] = f"Shift  →  go to state {act[1]}"
            steps.append(step)
            stack.append(act[1])
            pointer += 1

        elif act[0] == "reduce":
            lhs, rhs = act[1], act[2]
            step["action"] = f"Reduce   {lhs}  →  {' '.join(rhs) if rhs else 'ε'}"
            steps.append(step)
            for _ in rhs:
                stack.pop()
            top = stack[-1]
            stack.append(goto_table[(top, lhs)])

        elif act[0] == "accept":
            step["action"] = "Accept"
            step["status"] = "accept"
            steps.append(step)
            return True, steps



def parse_grammar_text(text):
    grammar = {}
    for line in text.strip().split('\n'):
        if '->' not in line:
            continue
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
        prods = [p.strip().split() for p in rhs.split('|')]
        if lhs:
            grammar[lhs] = prods
    return grammar



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


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/parse", methods=["POST"])
def api_parse():
    data         = request.json
    grammar_text = data.get("grammar", "")
    start        = data.get("start", "").strip()
    tokens       = data.get("tokens", [])

    try:
        grammar       = parse_grammar_text(grammar_text)
        non_terminals = list(grammar.keys())
        terminals     = get_terminals(grammar)
        first         = compute_first(grammar, terminals)
        states, aug   = build_canonical_collection(grammar, start, terminals, non_terminals, first)
        action, goto_table, conflicts = build_parsing_table(states, grammar, terminals, non_terminals, aug)
        accepted, steps = parse(tokens, action, goto_table)
        action_out, goto_out = serialise_table(action, goto_table)

        return jsonify({
            "accepted":    accepted,
            "steps":       steps,
            "states":      serialise_states(states),
            "action":      action_out,
            "goto":        goto_out,
            "terminals":   terminals,
            "non_terminals": [nt for nt in non_terminals if not nt.endswith("'")],
            "num_states":  len(states),
            "conflicts":   len(conflicts)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/build", methods=["POST"])
def api_build():
    data         = request.json
    grammar_text = data.get("grammar", "")
    start        = data.get("start", "").strip()

    try:
        grammar       = parse_grammar_text(grammar_text)
        non_terminals = list(grammar.keys())
        terminals     = get_terminals(grammar)
        first         = compute_first(grammar, terminals)
        states, aug   = build_canonical_collection(grammar, start, terminals, non_terminals, first)
        action, goto_table, conflicts = build_parsing_table(states, grammar, terminals, non_terminals, aug)
        action_out, goto_out = serialise_table(action, goto_table)

        return jsonify({
            "states":        serialise_states(states),
            "action":        action_out,
            "goto":          goto_out,
            "terminals":     terminals,
            "non_terminals": [nt for nt in non_terminals if not nt.endswith("'")],
            "num_states":    len(states),
            "conflicts":     len(conflicts)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    print("Starting LR(1) Parser server at http://localhost:5000")
    app.run(debug=True, port=5000)