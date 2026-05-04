# Semana 6 - Hill Climbing 

En esta semana se implementa el algoritmo **Hill Climbing** aplicado al problema de ubicación óptima de hospitales en un mapa.

---

## Descripción

Hill Climbing es un algoritmo de búsqueda local que busca minimizar (o maximizar) una función de costo moviéndose iterativamente hacia el vecino con mejor evaluación.

La idea es que:

* Se parte de una configuración inicial del mapa
* En cada iteración se evalúan **todos los movimientos posibles** de cada hospital
* Se elige el movimiento que **reduce más el costo total**
* Se repite hasta que ningún movimiento mejore el resultado (óptimo local)

El costo se calcula como la **suma de distancias Manhattan** de cada hospital a cada casa:

* Costo alto → hospitales lejos de las casas
* Costo bajo → hospitales cerca de las casas
* Costo mínimo local → ningún movimiento de un paso mejora el resultado

---

## Interfaz

Se hizo una interfaz con **Pygame** donde:

* Se visualiza el mapa con hospitales y casas en una grilla
* Se muestran en tiempo real las **líneas de distancia Manhattan**
* Se anima cada movimiento candidato evaluado por el algoritmo
* El usuario puede mover hospitales **manualmente** haciendo clic
* Se puede ajustar la velocidad de animación con un slider

---

## Archivos

* `hc.py`: lógica del algoritmo Hill Climbing
* `utils.py`: funciones auxiliares (costo, acciones, distancia Manhattan, etc.)
* `main.py`: interfaz gráfica con Pygame

---

## Cómo ejecutar

Instalar dependencias:

```
pip install pygame
```

Ejecutar:

```
python main.py
```

---

## Controles

| Tecla / Acción | Efecto |
|---|---|
| `ESPACIO` | Correr Hill Climbing automáticamente |
| `N` | Avanzar un paso a la vez |
| `R` | Reiniciar al mapa original |
| `G` | Generar un mapa aleatorio |
| Clic en 🏥 | Seleccionar hospital para mover |
| Clic en celda amarilla | Mover hospital seleccionado |

---

# Semana 9 - Simulated Annealing

En esta semana se agrega el algoritmo **Simulated Annealing** como segunda opción en la misma interfaz de Pygame del Hill Climbing.

---

## Descripción

Simulated Annealing es una extensión de la búsqueda local que, a diferencia del Hill Climbing puro, puede **aceptar movimientos que empeoran** el costo con cierta probabilidad. Esto le permite escapar de óptimos locales.

La idea es que:

* Se parte de una configuración inicial y una **temperatura alta**
* En cada iteración se elige un hospital aleatorio y un movimiento aleatorio
* Si el movimiento mejora el costo, se acepta siempre
* Si el movimiento empeora el costo, se acepta con probabilidad `e^(-Δ/T)`
* La temperatura se reduce en cada paso multiplicándola por el **factor de enfriamiento**
* A medida que la temperatura baja, el algoritmo se vuelve más selectivo

Parámetros utilizados:

* `T_inicial = 10.0` → temperatura de partida
* `T_min = 0.1` → temperatura mínima (criterio de parada)
* `cooling_rate = 0.95` → factor de enfriamiento por iteración

---

## Interfaz

Se integró Simulated Annealing en la misma interfaz con **Pygame**, agregando:

* **Botones de modo** para alternar entre Hill Climbing y Simulated Annealing
* Panel de estadísticas extendido que muestra **temperatura actual** y **probabilidad de aceptación** cuando SA está activo
* Las celdas candidatas se resaltan en **púrpura** (en lugar del naranja de HC) para distinguir visualmente el modo
* El log registra en cada movimiento el delta de costo, la probabilidad y la temperatura

---

## Archivos

* `hc.py`: lógica de Hill Climbing y Simulated Annealing
* `utils.py`: funciones auxiliares (compartidas entre ambos algoritmos)
* `main.py`: interfaz gráfica con Pygame (soporta ambos modos)

---

## Cómo ejecutar

```
pip install pygame
python main.py
```

---

## Controles adicionales (SA)

| Acción | Efecto |
|---|---|
| Clic en `Hill Climbing` | Cambiar al modo HC |
| Clic en `Simul. Annealing` | Cambiar al modo SA |
| Panel de stats | Muestra temperatura y P. aceptar en modo SA |