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
            step["action"] = f"Error — state {state}, token '{token}'"
            step["status"] = "error"
            steps.append(step)
            return False, steps

        act = action[(state, token)]

        if act[0] == "shift":
            step["action"] = f"Shift → {act[1]}"
            stack.append(act[1])
            pointer += 1

        elif act[0] == "reduce":
            lhs, rhs = act[1], act[2]
            for _ in rhs:
                stack.pop()
            stack.append(goto_table[(stack[-1], lhs)])

        else:
            step["action"] = "Accept"
            step["status"] = "accept"
            steps.append(step)
            return True, steps

        steps.append(step)