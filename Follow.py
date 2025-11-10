# ------------------------------------------------------------
# FOLLOW
# ------------------------------------------------------------
EPSILON = 'ε'
END = '$'
def first_of_seq(seq, FIRST):
    res = set()
    for X in seq:
        fx = FIRST.get(X, {X})
        res |= (fx - {EPSILON})
        if EPSILON not in fx:
            return res
    res.add(EPSILON)
    return res

def compute_follow(grammar, FIRST, start):
    FOLLOW = {nt: set() for nt in grammar}
    FOLLOW[start].add(END)
    changed = True
    while changed:
        changed = False
        for A in grammar:
            for rhs in grammar[A]:
                for i, B in enumerate(rhs):
                    if B in grammar:  # no terminal
                        beta = rhs[i+1:]
                        first_beta = first_of_seq(beta, FIRST)
                        before = set(FOLLOW[B])
                        FOLLOW[B] |= (first_beta - {EPSILON})
                        if EPSILON in first_beta or not beta:
                            FOLLOW[B] |= FOLLOW[A]
                        if before != FOLLOW[B]:
                            changed = True
    return FOLLOW
