 Descripción del Recocido Simulado Implementado

El fragmento de código presentado implementa la metaheurística de Recocido Simulado (Simulated Annealing, SA) aplicada al problema de asignación de empleados y días.
A continuación se describe su funcionamiento y los componentes clave del algoritmo.

 Función generar_vecino_swap(assignment, instance)

Esta función genera una solución vecina a partir de una solución actual intercambiando (swap) asignaciones de dos empleados en un mismo día.

Mecanismo:

Se obtiene la lista de días y empleados desde la instancia del problema.

Se selecciona un día aleatorio d ∈ Days.

Se eligen aleatoriamente dos empleados a y b asignados en ese día.

Se intercambian sus asignaciones, produciendo una nueva solución vecina.

Representación matemática:

Dada una solución 
𝑆
S, el vecino 
𝑆
′
S
′
 se genera mediante un operador 
𝑁
N tal que:

𝑆
′
=
𝑁
(
𝑆
)
donde
𝑁
:
𝑆
→
𝑆
′
S
′
=N(S)dondeN:S→S
′

En este caso, 
𝑁
N realiza un intercambio entre dos elementos (empleados) en un día seleccionado al azar.

 Función simulated_annealing(...)

Esta función implementa el algoritmo de recocido simulado, el cual busca escapar de óptimos locales mediante la aceptación controlada de soluciones peores según una temperatura decreciente.

Parámetros principales:

𝑇
𝑖
𝑛
𝑖
𝑐
𝑖
𝑎
𝑙
T
inicial
	​

: Temperatura inicial.

𝑇
𝑓
𝑖
𝑛
𝑎
𝑙
T
final
	​

: Temperatura final o umbral de parada.

𝛼
α: Factor de enfriamiento (0 < α < 1).

iter_por_temp: Número de iteraciones por cada temperatura.

🔹 Mecanismo del algoritmo

Inicialización:
Se parte de una solución inicial 
𝑆
0
S
0
	​

 y su evaluación 
𝑓
(
𝑆
0
)
f(S
0
	​

).
También se guarda la mejor solución encontrada 
𝑆
∗
S
∗
.

Iteraciones por temperatura:
Mientras 
𝑇
>
𝑇
𝑓
𝑖
𝑛
𝑎
𝑙
T>T
final
	​

, se repite el siguiente ciclo:

Se genera un vecino 
𝑆
′
S
′
 usando generar_vecino.

Se evalúa el cambio de calidad:

Δ
=
𝑓
(
𝑆
′
)
−
𝑓
(
𝑆
)
Δ=f(S
′
)−f(S)

Si 
Δ
>
0
Δ>0, la nueva solución es mejor y se acepta.

Si 
Δ
≤
0
Δ≤0, se acepta con probabilidad:

𝑃
=
𝑒
Δ
𝑇
P=e
T
Δ
	​


Esta probabilidad permite aceptar soluciones peores al inicio del proceso (cuando 
𝑇
T es alta), fomentando la exploración del espacio de búsqueda.

Actualización de temperatura:
Después de cada bloque de iteraciones, se actualiza la temperatura:

𝑇
=
𝛼
⋅
𝑇
T=α⋅T

Criterio de parada:
El algoritmo termina cuando 
𝑇
≤
𝑇
𝑓
𝑖
𝑛
𝑎
𝑙
T≤T
final
	​

.

Control global de la búsqueda

El mecanismo global del recocido simulado se basa en un control termodinámico del proceso:

La temperatura 
𝑇
T actúa como un mecanismo de control de aceptación de soluciones subóptimas.

A medida que 
𝑇
T disminuye, la búsqueda pasa de ser exploratoria (alta probabilidad de aceptar soluciones peores) a explotatoria (solo se aceptan mejoras o pequeños empeoramientos).

Este equilibrio permite escapar de óptimos locales y acercarse al óptimo global.

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

return mejor

 Conclusión

El algoritmo implementado utiliza el recocido simulado clásico con un operador de vecindad tipo swap, un esquema de enfriamiento geométrico y un control probabilístico de aceptación.
Este enfoque permite explorar ampliamente el espacio de soluciones al inicio y refinar la búsqueda hacia soluciones de alta calidad conforme avanza el proceso de enfriamiento.