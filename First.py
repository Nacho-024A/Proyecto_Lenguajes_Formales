# ------------------------------------------------------------
# FIRST (versión mejorada con detección de recursión)
# ------------------------------------------------------------
EPSILON = 'ε'
END = '$'

def compute_first(grammar):
    FIRST = {nt: set() for nt in grammar}

    def first(symbol, visited=None):
        if visited is None:
            visited = set()

        # Evitar bucles infinitos si hay recursividad izquierda
        if symbol in visited:
            # Aviso opcional
            print(f"[Aviso] Posible recursividad detectada en FIRST({symbol})")
            return set()
        visited.add(symbol)

        # Caso base: terminal o epsilon
        if symbol not in grammar:
            return {symbol}

        result = set()
        for prod in grammar[symbol]:
            for Y in prod:
                f = first(Y, visited.copy())
                result |= (f - {EPSILON})
                if EPSILON not in f:
                    break
            else:
                result.add(EPSILON)
        return result

    # Bucle iterativo hasta converger
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
