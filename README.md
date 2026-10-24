# Predicción de litofacies a partir de registros de pozo (FORCE 2020)

Proyecto Integrador II, Maestría en Ciencia de Datos y Analítica, Universidad EAFIT (2026-2). Equipo 7: Andrés Velasco, Daniel Pareja, Juan Morales, Santiago Molano, David Gómez.

El objetivo es predecir la litofacies (tipo de roca) a lo largo de un pozo a partir de sus registros geofísicos. Cada pozo se trata como una serie multivariada indexada por profundidad, y la evaluación se hace siempre sobre pozos completos que el modelo no vio durante el entrenamiento.

## Estado (avance del 23 de octubre de 2026)

| etapa | estado |
|---|---|
| 1. Inspección y consolidación de los datos | completa |
| 2. Curación y control de calidad | completa |
| 3. Análisis exploratorio como series (ventana W = 339 filas, 51.5 m) | completa |
| 4. Protocolo de evaluación | partición y reserva de la prueba cerradas; faltan las métricas |
| 5 en adelante (modelos, MLOps, despliegue) | pendiente |

Todavía no se ha entrenado ningún modelo. El protocolo de evaluación (`docs/protocolo/`) se publica en este repositorio antes del primer modelo.

## Contenido

```
Proyecto_Integrador_II.ipynb   notebook principal (Colab)
evaluacion_prueba.py           evaluate_test: evaluación única sobre la prueba y su registro
manifiesto_datos.json          huellas sha256 de la fuente, los productos y la partición
etapa4_particion.csv           partición por pozos: prueba (22) y 5 pliegues (96)
registro_ensayo.json           registro de los ensayos de evaluate_test sobre el pliegue 0
equipo/
  acceso_datos.py              load_split: única vía de carga de datos con etiqueta
  revision_notebooks.py        scan_notebook: detecta lecturas directas de archivos con etiqueta
  manifiesto_equipo.json       huellas esperadas de la partición y del archivo de trabajo
  etapa4_particion.csv         copia de la partición (misma huella)
docs/protocolo/                partición y regla de uso único de la prueba (Etapa 4)
informe/                       documento del proyecto (LaTeX y PDF)
```

La estructura replica la carpeta de Drive donde corre el notebook (`MyDrive/Proyecto_Integrador_II`), porque los módulos buscan sus archivos con rutas relativas a esa carpeta.

## Datos

Los datos no están en el repositorio. Son los del concurso FORCE 2020 Machine Learning Competition (litofacies, Mar del Norte, 118 pozos), en el repositorio público <https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition> (carpeta `lithology_competition/data`). El notebook los descarga directamente de ahí y verifica sus huellas contra `manifiesto_datos.json`.

Los archivos derivados (`etapa1_pool_consolidado.parquet`, `etapa2_pool_curado.parquet`, `equipo/etapa4_pool_trabajo.parquet`) los regenera el notebook y se validan con las huellas del manifiesto. El archivo con las etiquetas de los 22 pozos de prueba (`etapa4_prueba_sellada.parquet`) queda fuera del repositorio a propósito: solo lo lee `evaluate_test`, una vez, al final del proyecto.

## Reproducir

1. Copiar el contenido del repositorio en `MyDrive/Proyecto_Integrador_II` y abrir `Proyecto_Integrador_II.ipynb` en Google Colab.
2. Ejecutar todas las celdas. La primera monta Drive e instala las dependencias de `requirements.txt`.
3. Comprobar que las huellas impresas coinciden con `manifiesto_datos.json`: curado `82f590e8…`, partición `c55dc4d0…`, trabajo `45a0ed6f…`.

Desde la Etapa 5, los integrantes cargan los datos únicamente con `equipo/acceso_datos.py`:

```python
import sys
sys.path.insert(0, "/content/drive/MyDrive/Proyecto_Integrador_II/equipo")
from acceso_datos import load_split

train = load_split(["fold1", "fold2", "fold3", "fold4"])
val = load_split(["fold0"])
```

Pedir `"test"` con etiqueta lanza un error a propósito.
