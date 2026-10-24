import hashlib, json, os
import numpy as np
import pandas as pd

TEAM_DIR = os.path.dirname(os.path.abspath(__file__))
LITH = "FORCE_2020_LITHOFACIES_LITHOLOGY"
CONF = "FORCE_2020_LITHOFACIES_CONFIDENCE"


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_partition():
    with open(f"{TEAM_DIR}/manifiesto_equipo.json") as f:
        expected = json.load(f)
    path = f"{TEAM_DIR}/etapa4_particion.csv"
    assert file_sha256(path) == expected["particion_sha256"], "la particion no coincide con el manifiesto"
    part = pd.read_csv(path, dtype={"fold": "Int64"})
    part["set"] = np.where(part["split"] == "test", "test", "fold" + part["fold"].astype(str))
    return part


def load_split(sets, labels=True):
    if labels and "test" in sets:
        raise ValueError("la etiqueta de prueba solo se lee en evaluate_test; use labels=False")
    with open(f"{TEAM_DIR}/manifiesto_equipo.json") as f:
        expected = json.load(f)
    path = f"{TEAM_DIR}/etapa4_pool_trabajo.parquet"
    assert file_sha256(path) == expected["trabajo_sha256"], "el archivo de trabajo no coincide con el manifiesto"

    part = load_partition()
    wells = part.loc[part["set"].isin(sets), "WELL"].tolist()
    df = pd.read_parquet(path, filters=[("WELL", "in", wells)])
    if labels:
        df[LITH] = df[LITH].astype("int64")
    else:
        df = df.drop(columns=[LITH, CONF])
    return df.reset_index(drop=True)
