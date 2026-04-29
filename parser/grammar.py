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


def get_terminals(grammar):
    terminals = set()
    for prods in grammar.values():
        for prod in prods:
            for symbol in prod:
                if symbol not in grammar:
                    terminals.add(symbol)
    terminals.add("$")
    return list(terminals)