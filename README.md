# Predicción de litofacies a partir de registros de pozo (FORCE 2020)

Proyecto Integrador II, Maestría en Ciencia de Datos y Analítica, Universidad EAFIT (2026-2). Equipo 7: Andrés Velasco, Daniel Pareja, Juan Morales, Santiago Molano, David Gómez.

El objetivo es predecir el tipo de roca (litofacies) a lo largo de un pozo a partir de sus registros geofísicos. Cada pozo se trata como una serie multivariada indexada por profundidad, y la evaluación se hace siempre sobre pozos completos que el modelo no vio durante el entrenamiento.

## Estado (5 de noviembre de 2026)

| etapa | estado |
|---|---|
| 1. Inspección y consolidación de los datos | completa |
| 2. Curación y control de calidad | completa |
| 3. Análisis exploratorio como series (ventana W = 339 filas, 51.5 m) | completa |
| 4. Protocolo de evaluación (partición, prueba sellada, métricas) | completa, 12 controles de cierre cumplidos |
| 5. Modelos de referencia | en curso |
| 6. Preparación de datos para aprendizaje profundo | en curso |
| 7. Modelado profundo y comparación | en curso |
| 8 a 10 | pendientes |

Exposición final: 3 de diciembre de 2026.

El protocolo de evaluación se publicó en este repositorio antes de entrenar el primer modelo. Las reglas de `docs/protocolo/protocolo-evaluacion.md` no se cambian después de ver resultados.

## Contenido

```
Proyecto_Integrador_II.ipynb   notebook principal del custodio (secciones 1 a 4)
evaluacion_prueba.py           evaluate_test: evaluación única sobre la prueba, con registro (solo custodio)
manifiesto_datos.json          huellas sha256 de la fuente, los productos, la partición y la matriz
etapa4_particion.csv           partición por pozos: prueba (22) y 5 pliegues (96)
registro_ensayo.json           registro de los ensayos de evaluate_test sobre el pliegue 0
requirements.txt               dependencias del notebook
equipo/                        copia de la carpeta compartida con el equipo (sin el parquet)
  acceso_datos.py              load_split y load_partition: única vía de carga de datos con etiqueta
  metricas.py                  evaluate, paired_difference, strata, mlflow_scalars: toda evaluación
  revision_notebooks.py        scan_notebook: detecta lecturas directas de archivos con etiqueta
  manifiesto_equipo.json       huellas esperadas de la partición, el archivo de trabajo y la matriz
  etapa4_particion.csv         copia de la partición (misma huella)
  penalty_matrix.npy           matriz de penalización de FORCE 2020, sin modificar
docs/protocolo/                protocolo de evaluación consolidado y detalle de sus cuatro objetivos
informe/                       documento del proyecto (LaTeX y PDF)
```

## Dónde están los datos

Los datos no están en este repositorio. Viven en Google Drive:

| carpeta | quién la ve | contenido |
|---|---|---|
| `MyDrive/Proyecto_Integrador_II/` | solo el custodio (Juan José) | datos curados, archivo sellado con las etiquetas de prueba, notebook |
| `MyDrive/Proyecto_Integrador_II/equipo/` | todo el equipo (compartida) | `etapa4_pool_trabajo.parquet` y los módulos de esta carpeta `equipo/` |

`etapa4_pool_trabajo.parquet` tiene los 118 pozos con todas sus curvas, pero la roca de los 22 pozos de prueba está vacía (NaN). Es la única entrada con etiqueta de las Etapas 5 a 8.

La fuente original es el repositorio público de la competencia FORCE 2020 (<https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition>, carpeta `lithology_competition/data`, licencias CC-BY 4.0 y NOLD 2.0). El notebook la descarga de ahí y verifica sus huellas contra `manifiesto_datos.json`.

## Cómo empezar (Etapas 5, 6 y 7)

1. En Google Drive, abre "Compartido conmigo", haz clic derecho sobre la carpeta `equipo` y elige "Organizar > Añadir acceso directo" dentro de "Mi unidad".
2. En Colab:

```python
from google.colab import drive
drive.mount("/content/drive")

import sys
sys.dont_write_bytecode = True
TEAM_DIR = "/content/drive/MyDrive/equipo"   # ruta del acceso directo
sys.path.insert(0, TEAM_DIR)

from acceso_datos import load_split, load_partition
from metricas import evaluate, strata, paired_difference

train = load_split(["fold1", "fold2", "fold3", "fold4"])   # 76 pozos, con roca
val = load_split(["fold0"])                                # 20 pozos, con roca
test_x = load_split(["test"], labels=False)                # 22 pozos, solo curvas
```

Importa los módulos desde la carpeta de Drive, no desde una copia de este repositorio: buscan el parquet y los manifiestos en su misma carpeta, y verifican las huellas al cargar.

Pedir `"test"` con etiqueta lanza un error a propósito. La roca de la prueba solo la lee `evaluate_test`, una vez, al final del proyecto.

## Reglas que no se negocian

- Toda carga de datos con etiqueta pasa por `load_split`. Nunca se leen directamente los parquet del custodio.
- Entrenamiento = pliegues 1 a 4. Validación = pliegue 0. La validación sirve para elegir, nunca para ajustar parámetros.
- Todo lo que se ajusta (normalización global, pesos de clase, imputadores) se calcula solo con pozos de entrenamiento.
- Las ventanas nunca cruzan de un pozo a otro ni un salto de profundidad (`depth_segment`).
- Todo modelo predice todas las filas del conjunto que se evalúa, incluidos bordes y tramos cortos.
- Toda evaluación usa `evaluate` de `equipo/metricas.py`. La métrica principal es el puntaje de penalización de FORCE promediado por pozo (0 es perfecto, −4 el peor).
- Dos modelos son distintos solo si el intervalo del 95% de su diferencia pareada pozo a pozo (`paired_difference`) no incluye el cero.
- Antes de integrar un notebook, el custodio corre `scan_notebook` sobre él.

El detalle y la justificación de cada regla están en `docs/protocolo/protocolo-evaluacion.md`.

## Reproducir (custodio)

1. Copiar el contenido del repositorio en `MyDrive/Proyecto_Integrador_II` y abrir `Proyecto_Integrador_II.ipynb` en Colab.
2. Ejecutar las secciones 1 a 3 para regenerar los parquet. La sección 4 corre sola desde el parquet curado ("Ejecutar las celdas posteriores" desde su primera celda).
3. Comprobar que las huellas impresas coinciden con `manifiesto_datos.json`: curado `82f590e8…`, partición `c55dc4d0…`, trabajo `45a0ed6f…`, sellado `1904defd…`, matriz `c312481a…`. La última celda de la sección 4 debe imprimir `Etapa 4 verificada: True`.

El archivo con las etiquetas de los 22 pozos de prueba (`etapa4_prueba_sellada.parquet`) queda fuera del repositorio a propósito.

## Documentos

| documento | contenido |
|---|---|
| `docs/protocolo/protocolo-evaluacion.md` | protocolo completo en un solo documento; empezar por aquí |
| `docs/protocolo/etapa4-objetivo1-particion.md` | cómo se construyó la partición por pozos |
| `docs/protocolo/etapa4-objetivo2-prueba.md` | reserva de la prueba y regla de un solo uso |
| `docs/protocolo/etapa4-objetivo3-metricas.md` | métricas, matriz de penalización e incertidumbre |
| `docs/protocolo/etapa4-objetivo4-particion-aleatoria.md` | por qué no se reparten filas al azar, con la demostración |
