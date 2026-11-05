# Etapa 4 — Objetivo específico 4: por qué una partición aleatoria por filas sería inválida (CERRADO, 2026-11-03)

Sesión 17, 2026-11-03, con Claude. Sección 4.4 del notebook. Depende de la partición `etapa4_particion.csv` (`c55dc4d0…`), del mecanismo de prueba (`load_split`, `evaluate_test`) y de las métricas (`equipo/metricas.py`, `evaluate`). Con este objetivo se cierra la Etapa 4; el protocolo completo queda consolidado en `protocolo-evaluacion.md`.

**Resumen:** una partición aleatoria por filas estimaría otra cantidad (rellenar una fila de un pozo conocido) y la inflaría por la autocorrelación vertical y la identidad del pozo. Demostración prerregistrada en el pool (sin tocar la prueba): un predictor que no mira ningún registro y copia la etiqueta de la fila vecina obtiene −0.083 por pozo con filas al azar (F1 macro 0.94, exactitud 0.97) frente a −1.221 del modelo constante, que da lo mismo con ambas particiones; con partición por pozos ese predictor no existe.

## Revisión inicial (sesión 17)

- Sección 4 del notebook coherente con lo documentado: corrida de una sola vez (contadores 2–25); huellas `c55dc4d0`, `45a0ed6f`, `1904defd`, `c312481a` en las salidas; celdas 160, 166 y 167 como se documentaron en el objetivo 3.
- `registro_ensayo.json` tiene 5 entradas (la celda 168 imprime 4 antes de la 177): cada ejecución de la sección 4 agrega dos entradas de ensayo (celdas 167 y 177). Sin riesgo (registro de solo agregar); se documenta, no se modifican celdas.
- La celda 167 sí se re-ejecutó con la interfaz nueva (el documento del objetivo 3 decía que no); su `code_version` conserva la fecha del 2026-10-15 (cosmético; desaparece cuando la versión sea el commit).
- Variables reutilizadas entre celdas (`toy`, `rng`, `keys`, `prior`, `s`, `order`): en orden lineal ninguna se lee antes de redefinirse.
- `etapa1-objetivo4-faltantes-y-clases.md` decía que el tratamiento de las clases raras "sigue pendiente"; quedó resuelto en Etapa 4 objetivo 1. Corregido en esta sesión.
- Avance del 23 de octubre: sin registro; queda pendiente de nueva fecha con el profesor (Juan José, 2026-11-03). No afecta este objetivo.
- Carpeta local del repositorio (`force2020-litofacies`, en el computador de Juan José, preparada el 2026-10-24 para el Avance): sin `metricas.py`, `penalty_matrix.npy`, los documentos de los objetivos 3–4 ni el protocolo consolidado; el README dice "faltan las métricas". No es un repositorio git local (se subió por otra vía, no verificado). Pendiente de actualizar antes del primer modelo.

## Material del curso

- Estadística (libro guía): ec. 1.33, var(x̄) = n⁻¹ Σ (1 − |h|/n) γ(h): con dependencia, n filas no son n réplicas. §5.1 (ec. 5.6): con d > 0, Σ|ρ(h)| = ∞ (memoria larga); nuestras curvas tienen d ≈ 0.55–0.82. Diapositivas cap. 2: los suavizadores elegidos por GCV "assume iid observations… treat the bandwidth / λ as exploratory". §7.7 y Ej. 7.11: la validación cruzada de Lachenbruch–Mickey deja fuera un evento completo (cada sismo o explosión es una observación), no una muestra de su traza: el análogo de dejar fuera un pozo.
- Aprendizaje Profundo (`EAFIT-IA/si7011-DeepLearning`, sin cambios desde 2026-10-27, verificado 2026-11-03): diapositiva "Three ways to leak the future" (S05) y notebook 5.1 §6: barajar antes de partir, normalizar con toda la serie, ventanas que cruzan el corte. Cuantificado en Jena: validación barajada 2.30 °C frente a la referencia de sentido común 2.44; el mismo modelo en el bloque futuro 2.57 frente a 2.62 (notas de la diapositiva F12). En el curso el corte es temporal; en este proyecto el corte es el límite del pozo. S02: escalador solo con entrenamiento, prueba una vez.
- Sistemas de Aprendizaje Automático: sin material en el proyecto.
- Otros documentos leídos: rúbricas (Aprendizaje Profundo: "estrategia de validación"), programación (documento final, sección 3.4), preliminar (uso declarado: "que funcione en pozos que nunca vio antes"). "Fundamentos teóricos de la investigación" y "Tipo de conectores": no pertinentes.

## Mecanismos

Centrales:
1. **Estimando equivocado**: el uso declarado es un pozo nunca visto; filas al azar miden rellenar una fila faltante de un pozo conocido. Los demás mecanismos explican por qué esas dos cantidades difieren.
2. **Vecinos casi idénticos por autocorrelación vertical**: ACF a 0.15 m de 0.988–0.997 en las 5 curvas núcleo, 0.81–0.94 a 3.8 m; d 0.55–0.82 sin largo de decorrelación bajo 300 m; coherencia nula bajo 1.2 m (lo que separa a dos filas vecinas es ruido); distancia mediana al contacto ~5 m (~32 filas). Con 1/6 de filas en prueba, P(vecina adyacente en entrenamiento) = 1 − (1/6)² ≈ 0.97. Con ventanas (W_ref = 339) dos ventanas vecinas comparten 338 filas, y un modelo secuencia a secuencia habría entrenado con la etiqueta de ~283 filas de la ventana de cada fila evaluada. **El sesgo es diferencial**: favorece a los modelos con contexto o de alta capacidad (demostrado en el Bloque 1), justo la comparación de la Etapa 7.
3. **Identidad del pozo**: cociente entre/intra-pozo ≥ 1 en `MUDWEIGHT` 1.73, `ROPA` 1.42, `DTS` 1.38, `SGR` 1.32, `ROP` 1.24 (y 0.41–0.84 en las globales); `X_LOC`, `Y_LOC`, `DEPTH_MD` ubican la fila. Con filas al azar el atajo funciona; en un pozo nuevo no aporta.

Secundarios:
4. **Clases confinadas** (`Basement` 1 pozo, `Halite` 4, `Anhydrite` 9, `Chalk` 14): con filas al azar `Basement` tendría un F1 "evaluable" que mide memoria de un solo pozo (en el Bloque 1 la copia del vecino reconoce `Halite` y `Anhydrite` sin mirar registros).
5. **Normalización y estadísticos con datos de prueba**: ya controlado en el protocolo (globales ajustados en Etapa 6 solo con pozos de entrenamiento; escalado por pozo sin parámetros entre pozos).
6. **Incertidumbre falsa**: con 20 pozos el IC por pozo mide ~0.40; tratar 234,596 filas como réplicas lo estrecharía en más de un orden de magnitud (estimación, no calculada).

## Prerregistro de la demostración (aprobado por Juan José el 2026-11-03, antes de ejecutar código)

**Pregunta:** cuánto puntaje obtiene, con partición aleatoria por filas, un predictor que no usa ningún registro y solo copia la etiqueta de la fila de entrenamiento más cercana del mismo pozo.

**Predictor "copia del vecino":** para cada fila evaluada, la fila de entrenamiento más cercana del mismo pozo en el orden de profundidad (distancia en filas); empate entre la de arriba y la de abajo → gana la de arriba (menos profunda). Sin parámetros, sin curvas: solo pozo y orden en profundidad.

**Datos:** los 96 pozos del pool, `load_split(["fold0", …, "fold4"])`, todas las filas con etiqueta. La prueba no se carga.

**Partición aleatoria por filas:** filas ordenadas por `WELL` y `DEPTH_MD`; `np.random.default_rng(0).integers(0, 5, n)` asigna cada fila a uno de 5 pliegues; cada fila se predice una vez, fuera de su pliegue. Una sola corrida.

**Referencias:** (a) modelo constante (clase más frecuente del entrenamiento de cada pliegue) con la misma partición aleatoria; (b) el mismo modelo constante con la partición por pozos vigente (pliegues 0–4). El predictor copia del vecino no existe con partición por pozos (no hay filas del mismo pozo en entrenamiento).

**Métrica:** `evaluate` de `equipo/metricas.py` (principal: puntaje de penalización por pozo con IC bootstrap por pozo; complementarias), estratos con `strata`. Comparación copia − constante por `paired_difference` por pozo. Diagnóstico: fracción de filas cuya fila de entrenamiento más cercana está a 1 fila; exactitud por distancia (1, 2, ≥ 3 filas).

**Predicción antes de correr:** copia del vecino con exactitud ≥ 0.90 y puntaje por pozo ≥ −0.30; modelo constante entre −1.0 y −1.2 por pozo e igual (o casi) con ambas particiones; fracción a 1 fila ≈ 0.96 (1 − 0.2²).

**Regla de lectura:** la demostración se cumple si la copia del vecino supera al constante con diferencia pareada real (IC 95% excluye 0) y queda ≥ −0.30. Cualquiera que sea el resultado, la partición, las métricas y el protocolo no cambian.

**Cortafuegos:** el predictor no ajusta nada; no entra a ninguna lista de modelos de las Etapas 5–7; no se registra en MLflow; su resultado no se usa para elegir variables (en particular `X_LOC`, `Y_LOC`, `DEPTH_MD`) ni ninguna otra decisión de diseño; no se re-corre con otras semillas ni variantes.

## Resultados por bloque

### Bloque 1 — copia del vecino (corrida única, semilla 0, 2026-11-03)

96 pozos, 1,186,776 filas; 11 clases evaluables (validación cruzada fuera de pliegue).

| predictor | partición | score por pozo | IC 95% | score por filas | F1 macro | exactitud |
|---|---|---|---|---|---|---|
| copia del vecino (sin registros) | filas al azar | **−0.0834** | [−0.0912, −0.0756] | −0.0821 | **0.943** | **0.970** |
| constante (Shale) | filas al azar | −1.2210 | [−1.3316, −1.1124] | −1.1722 | 0.069 | 0.610 |
| constante (Shale) | pozos (pliegues 0–4) | −1.2210 | [−1.3316, −1.1124] | −1.1722 | 0.069 | 0.610 |

- Diferencia pareada copia − constante (filas al azar): **1.1376**, IC [1.0323, 1.2488], real; la copia gana en los **96 de 96** pozos.
- Fracción de filas con la fila de entrenamiento más cercana a 1 fila: **0.960** (teórico 1 − 0.2² = 0.96).
- Exactitud de la copia según la distancia a esa fila: 1 fila 0.9715; 2 filas 0.9435; ≥ 3 filas 0.9134.

**Contraste con la predicción prerregistrada:** copia — exactitud 0.970 ≥ 0.90 y score −0.083 ≥ −0.30 (cumple); fracción a 1 fila 0.960 (cumple); constante igual con ambas particiones (cumple, idéntico: la clase más frecuente es Shale en todos los pliegues de ambas particiones). **Desvío**: el constante quedó en −1.221, 0.02 por debajo del rango predicho [−1.2, −1.0] (la predicción se había anclado en el pliegue 0, −1.07; el pool completo tiene menos Shale por pozo). No afecta la regla de lectura. **Regla de lectura cumplida: la demostración se sostiene.** Controles internos del resultado (no fuga accidental): la fracción a 1 fila coincide con la teoría y el constante es idéntico con ambas particiones.

Lectura:
1. Un predictor que no mira ningún registro obtiene, con filas al azar, un puntaje de −0.08 (0 es perfecto) y F1 macro 0.94, incluidas `Halite` y `Anhydrite`, frente al piso de −1.22 del constante. Con partición por pozos ese predictor no existe. Toda la ventaja es información del propio pozo filtrada a través de la vecina: es el máximo que la fuga puede regalar sin aprender geología.
2. El modelo constante, que no usa vecinos, da exactamente el mismo puntaje con las dos particiones: la partición aleatoria no infla a todos los modelos por igual, infla en proporción a cuánto puede aprovechar la cercanía. Evidencia directa del sesgo diferencial (mecanismo 2).
3. La exactitud cae con la distancia a la vecina (0.97 → 0.94 → 0.91), firma de la persistencia vertical de la etiqueta; aun a ≥ 3 filas (≥ 0.46 m) copia bien más del 90% de las veces, coherente con capas de varios metros (distancia mediana al contacto ~5 m en la Etapa 3). Relación aproximada, no estimada formalmente.
4. Que la copia gane en los 96 pozos descarta que el efecto venga de unos pocos pozos.

### Bloque 2 — verificación de cierre de la Etapa 4 (2026-11-03)

Celda final de la sección 4.4; no carga etiquetas de prueba ni escribe en ningún registro. **Los 12 controles pasan** (`Etapa 4 verificada: True`):

| control | verifica | resultado |
|---|---|---|
| `particion` | huella de la partición = copia en `equipo/` = manifiesto del custodio = manifiesto del equipo = huella registrada en `etapa4_prueba` | True |
| `particion_estructura` | 118 pozos únicos, ninguna familia partida, tamaños 22/20/19/19/19/19 | True |
| `trabajo` | huella del archivo de trabajo = ambos manifiestos | True |
| `sellado` | huella del archivo sellado = manifiesto | True |
| `origen` | partición y archivos de prueba derivan del mismo curado | True |
| `penalizacion` | huella de la matriz = ambos manifiestos | True |
| `equipo_limpio` | `equipo/` sin sellado, curado, consolidado ni `__pycache__` | True |
| `reutilizable` | proceso Python nuevo que solo ve `equipo/`: `load_partition` (118) y `evaluate` del ejemplo de 5 filas (−0.5833, igual al cálculo a mano) | True |
| `huella_predicciones` | predicciones del ensayo = huella registrada | True |
| `evaluate_reproduce` | `evaluate` reproduce exactamente el ensayo registrado del pliegue 0 (−1.0718, diccionario completo) | True |
| `prueba_sin_usar` | `registro_prueba.json` no existe; las 5 entradas de `registro_ensayo.json` son ensayos | True |
| `scan_seccion5` | ninguna lectura directa de archivos con etiqueta después de `# 5.` | True |

Contenido de `equipo/`: `acceso_datos.py`, `etapa4_particion.csv`, `etapa4_pool_trabajo.parquet`, `manifiesto_equipo.json`, `metricas.py`, `penalty_matrix.npy`, `revision_notebooks.py`. Avisos `Mean of empty slice` / `All-NaN slice` en el proceso nuevo: esperados, el ejemplo de juguete no tiene ninguna clase con ≥ 8 filas en ≥ 2 pozos (F1 macro sin clases evaluables); no afectan la principal.

## Cierre de la Etapa 4

| producto de la hoja de ruta | evidencia |
|---|---|
| particiones fijas y versionadas, idénticas para todos los modelos | `etapa4_particion.csv` `c55dc4d0…` en custodio y `equipo/`, en ambos manifiestos; única vía `load_split`; controles `particion` y `particion_estructura` |
| protocolo de evaluación escrito, con métricas y criterios de comparación | `protocolo-evaluacion.md` (consolidado, con borrador de la sección 3.4) y los cuatro documentos de detalle |
| función de evaluación implementada y reutilizable | `equipo/metricas.py` (`evaluate`, `paired_difference`, `mlflow_scalars`), `evaluate_test`; controles `reutilizable` y `evaluate_reproduce` |

**Etapa 4 completa. Compuerta cumplida: ningún modelo entrenado.** El predictor copia del vecino no ajusta parámetros y quedó fuera de toda lista de modelos.

## Implicaciones para etapas posteriores

- **Etapa 5**: el modelo constante sobre la validación cruzada del pool da −1.2210 por pozo (piso de la tabla con validación cruzada; −1.0718 en el pliegue 0); se recalcula allí con el mismo código. Resto de obligaciones en `protocolo-evaluacion.md`, sección 9.
- **Etapa 7**: la comparación con y sin contexto vertical solo es válida con partición por pozos; el Bloque 1 muestra que el sesgo de filas al azar crece con la capacidad de aprovechar la cercanía.
- **Repositorio**: actualizar la carpeta `force2020-litofacies` (módulos de los objetivos 3–4, `penalty_matrix.npy`, documentos y protocolo, README) y subirla antes del primer modelo.
- **Presentación final**: el contraste −0.08 frente a −1.22 ("copiar la roca de al lado") es material para explicar a audiencia no geóloga por qué se evalúa por pozo.

## Celdas del notebook (sección 4.4)

1. Bloque 1: `cv_rows`, `row_fold`, predictor copia del vecino (`copy_pred`, `gap`), constantes (`const_rand`, `const_grp`), `demo`, diferencia pareada y diagnóstico por distancia.
2. Bloque 2: verificación de cierre (`checks`, proceso nuevo con `subprocess`, reproducción del ensayo).

Ninguna celda existente se modificó.

## Bibliografía

- Ya citadas en los objetivos 1–3 y verificadas: Roberts et al. (2017), *Ecography*, DOI 10.1111/ecog.02881; Ploton et al. (2020), *Nature Communications* 11, 4540, DOI 10.1038/s41467-020-18321-y; Kapoor & Narayanan (2023), *Patterns* 4(9), 100804, DOI 10.1016/j.patter.2023.100804.
- Búsqueda de evidencia específica en litofacies (2026-11-03): no se encontró un artículo Q2+ con DOI verificable que compare filas al azar frente a pozos y cuantifique la sobreestimación. Cao et al. (2026), *Artificial Intelligence in Geosciences* 7(2), 100224, DOI 10.1016/j.aiig.2026.100224: compara muestreos de filas en 9 pozos (exactitud > 0.95), sin pozos ciegos; ejemplo de la práctica, no de la brecha; cuartil no verificado. Benchmark en *Mathematical Geosciences* (2026), DOI 10.1007/s11004-026-10300-1: contenido no accesible, pendiente de verificar con acceso de biblioteca. Meyer et al. (2018), *Environmental Modelling & Software* (validación orientada al objetivo, leave-location-out): existencia confirmada en repositorios; DOI no verificado.
- Shumway & Stoffer, libro guía: ec. 1.33, §5.1, §7.7 (Ej. 7.11). Curso SI7011, sesión 5 (notebook 5.1).
