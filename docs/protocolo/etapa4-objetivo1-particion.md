# Etapa 4 — Objetivo específico 1: partición por pozos completos, agrupada por pozo y estratificada por clase (CERRADO, 2026-10-15)

Sesión 14, 2026-10-14/15, con Claude. Sección 4 del notebook. Partición vigente: `etapa4_particion.csv`, **sha256 `c55dc4d0…`** (registrado en `manifiesto_datos.json`, clave `etapa4_particion`).

**Resumen:**

| conjunto | familias | pozos | filas | % filas | uso |
|---|---|---|---|---|---|
| prueba | 22 | 22 | 242,918 | 17.0 | una sola vez, al final del proyecto |
| pliegue 0 | 19 | 20 | 234,596 | 16.4 | validación fija (aprendizaje profundo) y pliegue de la validación cruzada |
| pliegue 1 | 19 | 19 | 233,501 | 16.3 | validación cruzada |
| pliegue 2 | 19 | 19 | 223,839 | 15.7 | validación cruzada |
| pliegue 3 | 19 | 19 | 259,585 | 18.2 | validación cruzada |
| pliegue 4 | 19 | 19 | 235,255 | 16.5 | validación cruzada |
| total | 117 | 118 | 1,429,694 | 100 | |

Esquema con validación fija: entrenamiento = pliegues 1–4 (76 pozos), validación = pliegue 0 (20 pozos), prueba = 22 pozos. En validación cruzada, los 5 pliegues rotan como validación.

**Corrección (sesión 15, 2026-10-15):** este documento decía "pliegues 1–4 (77 pozos)". Son 76 (19 × 4; 96 − 20), verificado con `load_split` en el objetivo 2. Error aritmético de documentación, sin efecto sobre la partición.

**Pozos de prueba (22):** `15/9-15`, `16/1-2`, `16/2-11 A`, `16/7-5`, `17/4-1`, `25/5-4`, `25/8-5 S`, `26/4-1`, `31/2-21 S`, `31/2-9`, `31/3-3`, `31/4-10`, `34/3-2 S`, `34/7-13`, `34/7-21`, `34/8-7 R`, `35/11-10`, `35/11-12`, `35/6-2 S`, `35/9-2`, `35/9-5`, `35/9-8`. Cinco de ellos eran pozos de prueba de la competencia: `17/4-1`, `31/2-21 S`, `34/3-2 S` (hidden_test) y `35/6-2 S`, `35/9-8` (leaderboard_test). La precaución de no leer soluciones publicadas aplica a toda la lista, con prioridad a estos cinco.

## Prerregistro (fijado antes de ejecutar la partición)

Escrito y aprobado antes de correr cualquier bloque que asigne pozos a conjuntos y antes de entrenar cualquier modelo. No se modificó después de ver la partición; las notas fechadas se agregaron antes de la corrida real.

### Esquema

| elemento | valor |
|---|---|
| prueba | 1/6 de los grupos (≈ 20 pozos); se toca una sola vez, al final del proyecto |
| pool de validación cruzada | 5/6 (≈ 98 pozos) en K = 5 pliegues de ≈ 20 pozos |
| validación fija | pliegue 0 (hiperparámetros de aprendizaje profundo, early stopping, sensibilidad de W) |
| validación cruzada completa | pliegues 0–4 (modelos de referencia; dispersión entre pliegues) |
| unidad de partición | grupo = familia de pozos; 117 grupos (`34/5-1 A` y `34/5-1 S` forman la única familia con más de un pozo) |

Razones: la validación fija hace viable la búsqueda de aprendizaje profundo en Colab; la validación cruzada de los modelos de referencia (baratos) da la dispersión entre pliegues necesaria para juzgar diferencias; 1/6 iguala el tamaño de prueba y de cada pliegue; la unidad efectiva de muestra es el pozo (heterogeneidad entre pozos de la Etapa 3), y ~20 pozos de prueba reducen a la mitad la varianza de la media por pozo frente a 10; dejar un pozo fuera cada vez (98 entrenamientos por configuración) se descartó por costo.

### Estratificación

- Variable: vector binario por grupo con (a) presencia de cada una de las 12 clases de litofacies, donde una clase cuenta como presente si ocupa ≥ 8 filas (1.2 m, resolución de las curvas = `G_max`), y (b) tercil del número de curvas disponibles (`n_curves`), calculado sobre los 118 pozos con `pd.qcut(..., 3, duplicates="drop")`. Para una familia, unión de las presencias y tercil de su pozo con más filas.
- Cada pozo (grupo) vale un voto. La proporción de filas por clase no se optimiza (un solo pozo concentra 44% de la Halite y otro 27% de la Anhydrite); se reporta como control.
- Algoritmo: estratificación iterativa multietiqueta (Sechidis, Tsoumakas & Vlahavas, 2011, DOI 10.1007/978-3-642-23808-6_10), implementación propia, en dos pasos: (1) prueba vs. pool con proporciones [1/6, 5/6]; (2) pool en 5 pliegues con proporciones iguales. Dos pasos y no seis partes de una vez: con seis partes la prueba recibiría Halite con probabilidad 4/6; en dos pasos la recibe con certeza.
- Reglas del algoritmo: se procesa primero la etiqueta con menos grupos sin asignar; sus grupos se recorren en orden aleatorio; cada grupo va al conjunto con mayor demanda pendiente de esa etiqueta; empates por mayor demanda total de grupos; empates restantes al azar. Todas las demandas se descuentan al asignar cada grupo.
- Semilla: un único `np.random.default_rng(0)` creado al inicio del paso 1 y usado en secuencia en ambos pasos.
- **Nota (2026-10-15, antes de la corrida real):** el desempate entre etiquetas con el mismo número de grupos sin asignar se resuelve al azar con el mismo generador. La función se verificó contra un ejemplo resuelto a mano (5 familias, 3 etiquetas, 4 semillas).

### Uso de la etiqueta

La estratificación usa la etiqueta de los 118 pozos solo como resumen grueso (presencia binaria por pozo) para decidir qué pozos se evalúan, no cómo se construye el modelo. Condiciones: algoritmo y semilla fijados antes de correr; una sola corrida; ninguna métrica de modelo existe; la composición de la prueba no se usa después para nada (pesos de clase, estandarización y cualquier estadístico se ajustan solo con los pozos de entrenamiento de cada pliegue). Re-sortear después de ver resultados cruzaría la frontera.

### Estimando y factores no estratificados

- Lo que se estima: desempeño en un pozo nuevo dentro de un área ya perforada, no en una cuenca nueva. No se agrupa por zona: las clases raras están en los cuadrantes 15–17 y agrupar por zona haría imposible la estratificación. La única fuga real sería el mismo agujero en dos conjuntos, de ahí el agrupamiento por familia.
- Solo se reportan como control: largo del pozo, origen en la competencia, cuadrante, distancia de cada pozo evaluado al pozo más cercano fuera de su conjunto.
- Los 7 pozos representativos de la Etapa 3 no entran como insumo; después se registra dónde cayó cada uno.

### Controles de aceptación (fijados de antemano)

1. Los 118 pozos asignados una sola vez; ninguna familia partida; tamaños por conjunto.
2. Unión con las filas por `WELL` sin nulos; suma = 1,429,694 filas; cada pozo con un único conjunto.
3. Por conjunto: pozos con cada clase vs. esperado, filas por clase, clases ausentes listadas.
4. Restricciones: `Basement` fuera de prueba; toda clase presente en ≥ 3 pozos con ≥ 1 pozo en prueba y ≥ 2 en el pool.
5. Balance reportado de tercil de suite, largo, origen y cuadrante.
6. Distancia de cada pozo de prueba (y de cada pliegue) al pozo más cercano fuera de su conjunto.
7. Archivo de partición releído idéntico y con su huella registrada; ubicación de los 7 representativos.

Si un control falla por un error de código, se corrige el código y se corre de nuevo con la misma semilla. Nunca se re-sortea con otra semilla para "mejorar" el balance.

### Clases sin evaluación completa (consecuencia conocida de antemano)

- `Basement` (1 pozo): va al pool; no evaluable en prueba. Se declara no evaluable por clase (cuenta en métricas globales y en la matriz de penalización).
- `Halite` (4 pozos, uno con solo 20 filas): 1 pozo en prueba, elegido por el algoritmo. Si la prueba queda con soporte bajo, se resuelve con una regla de soporte mínimo en el objetivo 3 (métricas), nunca re-sorteando.

## Resultados

- Corrida única, semilla 0: huella `c55dc4d0…`; prueba 22 familias / 22 pozos; pool 95 / 96; pliegues de 19 familias (el 0 con 20 pozos por `34/5-1`).
- Los 7 controles pasan. La prueba contiene las 11 clases evaluables; solo le falta `Basement`. Distancia al pozo más cercano fuera del conjunto (km, mín / P25 / mediana / máx): prueba 1.8 / 4.0 / 8.2 / 40.9; pliegues entre 1.8–2.6 / 3.0–6.6 / 5.6–8.4 / 19.5–47.5. La prueba no está más cerca del entrenamiento que los pliegues.
- Representativos: `34/10-19` pliegue 3, `7/1-1` pliegue 2, `16/4-1` pliegue 4, `25/4-5` pliegue 0, `31/3-2` pliegue 1, `25/3-1` pliegue 3, `34/4-10 R` pliegue 4. Ninguno en prueba.

## Desviaciones (sin cambio de la partición)

- **Tamaño de prueba 22 en lugar de ≈ 20.** El algoritmo no impone el tamaño total, igual que el original de Sechidis. Aceptado sin re-correr (re-correr sería re-sortear).
- **Halite en prueba = `17/4-1`** (6,498 filas, 44.2% de las filas de Halite): soporte sustantivo.
- **El pliegue 0 casi no tiene Halite ni Anhydrite en filas** (0.1% y 0.9%). Consecuencia para las métricas y la Etapa 7, no motivo para cambiar la partición.

## Referencias

- Sechidis, K., Tsoumakas, G. & Vlahavas, I. (2011). On the stratification of multi-label data. ECML PKDD, LNCS, pp. 145–158. DOI 10.1007/978-3-642-23808-6_10.
- Roberts, D. R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*. DOI 10.1111/ecog.02881.
- Ploton, P. et al. (2020). Spatial validation reveals poor predictive performance of large-scale ecological mapping models. *Nature Communications* 11, 4540. DOI 10.1038/s41467-020-18321-y.
- Kapoor, S. & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 4(9), 100804. DOI 10.1016/j.patter.2023.100804.
