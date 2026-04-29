def closure(items, grammar, first, first_of_string):
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


def goto(items, symbol, grammar, first, closure_fn):
    moved = set()

    for (lhs, rhs, dot, lookahead) in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((lhs, rhs, dot + 1, lookahead))

    return closure_fn(moved, grammar, first)