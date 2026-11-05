# Etapa 4 — Objetivo específico 3: métricas, matriz de penalización y métricas por clase (CERRADO, 2026-11-03)

Sesión 16, 2026-11-03, con Claude. Sección 4.3 del notebook. Depende de la partición `etapa4_particion.csv` (`c55dc4d0…`) y del mecanismo de prueba del objetivo 2 (`evaluate_test`, `load_split`).

**Resumen:**

| elemento | valor |
|---|---|
| métrica principal | puntaje de penalización (matriz de FORCE tal cual) promediado por pozo, un voto por pozo; rango [−4, 0], mayor es mejor |
| complementarias | puntaje por filas agrupadas, F1 macro y exactitud balanceada (clases evaluables), exactitud, métricas por clase, matriz de confusión |
| regla de soporte | una clase entra a los promedios por clase si está presente (≥ 8 filas) en ≥ 2 pozos del conjunto |
| filas evaluadas | todas las filas con etiqueta del conjunto; estratos de diagnóstico `sin_ventana`, `borde`, `interior` (W_ref = 339) |
| incertidumbre | bootstrap por pozo, B = 2000, semilla 0, IC 95% por percentiles; comparación pareada pozo a pozo, diferencia real si el IC excluye 0 |
| implementación | `equipo/metricas.py` (`evaluate`, `paired_difference`, `mlflow_scalars`); `equipo/penalty_matrix.npy` (sha256 `c312481a…`); `evaluate_test` con `metric_fn = evaluate` |
| controles | los 7 cumplidos |

## Revisión inicial (sesión 16)

- Sección 4 del notebook coherente con lo documentado: huellas `c55dc4d0`, `45a0ed6f`, `1904defd` en las salidas; contadores vacíos en el archivo adjunto (orden no verificable desde él).
- `registro_ensayo.json` tenía 2 entradas, no 1 como dice `etapa4-objetivo2-prueba.md`: la sección 4 se corrió dos veces tras la reorganización de Drive. Sin riesgo (registro de solo agregar). Cada ejecución de una celda de ensayo agrega una entrada.
- `equipo/__pycache__` existía (resto de una corrida anterior a `sys.dont_write_bytecode`); se borró a mano.
- `metric_fn(y_true, y_pred)` no recibía el pozo: no permitía agregar ni remuestrear por pozo. Corregido en el Bloque 6.
- `json.dump` escribía NaN como JSON no estándar: la métrica devuelve `None` y el registro se escribe con `allow_nan=False` (Bloque 6).
- Un módulo reescrito con `%%writefile` no se recarga con `import` en la misma sesión: las celdas de prueba usan `importlib.reload`.
- La celda que escribe `equipo/manifiesto_equipo.json` (4.2) lo rehacía desde cero y habría borrado la huella de la matriz; corregida en el Bloque 6 para actualizar sin borrar claves.

## Fuentes revisadas

- **Competencia (verificado contra el repositorio, 2026-11-03):** `penalty_matrix.npy`, 1,280 bytes, blob git `b96178eb8d3287c36061f595f63ea454cb9ee891` (el mismo verificado en la Etapa 1; el manifiesto de la Etapa 1 ya lo traía). Matriz 12×12, simétrica, diagonal cero, valores 1.375–4 (mediana fuera de la diagonal 3.625; 17 de 66 pares en el máximo 4). Orden de filas y columnas = `lithology_numbers` del `starter_notebook.ipynb` (celda 31): Sandstone 0, Sandstone/Shale 1, Shale 2, Marl 3, Dolomite 4, Limestone 5, Chalk 6, Halite 7, Anhydrite 8, Tuff 9, Coal 10, Basement 11 (mismo orden que `lithology_keys`). Puntaje (celda 52, función `score`): S = −(1/N)·Σ A[y_true, y_pred]; rango [−4, 0], 0 = perfecto. La notación del markdown (celda 48) es confusa en los índices; irrelevante por la simetría.
- **Origen de la matriz:** la retrospectiva técnica de Sodir la llama "geologically motivated" y el resumen geológico "petrophysically based"; ninguno documenta cómo se construyó. Los tres primeros equipos no la usaron en la función de pérdida (a lo sumo para elegir modelos). Las etiquetas son interpretación humana con errores conocidos.
- **Estadística (libro, §7.7):** P(j|i) (7.104); error total P_e = Σ π_i Σ_{j≠i} P(j|i) (7.105), con la indicación de multiplicar P(j|i) por el costo C(j|i); tasas de error aparentes n_ij/Σ n_ij (7.119); sesgo del error aparente y opción de validación cruzada o bootstrap. El puntaje de FORCE es exactamente −Σ π̂_i Σ_j A(j|i) P̂(j|i) con π̂ = proporción de filas por clase: el costo esperado de mala clasificación del curso. El libro no trata F1, exactitud balanceada ni remuestreo por grupos.
- **Aprendizaje Profundo (`EAFIT-IA/si7011-DeepLearning`, 6 sesiones, último cambio 2026-10-27):** F1 macro junto a la exactitud cuando hay desbalance (2.6: "la accuracy engaña"; 3.6), matriz de confusión con filas reales y columnas predichas y reporte por clase (S01), selección por `val_loss`, MLflow con `log_params`/`log_metrics` por época y métricas de prueba registradas en la corrida elegida (2.5, 2.6). **No trata** exactitud balanceada, pérdida ponderada ni matrices de costo; **la calibración figura como "Not covered"** (plan de S06). La sesión 5.1 (ventanas sin fuga, descarte de ventanas que cruzan huecos, toda comparación contra una referencia en la misma tabla) es insumo de las Etapas 6–7.
- **Sistemas de Aprendizaje Automático:** sin material en el proyecto; solo la rúbrica (MLflow o equivalente, reproducibilidad).
- **Rúbricas y programación:** Aprendizaje Profundo pide "estrategia de validación y selección de métricas adecuadas" y comparación entre arquitecturas; Estadística, "comparación crítica entre enfoques"; el documento final, "métricas seleccionadas, estrategia de validación, comparación de enfoques" (3.4). Preliminar y plantilla de propuesta: no comprometen métricas.

## Prerregistro (aprobado por Juan José el 2026-11-03, antes de ejecutar código)

No se modificó después de ejecutar; las precisiones de implementación están en "Resultados por bloque".

### Matriz de penalización

- Se usa **tal cual**, sin ajustes. Motivo: no hay verdad contra la cual calibrarla; ajustarla ahora sería una decisión de diseño tomada después de ver los datos.
- Lectura geológica (para la discusión, no cambia la matriz). Defendibles: Limestone–Chalk 1.375; Marl–Limestone y Marl–Shale 2 (marga = mezcla carbonato–arcilla), Marl–Chalk 2.25; continuo Sandstone–Sandstone/Shale–Shale (2, 2.375; extremos 3.5); Halite–Anhydrite 2.75 (evaporitas); Dolomite–Limestone 2.625, Dolomite–Marl 2.5. Dudosas: Tuff–Coal y Tuff–Sandstone 2.5, sin relación genética; probable reflejo de respuesta similar en registros (no verificado). Limitación declarada: fuera de ~10 pares vecinos la matriz es casi plana (se comporta como la exactitud × ~3.5), y al pesar por fila la domina Shale.
- Archivo: copia en `equipo/penalty_matrix.npy`, descargada de la fuente, verificada por blob git y con su sha256 en `equipo/manifiesto_equipo.json` (`penalizacion_sha256`) y en el manifiesto del custodio (clave `etapa4_metricas`).

### Métrica principal

- **Puntaje de penalización promediado por pozo**: para cada pozo w, S_w = −(1/n_w)·Σ A[y, ŷ] sobre sus filas; métrica = media de S_w entre pozos (cada pozo un voto). Convención de signo de la competencia: rango [−4, 0], mayor es mejor.
- Motivo de la agregación: el estimando es el desempeño en un pozo nuevo (objetivo 1); los pozos tienen largos muy distintos; misma ponderación 1/n_w usada para W en la Etapa 3.
- Motivo de no usar F1 macro como principal: en prueba y en el pliegue 0 Halite y Anhydrite viven en un solo pozo cada una; el F1 macro daría peso 1/11 a cifras de un solo pozo y no distingue la gravedad del error.

### Métricas complementarias (siempre reportadas, no deciden)

- Puntaje de penalización por filas agrupadas (forma de la competencia).
- F1 macro y exactitud balanceada (media de las exhaustividades = 1 − media por clase de Σ_{j≠i} P̂(j|i)), sobre las clases evaluables del conjunto (regla de soporte).
- Exactitud.
- Por clase: precisión, exhaustividad, F1, filas y pozos de soporte, bandera de evaluable.
- Matriz de confusión 12×12 (filas reales, columnas predichas) y su versión normalizada por fila, P̂(j|i) (7.119).
- Si la principal y el F1 macro discrepan, se reporta como hallazgo; no es desempate.
- Las métricas por clase se calculan con las filas agrupadas del conjunto (por pozo quedarían indefinidas en los pozos sin la clase).

### Clases con soporte bajo

- `Basement`: no evaluable por clase; sus filas cuentan en la penalización y en la exactitud.
- **Regla de soporte**: una clase entra al F1 macro y a la exactitud balanceada de un conjunto si está presente (≥ 8 filas, misma definición de la partición) en **≥ 2 pozos** de ese conjunto. Por debajo: se reporta su fila por clase con filas y pozos y la marca "sin réplica entre pozos", fuera de los promedios.
- Consecuencia conocida de antemano: prueba y pliegue 0 → 9 clases en los promedios (fuera Halite, Anhydrite, Basement); validación cruzada fuera de pliegue sobre los 96 pozos → 11 clases (Halite 3 pozos, Anhydrite 8).
- Una clase predicha que no existe en el conjunto (p. ej. Basement en prueba) cuenta como error de la clase real y en la penalización; se reporta su número de falsos positivos.

### Conjunto común de filas evaluadas

- **Todas las filas con etiqueta del conjunto, sin exclusiones.** Fijado ahora; no depende de la Etapa 6. La Etapa 6 queda obligada a que todo modelo prediga todas las filas (relleno, contexto más corto o respaldo, como parte del modelo). Motivos: el uso requiere una etiqueta por metro; excluir bordes y huecos (filas difíciles) inflaría los modelos secuenciales. `evaluate_test` exige coincidencia de todas las filas.
- **Estratos de diagnóstico** (reportados, no deciden), calculados sin etiqueta con `depth_segment` y W_ref = 339: `sin_ventana` (sub-tramo más corto que W), `borde` (a menos de h = 169 filas del extremo de su sub-tramo), `interior`. La ganancia del contexto vertical (Etapa 7) se lee por estrato. Estratos por huecos > `G_max` se agregan en la Etapa 6, solo como diagnóstico. La confianza de la etiqueta (1–3) queda como estrato opcional de la Etapa 8.

### Incertidumbre y criterio de comparación

- Unidad de remuestreo: el pozo. Bootstrap por pozo con reemplazo, B = 2000, semilla 0, intervalo del 95% por percentiles.
- **Pliegue 0**: IC de cada modelo; comparación A vs. B por diferencia pareada pozo a pozo (S_A,w − S_B,w), IC bootstrap de la media; **una diferencia es real si su IC del 95% excluye 0**; se reporta además en cuántos pozos gana cada modelo. Solo para comparaciones declaradas de antemano, no para cada ensayo de una búsqueda.
- **Validación cruzada (referencias)**: puntaje por pozo con predicciones fuera de pliegue (96 pozos), mismo bootstrap, más la dispersión de las 5 medias por pliegue. Declarado: el IC es optimista porque ignora la variabilidad del entrenamiento entre pliegues (Nadeau & Bengio, 2003).
- **Prueba (22 pozos, una corrida)**: IC por modelo de la lista cerrada y diferencias pareadas solo para contrastes declarados antes. Nada se elige con ellos.
- F1 macro: IC por el mismo bootstrap de pozos, recalculando las métricas agrupadas.

### Implementación

- Módulo `equipo/metricas.py` (una sola implementación para validación y prueba); importa `file_sha256` de `acceso_datos.py`.
- `evaluate(df)` con columnas `WELL`, `y_true`, `y_pred` (códigos FORCE) y `stratum`; devuelve un diccionario serializable sin NaN.
- `evaluate_test` pasa a `metric_fn` la tabla unida por modelo; el estrato de los pozos de prueba se calcula con `load_split(..., labels=False)` (transformación sin parámetros, permitida); el registro se escribe con `allow_nan=False`.
- MLflow: escalares con `log_metrics` vía `mlflow_scalars` (`val_score_pozo`, `val_score_filas`, `val_f1_macro`, `val_exactitud_balanceada`, `val_exactitud`, `val_f1_<clase>` de las clases evaluables), diccionario completo con `log_dict`; la prueba solo vía `evaluate_test` y la corrida "evaluacion-prueba" con etiqueta `uso_prueba`.

### Controles de aceptación (fijados de antemano)

1. Ejemplo de 5 filas resuelto a mano = función.
2. Igualdad con la función `score` de la competencia (copiada textual) en 10,000 pares al azar, diferencia < 1e-12, en ambos órdenes.
3. Invariancias: predicción perfecta → 0 y F1 = 1; modelo constante → −Σ π̂_i A[i, c]; permutar filas no cambia nada; duplicar las filas de un pozo no cambia el puntaje por pozo y sí el agrupado.
4. Métricas por clase iguales a `precision_recall_fscore_support` de scikit-learn; la matriz de confusión suma el número de filas y sus filas suman el soporte de cada clase.
5. Bootstrap: un modelo contra sí mismo → IC [0, 0]; mismo resultado con la misma semilla.
6. `json.dumps(resultado, allow_nan=False)` no falla.
7. Ensayo repetido de `evaluate_test` sobre el pliegue 0 con la métrica final (módulos recargados); `registro_prueba.json` sigue sin existir.

## Resultados por bloque

Todos los bloques con teoría previa (intuición, ejemplo de 5 datos, esquema). Los controles 1–6 usan datos sintéticos (sin etiquetas reales), salvo el contraste de estratos del Bloque 5, que usa las curvas de los 118 pozos sin etiqueta.

- **Bloque 1** (matriz y puntaje por fila): matriz descargada de la fuente; blob git verificado; `equipo/penalty_matrix.npy`, **sha256 `c312481a…`**, registrada en `equipo/manifiesto_equipo.json` (`penalizacion_sha256`) y en `manifiesto_datos.json` (clave `etapa4_metricas`); el manifiesto de la Etapa 1 ya traía el mismo blob (`True`). Matriz: (12, 12), simétrica, diagonal 0, mínimo fuera de la diagonal 1.375, máximo 4. Ejemplo a mano: dos modelos con la misma exactitud (0.2) dan −1.625 (errores entre rocas vecinas) y −2.95 (errores entre ambientes). Igualdad con `score` en ambos órdenes (`True True`, −3.0971 con predicciones al azar). Código fuera de las 12 clases rechazado. **Controles 1 y 2 cumplidos.**
- **Bloque 2** (agregación por pozo): `row_penalty`, `well_scores`. Ejemplo a mano: pozos de 4 y 1 filas → por pozo −2.25, agrupado −1.2. Predicción perfecta = 0, modelo constante = −Σ π̂_i A[i, Shale], permutación sin efecto, duplicar un pozo no cambia su puntaje ni la media por pozo y sí el agrupado (`True False`). **Control 3 cumplido.**
- **Bloque 3** (métricas por clase y regla de soporte): `confusion`, `class_metrics`, `class_summary`; `MIN_ROWS = 8`, `MIN_WELLS = 2`. Ejemplo a mano: F1 Shale 0.667, Sandstone 0.5, matriz [[2, 1], [1, 1]]. Precisión, exhaustividad, F1 y soporte iguales a scikit-learn; matriz de confusión igual a `confusion_matrix`, suma = filas, filas de la matriz = soporte; F1 macro igual a `f1_score(average="macro", labels=evaluables)`. Casos de la regla: clase en 1 pozo fuera, clase en 2 pozos dentro (con F1 0 si nunca se predice), clase con menos de 8 filas fuera, clase predicha sin existir con exhaustividad indefinida y sus falsos positivos contados. Convención: precisión 0 si la clase existe y nunca se predice (`zero_division=0`, como el curso). **Control 4 cumplido.**
- **Bloque 4** (bootstrap por pozo): `rates` (cálculo por clase desde una matriz de confusión, reutilizado por las réplicas), `well_confusions`, `mean_ci`, `macro_f1_ci`, `paired_difference`. Ejemplo a mano (5 pozos): IC individuales traslapados ([−0.96, −0.48] y [−1.18, −0.54]) pero diferencia pareada 0.12, IC [0.04, 0.22], real; A gana en 4 pozos y empata en 1. Modelo contra sí mismo → IC [0, 0]; misma semilla → mismo resultado. Precisión de implementación: en el IC del F1 macro las clases evaluables quedan fijas y, si una falta en una réplica, esa réplica la omite. **Control 5 cumplido.**
- **Bloque 5** (estratos y `evaluate`): `strata`, `json_safe`, `evaluate`, `mlflow_scalars`; `W_REF = 339`. **Contraste con la Etapa 3 sobre las curvas de los 118 pozos (sin etiqueta): 1,429,694 filas, 5,683 sin ventana, 5.72% de borde, 24 pozos con filas sin ventana — idéntico a `etapa3-objetivo3-ventana-W.md`.** `json.dumps(allow_nan=False)` sin error; principal = media de `well_scores`; IC = `mean_ci`; clases sin filas con F1 `None`. **Control 6 cumplido.**
- **Bloque 6** (`evaluate_test` con la métrica final; notebook completo entregado): celda 160 (4.2) actualiza `manifiesto_equipo.json` sin borrar claves; celda 166 (4.2) calcula el estrato con `load_split(labels=False)`, pasa a `metric_fn` la tabla `[WELL, stratum, y_true, y_pred]` por modelo y escribe el registro con `allow_nan=False`; celda 167 (4.2) adapta `provisional_accuracy` a la nueva interfaz (no se re-ejecutó). Ensayo sobre el pliegue 0 con dos modelos ficticios (sin elegir nada con ellos): `mayoritaria` = Shale (clase más frecuente de los pliegues 1–4) y `aleatoria_prior` = sorteo con las proporciones de clase de los pliegues 1–4 (semilla 0). Una entrada nueva en `registro_ensayo.json`, igual a lo devuelto; `registro_prueba.json` no existe. **Control 7 cumplido.**

### Ensayo con la métrica final (pliegue 0, 20 pozos, 234,596 filas)

| modelo | score por pozo | IC 95% | score por filas | F1 macro | exactitud balanceada | exactitud |
|---|---|---|---|---|---|---|
| mayoritaria (Shale) | −1.0718 | [−1.2895, −0.8879] | −1.0327 | 0.0882 | 0.1111 | 0.6586 |
| aleatoria_prior | −1.7051 | [−1.8009, −1.6147] | −1.6957 | 0.1096 | 0.1101 | 0.4314 |

- Clases evaluables (9): Sandstone, Sandstone/Shale, Shale, Marl, Dolomite, Limestone, Chalk, Tuff, Coal (Halite y Anhydrite fuera, 1 pozo cada una; Basement ausente), como se previó en el prerregistro.
- Estratos: interior 219,838; borde 13,858; sin ventana 900.
- Diferencia pareada (mayoritaria − aleatoria): 0.6333, IC [0.5131, 0.7333], real; mayoritaria gana en 19 de 20 pozos.
- Valores verificables a mano, coincidentes: exactitud 0.6586 (la misma del ensayo del objetivo 2), F1 macro = F1 de Shale / 9 = 0.0882, exactitud balanceada = 1/9.

Lectura:
1. **Piso trivial**: el modelo constante Shale obtiene −1.07 por pozo. Todo modelo real debe superarlo con una diferencia pareada real; queda como fila de referencia en la tabla comparativa de la Etapa 5.
2. **Ancho del IC con 20 pozos**: ~0.40 para un modelo constante; la heterogeneidad entre pozos es grande. Los IC individuales de modelos parecidos se van a traslapar; la herramienta de comparación es la diferencia pareada.
3. **La principal y el F1 macro ordenan distinto**: la penalización prefiere el modelo constante (−1.07 frente a −1.71) y el F1 macro el sorteo (0.110 frente a 0.088). La matriz premia apostar a Shale cuando Shale domina. Ilustra por qué el F1 macro se reporta siempre junto a la principal y por qué una discrepancia se reporta como hallazgo.
4. Por filas (−1.03) sale algo mejor que por pozo (−1.07): los pozos largos de este pliegue tienen más Shale que el promedio.

## Cierre del objetivo 3

Los 7 controles de aceptación cumplidos. Productos:

| producto | ubicación |
|---|---|
| métricas, criterios de comparación y regla de soporte escritos | este documento (prerregistro) |
| matriz de penalización versionada | `equipo/penalty_matrix.npy` (`c312481a…`), `manifiesto_datos.json` (`etapa4_metricas`), `equipo/manifiesto_equipo.json` |
| función de evaluación reutilizable | `equipo/metricas.py` (`evaluate`, `paired_difference`, `mlflow_scalars`, más las funciones de base) |
| evaluación final con la métrica | `evaluacion_prueba.py` (`evaluate_test(pred_path, evaluate, models, ...)`) |
| ensayo con la métrica final | `ensayos/pred_ensayo_metrica_final.parquet`; última entrada de `registro_ensayo.json` |

Límites declarados:
- El registro en MLflow (`mlflow_scalars`, `log_dict`) no se ejercitó: aún no hay servidor de seguimiento. Se verifica con el primer modelo de la Etapa 5.
- Si se regenerara todo desde cero (sin `equipo/penalty_matrix.npy`), la celda 1 de la 4.3 debe correr antes de cualquier importación de `evaluacion_prueba`. Con los archivos existentes no aplica.

## Implicaciones para objetivos y etapas posteriores

- **Objetivo 4:** documento de por qué una partición aleatoria por filas es inválida. Al cerrarlo, consolidar en un solo documento el protocolo de evaluación (partición, prueba, métricas) para el equipo y el informe.
- **Etapa 5:** usar `evaluate` en el pliegue 0 y sobre las predicciones fuera de pliegue de la validación cruzada (96 pozos, 11 clases evaluables), con la dispersión de las 5 medias por pliegue; el modelo constante Shale como fila de piso en la tabla comparativa; registro en MLflow con `mlflow_scalars` y `log_dict`.
- **Etapa 6:** todo modelo predice todas las filas; estratos por huecos > `G_max` como diagnóstico.
- **Etapa 7:** la penalización en la pérdida es opcional y se decide allí; la métrica no cambia. Comparaciones pareadas solo para contrastes declarados; leer la ganancia del contexto por estrato (interior frente a borde). Una regla de decisión con costos (clase que minimiza Σ_i C(j|i)·p(i|x), curso §7.7) requiere probabilidades calibradas → Etapa 8.
- **Etapa 8:** calibración (no cubierta por el curso de Aprendizaje Profundo; traer literatura externa); estrato opcional por confianza de la etiqueta.
- **Etapa 9:** la brecha vistos/no vistos se mide con la misma `evaluate` (pozos de entrenamiento frente a pliegue 0 o prueba).
- **Repositorio:** subir `metricas.py` y `penalty_matrix.npy` junto con los demás módulos antes del primer modelo.

## Celdas del notebook

Sección 4.2 (modificadas en el Bloque 6): 160 (`manifiesto_equipo.json` sin borrar claves), 166 (`evaluacion_prueba.py`), 167 (`provisional_accuracy(df)`).

Sección 4.3:
1. Descarga y verificación de la matriz; huellas en ambos manifiestos.
2. `%%writefile equipo/metricas.py` (módulo completo).
3. Controles 1 y 2.
4. Control 3 (agregación por pozo e invariancias).
5. Control 4 (métricas por clase contra scikit-learn).
6. Control 5 (bootstrap).
7. Contraste de estratos con la Etapa 3 y control 6.
8. Ensayo de `evaluate_test` con la métrica final (control 7).

## Referencias

- Shumway, R. H. & Stoffer, D. S., libro guía del curso, §7.7 (ecs. 7.104, 7.105, 7.119).
- Sokolova, M. & Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks. *Information Processing & Management* 45(4), 427–437. DOI 10.1016/j.ipm.2009.03.002 (verificado; cuartil Q1 de memoria).
- Field, C. A. & Welsh, A. H. (2007). Bootstrapping clustered data. *JRSS Series B* 69(3), 369–390. DOI 10.1111/j.1467-9868.2007.00593.x (verificado; Q1 de memoria).
- Nadeau, C. & Bengio, Y. (2003). Inference for the generalization error. *Machine Learning* 52, 239–281. DOI 10.1023/A:1024068626366 (verificado; fuente canónica).
- Sodir/FORCE (2020). Technical retrospective y geological summary de la competencia (literatura gris; fuente primaria sobre la matriz): https://sodir.no/globalassets/2-force/2020/seminars/contest-machine-learning/technical_retrospective_force-2020-lithofacies-competition.pdf
