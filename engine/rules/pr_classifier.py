# -----------------------------------
# PR CLASSIFIER (HYBRID FINAL)
# -----------------------------------

_RULE = 0.95   # confianza asignada a toda regla determinista

def _r(code, text):
    """Shorthand para retorno de regla con confianza fija."""
    return {"code": code, "text": text, "confidence": _RULE, "source": "rule"}


# Códigos Uniclass PR por (elemento, material) → nivel 4 más específico posible
PR_STRUCTURAL = {
    # BEAMS
    ("beam",       "steel"):    _r("pr_20_76_51_90", "universal beam section"),
    ("beam",       "concrete"): _r("pr_20_85_08_15", "concrete beam"),
    ("beam",       "$"):        _r("pr_20_85_08",    "beams and joists"),
    # BEAM CONNECTIONS (plate / seat)
    ("beam_plate", "$"):        _r("pr_25_71_51_88", "steel plate, sheet and strip"),
    # COLUMNS
    ("column",     "steel"):    _r("pr_20_76_51_92", "universal column section"),
    ("column",     "concrete"): _r("pr_20_85_16_15", "concrete column"),
    ("column",     "$"):        _r("pr_20_85_16",    "columns and column accessories"),
    # COLUMN BASE PLATES
    ("column_plate","$"):       _r("pr_20_29_03_13", "carbon steel post base plate"),
    # SLABS
    ("slab",       "concrete"): _r("pr_20_85_14_16", "concrete solid slab"),
    ("slab",       "$"):        _r("pr_20_85_14_16", "concrete solid slab"),
    # WALLS
    ("wall",       "concrete"): _r("pr_20_93_85_14", "concrete solid wall and composite wall unit"),
    ("wall",       "$"):        _r("pr_20_93_96",    "walling units"),
    # FOUNDATIONS
    ("foundation", "concrete"): _r("pr_20_85_13_65", "concrete pocket foundations"),
    ("foundation", "$"):        _r("pr_20_85_13_30", "concrete floating slab foundation"),
    # REINFORCEMENT
    ("rebar",      "$"):        _r("pr_20_96_71_14", "carbon steel ribbed bar reinforcement"),
    ("mesh",       "$"):        _r("pr_20_96_71_97", "welded wire mesh reinforcement"),
}


def _pr_lookup(key, material):
    """Busca (key, material) y cae a (key, '$') si no existe."""
    return PR_STRUCTURAL.get((key, material)) or PR_STRUCTURAL.get((key, "$"))


def classify_pr(data, embedding_results):

    ifc = data.get("ifc_type", "").lower()
    name = (data.get("name") or "").lower()
    mat = data.get("material_category", "$") or "$"

    # -------------------------
    # 1. REGLAS → LOOKUP DIRECTO
    # -------------------------

    if ifc == "ifcbeam":
        if "plate" in name or "seat" in name:
            return _pr_lookup("beam_plate", "$")
        return _pr_lookup("beam", mat)

    if ifc == "ifccolumn":
        if "plate" in name:
            return _pr_lookup("column_plate", "$")
        return _pr_lookup("column", mat)

    if ifc == "ifcslab":
        return _pr_lookup("slab", mat)

    if ifc == "ifcwall":
        return _pr_lookup("wall", mat)

    if ifc == "ifcfooting":
        return _pr_lookup("foundation", mat)

    if ifc == "ifcreinforcingmesh":
        return _pr_lookup("mesh", "$")

    if ifc == "ifcreinforcingbar":
        return _pr_lookup("rebar", "$")

    # -------------------------
    # 2. REGLAS MEP
    # -------------------------

    if ifc == "ifcductsegment":
        if "flex" in name:
            return _r("pr_65_65_25_32", "flexible ductwork")
        if "circular" in name or "round" in name or "redondo" in name:
            return _r("pr_65_65_25_14", "circular sheet metal ductwork and fitting")
        return _r("pr_65_65_25_72", "rectangular sheet metal ductwork and fitting")

    if ifc == "ifcductfitting":
        return _r("pr_65_65_25", "ductwork and fitting")

    if ifc == "ifcairterminalbox":
        return _r("pr_70_65_04_94", "variable air volume (vav) terminal unit")

    if ifc == "ifcairterminal":
        pt = data.get("predefined_type", "").lower()
        if "diffuser" in pt:
            return _r("pr_70_65_04_02", "air diffuser")
        if "grille" in pt:
            return _r("pr_70_65_04_03", "air grille")
        return _r("pr_70_65_04", "air terminal and diffuser")

    if ifc == "ifcunitaryequipment":
        pt = data.get("predefined_type", "").lower()
        if "vrf" in pt or "variablerefrigerant" in pt:
            return _r("pr_70_65_03_94", "variable refrigerant flow (vrf) units")
        if "fancoil" in pt:
            return _r("pr_70_65_03_29", "fan coil units")
        if "airhandler" in pt or "ahu" in name:
            return _r("pr_60_65_03", "air-handling unit")
        # otros → embedding
        pass

    if ifc == "ifcfiresuppressionterminal":
        pt = data.get("predefined_type", "").lower()
        if "hosereel" in pt or "hose" in pt:
            return _r("pr_65_52_38_30", "fire hose reel")
        return _r("pr_70_55_97_84", "sprinkler head")

    if ifc == "ifcsensor":
        pt = data.get("predefined_type", "").lower()
        if "heat" in pt:
            return _r("pr_75_80_30_64", "point heat detector")
        return _r("pr_75_80_30_65", "point smoke detector")

    if ifc == "ifcfan":
        pt = data.get("predefined_type", "").lower()
        if "centrifugal" in pt:
            return _r("pr_65_67_29_12", "centrifugal fan")
        if "axial" in pt:
            return _r("pr_65_67_29_05", "axial flow fan")
        return _r("pr_65_67_29", "fan")

    if ifc == "ifcvalve":
        disc = data.get("discipline", "")
        pt = data.get("predefined_type", "").lower()
        if disc == "fire":
            return _r("pr_65_54_30_22", "deluge valve")
        if "butterfly" in pt:
            return _r("pr_65_54_95_08", "butterfly valve")
        if "gate" in pt or "isolating" in pt:
            return _r("pr_65_54_94_84", "steel gate valve")
        return _r("pr_65_54", "valve product")

    if ifc == "ifctank":
        return _r("pr_60_50_96", "water storage product")

    if ifc == "ifcpipesegment":
        if mat == "steel":
            return _r("pr_65_52_63_79", "stainless steel pipe fittings")
        return _r("pr_65_52", "pipe, tube and fitting product")

    if ifc == "ifcpipefitting":
        if mat == "steel":
            return _r("pr_65_52_63_83", "steel pipe fittings")
        return _r("pr_65_52_63", "pipe fitting product")

    # -------------------------
    # 3. REGLAS ELE
    # -------------------------

    if ifc in {"ifccablecarriersegment", "ifccablecarrierfitting"}:
        return _r("pr_65_70_11_17", "cable tray")

    if ifc == "ifcelectricdistributionboard":
        pt = data.get("predefined_type", "").lower()
        if "switchboard" in pt:
            return _r("pr_60_70_22_19", "cubicle switchboard")
        return _r("pr_60_70_22_22", "distribution boards")

    if ifc == "ifcjunctionbox":
        return _r("pr_65_70_11", "cable management and accessories")

    if ifc == "ifclightfixture":
        return _r("pr_70_70_48_01", "luminaire")

    # -------------------------
    # 4. REGLAS SAN
    # -------------------------

    if ifc == "ifcwasteterminal":
        return _r("pr_70_55_96", "wastewater outlets and plugs")

    if ifc in {"ifcflowterminal", "ifcsanitaryterminal"}:
        return _r("pr_40_20", "sanitary fitting product")

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

    return {"code": "pr_00", "text": "unknown", "confidence": 0.0, "source": "none"}
