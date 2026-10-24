# Etapa 4 — Objetivo específico 2: reservar el conjunto de prueba y la regla de un solo uso (CERRADO, 2026-10-15)

Sesión 15, 2026-10-15. Sección 4.2 del notebook. Depende de la partición vigente `etapa4_particion.csv` (sha256 `c55dc4d0…`, objetivo 1).

**Resumen:**

| elemento | valor |
|---|---|
| archivo de trabajo (equipo) | `equipo/etapa4_pool_trabajo.parquet`, sha256 `45a0ed6f…`; curado con etiqueta y confianza en NaN en los 22 pozos de prueba |
| archivo sellado (custodio) | `etapa4_prueba_sellada.parquet`, sha256 `1904defd…`; 22 pozos, 242,918 filas |
| acceso del equipo | `equipo/acceso_datos.py`: `load_split(sets, labels=True)`; pedir la etiqueta de `"test"` lanza `ValueError` |
| evaluación final | `evaluacion_prueba.py`: `evaluate_test(...)`, una sola vez, registro `registro_prueba.json` |
| modelo que va a prueba | entrenado con los pliegues 1–4 (76 pozos), todos los modelos; lista cerrada declarada antes |
| momento | después de fijar en validación todo lo que cambia predicciones (incluidos suavizado y calibración) |
| controles | los 7 cumplidos |

## Prerregistro (aprobado el 2026-10-15, antes de ejecutar código)

### Mecanismo

- `etapa4_pool_trabajo.parquet`: el curado con `FORCE_2020_LITHOFACIES_LITHOLOGY` y `FORCE_2020_LITHOFACIES_CONFIDENCE` en NaN para los 22 pozos de prueba. Única entrada de las Etapas 5 a 8.
- `etapa4_prueba_sellada.parquet`: `WELL`, `DEPTH_MD`, etiqueta y confianza de los 22 pozos de prueba (242,918 filas). Solo lo lee `evaluate_test`.
- El curado original (`82f590e8…`) no se modifica. El curado y el archivo sellado se guardan en una carpeta de Drive de acceso exclusivo del custodio; el equipo recibe el archivo de trabajo en la subcarpeta `equipo`.
- Huellas de ambos archivos en el manifiesto (clave `etapa4_prueba`).
- La confianza de la etiqueta nunca es variable de entrada.
- `load_split(sets, labels=True)` verifica las huellas de la partición y del archivo de trabajo y devuelve las filas de los conjuntos pedidos; con `labels=False` quita etiqueta y confianza; pedir `"test"` con `labels=True` lanza `ValueError`.
- `scan_notebook` (`equipo/revision_notebooks.py`) busca lecturas directas del curado, el consolidado o el archivo sellado fuera de las celdas permitidas.
- `evaluate_test` separa mecanismo y métrica (recibe `metric_fn`). Orden: (1) huella del parquet de predicciones antes de leer cualquier etiqueta; (2) modo ensayo: verdad = pliegue 0 vía `load_split`, registro `registro_ensayo.json`; modo real: si `registro_prueba.json` existe y no se declara re-evaluación (`reentry=True`, con motivo) se niega antes de leer el archivo sellado; luego verifica la huella del sellado y lo lee; (3) las columnas de predicción deben ser exactamente los modelos declarados y las filas deben coincidir una a una con la verdad; (4) agrega la entrada al registro y devuelve las métricas. Si una verificación falla no se escribe nada.

### Qué se puede hacer con los pozos de prueba antes de la evaluación final

- Sí: pasar sus curvas por transformaciones sin parámetros ajustados entre pozos (log10, escalado por pozo, interpolación de huecos, ventaneo) y controles de integridad de las entradas.
- No: ajustar nada con ellos aunque sea sin etiqueta (estadísticos globales, imputadores, preentrenamiento, selección de curvas por disponibilidad); inspección con etiqueta; análisis de error.

### Qué cuenta como tocar la prueba

Cualquier cálculo que junte la etiqueta de prueba con algo producido por un modelo, o que use esa etiqueta para ajustar o elegir algo. Re-analizar las predicciones guardadas de la evaluación registrada no es un nuevo uso, siempre que el resultado no vuelva al modelo.

### Momento de la evaluación única

Después de fijar en validación todo lo que cambia las predicciones, incluidos el suavizado y la calibración. El análisis de error se hace después, sobre las predicciones guardadas.

### Modelo que va a prueba

- Todos los modelos se entrenan con los pliegues 1–4 (76 pozos), no con los 96. Es el modelo validado, el entrenamiento es idéntico para todos y coincide con el curso de Aprendizaje Profundo (notebook 2.5).
- Modelos de referencia: hiperparámetros por validación cruzada de 5 pliegues; el ajuste que va a prueba, con los pliegues 1–4.
- Antes de la evaluación se declara una lista cerrada de modelos; todos se evalúan en una sola corrida. El modelo de despliegue se designa antes, por validación.
- Despliegue: se permite reentrenar con los 118 pozos después de la prueba, documentado como no evaluado.

### Re-evaluación tras un error

- Error en el código de evaluación: se recalcula sobre las mismas predicciones guardadas, con segunda entrada en el registro.
- Error en datos o entrenamiento: se reentrena la misma lista declarada sin ningún cambio de diseño; se reportan ambos resultados y el corregido se marca "prueba ya vista".
- Nunca se re-evalúa por un resultado decepcionante.

### Soluciones publicadas

17 de los 22 pozos de prueba estaban en el `train.csv` de la competencia y 5 eran su prueba. No se usan pesos ni predicciones publicados; las arquitecturas sí; los hiperparámetros publicados solo como punto de partida, re-ajustados en validación.

### Registro y reproducibilidad

- `registro_prueba.json`, solo se agregan entradas: fecha, quién, versión del código, `run_id` de MLflow de cada modelo, huellas de partición, archivo de trabajo, archivo sellado, pesos y predicciones, métricas y motivo.
- Este protocolo se sube a GitHub antes del primer modelo; desde entonces `version_codigo` es el commit.
- Límite declarado: el registro demuestra que no hubo uso no declarado en el código del repositorio, no que nadie miró en privado.

### Controles de aceptación (fijados de antemano)

1. Archivo de trabajo: etiqueta y confianza NaN en las 242,918 filas de prueba; filas de entrenamiento/validación idénticas al curado; mismo número de filas.
2. Archivo sellado: 22 pozos, etiquetas iguales al curado; huellas en el manifiesto.
3. La función de carga no devuelve etiquetas de prueba; pedir la prueba sin la bandera de evaluación final falla.
4. Revisión automática de los `.ipynb`: ninguna lectura directa del curado ni del archivo sellado fuera de las celdas permitidas.
5. Celda de cierre de la sección 4 que elimina de memoria las variables con etiqueta y lo verifica.
6. Ensayo de `evaluate_test` sobre el pliegue 0.
7. La celda de la partición no reescribe el archivo existente; recalcula y compara.

## Resultados

Los 7 controles se cumplieron. Ensayo de `evaluate_test` con un modelo constante (clase más frecuente en los pliegues 1–4, Shale): exactitud provisional 0.659 sobre el pliegue 0, registrada en `registro_ensayo.json`. Predicciones con una fila faltante fallan sin escribir en el registro; el modo real con un registro ocupado se niega antes de abrir el archivo sellado. `registro_prueba.json` no existe.

## Referencias

- Varma, S. & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics* 7, 91. DOI 10.1186/1471-2105-7-91.
- Cawley, G. C. & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *JMLR* 11, 2079–2107.
- Kapoor, S. & Narayanan, A. (2023). *Patterns* 4(9), 100804. DOI 10.1016/j.patter.2023.100804.
