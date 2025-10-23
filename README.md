**Proyecto Heurística – Asignación de Puestos en Trabajos Híbridos**

- Autoría del código base: ver `instances/entrega2.py` & `instances/entrega2_ILS.py` (Universidad EAFIT, 2025)
- Este repo contiene un heurístico con construcción aleatorizada, recocido simulado y ILS como metaheuristico de busqueda local

**Contenido**
- ¿Qué resuelve? y formato de instancias
- Puntaje y análisis lexicográfico
- SA como sustituto (y pseudocódigo)
- ILS como metaheuristico por swaps (y pseudocódigo)
- Validación, reporte y exportación a plantilla (CSV)
- Experimentos y análisis de resultados (scripts incluidos)



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


**Puntaje y Análisis Lexicográfico**
- `score_solution_lex(instance, assignment) -> (C1, C2, C3)`:
  - C1: conteo de asignaciones que respetan preferencias (`Desks_E`).
  - C2: por grupo y día, tamaño del mayor conjunto en una misma zona; se suman por todos los grupos y días.
  - C3: balance por día: `-(max_ocupación_zona - min_ocupación_zona)`.
- Comparación lexicográfica: una solución A es mejor que B si `C1_A > C1_B`, o si empatan en C1 y `C2_A > C2_B`, o si empatan en C1 y C2 y `C3_A > C3_B`.

**SA**
Como sustituto a la busqueda local implementamos un SA debido a que en la entrega anterior realizamos una busqueda local. Acontinuacion la explicacion del SA aplicada al problema de asignación de empleados y días.


 def generar_vecino_swap(assignment, instance)

Esta función genera una solución vecina a partir de una solución actual intercambiando (swap) asignaciones de dos empleados en un mismo día.

- Se obtiene la lista de días y empleados desde la instancia del problema.
- Se selecciona un día aleatorio d ∈ Days.
- Se eligen aleatoriamente dos empleados a y b asignados en ese día.
- Se intercambian sus asignaciones, produciendo una nueva solución vecina.
- Se realiza un intercambio entre dos empleados en un día seleccionado al azar.

 def simulated_annealing(...)

- Esta función implementa el algoritmo de recocido    simulado, el cual busca escapar de óptimos locales mediante la aceptación controlada de soluciones peores según una temperatura decreciente.

- Los parametros principales para el SA son: Tinicial, Tfinal, flag (para detenerse), cooldown

- Se parte de la solucion incial y su evaluacion, de ahi se repite el siguiente ciclo: Se genera vecino, se evalua el cambio de calidad, si la nueva solucion es mejor se acepta sino se acepta con probabilidad. Actualizacion de temperatura y evaluacion de criterio de parada.

 Pseudocódigo resumido
S = solucion_inicial
mejor = S
T = T_inicial

while T > T_final:
    for i in range(iter_por_temp):
        S' = generar_vecino(S)
        Δ = evaluar(S') - evaluar(S)
        if Δ > 0 or random() < exp(Δ / T):
            S = S'
            if evaluar(S) > evaluar(mejor):
                mejor = S
    T *= alpha


**ILS**
- A continuación, se describe cómo funciona el ILS en el contexto del problema de asignación de empleados y escritorios por día.

  def local_search_swaps_hillclimb(instance, assignment, evaluar, iters=500, seed=None)

- Esta función aplica una búsqueda local tipo hill climbing para mejorar la solución actual:

- Se copia la asignación inicial y se evalúa su puntaje con evaluar().

- En cada iteración:

- Se selecciona un día aleatorio dentro de los disponibles (Days).

- Se eligen dos empleados asignados ese día y se intercambian sus escritorios.

- Se evalúa la nueva solución; si el puntaje mejora, se acepta el cambio.

- Este proceso se repite un número fijo de veces (iters), intensificando la búsqueda en el vecindario inmediato de la solución actual.

- El resultado es una solución localmente óptima respecto a los intercambios (swaps).

  def perturbation_k_swaps(assignment, instance, k=3, seed=None)

- Esta función introduce una perturbación controlada en la solución actual para escapar de óptimos locales:

- Realiza k intercambios aleatorios entre empleados en días aleatorios.

- El objetivo es modificar ligeramente la estructura de la solución para que la siguiente búsqueda local explore una región diferente del espacio de soluciones.

- Este mecanismo mantiene la diversidad sin reiniciar completamente la búsqueda.

  def iterated_local_search(instance, initial, evaluar, local_search_func, perturb_func, ...)

Esta función implementa el esquema global del ILS.
Su flujo de ejecución es el siguiente:

Búsqueda local inicial:
Se aplica local_search_func (hill climbing) sobre la solución constructiva inicial para obtener una primera solución mejorada.

Iteraciones ILS:
En cada ciclo:

Se perturba la mejor solución actual mediante perturb_func (por defecto k=3 intercambios).

Se aplica nuevamente la búsqueda local a la solución perturbada.

Se evalúa la nueva solución (val_p) y si supera a la mejor conocida (best_val), se actualiza la solución óptima global.

En caso contrario, se mantiene la actual pero se continúa explorando desde la perturbada.

Criterio de parada:
Se repite el ciclo hasta alcanzar el número máximo de iteraciones (max_iters).

Resultado:
Devuelve la mejor asignación encontrada tras todas las perturbaciones y búsquedas locales.

Pseudocódigo resumido
S = local_search(initial)   # mejora inicial
best = S
best_val = evaluar(best)

for i in range(max_iters):
    S_p = perturbation(S, k)         # diversificación
    S_p = local_search(S_p)          # intensificación
    val_p = evaluar(S_p)
    if val_p > best_val:             # mejora global
        best = copy(S_p)
        best_val = val_p
        S = S_p
    else:
        S = S_p                      # continuar explorando

return best


En resumen, el ILS combina fases de búsqueda local intensiva y perturbaciones controladas para mantener un equilibrio entre mejora continua y exploración global.
Aplicado al problema de asignación de empleados y escritorios, el algoritmo logra soluciones de alta calidad:

La ILS mejora la coherencia diaria de asignaciones.

Las perturbaciones permiten encontrar nuevas combinaciones de días y empleados que satisfacen mejor las preferencias y cohesionan los grupos.

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
En términos de tiempo de cómputo, el método de la primera entrega (heurística constructiva + búsqueda local) mostró que sin mejora local la ejecución fue casi instantánea (≈ 0.0003 s en la instancia 1), mientras que al aplicar la búsqueda local aumentó a ≈ 0.02 s.
Esto demuestra que la fase de mejora local introduce un coste moderado, pero sigue siendo muy bajo en relación con el tamaño del problema, lo cual es favorable para aplicaciones en tiempo real.

En la segunda entrega, el enfoque ILS (Iterated Local Search) elevó el tiempo promedio por instancia a alrededor de 0.15 s, debido a la ejecución repetida de la búsqueda local con perturbaciones. Sin embargo, este coste adicional permitió una exploración más profunda del espacio de soluciones y una mayor robustez frente a las condiciones iniciales.

En cuanto a la calidad de las soluciones, en la primera entrega el paso de sin búsqueda local → con búsqueda local permitió mejorar C1 (preferencias de empleados) de 34 → 38, a costa de una ligera reducción en C2 (cohesión de grupo) de 38 → 34, manteniendo C3 (balance de zonas) prácticamente constante.
Dado que la comparación se realiza de forma lexicográfica, el aumento en C1 justifica la pérdida marginal en C2, por lo que la versión mejorada de la segunda entrega resulta preferible.

En la segunda entrega, el método ILS alcanzó valores aún mayores: C1 = 39, C2 = 36 y C3 = –7, mostrando un mejor cumplimiento de preferencias y una distribución más estable. Además, la variabilidad entre ejecuciones fue menor, lo que indica que el método escala correctamente y produce soluciones de buena calidad de manera consistente.

En síntesis, el desempeño global obtenido es muy positivo: la relación entre tiempo y calidad está bien equilibrada.
El aumento de tiempo asociado a los métodos (SA e ILS) es bajo comparado con la mejora significativa en la calidad de las soluciones.
Aunque existe margen de mejora —por ejemplo, aumentar el número de iteraciones, diseñar operadores de intercambio más informados o realizar un análisis de sensibilidad sobre la sedd y el parámetro top-k—, los resultados demuestran que el modelo híbrido desarrollado cumple los objetivos del proyecto del curso de forma eficiente.

Aspecto a mejorar: Me gustaria estudiar la escalabilidad del método en instancias de mayor tamaño y ajustar el equilibrio entre exploración y explotación, con el fin de seguir reduciendo el tiempo de cómputo sin sacrificar la calidad de las soluciones ademas de organizar mejor los archivos para proximas entregas.


- Se incluyen scripts para ejecutar barridos y resumir resultados:
  - `scripts/run_experiments.py`: recorre instancias y semillas y guarda `results/experiments.csv` con columnas `instance,method,seed,iters,top_k,C1,C2,C3,runtime_sec`.
  - `scripts/summarize_results.py`: genera `results/summary.csv` y `results/summary.md` con promedios y mejor corrida por instancia y método.
- Ejemplo rápido (solo instance1, 3 semillas):
  - `python scripts/run_experiments.py --instances-glob "instances/instance1.json" --num-seeds 3 --seed-start 1 --methods both --iters 300 --top-k 3 --out results/experiments.csv`
  - `python scripts/summarize_results.py --in results/experiments.csv --out-csv results/summary.csv --out-md results/summary.md`
- Muestra de resumen real obtenido:
  - instance1.json: local avg=(39.0, 31.667, -7.667) vs no_local avg=(36.667, 31.667, -7.667); tiempo promedio local≈0.022s, no_local≈0.0003s; conclusión: promedio lexicográfico favorece local.


**Guía Paso a Paso (Windows – VS Code)**
- Ejecutar recocido simulado por instancia
 python entrega2_ILS.py --in instance1.json --outdir results_sa --iters 500 --top-k 3 --tinit 200 --tfinal 1 --alpha 0.95 --report --validate --export-csv

- Ejecutar ILS por instancia 
python entrega2_ILS.py --in instance1.json --outdir results_ils --ils --ils-iters 20 --ls-iters 500 --perturb-k 3 --top-k 3 --report --validate --export-csv


- Con el siguiente comando se genera un resultado y su respectivo CSV.
cd "C:\Users\Polnareff\Desktop\Heuristikaka\Heuristicas\scripts"
python summarize_results.py --in "..\results\experiments.csv" --out-csv "..\results\summary.csv" --out-md "..\results\summary.md"

- Abrir VS Code en la carpeta del repo > Terminal > New Terminal.
- Prueba rápida (una instancia, con local):
  - `python .\instances\entrega1.py --in instance1.json --report --validate --export-csv`
- Experimentos completos y resúmenes:
  - `python .\scripts\run_experiments.py --instances-glob "instances\instance*.json" --num-seeds 10 --seed-start 1 --methods both --iters 1200 --top-k 3 --out results\experiments.csv`
  - `python .\scripts\summarize_results.py --in results\experiments.csv --out-csv results\summary.csv --out-md results\summary.md`
- Limpieza de salidas (opcional):
  - `rmdir /s /q results` y `rmdir /s /q instances\solutions` (CMD) o
  - `Remove-Item -Recurse -Force .\results, .\instances\solutions, .\instances\solutions_no_local` (PowerShell)


# Heuristicas
