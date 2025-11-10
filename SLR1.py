# ================================================================
# SLR(1) Parser
# ================================================================
from colorama import Fore, Style
from tabulate import tabulate

EPSILON = 'ε'
END = '$'

# ------------------------------------------------------------
# CLOSURE
# ------------------------------------------------------------
def closure(G, items):
    items = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for (A, prod, dot) in items:
            if dot < len(prod):
                X = prod[dot]
                if X in G:
                    for prod_X in G[X]:
                        if prod_X == [EPSILON]:
                            new_items.add((X, tuple(), 0))  # manejo explícito de epsilon
                        else:
                            new_item = (X, tuple(prod_X), 0)
                            if new_item not in items:
                                new_items.add(new_item)
        if not new_items.issubset(items):
            items |= new_items
            changed = True
    return items

# ------------------------------------------------------------
# GOTO
# ------------------------------------------------------------
def goto(G, items, symbol):
    moved = set()
    for (A, prod, dot) in items:
        if dot < len(prod) and prod[dot] == symbol:
            moved.add((A, prod, dot + 1))
    if not moved:
        return set()
    return closure(G, moved)

# ------------------------------------------------------------
# COLECCIÓN CANÓNICA DE ITEMS
# ------------------------------------------------------------
def canonical_collection(grammar, start):
    augmented = {"S'": [[start]]}
    G = {**augmented, **grammar}
    start_item = ("S'", tuple(G["S'"][0]), 0)
    C = [closure(G, {start_item})]

    changed = True
    while changed:
        changed = False
        for I in list(C):
            symbols = {prod[dot] for (A, prod, dot) in I if dot < len(prod)}
            for X in symbols:
                J = goto(G, I, X)
                if J and J not in C:
                    C.append(J)
                    changed = True
    return C, G

# ------------------------------------------------------------
# CONSTRUCCIÓN DE TABLAS ACTION y GOTO
# ------------------------------------------------------------
def build_slr_tables(grammar, FIRST, FOLLOW, start):
    C, G = canonical_collection(grammar, start)
    ACTION, GOTO = {}, {}

    for i, I in enumerate(C):
        for (A, prod, dot) in I:
            # ----------------------------------------------------------
            # Caso 1: desplazamiento (shift)
            # ----------------------------------------------------------
            if dot < len(prod):
                a = prod[dot]
                j_set = goto(G, I, a)

                if not j_set:
                    continue

                # Si 'a' es terminal -> tabla ACTION
                if a not in G:
                    for idx, s in enumerate(C):
                        if s == j_set:  # comparar por contenido, no por referencia
                            ACTION[(i, a)] = ("shift", idx)
                            break

                # Si 'a' es no terminal -> tabla GOTO
                else:
                    for idx, s in enumerate(C):
                        if s == j_set:
                            GOTO[(i, a)] = idx
                            break

            # ----------------------------------------------------------
            # Caso 2: reducción o aceptación
            # ----------------------------------------------------------
            else:
                if A != "S'":
                    for b in FOLLOW.get(A, set()):
                        # Evitar sobrescribir conflictos sin aviso
                        if (i, b) in ACTION:
                            print(f"⚠️ Conflicto en ({i}, {b}): {ACTION[(i, b)]} vs reduce {A} -> {' '.join(prod)}")
                        ACTION[(i, b)] = ("reduce", (A, prod))
                else:
                    ACTION[(i, END)] = ("accept",)

    return ACTION, GOTO

# ------------------------------------------------------------
# PARSER SLR(1) CON SALIDA FORMATEADA
# ------------------------------------------------------------
def parse_slr(tokens, ACTION, GOTO, start):
    tokens = tokens + [END]
    stack = [0]            # pila: alterna [ ... , símbolo, estado ] pero inicia con solo estado 0
    i = 0

    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Análisis SLR(1) paso a paso ===" + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + "---------------------------------------------")

    print(tabulate(
        [["Pila", "Entrada", "Acción"]],
        tablefmt="fancy_grid"
    ))

    while True:
        s = stack[-1]              # estado en cima
        a = tokens[i]
        act = ACTION.get((s, a))

        # representación de pila para mostrarla (mezcla de símbolos y estados)
        pila_str = ' '.join(map(str, stack))
        entrada_str = ' '.join(tokens[i:])

        # Si no hay acción -> error
        if not act:
            print(tabulate([[
                Fore.YELLOW + pila_str + Style.RESET_ALL,
                Fore.CYAN + entrada_str + Style.RESET_ALL,
                Fore.RED + f"Error: no hay acción para ({s}, {a})" + Style.RESET_ALL
            ]], tablefmt="fancy_grid"))
            return False

        # SHIFT: empuja símbolo (a) y estado j
        if act[0] == "shift":
            j = act[1]
            accion = f"Shift → Estado {j}"
            print(tabulate([[
                Fore.YELLOW + pila_str + Style.RESET_ALL,
                Fore.CYAN + entrada_str + Style.RESET_ALL,
                Fore.LIGHTGREEN_EX + accion + Style.RESET_ALL
            ]], tablefmt="fancy_grid"))

            # empujar símbolo y estado (estructura clásica LR)
            stack.append(a)   # símbolo (terminal)
            stack.append(j)   # estado
            i += 1
            continue

        # REDUCE
        if act[0] == "reduce":
            A, rhs = act[1]   # rhs puede ser tuple() para ε
            # cantidad de símbolos (excluyendo EPSILON). Si rhs vacío -> 0
            count_symbols = len([x for x in rhs if x != EPSILON]) if rhs else 0
            accion_desc = f"Reduciendo por {A} → {' '.join(rhs) if rhs else 'ε'}"
            print(tabulate([[
                Fore.YELLOW + pila_str + Style.RESET_ALL,
                Fore.CYAN + entrada_str + Style.RESET_ALL,
                Fore.LIGHTYELLOW_EX + accion_desc + Style.RESET_ALL
            ]], tablefmt="fancy_grid"))

            # pop 2 * count_symbols entradas (símbolo+estado por cada símbolo)
            k = count_symbols * 2
            if k:
                stack = stack[:-k]
            # ahora el estado de cima
            s_prime = stack[-1]

            # pushear el no terminal A y el estado goto(s_prime, A)
            goto_state = GOTO.get((s_prime, A))
            if goto_state is None:
                print(tabulate([[
                    Fore.YELLOW + ' '.join(map(str, stack)) + Style.RESET_ALL,
                    Fore.CYAN + entrada_str + Style.RESET_ALL,
                    Fore.RED + f"Error: no hay GOTO para ({s_prime}, {A}) tras reducción" + Style.RESET_ALL
                ]], tablefmt="fancy_grid"))
                return False

            stack.append(A)
            stack.append(goto_state)

            # mostrar la acción resultante (ya con el nuevo estado)
            print(tabulate([[
                Fore.YELLOW + ' '.join(map(str, stack)) + Style.RESET_ALL,
                Fore.CYAN + entrada_str + Style.RESET_ALL,
                Fore.LIGHTGREEN_EX + f"GOTO({s_prime}, {A}) = {goto_state}" + Style.RESET_ALL
            ]], tablefmt="fancy_grid"))
            continue

        # ACCEPT
        if act[0] == "accept":
            print(tabulate([[
                Fore.YELLOW + pila_str + Style.RESET_ALL,
                Fore.CYAN + entrada_str + Style.RESET_ALL,
                Fore.GREEN + "Cadena aceptada (SLR(1))" + Style.RESET_ALL
            ]], tablefmt="fancy_grid"))
            return True
# ================================================================

