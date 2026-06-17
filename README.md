# Lenguajes y Compiladores - Actividad 03 (Fase I)

Este repositorio contiene la entrega de la **Fase I** de la evaluación correspondiente al Tema 3: "Lenguajes y Gramáticas Formales", de la asignatura **Lenguajes y Compiladores** dictada en la Universidad Nacional Experimental de Guayana (UNEG) para la sección 01 (Trimestre 2026-I).

El objetivo principal de este proyecto es llevar a la práctica los conceptos teóricos de modelado de lenguajes formales, la higiene de gramáticas para compiladores y la implementación de expresiones regulares y autómatas finitos.

## 📂 Contenido del Repositorio

El repositorio está organizado en directorios independientes para cada requerimiento técnico, garantizando la modularidad y facilitando su evaluación:

### 1. Informe de Investigación
- 📄 **`Lenguajes y compiladores.pdf`**: Documento central que aborda de forma exhaustiva los fundamentos teóricos (Jerarquía de Chomsky, relación gramática-lenguaje) y explica el marco conceptual de los códigos fuente que acompañan esta entrega.

### 2. Modelado de Derivaciones (Caso Práctico: Genoma)
- 📁 **`programa1_derivaciones/`**:
  Contiene la implementación y ejemplos de derivación basados en una Gramática Libre de Contexto (GLC). Utiliza un alfabeto inspirado en bases nitrogenadas `Σ = {a, c, g, t}` para modelar herramientas de dibujo y generar cadenas válidas que representen figuras geométricas como cuadrados, árboles con ramas/hojas y cubos.

### 3. Higiene y Optimización de Gramáticas
- 📁 **`programa2_higiene_gramaticas/`**:
  Aborda de manera algorítmica las patologías comunes en el diseño de gramáticas que provocan errores durante la fase de análisis sintáctico en un compilador:
  - Detección de gramáticas ambiguas (demostrando árboles de derivación múltiples).
  - Algoritmos para la eliminación de la **Recursividad por la Izquierda**.
  - Optimización mediante la técnica de **Factorización por la Izquierda**.

### 4. Expresiones Regulares y Autómatas (Caso Práctico: Ajedrez)
- 📁 **`programa3_pgn_afd/`**:
  Contiene la definición y el script computacional (Autómata Finito Determinístico - AFD) que simula el motor de reconocimiento para un subconjunto simplificado del lenguaje **PGN (Portable Game Notation)** utilizado en el ajedrez.
  El autómata valida exclusivamente la sintaxis de los movimientos básicos hacia una casilla de destino (ej. `Nf3`, `e4`), aplicando estrictamente la expresión regular diseñada.

---

## 👥 Integrantes del Equipo

- **Castro Robert** (C.I: V-30.994.039)
- **Flores Endrys** (C.I: V-30.451.556)
- **Ramírez Alexmary** (C.I: V-31.809.930)
- **Vallenilla Daniel** (C.I: V-31.159.105)

**Profesor:** Ing. Félix Márquez  
*Ciudad Guayana, Junio de 2026*
