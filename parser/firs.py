from collections import defaultdict

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