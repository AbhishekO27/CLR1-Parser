from collections import deque

def build_canonical_collection(grammar, start_symbol, terminals, non_terminals, first, closure, goto):
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