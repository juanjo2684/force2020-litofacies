import json

SENSITIVE = ["etapa2_pool_curado", "etapa1_pool_consolidado", "etapa4_prueba_sellada",
             "curated_path", "sealed_path"]


def scan_notebook(path, after_heading=None):
    with open(path) as f:
        cells = json.load(f)["cells"]
    active = after_heading is None
    hits = []
    for i, cell in enumerate(cells):
        src = "".join(cell["source"])
        if not active:
            active = cell["cell_type"] == "markdown" and src.lstrip().startswith(after_heading)
            continue
        if cell["cell_type"] != "code" or "def evaluate_test" in src:
            continue
        hits += [(i, name) for name in SENSITIVE if name in src]
    return hits
