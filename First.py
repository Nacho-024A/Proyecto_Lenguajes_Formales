# ------------------------------------------------------------
# FIRST
# ------------------------------------------------------------
EPSILON = 'ε'
END = '$'

def compute_first(grammar):
    FIRST = {nt: set() for nt in grammar}

    def first(symbol):
        # terminal o epsilon
        if symbol not in grammar:
            return {symbol}
        result = set()
        for prod in grammar[symbol]:
            for Y in prod:
                f = first(Y)
                result |= (f - {EPSILON})
                if EPSILON not in f:
                    break
            else:
                result.add(EPSILON)
        return result

    changed = True
    while changed:
        changed = False
        for A in grammar:
            before = set(FIRST[A])
            for rhs in grammar[A]:
                for Y in rhs:
                    f = first(Y)
                    FIRST[A] |= (f - {EPSILON})
                    if EPSILON not in f:
                        break
                else:
                    FIRST[A].add(EPSILON)
            if before != FIRST[A]:
                changed = True
    return FIRST
