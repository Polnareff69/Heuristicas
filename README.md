**Proyecto Heurística – Asignación de Puestos en Trabajos Híbridos**

- Autoría del código base: ver `instances/entrega1.py` (Universidad EAFIT, 2025)
- Este repo contiene un heurístico con construcción aleatorizada y mejora local para asignar empleados a escritorios por día, respetando preferencias y promoviendo cohesión de grupos y balance por zonas.

**Contenido**
- ¿Qué resuelve? y formato de instancias
- Método constructivo + aleatorización (y pseudocódigo)
- Puntaje y análisis lexicográfico
- Búsqueda local por swaps (y pseudocódigo)
- Validación, reporte y exportación a plantilla (CSV)
- Uso del CLI con ejemplos (Windows y Linux/macOS)
- Experimentos y análisis de resultados (scripts incluidos)
- Resultados de referencia (con vs sin búsqueda local)
- Reproducibilidad, código y póster
- Troubleshooting (Windows)

**Requisitos**
- Python 3.8 o superior.
- Sin dependencias externas para correr el algoritmo y exportar CSV.
- Para generar gráficas del póster: `matplotlib` (opcional).
  - Windows (PowerShell): `python -m pip install matplotlib`
  - Linux/macOS: `python3 -m pip install matplotlib`

**Qué Resuelve**
- Asigna, para cada día de la semana, a qué escritorio se sienta cada empleado.
- Objetivos (orden lexicográfico):
  - C1 Preferencias: maximizar empleados sentados en uno de sus escritorios preferidos.
  - C2 Cohesión de grupo: para cada grupo, maximizar el tamaño de su mayor agregado por zona.
  - C3 Balance por zonas: minimizar la diferencia de ocupación entre zonas (se suma como `-(max-min)`).

**Formato De Instancias**
- Archivo JSON (ver `instances/instance1.json`):
  - `Employees`: lista de empleados (`"E0"`, `"E1"`, …).
  - `Desks`: lista de escritorios (`"D0"`, `"D1"`, …).
  - `Days`: lista de días (p. ej. `"L"`, `"Ma"`, `"Mi"`, `"J"`, `"V"`).
  - `Groups`: lista de grupos (`"G0"`, …) y `Employees_G`: mapa grupo → empleados.
  - `Zones`: lista de zonas (`"Z0"`, `"Z1"`) y `Desks_Z`: mapa zona → escritorios.
  - `Desks_E`: mapa empleado → lista de escritorios preferidos.
  - `Days_E`: mapa empleado → días en los que asiste (si falta, se asume todos los días).

**Método Constructivo + Aleatorización**
- Para cada día:
  - Determina empleados presentes (`Days_E`).
  - Recorre empleados (orden aleatorio con semilla `--seed`).
  - Intenta asignar un escritorio disponible siguiendo esta prioridad:
    - Preferidos del empleado, de la zona predominante de su grupo ese día (si la hay).
    - Preferidos del empleado (sin filtrar por zona), top-k aleatorizado (`--top-k`).
    - Cualquier escritorio libre, idealmente en la zona predominante de su grupo si existe.
  - Mantiene el conteo de zonas ocupadas por grupo para fomentar proximidad.

- Pseudocódigo (constructivo):
  - Dado `Days`, `Employees`, `Desks`, `Desks_E`, `Employees_G`, `Desks_Z`:
  - Para cada día d en Days:
    - `present = {e ∈ Employees | d ∈ Days_E[e]}` (o todos si no hay Days_E)
    - Mezclar `present` con semilla (`--seed`)
    - `used = ∅` y `group_zone[d][g][z] = 0` para todo grupo g, zona z
    - Para cada empleado e en `present`:
      - `g = grupo(e)`; `z* = argmax_z group_zone[d][g][z]` si existe
      - `P = [p ∈ Desks_E[e] | p ∉ used]`
      - Si `z*` existe, `Pz = [p ∈ P | zone(p) = z*]` sino `Pz = P`
      - Elegir `desk` de: `Pz` (aleatorio en top-k), luego `P` (aleatorio en top-k), luego cualquier libre (idealmente zona z*)
      - Asignar `assign[d][e] = desk` o `None` si no hay
      - Marcar `desk` en `used` y actualizar `group_zone[d][g][zone(desk)]++`
    - Completar con `None` a empleados no presentes

- Método aleatorizado: el constructivo anterior es la base; la aleatorización se controla por:
  - El orden aleatorio de empleados presentes (semilla `--seed`).
  - La elección aleatoria dentro del `top-k` de preferencias disponibles (`--top-k`).
  - Esto induce diversidad en soluciones de partida, útil para la búsqueda local.

**Puntaje y Análisis Lexicográfico**
- `score_solution_lex(instance, assignment) -> (C1, C2, C3)`:
  - C1: conteo de asignaciones que respetan preferencias (`Desks_E`).
  - C2: por grupo y día, tamaño del mayor conjunto en una misma zona; se suman por todos los grupos y días.
  - C3: balance por día: `-(max_ocupación_zona - min_ocupación_zona)`.
- Comparación lexicográfica: una solución A es mejor que B si `C1_A > C1_B`, o si empatan en C1 y `C2_A > C2_B`, o si empatan en C1 y C2 y `C3_A > C3_B`.

**Búsqueda Local Por Swaps**
- `local_search_swaps`: por iteraciones (`--iters`), elige un día aleatorio y realiza un swap entre dos empleados asignados ese día.
- Acepta el movimiento si mejora el puntaje lexicográfico.
- Búsqueda local activada por defecto; se puede desactivar con `--no-local-search`.

- Pseudocódigo (búsqueda local):
  - Entrada: `assign`, `iters`, `seed`
  - `best = assign`; `score_best = score(best)`
  - Repetir `iters` veces:
    - Muestrear día `d` con semilla
    - `A = {e | best[d][e] ≠ None}`; si `|A| < 2`, continuar
    - Tomar `a, b` al azar en `A` y proponer swap: `new = best` con `new[d][a] ↔ new[d][b]`
    - Si `score(new) > score_best` (lexicográfico): `best = new`; `score_best = score(new)`
  - Devolver `best`

**Validación y Reporte**
- `--validate`: verifica por día empleados faltantes, escritorios inexistentes y duplicados; si hay errores, sale con código 2.
- `--report`: imprime, por día y totales, asignados y valores C1/C2/C3 para auditar la solución.

**Exportación A Plantilla (CSV)**
- Para cumplir la entrega tipo plantilla Excel, se generan CSVs equivalentes con `--export-csv`:
  - `EmployeeAssignment.csv`: columnas `[Employee, Day1, Day2, ...]` con `Dk` o `none`.
  - `Groups_Meeting_day.csv`: día de reunión por grupo (día con más miembros del grupo asignados).
  - `Summary.csv`: `Valid_assignments`, `Employee_preferences` (C1), `Isolated_employees`, y también `C2`, `C3`.
- Ubicación por defecto: `instances/solutions/csv_export/` (configurable con `--export-dir`).
- Abra cada CSV en Excel y copie su contenido a las hojas correspondientes de la plantilla oficial.

**Uso Del CLI (Command-Line Interface)**
- El código está diseñado para ser ejecutado desde línea de comandos con múltiples parámetros (--seed, --iters, --report, --validate, etc.) para reproducibilidad y análisis comparativo.
- Requisitos: Python 3.8+.
- Comando base (desde la raíz del repo):
  - `python instances/entrega1.py` (lee `instances/instance1.json`, guarda en `instances/solutions/…`).
- Comando PRINCIPAL.
  -  `python .\instances\entrega1.py --in instance10.json --local-search --iters 1000 --seed 42 --top-k 3 --report --validate` (ejemplo de comando para evaluar cualquier instancia, solo es cambiarle el numero de la instancia -> (--in instanceX.json), tambien se le puede ajustar la aleatoriedad cambiandole el numero a la semilla -> (--seed <n>) y los puestos preferidos a tener en cuenta del empleado -> (--top-k <k>)) 

- Flags principales:
  - `--in <archivo>`: instancia a usar. Ej: `--in instance7.json`.
  - `--outdir <carpeta>`: carpeta de salida (acepta absoluta, `~`, variables de entorno). Ej: `--outdir "%TEMP%\heuristica_out"` en Windows.
  - `--seed <int>`: semilla para la aleatorización del constructivo.
  - `--top-k <int>`: limita el muestreo de preferencias al top-k disponible.
  - `--iters <int>`: iteraciones de búsqueda local (por defecto 1000).
  - `--no-local-search`: desactiva la búsqueda local (por defecto está activa).
  - `--local-search`: (compatibilidad) activa, aunque ya viene activa por defecto.
  - `--report`: imprime resumen por día y totales.
  - `--validate`: valida la estructura de la solución antes de guardar.
  - `--stdout`: imprime la solución a consola en lugar de escribir archivo.
  - `--export-csv`: exporta CSVs de plantilla. `--export-dir` para elegir carpeta.

- Ejemplos (Windows PowerShell):
  - Básico: `python .\instances\entrega1.py`
  - Sin búsqueda local: `python .\instances\entrega1.py --no-local-search`
  - Con reporte y validación: `python .\instances\entrega1.py --report --validate`
  - Más iteraciones: `python .\instances\entrega1.py --iters 2000 --report`
  - Cambiar carpeta de salida: `python .\instances\entrega1.py --outdir "%TEMP%\heuristica_out"`
  - Ver JSON por consola: `python .\instances\entrega1.py --stdout > <sol>.json`


**Resultados De Referencia (instance1.json)**
- Semilla por defecto (`--seed 42`), `--top-k 3`:
  - Sin búsqueda local: Puntaje `(C1, C2, C3) = (34, 38, -7)`.
  - Con búsqueda local (1000 iteraciones): Puntaje `(C1, C2, C3) = (38, 34, -7)`.
- Interpretación:
  - La búsqueda local mejoró C1 (más preferencias satisfechas) aunque intercambió parte de la cohesión C2. Al comparar lexicográficamente, la solución con búsqueda local es mejor porque incrementa C1, el objetivo principal.
- Ejemplo de reporte por día con búsqueda local (resumen real obtenido en pruebas):
  - L: asignados=8 | C1=8 C2=6 C3=-2
  - Ma: asignados=9 | C1=9 C2=7 C3=-1
  - Mi: asignados=9 | C1=9 C2=8 C3=-1
  - J: asignados=6 | C1=6 C2=6 C3=0
  - V: asignados=7 | C1=6 C2=7 C3=-3
  - Totales: C1=38 C2=34 C3=-7

**Experimentos y Análisis de Resultados**
- Se incluyen scripts para ejecutar barridos y resumir resultados:
  - `scripts/run_experiments.py`: recorre instancias y semillas y guarda `results/experiments.csv` con columnas `instance,method,seed,iters,top_k,C1,C2,C3,runtime_sec`.
  - `scripts/summarize_results.py`: genera `results/summary.csv` y `results/summary.md` con promedios y mejor corrida por instancia y método.
- Ejemplo rápido (solo instance1, 3 semillas):
  - `python scripts/run_experiments.py --instances-glob "instances/instance1.json" --num-seeds 3 --seed-start 1 --methods both --iters 300 --top-k 3 --out results/experiments.csv`
  - `python scripts/summarize_results.py --in results/experiments.csv --out-csv results/summary.csv --out-md results/summary.md`
- Muestra de resumen real obtenido:
  - instance1.json: local avg=(39.0, 31.667, -7.667) vs no_local avg=(36.667, 31.667, -7.667); tiempo promedio local≈0.022s, no_local≈0.0003s; conclusión: promedio lexicográfico favorece local.

**Póster y Gráficas (C1/C2/C3 y tiempo)**
- Los gráficos y un borrador de póster se generan a partir de `results/summary.csv`.
- Pasos:
  1) Asegúrate de tener resultados: ejecuta los scripts de Experimentos y Resumen (sección anterior).
  2) Instala `matplotlib` (opcional pero necesario para imágenes):
     - Windows: `python -m pip install matplotlib`
  3) Genera póster + imágenes: `python scripts/make_poster_assets.py`
- Archivos generados:
  - `results/poster.md`: texto base del póster (método, tabla comparativa, pseudocódigo, conclusiones y links a imágenes).
  - `results/plots/avg_C1.png`, `avg_C2.png`, `avg_C3.png`, `avg_time.png`.
- Si no ves imágenes, revisa `results/plots/NO_PLOTS.txt` (explica el motivo, p.ej., falta `matplotlib`).

**Guía Paso a Paso (Windows – VS Code)**
- Abrir VS Code en la carpeta del repo > Terminal > New Terminal.
- Prueba rápida (una instancia, con local):
  - `python .\instances\entrega1.py --in instance1.json --report --validate --export-csv`
- Experimentos completos y resúmenes:
  - `python .\scripts\run_experiments.py --instances-glob "instances\instance*.json" --num-seeds 10 --seed-start 1 --methods both --iters 1200 --top-k 3 --out results\experiments.csv`
  - `python .\scripts\summarize_results.py --in results\experiments.csv --out-csv results\summary.csv --out-md results\summary.md`
- Póster + gráficas:
  - (Primero) `python -m pip install matplotlib`
  - (Luego) `python .\scripts\make_poster_assets.py`
- Limpieza de salidas (opcional):
  - `rmdir /s /q results` y `rmdir /s /q instances\solutions` (CMD) o
  - `Remove-Item -Recurse -Force .\results, .\instances\solutions, .\instances\solutions_no_local` (PowerShell)

**Como Clonar y Correr (para terceros)**
- Clonar el repositorio:
  - Windows (PowerShell): `git clone https://github.com/<usuario>/<repo>.git`
  - `cd <repo>`
- (Opcional) Instalar `matplotlib` para gráficas:
  - `python -m pip install matplotlib`
- Ejecutar una instancia con exportación CSV:
  - `python .\instances\entrega1.py --in instance1.json --report --validate --export-csv`
- Experimentos (todas las instancias) y resúmenes:
  - `python .\scripts\run_experiments.py --instances-glob "instances\instance*.json" --num-seeds 10 --seed-start 1 --methods both --iters 1200 --top-k 3 --out results\experiments.csv`
  - `python .\scripts\summarize_results.py --in results\experiments.csv --out-csv results\summary.csv --out-md results\summary.md`
- Póster y gráficas:
  - `python .\scripts\make_poster_assets.py`
  - Abrir `results\poster.md` y `results\plots\*.png`

**Reproducibilidad, Código y Póster**
- Reproducibilidad: usa `--seed` para fijar el orden aleatorio; con la misma semilla, `--top-k` e `--iters` se reproducen los resultados. Guarda el comando y semilla junto a las soluciones.
- Código: el entregable principal es `instances/entrega1.py`. Se ejecuta desde CLI y no requiere dependencias externas. Scripts de experimentación en `scripts/`.
- Póster: sugiere incluir secciones de método constructivo (con pseudocódigo), variante aleatorizada, evaluación lexicográfica, búsqueda local, tabla de resultados (promedios y mejores por instancia), conclusiones y referencias. Puedes copiar tablas desde `results/summary.csv` y `results/summary.md`.

**Troubleshooting (Windows)**
- Si aparece un error al escribir en `instances\solutions`, revisa “Carpetas controladas” (Windows Defender) y permite acceso a `python.exe` o usa otra carpeta con `--outdir "%TEMP%\heuristica_out"`.
- Si alguna app mantiene abierto el archivo de salida, ejecuta con `--stdout` y redirige a un nuevo archivo.

**Estructura Del Código**
- `constructive_assignment`: construcción aleatorizada por día con sesgo de cohesión por zona de grupo.
- `score_solution_lex`: cálculo del puntaje `(C1, C2, C3)` y base para comparación lexicográfica.
- `local_search_swaps`: mejora local por intercambios entre empleados del mismo día.
- `validate_assignment`: verificación de duplicados, empleados faltantes y escritorios inexistentes.
- `report_assignment`: resumen por día y totales de C1/C2/C3.
- `export_csv_template`: exporta CSVs equivalentes a la plantilla Excel (tres hojas).
- `scripts/run_experiments.py`: barridos de semillas e instancias.
- `scripts/summarize_results.py`: genera resúmenes CSV/MD.
- `scripts/make_poster_assets.py`: genera `results/poster.md` y las gráficas `results/plots/*.png` a partir de `results/summary.csv`.
#   H e u r i s t i c a s  
 # Heuristicas
