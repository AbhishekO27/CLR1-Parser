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