# -*- coding: utf-8 -*-
# ============================================================
# programa2_higiene_gramaticas.py
# Tema 3 - Lenguajes y Gramaticas Formales  (UNEG 2026-I)
# Sección 2.3: Higiene y Optimización de Gramáticas
#
# Tres subcasos:
#   A) Gramática Ambigua  →  dos árboles para la misma cadena
#   B) Recursividad por la Izquierda  →  algoritmo de eliminación
#   C) Factorización por la Izquierda →  gramática optimizada
# ============================================================


# ============================================================
#   ESTRUCTURAS PARA ÁRBOLES DE DERIVACIÓN (ASCII)
# ============================================================

class NodoArbol:
    """Nodo de un árbol de derivación."""
    def __init__(self, etiqueta: str, hijos: list = None):
        self.etiqueta = etiqueta
        self.hijos: list["NodoArbol"] = hijos or []

    def __str__(self):
        return self.etiqueta


def _imprimir_arbol(nodo: NodoArbol, prefijo: str = "", es_ultimo: bool = True):
    """Imprime un árbol de derivación en formato ASCII."""
    conector = "└── " if es_ultimo else "├── "
    print(prefijo + conector + nodo.etiqueta)
    prefijo_hijo = prefijo + ("    " if es_ultimo else "│   ")
    for i, hijo in enumerate(nodo.hijos):
        _imprimir_arbol(hijo, prefijo_hijo, i == len(nodo.hijos) - 1)


def imprimir_arbol(nodo: NodoArbol, titulo: str):
    sep = "─" * 55
    print(f"\n  ┌{sep}┐")
    print(f"  │  {titulo:<53}│")
    print(f"  └{sep}┘")
    # Raíz sin conector
    print("  " + nodo.etiqueta)
    for i, hijo in enumerate(nodo.hijos):
        _imprimir_arbol(hijo, "  ", i == len(nodo.hijos) - 1)


# ============================================================
#   CLASE PRINCIPAL
# ============================================================

class HigieneGramaticas:

    def _cabecera(self, titulo: str):
        sep = "=" * 65
        print(f"\n{sep}")
        print(f"  {titulo}")
        print(sep)

    def _subcabecera(self, titulo: str):
        print(f"\n  {'─' * 60}")
        print(f"  {titulo}")
        print(f"  {'─' * 60}")

    # ----------------------------------------------------------
    #  CASO A: GRAMÁTICA AMBIGUA
    # ----------------------------------------------------------
    def caso_a_gramatica_ambigua(self):
        """
        Gramática clásica de expresiones aritméticas:
            E → E + E
            E → E * E
            E → id

        Para la cadena  "id + id * id"  existen al menos dos
        árboles de derivación distintos, lo que demuestra ambigüedad.

        Árbol 1:  la multiplicación tiene mayor precedencia  (id + (id * id))
        Árbol 2:  la suma tiene mayor precedencia            ((id + id) * id)
        """
        self._cabecera("CASO A – GRAMÁTICA AMBIGUA")

        print("""
  Gramática G_amb:
      E → E + E
      E → E * E
      E → id

  Cadena de prueba:  id + id * id

  DEMOSTRACIÓN DE AMBIGÜEDAD:
  Una gramática es ambigua si existe al menos UNA cadena
  para la cual se pueden construir DOS o más árboles de
  derivación diferentes (equivalentemente, dos derivaciones
  más a la izquierda distintas).
        """)

        # ── Árbol 1 ──────────────────────────────────────────────
        # E → E + E  →  id + (E * E)  →  id + id * id
        arbol1 = NodoArbol("E", [
            NodoArbol("E", [NodoArbol("id")]),
            NodoArbol("+"),
            NodoArbol("E", [
                NodoArbol("E", [NodoArbol("id")]),
                NodoArbol("*"),
                NodoArbol("E", [NodoArbol("id")]),
            ]),
        ])
        imprimir_arbol(arbol1, "Árbol 1: id + (id * id)   [* tiene prioridad]")

        print("""
  Derivación más a la izquierda (Árbol 1):
    E ⟹ E + E
      ⟹ id + E
      ⟹ id + E * E
      ⟹ id + id * E
      ⟹ id + id * id    ✓
        """)

        # ── Árbol 2 ──────────────────────────────────────────────
        # E → E * E  →  (E + E) * id  →  id + id * id
        arbol2 = NodoArbol("E", [
            NodoArbol("E", [
                NodoArbol("E", [NodoArbol("id")]),
                NodoArbol("+"),
                NodoArbol("E", [NodoArbol("id")]),
            ]),
            NodoArbol("*"),
            NodoArbol("E", [NodoArbol("id")]),
        ])
        imprimir_arbol(arbol2, "Árbol 2: (id + id) * id   [+ tiene prioridad]")

        print("""
  Derivación más a la izquierda (Árbol 2):
    E ⟹ E * E
      ⟹ E + E * E
      ⟹ id + E * E
      ⟹ id + id * E
      ⟹ id + id * id    ✓

  CONCLUSIÓN:
  La misma cadena "id + id * id" posee DOS árboles de
  derivación distintos  →  la gramática ES AMBIGUA.

  SOLUCIÓN ESTÁNDAR (gramática no ambigua equivalente):
      E  → E + T | T
      T  → T * F | F
      F  → id
  Esta versión incorpora la precedencia de operadores
  directamente en la jerarquía de no terminales.
        """)

    # ----------------------------------------------------------
    #  CASO B: RECURSIVIDAD POR LA IZQUIERDA
    # ----------------------------------------------------------
    def caso_b_recursividad_izquierda(self):
        """
        Gramática con recursividad izquierda directa:
            E  → E + T
            E  → T
            T  → T * F
            T  → F
            F  → id | ( E )

        Problema: un parser LL(1) entraría en bucle infinito porque
        al querer derivar E, vuelve a intentar derivar E.

        Algoritmo de eliminación (Aho, Lam, Sethi, Ullman):
          Para cada A → A α₁ | A α₂ | ... | β₁ | β₂ | ...
          Transformar en:
            A  → β₁ A' | β₂ A' | ...
            A' → α₁ A' | α₂ A' | ε
        """
        self._cabecera("CASO B – RECURSIVIDAD POR LA IZQUIERDA")

        print("""
  Gramática ORIGINAL con recursividad izquierda:
      E  → E + T    ← recursividad izquierda directa en E
      E  → T
      T  → T * F    ← recursividad izquierda directa en T
      T  → F
      F  → id  |  ( E )
        """)

        self._subcabecera("PASO 1 – Identificar producciones con recursividad izquierda")
        print("""
  Regla A es recursiva a la izquierda si:  A ⟹⁺ A α

  ┌──────────────────────────────────────────────────────┐
  │  No terminal  │  Producción       │  Tipo            │
  ├───────────────┼───────────────────┼──────────────────┤
  │  E            │  E → E + T        │  Recursiva izq.  │
  │  E            │  E → T            │  Normal (β)      │
  │  T            │  T → T * F        │  Recursiva izq.  │
  │  T            │  T → F            │  Normal (β)      │
  │  F            │  F → id | ( E )   │  Sin recursión   │
  └──────────────────────────────────────────────────────┘
        """)

        self._subcabecera("PASO 2 – Aplicar el algoritmo de transformación")
        print("""
  FÓRMULA GENERAL:
    A  → A α  |  β
    ──────────────────
    A  → β A'
    A' → α A'  |  ε

  Para  E:
    E → E + T  (α = "+ T")
    E → T      (β = "T")
    ──────────────────
    E  → T E'
    E' → + T E'  |  ε

  Para  T:
    T → T * F  (α = "* F")
    T → F      (β = "F")
    ──────────────────
    T  → F T'
    T' → * F T'  |  ε
        """)

        self._subcabecera("PASO 3 – Gramática resultante SIN recursividad izquierda")
        print("""
  Gramática TRANSFORMADA (apta para parsers LL):
  ┌─────────────────────────────────────────────┐
  │  E  → T E'                                  │
  │  E' → + T E'  |  ε                          │
  │  T  → F T'                                  │
  │  T' → * F T'  |  ε                          │
  │  F  → id  |  ( E )                          │
  └─────────────────────────────────────────────┘

  VERIFICACIÓN con la cadena "id + id * id":
    E  ⟹ T E'
       ⟹ F T' E'
       ⟹ id T' E'
       ⟹ id ε E'              (T' → ε)
       ⟹ id + T E'            (E' → + T E')
       ⟹ id + F T' E'
       ⟹ id + id T' E'
       ⟹ id + id * F T' E'    (T' → * F T')
       ⟹ id + id * id T' E'
       ⟹ id + id * id ε ε     (T'→ε, E'→ε)
       ⟹ id + id * id  ✓

  CONCLUSIÓN: la recursividad izquierda fue eliminada exitosamente.
  Los nuevos no terminales E' y T' implementan la asociatividad
  por la derecha sin entrar en ciclos.
        """)

    # ----------------------------------------------------------
    #  CASO C: FACTORIZACIÓN POR LA IZQUIERDA
    # ----------------------------------------------------------
    def caso_c_factorizacion_izquierda(self):
        """
        Gramática que requiere factorización izquierda:
            S → if E then S else S
            S → if E then S
            S → otras

        Problema: un parser LL(1) no puede decidir qué producción
        aplicar al ver solo "if", porque ambas alternativas
        comparten el prefijo "if E then S".

        Algoritmo de factorización:
          Para cada A → α β₁ | α β₂ | ... (prefijo α común)
          Crear nuevo no terminal A' y reescribir:
            A  → α A'
            A' → β₁ | β₂ | ...
        """
        self._cabecera("CASO C – FACTORIZACIÓN POR LA IZQUIERDA")

        print("""
  Gramática ORIGINAL con prefijo común:
      S  → if E then S else S
      S  → if E then S
      S  → otras

  Problema: al ver el token "if", el parser no sabe si usar
  la producción con "else" o la que termina en S.
  Esto impide construir un parser LL(1) sin ambigüedad de
  decisión.
        """)

        self._subcabecera("PASO 1 – Identificar el prefijo común más largo")
        print("""
  Producción 1:  if  E  then  S  [else S]
  Producción 2:  if  E  then  S  [<nada>]
                 ──────────────
  Prefijo común: "if E then S"

  Las partes que difieren (sufijos):
    β₁ = else S
    β₂ = ε  (la producción termina aquí)
        """)

        self._subcabecera("PASO 2 – Crear el nuevo no terminal y reescribir")
        print("""
  FÓRMULA GENERAL:
    A  → α β₁  |  α β₂
    ──────────────────────
    A  → α A'
    A' → β₁  |  β₂

  Aplicado:
    S  → if E then S  S_prima
    S_prima → else S
    S_prima → ε
        """)

        self._subcabecera("PASO 3 – Gramática OPTIMIZADA resultante")
        print("""
  ┌───────────────────────────────────────────────────────┐
  │  S_prima = S'  (nuevo no terminal)                    │
  │                                                       │
  │  S  → if E then S S'                                  │
  │  S  → otras                                           │
  │  S' → else S  |  ε                                    │
  └───────────────────────────────────────────────────────┘

  VENTAJA:
  Ahora el parser LL(1) puede decidir inmediatamente:
    • Si ve "else"  →  aplica  S' → else S
    • Si ve otra cosa (FOLLOW(S'))  →  aplica  S' → ε

  VERIFICACIÓN con "if E then if E then S else S":
    S  ⟹ if E then S S'
       ⟹ if E then if E then S S' S'
       ⟹ if E then if E then S else S S'   (S'→else S)
       ⟹ if E then if E then S else S ε    (S'→ε)
       ⟹ if E then if E then S else S  ✓

  NOTA – Ambigüedad del "else colgante":
  La factorización izquierda elimina el problema de prefijos
  compartidos, pero la gramática if-then-else tiene también la
  ambigüedad del "dangling else". La convención usual es asociar
  cada "else" con el "if" más cercano, lo que se logra con la
  gramática:
      stmt    → matched  |  unmatched
      matched → if E then matched else matched  |  otras
      unmatched→ if E then stmt
               | if E then matched else unmatched
        """)

    # ----------------------------------------------------------
    # Menú Interactivo
    # ----------------------------------------------------------
    def menu_interactivo(self):
        import time
        import os
        while True:
            print("\n" + "=" * 65)
            print("  PROGRAMA 2 – HIGIENE DE GRAMÁTICAS")
            print("  Tema 3 | Lenguajes y Gramáticas Formales | UNEG 2026-I")
            print("=" * 65)
            print("  1. Caso A: Gramática Ambigua")
            print("  2. Caso B: Recursividad por la Izquierda")
            print("  3. Caso C: Factorización por la Izquierda")
            print("  4. Ejecutar todos los casos")
            print("  0. Salir")
            print("=" * 65)
            
            opcion = input("  Seleccione una opción: ").strip()
            
            if opcion == "1":
                self.caso_a_gramatica_ambigua()
            elif opcion == "2":
                self.caso_b_recursividad_izquierda()
            elif opcion == "3":
                self.caso_c_factorizacion_izquierda()
            elif opcion == "4":
                self.caso_a_gramatica_ambigua()
                self.caso_b_recursividad_izquierda()
                self.caso_c_factorizacion_izquierda()
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
    h = HigieneGramaticas()
    h.menu_interactivo()
