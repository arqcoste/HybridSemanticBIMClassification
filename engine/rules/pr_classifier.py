# -----------------------------------
# PR CLASSIFIER (HYBRID FINAL 🔥)
# -----------------------------------

def classify_pr(data, embedding_results):

    ifc = data.get("ifc_type", "").lower()
    name = (data.get("name") or "").lower()

    # -------------------------
    # 1. REGLAS DIRECTAS
    # -------------------------

    # BEAMS
    if ifc == "ifcbeam":
        if "plate" in name or "seat" in name:
            return {"code": "pr_connection", "text": "structural connection"}
        return {"code": "pr_beam", "text": "beam"}

    # COLUMNS
    if ifc == "ifccolumn":
        if "plate" in name:
            return {"code": "pr_connection", "text": "base plate"}
        return {"code": "pr_column", "text": "column"}

    # SLABS
    if ifc == "ifcslab":
        return {"code": "pr_slab", "text": "slab"}

    # WALLS
    if ifc == "ifcwall":
        return {"code": "pr_wall", "text": "wall"}

    # FOUNDATIONS
    if ifc == "ifcfooting":
        return {"code": "pr_foundation", "text": "foundation"}

    # REINFORCEMENT
    if ifc in ["ifcreinforcingbar", "ifcreinforcingmesh"]:
        return {"code": "pr_reinforcement", "text": "reinforcement"}

    # -------------------------
    # 2. FALLBACK → EMBEDDING
    # -------------------------

    if embedding_results:
        return embedding_results[0]

    return {"code": "pr_00", "text": "unknown"}