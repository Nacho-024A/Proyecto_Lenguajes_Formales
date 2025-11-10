# Main.py - Menú interactivo
from First import compute_first
from Follow import compute_follow, first_of_seq
from LL_1_ import build_ll1_table
from ParserLL1 import parse_ll1
from SLR1 import build_slr_tables, parse_slr, EPSILON, END
from colorama import Fore, Style, init
from tabulate import tabulate
import os

init(autoreset=True)

#------------------------------------------------------------
# Encabezado del programa
#------------------------------------------------------------
def mostrar_encabezado():
    info = [
        [Fore.LIGHTGREEN_EX + "Proyecto:" + Style.RESET_ALL, "Analizador Sintáctico LL(1) y SLR(1)"],
        [Fore.LIGHTGREEN_EX + "Autores:" + Style.RESET_ALL, "Andres Osorio - William Villa - Gisel Jaramillo"],
        [Fore.LIGHTGREEN_EX + "Universidad:" + Style.RESET_ALL, "EAFIT"],
        [Fore.LIGHTGREEN_EX + "Asignatura:" + Style.RESET_ALL, "Lenguajes Formales (Clase 5464)"],
        [Fore.LIGHTGREEN_EX + "Versión:" + Style.RESET_ALL, "2.4 — Noviembre 2025"],
        [Fore.LIGHTGREEN_EX + "Descripción:" + Style.RESET_ALL, "Implementación modular de analizadores LL(1) y SLR(1) con salida formateada."]
    ]

    print("\n" + Fore.CYAN + Style.BRIGHT + "========================================================================================" + Style.RESET_ALL)
    print(tabulate(info, tablefmt="fancy_grid"))
    print(Fore.LIGHTBLACK_EX + "-----------------------------------------------------------------------------------" + Style.RESET_ALL)

# ------------------------------------------------------------
# Utilidades: leer gramática desde archivo (formato simple)
# ------------------------------------------------------------
def cargar_gramatica():
    nombre = input(Fore.CYAN + "\nIngrese el nombre del archivo de gramática (ej: gramatica.txt): " + Style.RESET_ALL)
    
    # Obtener la ruta absoluta del directorio donde está Main.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, nombre)
    
    if not os.path.exists(ruta):
        print(Fore.RED + f"No se encontró el archivo '{nombre}'. Debe estar en la misma carpeta que Main.py." + Style.RESET_ALL)
        print(Fore.YELLOW + f"(Ruta buscada: {ruta})" + Style.RESET_ALL)
        return None, None

    grammar = {}
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or "->" not in linea:
                continue
            izquierda, derecha = linea.split("->")
            izquierda = izquierda.strip()
            producciones = [p.strip().split() for p in derecha.split("|")]
            grammar[izquierda] = producciones

    start_symbol = list(grammar.keys())[0]
    
    # Preparar datos para la tabla
    tabla_datos = []
    for no_terminal, producciones in grammar.items():
        for i, prod in enumerate(producciones):
            prod_str = " ".join(prod) if prod else "ε"
            if i == 0:
                tabla_datos.append([no_terminal, "→", prod_str])
            else:
                tabla_datos.append(["", "|", prod_str])
    
    # Mostrar tabla
    print(Fore.CYAN + f"\n{'='*50}")
    print(f"  GRAMÁTICA CARGADA - Símbolo Inicial: {Fore.MAGENTA}{start_symbol}{Fore.CYAN}")
    print(f"{'='*50}" + Style.RESET_ALL)
    print(tabulate(tabla_datos, headers=["No Terminal", "", "Producción"], tablefmt="fancy_grid"))
    
    return grammar, start_symbol

# ------------------------------------------------------------
# Pedir cadena (tokens separados por espacio)
# ------------------------------------------------------------
def pedir_tokens():
    linea = input(Fore.CYAN + "Ingrese la cadena (tokens separados por espacio): " + Style.RESET_ALL)
    tokens = linea.strip().split()
    print(Fore.YELLOW + f"Tokens: {tokens}" + Style.RESET_ALL)
    return tokens

# ------------------------------------------------------------
# Mostrar FIRST y FOLLOW con tabulate
# ------------------------------------------------------------
def mostrar_first_follow(grammar, start):
    FIRST = compute_first(grammar)
    FOLLOW = compute_follow(grammar, FIRST, start)

    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Conjuntos FIRST ===" + Style.RESET_ALL)
    print(tabulate([(A, ', '.join(sorted(FIRST[A], key=lambda x: (x != EPSILON, x)))) for A in FIRST],
                   headers=["No Terminal", "FIRST"], tablefmt="fancy_grid"))

    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Conjuntos FOLLOW ===" + Style.RESET_ALL)
    print(tabulate([(A, ', '.join(sorted(FOLLOW[A], key=lambda x: (x != EPSILON, x)))) for A in FOLLOW],
                   headers=["No Terminal", "FOLLOW"], tablefmt="fancy_grid"))
    return FIRST, FOLLOW

# ------------------------------------------------------------
# Mostrar tabla LL(1)
# ------------------------------------------------------------
def mostrar_tabla_ll1(grammar, FIRST, FOLLOW):
    table = build_ll1_table(grammar, FIRST, FOLLOW)
    rows = []
    for (A, a), rhs in sorted(table.items()):
        rows.append((A, a, ' '.join(rhs)))
    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Tabla LL(1) ===" + Style.RESET_ALL)
    if rows:
        print(tabulate(rows, headers=["No Terminal", "Terminal", "Producción"], tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "La tabla LL(1) está vacía (gramática posiblemente no válida)." + Style.RESET_ALL)
    return table

# ------------------------------------------------------------
# Mostrar tabla ACTION / GOTO (resumen)
# ------------------------------------------------------------
def mostrar_tablas_slr(ACTION, GOTO, max_rows=30):
    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Tabla ACTION (resumen) ===" + Style.RESET_ALL)
    rows = [ (str(k), str(v)) for k, v in list(ACTION.items())[:max_rows] ]
    print(tabulate(rows, headers=["(Estado, Símbolo)", "Acción"], tablefmt="fancy_grid"))

    print("\n" + Fore.CYAN + Style.BRIGHT + "=== Tabla GOTO (resumen) ===" + Style.RESET_ALL)
    rows = [ (str(k), str(v)) for k, v in list(GOTO.items())[:max_rows] ]
    print(tabulate(rows, headers=["(Estado, NoTerminal)", "Destino"], tablefmt="fancy_grid"))

# ------------------------------------------------------------
# Menu principal
# ------------------------------------------------------------
def menu():
    grammar = None
    start = None
    FIRST = None
    FOLLOW = None
    LL1_TABLE = None
    ACTION = None
    GOTO = None

    while True:

        print("\n" + Fore.MAGENTA + Style.BRIGHT + "=== MENÚ PRINCIPAL ===" + Style.RESET_ALL)
        print("1) Cargar gramática desde archivo")
        print("2) Mostrar FIRST y FOLLOW")
        print("3) Mostrar Tabla LL(1)")
        print("4) Ejecutar Parser LL(1)")
        print("5) Construir y mostrar tablas SLR(1)")
        print("6) Ejecutar Parser SLR(1)")
        print("7) Salir")

        opcion = input(Fore.CYAN + "Elige una opción [1-7]: " + Style.RESET_ALL).strip()

        if opcion == "1":
            g, s = cargar_gramatica()
            if g:
                grammar = g
                start = s
                FIRST = None; FOLLOW = None; LL1_TABLE = None; ACTION = None; GOTO = None

        elif opcion == "2":
            if not grammar:
                print(Fore.RED + "Primero carga una gramática (opción 1)." + Style.RESET_ALL)
                continue
            FIRST, FOLLOW = mostrar_first_follow(grammar, start)

        elif opcion == "3":
            if not grammar:
                print(Fore.RED + "Primero carga una gramática (opción 1)." + Style.RESET_ALL)
                continue
            if FIRST is None or FOLLOW is None:
                FIRST = compute_first(grammar)
                FOLLOW = compute_follow(grammar, FIRST, start)
            LL1_TABLE = mostrar_tabla_ll1(grammar, FIRST, FOLLOW)

        elif opcion == "4":
            if not grammar:
                print(Fore.RED + "Primero carga una gramática (opción 1)." + Style.RESET_ALL)
                continue
            if LL1_TABLE is None:
                FIRST = compute_first(grammar)
                FOLLOW = compute_follow(grammar, FIRST, start)
                LL1_TABLE = build_ll1_table(grammar, FIRST, FOLLOW)
            tokens = pedir_tokens()
            print(Fore.YELLOW + "\n--- Ejecución LL(1) ---" + Style.RESET_ALL)
            ok = parse_ll1(tokens, grammar, LL1_TABLE, start)
            print(Fore.GREEN + f"Resultado: {'ACEPTADA' if ok else 'RECHAZADA'}" + Style.RESET_ALL)

        elif opcion == "5":
            if not grammar:
                print(Fore.RED + "Primero carga una gramática (opción 1)." + Style.RESET_ALL)
                continue
            FIRST = compute_first(grammar)
            FOLLOW = compute_follow(grammar, FIRST, start)
            ACTION, GOTO = build_slr_tables(grammar, FIRST, FOLLOW, start)
            mostrar_tablas_slr(ACTION, GOTO)

        elif opcion == "6":
            if not grammar:
                print(Fore.RED + "Primero carga una gramática (opción 1)." + Style.RESET_ALL)
                continue
            if ACTION is None or GOTO is None:
                FIRST = compute_first(grammar)
                FOLLOW = compute_follow(grammar, FIRST, start)
                ACTION, GOTO = build_slr_tables(grammar, FIRST, FOLLOW, start)
            tokens = pedir_tokens()
            print(Fore.YELLOW + "\n--- Ejecución SLR(1) ---" + Style.RESET_ALL)
            ok = parse_slr(tokens, ACTION, GOTO, start)
            print(Fore.GREEN + f"Resultado: {'ACEPTADA' if ok else 'RECHAZADA'}" + Style.RESET_ALL)

        elif opcion == "7":
            print(Fore.CYAN + "Saliendo." + Style.RESET_ALL)
            break

        else:
            print(Fore.RED + "Opción inválida. Intenta otra vez." + Style.RESET_ALL)

if __name__ == "__main__":
    mostrar_encabezado()
    menu()

