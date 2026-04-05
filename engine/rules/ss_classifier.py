# -----------------------------------
# SS CLASSIFIER (HYBRID)
# Reglas deterministas → fallback embedding
# -----------------------------------

_RULE = 0.95   # confianza asignada a toda regla determinista

def _r(code, text):
    """Shorthand para retorno de regla con confianza fija."""
    return {"code": code, "text": text, "confidence": _RULE, "source": "rule"}


def classify_ss(data, embedding_results):

    ifc  = data.get("ifc_type", "").lower()
    disc = data.get("discipline", "")

    # -------------------------
    # 1. REGLAS MEP — HVAC
    # -------------------------

    if ifc == "ifcairterminalbox":
        return _r("ss_65_80", "air conditioning systems")

    if ifc == "ifcfan":
        return _r("ss_65_40", "ventilation systems")

    # -------------------------
    # 2. REGLAS MEP — PCI (fire)
    # -------------------------

    if disc == "fire":
        if ifc in {"ifcvalve", "ifcpump", "ifctank",
                   "ifcpipesegment", "ifcpipefitting",
                   "ifcfiresuppressionterminal", "ifcsensor"}:
            return _r("ss_55_30_98", "water fire suppression systems")

    # -------------------------
    # 3. REGLAS MEP — ELE
    # -------------------------

    if ifc in {"ifccablecarriersegment", "ifccablecarrierfitting"}:
        return _r("ss_70_30_10_45", "low-voltage cable management systems")

    if ifc == "ifcelectricdistributionboard":
        return _r("ss_70_30_45", "low-voltage systems")

    if ifc == "ifcjunctionbox":
        return _r("ss_70_30_80", "small power systems")

    if ifc == "ifclightfixture":
        return _r("ss_70_80_33", "general lighting systems")

    # -------------------------
    # 4. REGLAS MEP — SAN (sanitary)
    # -------------------------

    if disc == "sanitary":
        if ifc in {"ifcpipesegment", "ifcpipefitting"}:
            return _r("ss_55_70_38", "hot and cold water supply systems")
        if ifc in {"ifcvalve", "ifcpump"}:
            return _r("ss_55_70_38_65", "pumped cold water supply systems")
        if ifc == "ifctank":
            return _r("ss_55_70_38_42", "indirect hot water storage supply systems")

    if ifc == "ifcwasteterminal":
        return _r("ss_50_30_04", "above-ground wastewater drainage systems")

    if ifc in {"ifcflowterminal", "ifcsanitaryterminal"}:
        return _r("ss_40_15_75", "sanitary appliance systems")

    # -------------------------
    # 5. FALLBACK → EMBEDDING
    # -------------------------

    if embedding_results:
        best = embedding_results[0]
        return {
            "code":       best["code"],
            "text":       best["text"],
            "confidence": best.get("score", 0.0),
            "source":     "embedding",
        }

    return {"code": "ss_00", "text": "unknown", "confidence": 0.0, "source": "none"}
