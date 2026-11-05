# Protocolo de evaluación — Proyecto Integrador II (Etapa 4, cerrado el 2026-11-03)

Documento único del protocolo para el equipo y para la sección 3.4 del informe. Consolida los cuatro objetivos de la Etapa 4; el detalle, los prerregistros y la evidencia están en `etapa4-objetivo1-particion.md`, `etapa4-objetivo2-prueba.md`, `etapa4-objetivo3-metricas.md` y `etapa4-objetivo4-particion-aleatoria.md`. Fijado antes de entrenar cualquier modelo (compuerta de la hoja de ruta). Ninguna regla de este documento se cambia después de ver resultados de modelos; un cambio con información nueva se registra con fecha y motivo.

## Resumen

| elemento | regla |
|---|---|
| qué se estima | desempeño en un **pozo nuevo** dentro de un área ya perforada |
| unidad de partición y de evaluación | el pozo (familia de pozos; solo `34/5-1 A` y `34/5-1 S` forman familia) |
| partición | prueba 22 pozos + pool de 96 pozos en 5 pliegues; `etapa4_particion.csv`, sha256 `c55dc4d0…` |
| esquema | entrenamiento = pliegues 1–4 (76 pozos); validación fija = pliegue 0 (20 pozos); referencias con validación cruzada de 5 pliegues |
| prueba | separada físicamente; se usa una sola vez, al final, con `evaluate_test` |
| métrica principal | puntaje de penalización de FORCE (matriz tal cual) promediado por pozo; rango [−4, 0] |
| complementarias | puntaje por filas, F1 macro, exactitud balanceada, exactitud, por clase, matriz de confusión |
| filas evaluadas | todas las filas con etiqueta; estratos de diagnóstico `sin_ventana` / `borde` / `interior` |
| incertidumbre | bootstrap por pozo (B = 2000, semilla 0, IC 95%) |
| criterio de comparación | diferencia pareada pozo a pozo; real si su IC 95% excluye 0; solo contrastes declarados |
| partición aleatoria por filas | inválida (ver sección 7) |

## 1. Qué se estima

El uso declarado del modelo (documento preliminar) es interpretar un pozo que nunca vio. El estimando es por tanto el desempeño esperado en un pozo nuevo de la misma área (Mar del Norte noruego), no en una cuenca nueva ni en una fila faltante de un pozo conocido. La unidad de muestra efectiva es el pozo: las filas de un pozo están fuertemente correlacionadas (Etapa 3) y los pozos difieren entre sí. Por eso la partición, la métrica principal, la incertidumbre y las comparaciones se construyen por pozo.

No se agrupa por zona geográfica: las clases raras están concentradas en los cuadrantes 15–17 y agrupar por zona haría imposible la estratificación. La distancia de cada pozo al pozo más cercano fuera de su conjunto se reporta como diagnóstico (prueba: mediana 8.2 km, mínimo 1.8 km, similar a los pliegues).

## 2. Partición

| conjunto | pozos | filas | % filas |
|---|---|---|---|
| prueba | 22 | 242,918 | 17.0 |
| pliegue 0 (validación fija) | 20 | 234,596 | 16.4 |
| pliegue 1 | 19 | 233,501 | 16.3 |
| pliegue 2 | 19 | 223,839 | 15.7 |
| pliegue 3 | 19 | 259,585 | 18.2 |
| pliegue 4 | 19 | 235,255 | 16.5 |
| total | 118 | 1,429,694 | 100 |

- Estratificación iterativa multietiqueta (Sechidis et al., 2011), dos pasos (prueba vs. pool; pool en 5 pliegues), semilla 0, una sola corrida, prerregistrada. Etiquetas: presencia por pozo de cada clase (≥ 8 filas = 1.2 m) y tercil del número de curvas disponibles. Cada pozo vale un voto.
- Clases raras: `Basement` (1 pozo) solo en el pliegue 4, no evaluable por clase; `Halite` (4 pozos) con 1 en prueba (`17/4-1`); `Anhydrite` y `Chalk` presentes en prueba.
- La partición no se re-sortea nunca. La celda que la genera verifica la huella y recalcula para comparar; no reescribe el archivo.

## 3. Qué se puede hacer con cada conjunto

| operación | entrenamiento (pliegues 1–4) | validación (pliegue 0) | pool en CV (pliegues 0–4) | prueba |
|---|---|---|---|---|
| ajustar parámetros del modelo | sí | no | sí, dentro de cada pliegue | no |
| ajustar estadísticos globales, pesos de clase, imputadores | sí | no | sí, dentro de cada pliegue | no |
| elegir hiperparámetros, arquitectura, parada temprana, suavizado, calibración | — | sí | sí (referencias) | no |
| inspección con etiqueta (figuras, verificación de W) | sí | evitar | — | no |
| transformaciones sin parámetros entre pozos (log10, escalado por pozo, `interpolate_gaps`, ventaneo, estratos) | sí | sí | sí | sí |
| leer la etiqueta | vía `load_split` | vía `load_split` | vía `load_split` | solo `evaluate_test` |

Frontera de fondo: "¿este paso usa la etiqueta, o ajusta algo con pozos que no son de entrenamiento?". Las curvas sin etiqueta de los pozos de prueba no se usan para ajustar nada, aunque sea sin etiqueta (estadísticos globales, preentrenamiento, selección de curvas por disponibilidad).

## 4. Reserva y uso único de la prueba

- **Archivos**: `equipo/etapa4_pool_trabajo.parquet` (`45a0ed6f…`) = curado con etiqueta y confianza en NaN en los 22 pozos de prueba, única entrada con etiqueta de las Etapas 5–8. `etapa4_prueba_sellada.parquet` (`1904defd…`) = etiquetas de prueba, en la carpeta del custodio (no compartida); solo lo lee `evaluate_test`.
- **Acceso**: `equipo/acceso_datos.py` → `load_split(sets, labels=True)` verifica las huellas; pedir la etiqueta de `"test"` lanza `ValueError`. `equipo/revision_notebooks.py` → `scan_notebook` detecta lecturas directas del curado, el consolidado o el sellado; se corre sobre cada notebook del equipo antes de integrarlo.
- **Qué cuenta como tocar la prueba**: cualquier cálculo que junte su etiqueta con algo producido por un modelo, o que la use para ajustar o elegir. Re-analizar las predicciones ya registradas no es un nuevo uso.
- **Momento**: después de fijar en validación todo lo que cambia predicciones, incluidos suavizado y calibración (Etapa 8).
- **Modelo que va a prueba**: todos entrenados con los pliegues 1–4 (76 pozos); lista cerrada de modelos declarada antes y evaluada en una sola corrida; modelo de despliegue designado antes, por validación. Reentrenar con los 118 pozos solo después, como modelo no evaluado.
- **Re-evaluación**: error de código de evaluación → recalcular sobre las mismas predicciones (segunda entrada); error de datos o entrenamiento → reentrenar la misma lista sin cambios de diseño, reportar ambos y marcar "prueba ya vista". Nunca por un resultado decepcionante.
- **Registro**: `evaluacion_prueba.py` → `evaluate_test(pred_path, evaluate, models, author, code_version, reason, dry_run=False)`; fija la huella de las predicciones antes de leer etiquetas, exige coincidencia de todas las filas y escribe `registro_prueba.json` (se niega si ya existe). Ensayos sobre el pliegue 0 en `registro_ensayo.json`.
- **Soluciones publicadas**: 17 de los 22 pozos de prueba estaban en el entrenamiento de la competencia. No se usan pesos ni predicciones publicados; arquitecturas sí; hiperparámetros publicados solo como punto de partida.

## 5. Métricas

- **Principal**: para cada pozo w, S_w = −(1/n_w)·Σ A[y, ŷ] con la matriz de penalización de FORCE tal cual (12×12, simétrica, 1.375–4 fuera de la diagonal); métrica = media de S_w (un voto por pozo). Es el costo esperado de mala clasificación del curso de estadística (§7.7, ec. 7.105 con costos C(j|i)).
- **Complementarias** (siempre reportadas, no deciden): puntaje por filas agrupadas (forma de la competencia), F1 macro y exactitud balanceada sobre clases evaluables, exactitud, precisión/exhaustividad/F1 por clase con filas y pozos de soporte, matriz de confusión (filas reales) y P̂(j|i). Una discrepancia entre principal y F1 macro se reporta como hallazgo.
- **Regla de soporte**: una clase entra a los promedios por clase si está presente (≥ 8 filas) en ≥ 2 pozos del conjunto. Prueba y pliegue 0 → 9 clases evaluables; validación cruzada fuera de pliegue (96 pozos) → 11.
- **Filas evaluadas**: todas las filas con etiqueta, sin exclusiones. Todo modelo debe predecir todas las filas (la Etapa 6 resuelve bordes y huecos como parte del modelo).
- **Estratos de diagnóstico** (sin etiqueta, con `depth_segment` y W_ref = 339): `sin_ventana` (sub-tramo más corto que W; 5,683 filas en 24 pozos), `borde` (a menos de 169 filas del extremo; 5.72%), `interior`. La ganancia del contexto vertical se lee por estrato.

## 6. Incertidumbre y criterios de comparación

- Bootstrap por pozo con reemplazo, B = 2000, semilla 0, IC 95% por percentiles; también para el F1 macro (recalculando las métricas agrupadas).
- **Comparación A vs. B**: diferencia pareada pozo a pozo; real si su IC 95% excluye 0; se reporta en cuántos pozos gana cada uno. Solo para contrastes declarados de antemano, no para cada ensayo de una búsqueda.
- **Validación cruzada (referencias)**: puntaje sobre las predicciones fuera de pliegue de los 96 pozos, mismo bootstrap, más la dispersión de las 5 medias por pliegue (IC optimista, Nadeau & Bengio, 2003; declarado).
- **Prueba**: IC por modelo de la lista cerrada y diferencias pareadas solo para contrastes declarados. Nada se elige con ellos.
- **Piso trivial**: modelo constante (Shale). Pliegue 0: −1.0718 por pozo, IC [−1.29, −0.89]; validación cruzada sobre el pool: −1.2210, IC [−1.33, −1.11]. Todo modelo real debe superarlo con diferencia pareada real. Con 20 pozos el IC de un modelo mide ~0.40: la herramienta de comparación es la diferencia pareada, no el traslape de IC individuales.

## 7. Por qué no se usa una partición aleatoria por filas

Mecanismos centrales:
1. **Estimaría otra cantidad**: rellenar una fila de un pozo conocido, no interpretar un pozo nuevo.
2. **Vecinos casi idénticos**: ACF a 0.15 m de 0.988–0.997 en las curvas núcleo y 0.81–0.94 a 3.8 m; memoria larga (d ≈ 0.55–0.82, sin largo de decorrelación bajo 300 m); la etiqueta cambia cada varios metros (distancia mediana al contacto ~5 m). Con filas al azar, el 96% de las filas evaluadas tiene su vecina inmediata en entrenamiento. Con ventanas de 339 filas, dos ventanas vecinas comparten 338.
3. **Identidad del pozo**: varias curvas tienen más variación entre pozos que dentro del pozo (`MUDWEIGHT` 1.73, `ROPA` 1.42, `DTS` 1.38, `SGR` 1.32, `ROP` 1.24), y la posición (`X_LOC`, `Y_LOC`, `DEPTH_MD`) identifica la fila; un modelo puede aprender el pozo en lugar de la roca.

Secundarios: clases confinadas a pocos pozos (`Basement` 1, `Halite` 4) aparecerían como "evaluables"; normalización con datos de prueba (ya controlada); intervalos falsamente estrechos al tratar filas como réplicas (curso de estadística, ec. 1.33).

**Demostración en nuestros datos** (96 pozos del pool, sin tocar la prueba, prerregistrada): un predictor que no mira ningún registro y copia la etiqueta de la fila de entrenamiento más cercana del mismo pozo obtiene con filas al azar **−0.083** por pozo (0 es perfecto), F1 macro 0.94 y exactitud 0.97, frente a −1.221 del modelo constante; gana en los 96 pozos. Con partición por pozos ese predictor no existe. El modelo constante da exactamente lo mismo con ambas particiones: la partición al azar no infla a todos los modelos por igual, infla en proporción a cuánto aprovecha la cercanía; sesgaría precisamente la comparación entre modelos con y sin contexto vertical. El curso de Aprendizaje Profundo muestra el mismo fenómeno en una serie temporal (sesión 5, "Three ways to leak the future").

## 8. Artefactos versionados y código

| artefacto | huella (sha256) | dónde |
|---|---|---|
| dataset curado (origen) | `82f590e8…` | custodio |
| partición | `c55dc4d0…` | custodio y `equipo/` |
| archivo de trabajo | `45a0ed6f…` | `equipo/` |
| archivo sellado | `1904defd…` | custodio |
| matriz de penalización | `c312481a…` (blob git `b96178eb…`) | `equipo/` |

Huellas registradas en `manifiesto_datos.json` (claves `etapa4_particion`, `etapa4_prueba`, `etapa4_metricas`) y en `equipo/manifiesto_equipo.json`.

| módulo | funciones | uso |
|---|---|---|
| `equipo/acceso_datos.py` | `load_split`, `load_partition`, `file_sha256` | toda carga con etiqueta |
| `equipo/metricas.py` | `evaluate`, `paired_difference`, `mlflow_scalars`, `strata`, `well_scores` | toda evaluación (validación y prueba) |
| `equipo/revision_notebooks.py` | `scan_notebook` | revisión de notebooks antes de integrar |
| `evaluacion_prueba.py` (custodio) | `evaluate_test` | evaluación única de la prueba |

`evaluate(df)` recibe una tabla con `WELL`, `stratum`, `y_true`, `y_pred` (códigos FORCE) y devuelve un diccionario serializable. En MLflow: `log_metrics(mlflow_scalars(resultado))` y `log_dict(resultado, ...)`.

Verificación de cierre (2026-11-03, celda final de la sección 4.4): los 12 controles pasan, incluida la reutilización desde un proceso nuevo que solo ve `equipo/` y la reproducción exacta del ensayo registrado del pliegue 0.

## 9. Obligaciones para las etapas siguientes

- **Etapa 5**: cargar con `load_split`; referencias con validación cruzada de 5 pliegues y `evaluate` sobre las predicciones fuera de pliegue (11 clases evaluables) más la dispersión por pliegue; fila de piso con el modelo constante; primer registro real en MLflow; verificación de W con la etiqueta y figuras con etiqueta solo con los pliegues 1–4.
- **Etapa 6**: normalización global y pesos de clase ajustados dentro de cada pliegue solo con sus pozos de entrenamiento; ventanas que nunca crucen pozo ni sub-tramo; todo modelo predice todas las filas; decidir si `FORMATION`/`GROUP` entran como variables (interpretación humana que un pozo nuevo puede no tener).
- **Etapa 7**: búsqueda de hiperparámetros solo en el pliegue 0 (no verá `Halite` ni `Anhydrite`); comparaciones pareadas solo para contrastes declarados; ganancia del contexto por estrato; la penalización en la pérdida es opcional, la métrica no cambia; registrar `run_id` y huella de pesos de cada modelo de la lista cerrada.
- **Etapa 8**: suavizado y calibración fijados en el pliegue 0 antes de la evaluación única; análisis de error de prueba después, sobre las predicciones guardadas.
- **Etapa 9**: brecha entre pozos vistos y no vistos con la misma `evaluate`; el modelo reentrenado con 118 pozos se documenta como no evaluado.
- **Repositorio**: subir este protocolo y los módulos (`acceso_datos.py`, `revision_notebooks.py`, `metricas.py`, `penalty_matrix.npy`, `evaluacion_prueba.py`) antes del primer modelo; desde entonces `version_codigo` es el commit.

## 10. Límites declarados

- El registro demuestra que no hubo uso no declarado de la prueba en el código del repositorio, no que nadie miró en privado.
- La estratificación de la partición usó un resumen grueso de la etiqueta de los 118 pozos (presencia por clase), con algoritmo y semilla prerregistrados y una sola corrida.
- 22 pozos de prueba (no ~20): variabilidad normal del algoritmo, aceptada sin re-sortear.
- La matriz de penalización no tiene derivación documentada; fuera de ~10 pares vecinos es casi plana.
- El IC de la validación cruzada es optimista (ignora la variabilidad del entrenamiento entre pliegues).
- No se encontró literatura Q2+ verificable que cuantifique la sobreestimación por filas al azar específicamente en litofacies; la evidencia es la propia (sección 7) más la literatura general de validación con datos dependientes.

## 11. Texto para la sección 3.4 del informe (borrador)

La evaluación se diseñó y fijó antes de entrenar cualquier modelo. Como el objetivo es interpretar pozos que el modelo nunca vio, la unidad de evaluación es el pozo: los 118 pozos se repartieron, por pozo completo, en un conjunto de prueba de 22 pozos y un conjunto de 96 pozos dividido en cinco pliegues, mediante estratificación iterativa multietiqueta que equilibra la presencia de cada tipo de roca y la disponibilidad de curvas. Los modelos se entrenan con cuatro pliegues (76 pozos) y se ajustan con el quinto (20 pozos); los modelos de referencia usan además validación cruzada de cinco pliegues. Las etiquetas de prueba se separaron físicamente y solo las lee una función que registra su único uso, al final del proyecto. La métrica principal es el puntaje de penalización de la competencia FORCE 2020, que asigna un costo distinto a cada confusión entre rocas según su cercanía geológica (equivalente al costo esperado de mala clasificación), promediado por pozo para que cada pozo pese igual; se reportan además F1 macro, exactitud balanceada, métricas por clase y la matriz de confusión. La incertidumbre se estima con bootstrap por pozo y dos modelos se consideran distintos solo si el intervalo del 95% de su diferencia pareada pozo a pozo excluye el cero. Una partición aleatoria por filas sería inválida: las mediciones vecinas en profundidad son casi idénticas y comparten la misma roca, de modo que un predictor que solo copia la etiqueta de la fila vecina, sin mirar ningún registro, obtendría un puntaje casi perfecto (−0.08 frente a −1.22 del modelo trivial), sesgo que además favorecería a los modelos que usan contexto vertical, justo lo que el proyecto quiere medir.

## Referencias

- Shumway, R. H. & Stoffer, D. S. *Time Series Analysis and Its Applications*, 3.ª ed. (libro guía): ec. 1.33; §5.1; §7.7 (ecs. 7.104, 7.105, 7.119; Ej. 7.11).
- Sechidis, K., Tsoumakas, G. & Vlahavas, I. (2011). On the stratification of multi-label data. ECML PKDD. DOI 10.1007/978-3-642-23808-6_10.
- Roberts, D. R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*. DOI 10.1111/ecog.02881.
- Ploton, P. et al. (2020). Spatial validation reveals poor predictive performance of large-scale ecological mapping models. *Nature Communications* 11, 4540. DOI 10.1038/s41467-020-18321-y.
- Kapoor, S. & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 4(9), 100804. DOI 10.1016/j.patter.2023.100804.
- Field, C. A. & Welsh, A. H. (2007). Bootstrapping clustered data. *JRSS B* 69(3), 369–390. DOI 10.1111/j.1467-9868.2007.00593.x.
- Nadeau, C. & Bengio, Y. (2003). Inference for the generalization error. *Machine Learning* 52, 239–281. DOI 10.1023/A:1024068626366.
- Varma, S. & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics* 7, 91. DOI 10.1186/1471-2105-7-91.
- Sokolova, M. & Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks. *Information Processing & Management* 45(4), 427–437. DOI 10.1016/j.ipm.2009.03.002.
- Curso SI7011 Aprendizaje Profundo (EAFIT), repositorio `EAFIT-IA/si7011-DeepLearning`, sesión 5 (notebook 5.1).
