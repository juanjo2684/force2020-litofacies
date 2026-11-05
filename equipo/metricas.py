import json, os
import numpy as np
import pandas as pd
from acceso_datos import file_sha256

TEAM_DIR = os.path.dirname(os.path.abspath(__file__))

# orden de filas y columnas de penalty_matrix.npy (lithology_numbers del starter notebook)
CODES = [30000, 65030, 65000, 80000, 74000, 70000, 70032, 88000, 86000, 99000, 90000, 93000]
NAMES = ["Sandstone", "Sandstone/Shale", "Shale", "Marl", "Dolomite", "Limestone",
         "Chalk", "Halite", "Anhydrite", "Tuff", "Coal", "Basement"]
INDEX = {c: i for i, c in enumerate(CODES)}

MIN_ROWS = 8   # presencia de una clase en un pozo (misma definicion de la particion)
MIN_WELLS = 2  # pozos con la clase para que entre a los promedios por clase
N_BOOT = 2000


def load_penalty():
    with open(f"{TEAM_DIR}/manifiesto_equipo.json") as f:
        expected = json.load(f)["penalizacion_sha256"]
    path = f"{TEAM_DIR}/penalty_matrix.npy"
    assert file_sha256(path) == expected, "la matriz de penalizacion no coincide con el manifiesto"
    return np.load(path)


PENALTY = load_penalty()


def to_index(codes):
    idx = pd.Series(np.asarray(codes)).map(INDEX)
    assert idx.notna().all(), "codigo de litologia fuera de las 12 clases"
    return idx.to_numpy(dtype=int)


def row_penalty(y_true, y_pred):
    return PENALTY[to_index(y_true), to_index(y_pred)]


def penalty_score(y_true, y_pred):
    return -float(row_penalty(y_true, y_pred).mean())


def well_scores(wells, y_true, y_pred):
    cost = pd.Series(row_penalty(y_true, y_pred), index=np.asarray(wells))
    return -cost.groupby(level=0).mean()


def confusion(y_true, y_pred):
    cm = np.zeros((len(CODES), len(CODES)), dtype=int)
    np.add.at(cm, (to_index(y_true), to_index(y_pred)), 1)
    return cm


def well_confusions(wells, y_true, y_pred):
    wells = np.asarray(wells)
    names = np.unique(wells)
    stack = np.zeros((len(names), len(CODES), len(CODES)), dtype=int)
    np.add.at(stack, (np.searchsorted(names, wells), to_index(y_true), to_index(y_pred)), 1)
    return names, stack


def rates(cm):
    tp = np.diag(cm)
    real, predicted = cm.sum(axis=1), cm.sum(axis=0)
    # precision 0 si la clase existe y nunca se predice (zero_division=0, como en el curso)
    precision = np.divide(tp, predicted, out=np.where(real > 0, 0.0, np.nan), where=predicted > 0)
    recall = np.divide(tp, real, out=np.full(len(CODES), np.nan), where=real > 0)
    denom = precision + recall
    f1 = np.divide(2 * precision * recall, denom, out=np.where(real > 0, 0.0, np.nan), where=denom > 0)
    return precision, recall, f1


def class_metrics(wells, y_true, y_pred):
    cm = confusion(y_true, y_pred)
    precision, recall, f1 = rates(cm)
    real, predicted = cm.sum(axis=1), cm.sum(axis=0)
    rows_by_well = (pd.crosstab(np.asarray(wells), np.asarray(y_true))
                    .reindex(columns=CODES, fill_value=0))
    n_wells = (rows_by_well >= MIN_ROWS).sum().to_numpy()
    return pd.DataFrame({"precision": precision, "recall": recall, "f1": f1,
                         "filas": real, "pozos": n_wells, "predichas": predicted,
                         "falsos_positivos": predicted - np.diag(cm),
                         "evaluable": n_wells >= MIN_WELLS}, index=NAMES)


def class_summary(table, y_true, y_pred):
    ev = table[table["evaluable"]]
    return {"f1_macro": float(ev["f1"].mean()),
            "exactitud_balanceada": float(ev["recall"].mean()),
            "exactitud": float((np.asarray(y_true) == np.asarray(y_pred)).mean()),
            "clases_evaluables": list(ev.index)}


def resample_index(n_wells, n_boot=N_BOOT, seed=0):
    return np.random.default_rng(seed).integers(0, n_wells, (n_boot, n_wells))


def percentile_ci(values, level=0.95):
    lo, hi = np.nanquantile(values, [(1 - level) / 2, (1 + level) / 2])
    return [float(lo), float(hi)]


def mean_ci(per_well, n_boot=N_BOOT, seed=0):
    v = np.asarray(per_well, dtype=float)
    return percentile_ci(v[resample_index(len(v), n_boot, seed)].mean(axis=1))


def macro_f1_ci(stack, evaluable, n_boot=N_BOOT, seed=0):
    # las clases evaluables quedan fijas; si una falta en una replica, se omite en esa replica
    values = [np.nanmean(rates(stack[idx].sum(axis=0))[2][evaluable])
              for idx in resample_index(len(stack), n_boot, seed)]
    return percentile_ci(values)


def paired_difference(scores_a, scores_b, n_boot=N_BOOT, seed=0):
    assert set(scores_a.index) == set(scores_b.index), "los modelos no se evaluaron en los mismos pozos"
    d = scores_a - scores_b.reindex(scores_a.index)
    ci = mean_ci(d, n_boot, seed)
    return {"diferencia": float(d.mean()), "ic95": ci, "real": not (ci[0] <= 0 <= ci[1]),
            "gana_a": int((d > 0).sum()), "gana_b": int((d < 0).sum()), "empates": int((d == 0).sum())}


W_REF = 339  # ventana de referencia de la Etapa 3, en filas


def strata(wells, depth, segment, w=W_REF):
    h = w // 2
    d = pd.DataFrame({"well": np.asarray(wells), "seg": np.asarray(segment), "depth": np.asarray(depth)})
    d = d.sort_values(["well", "seg", "depth"])
    g = d.groupby(["well", "seg"], sort=False)
    pos, n = g.cumcount(), g["depth"].transform("size")
    label = np.where(n < w, "sin_ventana", np.where((pos < h) | (pos >= n - h), "borde", "interior"))
    return pd.Series(label, index=d.index).sort_index().to_numpy()


def json_safe(x):
    if isinstance(x, dict):
        return {str(k): json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [json_safe(v) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if np.isnan(x) else float(x)
    return x


def evaluate(df, n_boot=N_BOOT, seed=0):
    wells, y_true, y_pred = df["WELL"], df["y_true"], df["y_pred"]
    scores = well_scores(wells, y_true, y_pred)
    table = class_metrics(wells, y_true, y_pred)
    summary = class_summary(table, y_true, y_pred)
    _, stack = well_confusions(wells, y_true, y_pred)

    by_stratum = {}
    for name, part in df.groupby("stratum"):
        s = well_scores(part["WELL"], part["y_true"], part["y_pred"])
        by_stratum[name] = {"filas": len(part), "pozos": len(s), "score_pozo": s.mean(),
                            "score_filas": penalty_score(part["y_true"], part["y_pred"]),
                            "exactitud": (part["y_true"] == part["y_pred"]).mean()}

    return json_safe({
        "filas": len(df),
        "principal": {"score_pozo": scores.mean(), "ic95": mean_ci(scores, n_boot, seed), "pozos": len(scores)},
        "complementarias": {"score_filas": penalty_score(y_true, y_pred),
                            "f1_macro_ic95": macro_f1_ci(stack, table["evaluable"].to_numpy(), n_boot, seed),
                            **summary},
        "por_clase": table.to_dict("index"),
        "confusion": stack.sum(axis=0),
        "por_pozo": scores.to_dict(),
        "por_estrato": by_stratum,
    })


def mlflow_scalars(result, prefix="val_"):
    out = {"score_pozo": result["principal"]["score_pozo"]}
    comp = result["complementarias"]
    out.update({k: comp[k] for k in ["score_filas", "f1_macro", "exactitud_balanceada", "exactitud"]})
    out.update({"f1_" + name.replace("/", "_"): row["f1"]
                for name, row in result["por_clase"].items() if row["evaluable"]})
    return {prefix + k: v for k, v in out.items()}
