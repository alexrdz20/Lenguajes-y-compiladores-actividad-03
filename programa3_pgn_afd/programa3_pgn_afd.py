# -*- coding: utf-8 -*-
# ============================================================
# programa3_pgn_afd.py
# Tema 3 - Lenguajes y Gramaticas Formales  (UNEG 2026-I)
# Sección 2.4: De la Expresión al Autómata (Caso: Ajedrez PGN)
#
# Subconjunto PGN aceptado (movimientos básicos):
#   1. Movimientos de peón:        e4   d5   exd5
#   2. Movimientos de pieza:       Nf3  Bxc4  Qd1
#   3. Enroques:                   O-O  O-O-O
#   4. Promoción de peón:          e8=Q  d1=N
#   5. Jaque / Jaque mate:         +  o  #  al final (opcional)
#
# Gramática informal del subconjunto:
#   movimiento → pieza? columna_origen? fila_origen? captura? columna fila (=pieza_promo)? sufijo?
#              | O-O(-O)?   sufijo?
#
#   donde:
#     pieza        = K|Q|R|B|N
#     columna      = a|b|c|d|e|f|g|h
#     fila         = 1|2|3|4|5|6|7|8
#     captura      = x
#     pieza_promo  = Q|R|B|N
#     sufijo       = +|#
#
# Expresión Regular (ER):
#   ^([KQRBN][a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?|[a-h][1-8]?x?[a-h]?[1-8](=[QRBN])?|O-O(-O)?)[+#]?$
#
# Autómata Finito Determinístico (AFD):
#   Se modela con 10 estados explícitos más estado trampa.
#   La tabla de transiciones cubre todas las categorías de
#   caracteres relevantes en notación PGN.
# ============================================================

import re

# ============================================================
#   CONSTANTES DE CATEGORÍAS DE CARACTERES
# ============================================================
CAT_PIEZA      = "PIEZA"      # K Q R B N
CAT_COLUMNA    = "COLUMNA"    # a-h
CAT_FILA       = "FILA"       # 1-8
CAT_CAPTURA    = "CAPTURA"    # x
CAT_IGUAL      = "IGUAL"      # =
CAT_PROMO      = "PROMO"      # Q R B N (tras =)
CAT_JAQUE      = "JAQUE"      # + #
CAT_GUION      = "GUION"      # -
CAT_O          = "O"          # O (enroque)
CAT_INVALIDO   = "INVALIDO"


def categoria(ch: str, estado: int) -> str:
    """
    Clasifica un carácter en su categoría según el estado actual.
    En estado 7 (tras '=') la letra es PROMO, no PIEZA ni COLUMNA.
    """
    if ch in "KQRBN":
        if estado == 7:            # tras '=' sólo puede ser pieza de promoción
            return CAT_PROMO
        return CAT_PIEZA
    if ch in "abcdefgh":
        return CAT_COLUMNA
    if ch in "12345678":
        return CAT_FILA
    if ch == "x":
        return CAT_CAPTURA
    if ch == "=":
        return CAT_IGUAL
    if ch in "+#":
        return CAT_JAQUE
    if ch == "-":
        return CAT_GUION
    if ch == "O":
        return CAT_O
    return CAT_INVALIDO


# ============================================================
#   TABLA DE TRANSICIONES DEL AFD
#
#  Diseno de estados:
#   q0  -> estado inicial
#   q1  -> leida una PIEZA (K/Q/R/B/N) al inicio
#   q2  -> leida una COLUMNA como primer caracter
#   q3  -> leida una COLUMNA como destino (tras pieza o columna+captura)
#   q4  -> leida una FILA de destino  -> estado ACEPTACION principal
#   q5  -> leido '=' (espera pieza de promocion)
#   q6  -> leida pieza de promocion  -> ACEPTACION con promocion
#   q7  -> leido '+' o '#'  -> ACEPTACION con jaque/mate
#   q8  -> leida 'O' (inicio enroque)
#   q9  -> leido 'O-' (guion enroque)
#   q10 -> leido 'O-O' -> ACEPTACION (enroque corto)
#   q11 -> leido 'O-O-' (en camino a enroque largo)
#   q12 -> leida captura 'x' o ultimo 'O' del enroque largo
#   q13 -> leida FILA de origen tras pieza (R1e4, Q3d5)
#   qT  -> estado trampa (error)
#
#  Estados de aceptacion: {q4, q6, q7, q10, q12}
# ============================================================

TRAMPA = "qT"

TABLA = {
    #  estado  ┃  PIEZA      COLUMNA   FILA    CAPTURA  IGUAL   PROMO   JAQUE   GUION   O
    "q0": {
        CAT_PIEZA:    "q1",
        CAT_COLUMNA:  "q2",
        CAT_O:        "q8",
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q1: ya leímos una PIEZA (p.ej. 'N' o 'R') ───────────
    "q1": {
        CAT_COLUMNA:  "q3",   # Nf → columna destino
        CAT_CAPTURA:  "q12",  # Nx → captura
        CAT_FILA:     "q13",  # R1 → desambiguacion por fila (R1e4)
        CAT_PIEZA:    TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q2: leímos una COLUMNA como primer carácter (peón) ────
    "q2": {
        CAT_FILA:     "q4",   # e4 → aceptación (movimiento de peón)
        CAT_CAPTURA:  "q12",  # ex → captura de peón
        CAT_COLUMNA:  "q3",   # columna_orig + columna_dest (con origen desambiguado)
        CAT_PIEZA:    TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # -- q3: columna de origen/intermedia (tras pieza) ---------
    #   puede ser columna_origen (Nbd2) o columna_destino directa
    "q3": {
        CAT_FILA:     "q4",   # Nf3 -> aceptacion
        CAT_CAPTURA:  "q12",  # Nfx -> captura con origen completo
        CAT_COLUMNA:  "q3",   # Nbd -> segunda columna (destino real, Nbd2)
        CAT_PIEZA:    TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q4: FILA de destino → ACEPTACIÓN ─────────────────────
    "q4": {
        CAT_IGUAL:    "q5",   # e8= → promoción
        CAT_JAQUE:    "q7",   # Nf3+ → jaque
        # fin de cadena → aceptación, resto inválido
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q5: leímos '=' → esperamos pieza de promoción ────────
    "q5": {
        CAT_PROMO:    "q6",   # =Q → promoción aceptada
        # en q5, la categoría de K/Q/R/B/N la determina categoria()
        # devolviendo PROMO porque estado==7 en el recorrido
        # (nota: q5 internamente == índice 5, la función usa q5 ≡ 5)
        CAT_PIEZA:    "q6",   # fallback por si el clasificador no está en q7
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q6: pieza de promoción → ACEPTACIÓN ──────────────────
    "q6": {
        CAT_JAQUE:    "q7",
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q7: '+' o '#' → ACEPTACIÓN final ─────────────────────
    "q7": {
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q8: leímos 'O' (inicio enroque) ──────────────────────
    "q8": {
        CAT_GUION:    "q9",   # O- → continuar enroque
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q9: leímos 'O-' → esperamos 'O' ──────────────────────
    "q9": {
        CAT_O:        "q10",  # O-O → enroque corto (intermedio)
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q10: 'O-O' → ACEPTACIÓN (enroque corto) o continúa ───
    "q10": {
        CAT_GUION:    "q11",  # O-O- → hacia enroque largo
        CAT_JAQUE:    "q7",   # O-O+ → jaque
        # fin → aceptación
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q11: 'O-O-' → esperamos 'O' ──────────────────────────
    "q11": {
        CAT_O:        "q12",  # O-O-O → enroque largo (intermedio)
        CAT_PIEZA:    TRAMPA,
        CAT_COLUMNA:  TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # ── q12: captura 'x' o último 'O' del enroque largo ──────
    "q12": {
        CAT_COLUMNA:  "q3",   # xd → columna destino tras captura
        CAT_JAQUE:    "q7",   # O-O-O+ → jaque tras enroque largo
        # fin (O-O-O) → aceptación si llegamos a q12 desde q11
        CAT_PIEZA:    TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_CAPTURA:  TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # -- q13: FILA de origen tras pieza (R1e4, Q3d5) ----------
    "q13": {
        CAT_COLUMNA:  "q3",   # R1e -> columna destino
        CAT_CAPTURA:  "q12",  # R1x -> captura con origen completo
        CAT_PIEZA:    TRAMPA,
        CAT_FILA:     TRAMPA,
        CAT_IGUAL:    TRAMPA,
        CAT_PROMO:    TRAMPA,
        CAT_JAQUE:    TRAMPA,
        CAT_GUION:    TRAMPA,
        CAT_O:        TRAMPA,
        CAT_INVALIDO: TRAMPA,
    },
    # -- estado trampa (absorbe todo) -------------------------
    TRAMPA: {c: TRAMPA for c in [
        CAT_PIEZA, CAT_COLUMNA, CAT_FILA, CAT_CAPTURA,
        CAT_IGUAL, CAT_PROMO, CAT_JAQUE, CAT_GUION, CAT_O, CAT_INVALIDO
    ]},
}

# Estados de aceptacion del AFD
# q4:  movimiento normal (Nf3, e4, exd5, R1e4)
# q6:  movimiento con promocion (e8=Q)
# q7:  movimiento con jaque/mate (Nf3+, O-O#)
# q10: enroque corto O-O
# q12: enroque largo O-O-O  (llegamos desde q11->q12)
ESTADOS_ACEPTACION = {"q4", "q6", "q7", "q10", "q12"}

# Descripcion legible de cada estado
DESC_ESTADOS = {
    "q0":  "Inicio",
    "q1":  "Pieza leida (K/Q/R/B/N)",
    "q2":  "Columna inicial (peon/origen)",
    "q3":  "Columna destino",
    "q4":  "OK Fila destino [ACEPTA]",
    "q5":  "Signo '=' (espera promocion)",
    "q6":  "OK Pieza de promocion [ACEPTA]",
    "q7":  "OK Jaque/Mate [ACEPTA]",
    "q8":  "O (inicio enroque)",
    "q9":  "O- (guion enroque)",
    "q10": "OK O-O enroque corto [ACEPTA]",
    "q11": "O-O- (guion enroque largo)",
    "q12": "OK O-O-O enroque largo / destino captura [ACEPTA]",
    "q13": "Fila de origen tras pieza (desambiguacion)",
    TRAMPA: "TRAMPA (cadena invalida)",
}


# ============================================================
#   CLASE VALIDADOR PGN
# ============================================================

class ValidadorPGN:

    # ──────────────────────────────────────────────────────────
    # Expresión Regular
    # ──────────────────────────────────────────────────────────
    # Subconjunto cubierto:
    #   [KQRBN]?          pieza opcional (ausencia → peón)
    #   [a-h]?            columna de origen desambiguación
    #   [1-8]?            fila de origen desambiguación
    #   x?                captura opcional
    #   [a-h]             columna destino (obligatoria)
    #   [1-8]             fila destino (obligatoria)
    #   (=[QRBN])?        promoción opcional
    #   |  O-O(-O)?       enroque corto o largo
    #   [+#]?             jaque o jaque mate opcional
    REGEX_PGN = (
        r"^("
        r"[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?"  # movimiento normal
        r"|"
        r"O-O(-O)?"                                        # enroque
        r")[+#]?$"
    )

    def __init__(self):
        self._regex = re.compile(self.REGEX_PGN)

    # ──────────────────────────────────────────────────────────
    # Validación por Regex
    # ──────────────────────────────────────────────────────────
    def validar_regex(self, movimiento: str) -> bool:
        return bool(self._regex.match(movimiento))

    # ──────────────────────────────────────────────────────────
    # Validación por AFD  (recorrido carácter a carácter)
    # ──────────────────────────────────────────────────────────
    def validar_afd(self, movimiento: str, verbose: bool = False) -> bool:
        estado = "q0"
        if verbose:
            print(f"  Estado inicial: {estado} – {DESC_ESTADOS[estado]}")

        for i, ch in enumerate(movimiento):
            # Calcular número de estado para clasificar correctamente el '=' y promoción
            num_estado = int(estado[1:]) if estado != TRAMPA else -1
            # Usamos num_estado == 5 para indicar que estamos en q5 (tras '=')
            cat = categoria(ch, num_estado)
            siguiente = TABLA.get(estado, {}).get(cat, TRAMPA)

            if verbose:
                print(f"  [{i}] char='{ch}'  cat={cat:<10}  {estado} → {siguiente}  ({DESC_ESTADOS.get(siguiente,'')})")
            estado = siguiente

        if verbose:
            acepta = estado in ESTADOS_ACEPTACION
            print(f"\n  Estado final: {estado} – {DESC_ESTADOS.get(estado,'')}")
            print(f"  Resultado AFD: {'✓ VÁLIDO' if acepta else '✗ INVÁLIDO'}")

        return estado in ESTADOS_ACEPTACION

    # ──────────────────────────────────────────────────────────
    # Tabla de validación múltiple
    # ──────────────────────────────────────────────────────────
    def validar_lista(self, movimientos: list[str]):
        sep = "─" * 58
        print(f"\n  {sep}")
        print(f"  {'Movimiento':<14} {'Regex':<10} {'AFD':<10} {'Resultado'}")
        print(f"  {sep}")

        for mov in movimientos:
            ok_r = self.validar_regex(mov)
            ok_a = self.validar_afd(mov)
            concordancia = ok_r == ok_a
            resultado = ("✓ VÁLIDO" if ok_r else "✗ INVÁLIDO")
            alerta = "" if concordancia else "  ⚠ discordancia"
            print(f"  {repr(mov):<14} {str(ok_r):<10} {str(ok_a):<10} {resultado}{alerta}")

        print(f"  {sep}\n")

    # ──────────────────────────────────────────────────────────
    # Mostrar tabla de transiciones del AFD
    # ──────────────────────────────────────────────────────────
    def mostrar_tabla_transiciones(self):
        categorias = [CAT_PIEZA, CAT_COLUMNA, CAT_FILA, CAT_CAPTURA,
                      CAT_IGUAL, CAT_PROMO, CAT_JAQUE, CAT_GUION, CAT_O]
        cabeceras = ["PIEZA", "COL", "FILA", "CAP", "=", "PROM", "JQ", "-", "O"]

        ancho_estado = 5
        ancho_col = 5
        sep_col = " │ "

        # cabecera
        print(f"\n  {'Estado':<{ancho_estado}} │ " +
              sep_col.join(f"{h:<{ancho_col}}" for h in cabeceras))
        print("  " + "─" * (ancho_estado + 3 + len(cabeceras) * (ancho_col + 3)))

        for estado in sorted(TABLA.keys(), key=lambda s: (s == TRAMPA, s)):
            fila = []
            for cat in categorias:
                dest = TABLA[estado].get(cat, TRAMPA)
                fila.append(dest[:ancho_col])
            acepta = " ✓" if estado in ESTADOS_ACEPTACION else "  "
            print(f"  {estado:<{ancho_estado}}{acepta}│ " +
                  sep_col.join(f"{c:<{ancho_col}}" for c in fila))

    # ──────────────────────────────────────────────────────────
    # Trazar recorrido detallado de un movimiento
    # ──────────────────────────────────────────────────────────
    def trazar_recorrido(self, movimiento: str):
        sep = "─" * 55
        print(f"\n  {sep}")
        print(f"  RECORRIDO AFD para: {repr(movimiento)}")
        print(f"  {sep}")
        self.validar_afd(movimiento, verbose=True)
        print(f"  {sep}")

    # ──────────────────────────────────────────────────────────
    # Punto de entrada
    # ──────────────────────────────────────────────────────────
    def menu_interactivo(self):
        import time
        import os
        while True:
            print("\n" + "=" * 65)
            print("  PROGRAMA 3 – REGEX + AFD PARA NOTACIÓN PGN (AJEDREZ)")
            print("  Tema 3 | Lenguajes y Gramáticas Formales | UNEG 2026-I")
            print("=" * 65)
            print("  1. Ver Subconjunto PGN Aceptado")
            print("  2. Ver Expresión Regular")
            print("  3. Ver Tabla de Transiciones del AFD")
            print("  4. Ejecutar validación de casos de prueba")
            print("  5. Ver recorridos detallados de ejemplo")
            print("  6. Probar movimiento personalizado")
            print("  7. Ejecutar todos los ejemplos")
            print("  0. Salir")
            print("=" * 65)
            
            opcion = input("  Seleccione una opción: ").strip()
            
            if opcion == "1":
                self._mostrar_subconjunto()
            elif opcion == "2":
                self._mostrar_regex()
            elif opcion == "3":
                self.mostrar_tabla_transiciones()
            elif opcion == "4":
                self._validar_casos_prueba()
            elif opcion == "5":
                self._recorridos_ejemplo()
            elif opcion == "6":
                mov = input("  Ingrese el movimiento a probar: ").strip()
                self.trazar_recorrido(mov)
            elif opcion == "7":
                self._mostrar_subconjunto()
                self._mostrar_regex()
                self.mostrar_tabla_transiciones()
                self._validar_casos_prueba()
                self._recorridos_ejemplo()
            elif opcion == "0":
                print("\n  Saliendo del programa...")
                break
            else:
                print("\n  Opción no válida. Intente de nuevo.")

            print("\n  [Limpiando pantalla y regresando al menú en 10 segundos...]")
            time.sleep(10)
            os.system('cls' if os.name == 'nt' else 'clear')

    def _mostrar_subconjunto(self):
        print("""
  SUBCONJUNTO PGN ACEPTADO:
  ─────────────────────────
  • Movimientos de peón      : e4  d5  e5
  • Movimientos de pieza     : Nf3  Bc4  Qd1  Ke2  Re1
  • Capturas de peón         : exd5  cxd4
  • Capturas de pieza        : Nxf3  Bxc4  Qxe5
  • Desambiguación de origen : Nbd2  R1e4  Qf3e4
  • Enroque corto            : O-O
  • Enroque largo            : O-O-O
  • Promoción de peón        : e8=Q  d1=N  a8=R
  • Jaque                    : Nf3+  exd5+  O-O+
  • Jaque mate               : Qxf7#  e8=Q#
        """)

    def _mostrar_regex(self):
        print("  EXPRESIÓN REGULAR:")
        print(f"  {self.REGEX_PGN}\n")
        print("  Descomposición:")
        print("    [KQRBN]?          →  pieza (opcional; ausencia = peón)")
        print("    [a-h]?[1-8]?      →  columna/fila de origen (desambiguación)")
        print("    x?                →  captura (opcional)")
        print("    [a-h][1-8]        →  casilla destino (obligatoria)")
        print("    (=[QRBN])?        →  promoción (opcional)")
        print("    | O-O(-O)?        →  enroque corto o largo")
        print("    [+#]?             →  jaque o jaque mate (opcional)")

    def _validar_casos_prueba(self):
        print("\n  VALIDACIÓN DE MOVIMIENTOS DE PRUEBA:")
        movimientos_validos = [
            "e4", "d5", "Nf3", "Bc4", "Qd1",
            "exd5", "Nxf3", "O-O", "O-O-O",
            "e8=Q", "d1=N", "Nf3+", "Qxf7#",
            "Nbd2", "R1e4",
        ]
        movimientos_invalidos = [
            "Z9", "x", "", "e9", "Nf9",
            "OOO", "O--O", "==Q", "e4=",
            "e8=P", "Nf33", "++",
        ]
        print("\n  [Movimientos válidos]")
        self.validar_lista(movimientos_validos)
        print("  [Movimientos inválidos]")
        self.validar_lista(movimientos_invalidos)

    def _recorridos_ejemplo(self):
        print("\n  RECORRIDOS DETALLADOS (paso a paso por el AFD):")
        for mov in ["e4", "Nf3", "exd5", "O-O-O", "e8=Q", "Nf3+", "Z9"]:
            self.trazar_recorrido(mov)

# ============================================================
if __name__ == "__main__":
    import sys as _sys
    import io as _io
    # Asegurar UTF-8 en consola Windows
    if hasattr(_sys.stdout, 'buffer'):
        _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding='utf-8', errors='replace')
    v = ValidadorPGN()
    v.menu_interactivo()
