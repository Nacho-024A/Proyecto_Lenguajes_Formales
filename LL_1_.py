from Follow import first_of_seq
from colorama import Fore, Style, init
from tabulate import tabulate
# ------------------------------------------------------------
# TABLA LL(1)
# ------------------------------------------------------------
EPSILON = 'ε'
END = '$'

def build_ll1_table(grammar, FIRST, FOLLOW):
    table = {}
    for A in grammar:
        for rhs in grammar[A]:
            first = first_of_seq(rhs, FIRST)
            for t in (first - {EPSILON}):
                if (A, t) in table:
                    print(Fore.RED + f"Conflicto LL(1): ({A}, {t}) ya tiene una producción definida." + Style.RESET_ALL)
                table[(A, t)] = rhs
            if EPSILON in first:
                for b in FOLLOW[A]:
                    if (A, b) in table:
                        print(Fore.RED + f"Conflicto LL(1): ({A}, {b}) ya tiene una producción definida." + Style.RESET_ALL)
                    table[(A, b)] = rhs
    return table