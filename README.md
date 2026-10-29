# Algoritmo genético para optimizar una función

**Tecnológico de Estudios Superiores de Ixtapaluca (TESI)**  
Ingeniería en Sistemas Computacionales · Algoritmos Evolutivos · Segundo parcial  
Grupo 1951 · Noveno semestre

**Equipo:** Chazari Martinez Leonardo, Rubi Cabrera Jose Antonio y Torres Lucero Uriel.

## ¿Qué hicimos en este proyecto?

El objetivo es buscar el valor máximo de la función

`f(x) = x * sen(10πx) + 1`, con `x` entre `-1` y `2`.

Para resolverlo utilizamos un algoritmo genético con cromosomas de 16 bits. En cada generación se evalúan las soluciones, se eligen padres mediante ruleta, se cruzan en un punto y se aplican mutaciones a los bits. El elitismo puede activarse o desactivarse.

También comparamos la mejor solución encontrada contra una búsqueda exhaustiva de los 65 536 cromosomas posibles. Esa comparación es válida para la **representación binaria elegida**, no necesariamente para todos los números reales del intervalo.

## Antes de empezar

Necesitas Python 3.10 o superior, Visual Studio Code y Git si vas a subir el proyecto a GitHub. Para crear las gráficas usamos Matplotlib.

En Windows, abre esta carpeta en Visual Studio Code y escribe en la terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe menu.py
```

El menú sirve para consultar los parámetros, cambiarlos y ejecutar las pruebas sin modificar el código del algoritmo.

Si prefieres ejecutar cada parte por separado:

```powershell
.\.venv\Scripts\python.exe algoritmo_genetico.py --config config.json --out salida_basica
.\.venv\Scripts\python.exe experimentos.py --out resultados --generations 70
.\.venv\Scripts\python.exe -m unittest test_algoritmo -v
```

## Archivos del proyecto

| Archivo | ¿Para qué lo usamos? |
| --- | --- |
| `algoritmo_genetico.py` | Contiene las operaciones del algoritmo y genera resultados de una ejecución. |
| `config.json` | Guarda la población, generaciones, probabilidades, semilla y elitismo. |
| `menu.py` | Muestra las opciones en la terminal y permite modificar la configuración. |
| `experimentos.py` | Compara 8 combinaciones de parámetros con 5 semillas cada una. |
| `test_algoritmo.py` | Verifica el dominio, algunos operadores y la reproducibilidad. |
| `requirements.txt` | Dependencia utilizada para generar las gráficas. |
| `resultados_ejemplo/` | Archivos de referencia de ejecuciones anteriores; pueden regenerarse. |
| `docs/` | Notas de configuración, resultados y guía para trabajar en GitHub. |

## Cambiar parámetros

Los valores iniciales están en `config.json`. Por ejemplo:

```json
{
  "population_size": 30,
  "generations": 80,
  "crossover_probability": 0.8,
  "mutation_probability": 0.01,
  "seed": 42,
  "elitism": true,
  "plateau_window": 15
}
```

Se pueden editar desde el menú (opción 2) o directamente en el archivo JSON. Es importante escribir las probabilidades como números entre 0 y 1. La mutación se aplica **por bit** y el tamaño de población debe ser par y al menos 4.

La opción 4 del menú usa el valor de `generations` del JSON, pero las 8 combinaciones de población, cruce y mutación, así como las 5 semillas, se encuentran en `experimentos.py`. Para repetir las mediciones de ejemplo con 70 generaciones usa el segundo comando del apartado anterior.

## ¿Qué resultados aparecen?

Después de ejecutar el algoritmo se crea `salida_basica/` con el resultado en JSON, el historial en CSV y la gráfica de convergencia. El programa experimental crea `resultados/` con tablas y gráficas de comparación. Estas carpetas de salida están excluidas de Git para evitar subir archivos generados cada vez que se ejecuta.
