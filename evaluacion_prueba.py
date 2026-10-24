import datetime, json, os, sys
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{DATA_DIR}/equipo")
from acceso_datos import file_sha256, load_split, LITH

KEYS = ["WELL", "DEPTH_MD"]


def evaluate_test(pred_path, metric_fn, models, author, code_version, reason,
                  dry_run=True, reentry=False, registry_dir=DATA_DIR):
    # la huella de las predicciones se fija antes de leer cualquier etiqueta
    pred_sha = file_sha256(pred_path)
    with open(f"{DATA_DIR}/manifiesto_datos.json") as f:
        manifest = json.load(f)
    sealed = manifest["etapa4_prueba"]["sellado"]

    if dry_run:
        registry = f"{registry_dir}/registro_ensayo.json"
        truth = load_split(["fold0"])[KEYS + [LITH]]
    else:
        registry = f"{registry_dir}/registro_prueba.json"
        if os.path.exists(registry) and not reentry:
            raise RuntimeError("la prueba ya se uso; una re-evaluacion exige reentry=True y motivo")
        sealed_path = f"{DATA_DIR}/{sealed['archivo']}"
        assert file_sha256(sealed_path) == sealed["sha256"], "el archivo sellado no coincide con el manifiesto"
        truth = pd.read_parquet(sealed_path, columns=KEYS + [LITH])

    preds = pd.read_parquet(pred_path)
    assert set(preds.columns) == set(KEYS) | set(models), "columnas de prediccion distintas de los modelos declarados"
    assert not preds.duplicated(KEYS).any()
    merged = truth.merge(preds, on=KEYS, how="outer", indicator=True)
    assert (merged["_merge"] == "both").all(), "las filas de predicciones y verdad no coinciden"

    metrics = {m: metric_fn(merged[LITH].to_numpy(), merged[m].to_numpy()) for m in models}

    entries = []
    if os.path.exists(registry):
        with open(registry) as f:
            entries = json.load(f)
    entries.append({
        "fecha": datetime.datetime.now().isoformat(timespec="seconds"),
        "modo": "ensayo" if dry_run else "prueba",
        "autor": author,
        "version_codigo": code_version,
        "motivo": reason,
        "modelos": models,
        "huellas": {"particion": manifest["etapa4_particion"]["sha256"],
                    "trabajo": manifest["etapa4_prueba"]["trabajo"]["sha256"],
                    "sellado": sealed["sha256"],
                    "predicciones": pred_sha},
        "filas": len(merged),
        "pozos": int(merged["WELL"].nunique()),
        "metricas": metrics,
    })
    with open(registry, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    return metrics
