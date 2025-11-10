from colorama import Fore, Style
from tabulate import tabulate

# ------------------------------------------------------------
# PARSER LL(1)
# ------------------------------------------------------------
def parse_ll1(tokens, grammar, table, start):
    EPSILON = 'ε'
    END = '$'

    stack = [END, start]
    tokens = tokens + [END]
    i = 0

    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Análisis LL(1) paso a paso ===" + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + "---------------------------------------------")

    # Tabla inicial
    print(tabulate(
        [["Pila", "Entrada", "Acción"]],
        tablefmt="fancy_grid"
    ))

    while stack:
        top = stack.pop()
        current = tokens[i]

        pila_str = ' '.join(stack + [top])
        entrada_str = ' '.join(tokens[i:])

        if top == END and current == END:
            print(tabulate([[Fore.YELLOW + pila_str + Style.RESET_ALL,
                             Fore.CYAN + entrada_str + Style.RESET_ALL,
                             Fore.GREEN + "Cadena aceptada (LL(1))" + Style.RESET_ALL]],
                           tablefmt="fancy_grid"))
            return True

        elif top not in grammar:  # terminal
            if top == current:
                print(tabulate([[Fore.YELLOW + pila_str + Style.RESET_ALL,
                                 Fore.CYAN + entrada_str + Style.RESET_ALL,
                                 Fore.GREEN + f"Coincide '{top}'" + Style.RESET_ALL]],
                               tablefmt="fancy_grid"))
                i += 1
            else:
                print(tabulate([[Fore.YELLOW + pila_str + Style.RESET_ALL,
                                 Fore.CYAN + entrada_str + Style.RESET_ALL,
                                 Fore.RED + f"Error: se esperaba '{top}', se encontró '{current}'" + Style.RESET_ALL]],
                               tablefmt="fancy_grid"))
                return False

        else:
            rule = table.get((top, current))
            if not rule:
                print(tabulate([[Fore.YELLOW + pila_str + Style.RESET_ALL,
                                 Fore.CYAN + entrada_str + Style.RESET_ALL,
                                 Fore.RED + f"Error: no hay regla para [{top}, {current}]" + Style.RESET_ALL]],
                               tablefmt="fancy_grid"))
                return False

            accion = f"Usando producción: {top} → {' '.join(rule)}"
            print(tabulate([[Fore.YELLOW + pila_str + Style.RESET_ALL,
                             Fore.CYAN + entrada_str + Style.RESET_ALL,
                             Fore.LIGHTGREEN_EX + accion + Style.RESET_ALL]],
                           tablefmt="fancy_grid"))

            for sym in reversed(rule):
                if sym != EPSILON:
                    stack.append(sym)

    return False
