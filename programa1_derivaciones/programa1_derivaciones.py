# -*- coding: utf-8 -*-
# ============================================================
# programa1_derivaciones.py
# Tema 3 - Lenguajes y Gramaticas Formales  (UNEG 2026-I)
# Sección 2.2: Derivación y Modelado (Caso Práctico: Genoma)
#
# Gramática Libre de Contexto (GLC) para modelar herramientas
# de dibujo sobre el alfabeto Σ = {a, c, g, t}
#
# Codificación semántica:
#   a → avanzar / trazar línea recta
#   c → curvar / rotar izquierda (corner)
#   g → girar derecha
#   t → terminar / fin de segmento
#
# No terminales:
#   S   → símbolo inicial (figura completa)
#   L   → lado / segmento recto
#   R   → rama (estructura recursiva)
#   B   → base/bifurcación
#   C   → cuerpo (bloque de trazado)
#
# Producciones (G):
#   S → L c L c L c L t          (cuadrado: 4 lados + 4 giros de 90°)
#   S → L g L c L t              (triángulo simplificado)
#   S → a S a t                  (estructura recursiva simétrica)
#   S → R B R t                  (árbol con ramas)
#   S → C c C c C c C c C c C t  (cubo: 6 caras)
#   L → a L a | a a | a          (lado: uno o más avances)
#   R → a R c g | a c            (rama recursiva con desvíos)
#   B → c R g B | t              (bifurcación)
#   C → a C g | a g | a          (cara del cubo)
# ============================================================

class GramaticaDibujo:
    """
    GLC formal G = (V, Σ, P, S) donde:
      V = {S, L, R, B, C}          (no terminales)
      Σ = {a, c, g, t}             (terminales)
      P = producciones definidas abajo
      S = símbolo inicial
    """

    def __init__(self):
        # Producciones: cada clave es un no terminal,
        # cada valor es una lista de alternativas (cadenas de tokens)
        self.producciones = {
            "S": [
                "L c L c L c L t",          # cuadrado
                "L g L c L t",              # triángulo
                "a S a t",                  # recursiva simétrica
                "R B R t",                  # árbol
                "C c C c C c C c C c C t",  # cubo
            ],
            "L": [
                "a L a",   # extensión recursiva del lado
                "a a",     # lado de longitud 2
                "a",       # lado mínimo
            ],
            "R": [
                "a R c g", # rama que se desvía y vuelve
                "a c",     # hoja simple
            ],
            "B": [
                "c R g B", # bifurcación con más ramas
                "t",       # fin de bifurcaciones
            ],
            "C": [
                "a C g",  # cara recursiva con giro
                "a g",    # cara mínima con giro
                "a",      # cara de un trazo
            ],
        }
        self.terminales = {"a", "c", "g", "t"}

    # ----------------------------------------------------------
    # Utilidades de formato
    # ----------------------------------------------------------
    def _es_terminal(self, token: str) -> bool:
        return token in self.terminales

    def _primer_no_terminal(self, cadena: str) -> str | None:
        """Retorna el primer no terminal encontrado en la cadena."""
        for tok in cadena.split():
            if not self._es_terminal(tok):
                return tok
        return None

    def _aplicar_produccion(self, cadena: str, no_terminal: str, produccion: str) -> str:
        """Reemplaza la PRIMERA ocurrencia de no_terminal por produccion."""
        tokens = cadena.split()
        for i, tok in enumerate(tokens):
            if tok == no_terminal:
                tokens = tokens[:i] + produccion.split() + tokens[i + 1:]
                break
        return " ".join(tokens)

    # ----------------------------------------------------------
    # Derivación dirigida (para mostrar pasos concretos)
    # ----------------------------------------------------------
    def derivar_secuencia(self, pasos: list[tuple[str, str]], titulo: str):
        """
        Ejecuta una secuencia de derivaciones dada explícitamente.
        pasos: lista de (no_terminal_a_expandir, produccion_elegida)
        """
        sep = "─" * 60
        print(f"\n{sep}")
        print(f"  {titulo}")
        print(sep)

        cadena = "S"
        print(f"  Paso  0:  {cadena}")

        for i, (nt, prod) in enumerate(pasos, start=1):
            cadena = self._aplicar_produccion(cadena, nt, prod)
            print(f"  Paso {i:2d}:  {cadena}")
            if i < len(pasos):
                print(f"         ↓  ({nt} → {prod})")

        # Verificar que la cadena final sólo tiene terminales
        tokens_finales = cadena.split()
        es_sentencia = all(self._es_terminal(t) for t in tokens_finales)
        print()
        print(f"  Cadena generada : {cadena}")
        print(f"  Sólo terminales : {'✓  SÍ – es sentencia válida del lenguaje' if es_sentencia else '✗  NO – aún contiene no terminales'}")
        print(sep)

    # ----------------------------------------------------------
    # 5 derivaciones requeridas
    # ----------------------------------------------------------
    def ejemplo_cuadrado(self):
        """
        Figura: CUADRADO
        Idea: cuatro lados (L) separados por 4 giros de 90° (c), cierre con t.
        S → L c L c L c L t
        L → a a  (lado de longitud 2, 4 veces)
        Cadena final: a a c a a c a a c a a t
        Interpretación: traza 2 pasos, gira, repite × 4 → cuadrado.
        """
        self.derivar_secuencia(
            titulo="FIGURA 1 – CUADRADO  (4 lados de longitud 2, giros de 90°)",
            pasos=[
                ("S", "L c L c L c L t"),  # paso 1: expandir S
                ("L", "a a"),              # paso 2: primer lado
                ("L", "a a"),              # paso 3: segundo lado
                ("L", "a a"),              # paso 4: tercer lado
                ("L", "a a"),              # paso 5: cuarto lado
            ],
        )

    def ejemplo_arbol(self):
        """
        Figura: ÁRBOL CON RAMAS Y HOJAS
        S → R B R t
        R → a R c g  (tronco con desvío)
        R → a c       (hoja)
        B → c R g B  (bifurcación)
        B → t
        Cadena final: a a c c g g a c c a c g t t t
        Interpretación: tronco, bifurcación con dos hojas, cierre.
        """
        self.derivar_secuencia(
            titulo="FIGURA 2 – ÁRBOL CON RAMAS Y HOJAS",
            pasos=[
                ("S", "R B R t"),        # paso 1
                ("R", "a R c g"),        # paso 2: tronco
                ("R", "a c"),            # paso 3: hoja del tronco
                ("B", "c R g B"),        # paso 4: primera bifurcación
                ("R", "a c"),            # paso 5: primera rama
                ("B", "t"),              # paso 6: fin bifurcaciones
                ("R", "a c"),            # paso 7: segunda rama (R final de S)
            ],
        )

    def ejemplo_cubo(self):
        """
        Figura: CUBO (6 caras)
        S → C c C c C c C c C c C t
        C → a g   (cara mínima con giro de perspectiva)
        Cadena final: a g c a g c a g c a g c a g c a g t
        Interpretación: 6 caras en perspectiva isométrica, rotación entre caras.
        """
        self.derivar_secuencia(
            titulo="FIGURA 3 – CUBO  (6 caras con perspectiva isométrica)",
            pasos=[
                ("S", "C c C c C c C c C c C t"),  # paso 1
                ("C", "a g"),  # cara 1
                ("C", "a g"),  # cara 2
                ("C", "a g"),  # cara 3
                ("C", "a g"),  # cara 4
                ("C", "a g"),  # cara 5
                ("C", "a g"),  # cara 6
            ],
        )

    def ejemplo_espiral(self):
        """
        Figura: ESPIRAL
        Idea: el lado crece recursivamente (L → a L a)
        S → a S a t   (expansión simétrica creciente)
        S → L c L t   (base)
        L → a a
        Derivación:
          S → a S a t → a L c L t a t → a a a c a a t a t
        Cadena final muestra crecimiento espiral.
        """
        self.derivar_secuencia(
            titulo="FIGURA 4 – ESPIRAL  (lado que crece simétricamente)",
            pasos=[
                ("S", "a S a t"),        # paso 1: expansión externa
                ("S", "L c L t"),        # paso 2: nucleo con giro
                ("L", "a L a"),          # paso 3: lado izq. crece
                ("L", "a"),              # paso 4: nucleo del lado
                ("L", "a a"),            # paso 5: lado derecho
            ],
        )

    def ejemplo_estrella(self):
        """
        Figura: ESTRELLA DE 5 PUNTAS
        Idea: 5 ramas R repetidas, separadas por giros g (72° cada uno).
        Usamos la producción S → R B R t con B expandido 4 veces.
        R → a c  (punta de la estrella)
        B → c R g B (giro + punta + nuevo giro)
        Cadena: a c c a c g c a c g c a c g c a c g t
        """
        self.derivar_secuencia(
            titulo="FIGURA 5 – ESTRELLA DE 5 PUNTAS  (5 ramas radiales)",
            pasos=[
                ("S", "R B R t"),         # paso 1: estructura base
                ("R", "a c"),             # paso 2: punta 1
                ("B", "c R g B"),         # paso 3: giro + punta 2
                ("R", "a c"),             # paso 4: punta 2
                ("B", "c R g B"),         # paso 5: giro + punta 3
                ("R", "a c"),             # paso 6: punta 3
                ("B", "c R g B"),         # paso 7: giro + punta 4
                ("R", "a c"),             # paso 8: punta 4
                ("B", "t"),               # paso 9: fin bifurcaciones
                ("R", "a c"),             # paso 10: punta 5 (R de S)
            ],
        )

    # ----------------------------------------------------------
    # Mostrar la gramática formal
    # ----------------------------------------------------------
    def mostrar_gramatica(self):
        sep = "=" * 60
        print(sep)
        print("  GRAMÁTICA LIBRE DE CONTEXTO  G = (V, Σ, P, S)")
        print(sep)
        print(f"  V  (no terminales) = {{ S, L, R, B, C }}")
        print(f"  Σ  (terminales)    = {{ a, c, g, t }}")
        print(f"  S  (inicio)        = S")
        print()
        print("  P  (producciones):")
        for nt, alternativas in self.producciones.items():
            for idx, alt in enumerate(alternativas):
                if idx == 0:
                    print(f"    {nt}  →  {alt}")
                else:
                    print(f"    {' ' * len(nt)}  |  {alt}")
        print()
        print("  Codificación semántica del alfabeto:")
        print("    a → avanzar / trazar segmento recto")
        print("    c → curvar / girar a la izquierda (corner)")
        print("    g → girar a la derecha")
        print("    t → terminar segmento / fin de figura")
        print(sep)

    # ----------------------------------------------------------
    # Menú Interactivo
    # ----------------------------------------------------------
    def menu_interactivo(self):
        import time
        import os
        while True:
            print("\n" + "=" * 60)
            print("  PROGRAMA 1 – DERIVACIONES CON GLC")
            print("  Tema 3 | Lenguajes y Gramáticas Formales | UNEG 2026-I")
            print("=" * 60)
            print("  1. Mostrar Gramática")
            print("  2. Ejemplo: Cuadrado")
            print("  3. Ejemplo: Árbol")
            print("  4. Ejemplo: Cubo")
            print("  5. Ejemplo: Espiral")
            print("  6. Ejemplo: Estrella")
            print("  7. Ejecutar todos los ejemplos")
            print("  0. Salir")
            print("=" * 60)
            
            opcion = input("  Seleccione una opción: ").strip()
            
            if opcion == "1":
                self.mostrar_gramatica()
            elif opcion == "2":
                self.ejemplo_cuadrado()
            elif opcion == "3":
                self.ejemplo_arbol()
            elif opcion == "4":
                self.ejemplo_cubo()
            elif opcion == "5":
                self.ejemplo_espiral()
            elif opcion == "6":
                self.ejemplo_estrella()
            elif opcion == "7":
                self.mostrar_gramatica()
                self.ejemplo_cuadrado()
                self.ejemplo_arbol()
                self.ejemplo_cubo()
                self.ejemplo_espiral()
                self.ejemplo_estrella()
            elif opcion == "0":
                print("\n  Saliendo del programa...")
                break
            else:
                print("\n  Opción no válida. Intente de nuevo.")

            print("\n  [Limpiando pantalla y regresando al menú en 10 segundos...]")
            time.sleep(10)
            os.system('cls' if os.name == 'nt' else 'clear')

# ============================================================
if __name__ == "__main__":
    import sys
    import io
    # Asegurar UTF-8 en consola Windows
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    g = GramaticaDibujo()
    g.menu_interactivo()
