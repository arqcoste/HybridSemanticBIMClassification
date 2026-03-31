# -----------------------------------
# CLEAN SEMANTIC TRANSLATOR
# -----------------------------------

def detect_element(data):

    ifc = data.get("ifc_type", "").lower()

    mapping = {
        "ifcbeam": "beam",
        "ifccolumn": "column",
        "ifcslab": "slab",
        "ifcwall": "wall",
        "ifcfooting": "foundation",
        "ifcreinforcingbar": "reinforcement",
        "ifcreinforcingmesh": "reinforcement"
    }

    return mapping.get(ifc, "$")


# -----------------------------------
# FRASE EF
# -----------------------------------

def build_phrase_ef(data):

    ifc = data.get("ifc_type", "")
    material = data.get("material_category", "")
    load = data.get("load_bearing", "")

    parts = [ifc]

    if material != "$":
        parts.append(material)

    if load == "true":
        parts.append("structural")

    return " ".join(parts)


# -----------------------------------
# FRASE SS
# -----------------------------------

def build_phrase_ss(data):

    element = detect_element(data)

    parts = []

    if element != "$":
        parts.append(element)

    parts.append("system")

    if data.get("connected_to") and data["connected_to"] != ["$"]:
        parts.append("connected")

    return " ".join(parts)


# -----------------------------------
# FRASE PR
# -----------------------------------

def build_phrase_pr(data):

    element = detect_element(data)
    material = data.get("material_category", "")
    name = data.get("name", "")

    parts = []

    if material != "$":
        parts.append(material)

    if element != "$":
        parts.append(element)

    if name and name != "$":
        parts.append(name)

    return " ".join(parts)