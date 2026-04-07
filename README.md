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