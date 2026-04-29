def parse(tokens, action, goto_table):
    stack = [0]
    tokens = list(tokens) + ["$"]
    pointer = 0
    steps = []

    while True:
        state = stack[-1]
        token = tokens[pointer]

        if (state, token) not in action:
            return False, steps

        act = action[(state, token)]

        if act[0] == "shift":
            stack.append(act[1])
            pointer += 1

        elif act[0] == "reduce":
            lhs, rhs = act[1], act[2]
            for _ in rhs:
                stack.pop()
            stack.append(goto_table[(stack[-1], lhs)])

        elif act[0] == "accept":
            return True, steps