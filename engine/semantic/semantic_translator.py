# -----------------------------------
# CLEAN SEMANTIC TRANSLATOR
# -----------------------------------

def detect_element(data):

    ifc = data.get("ifc_type", "").lower()

    mapping = {
        # --- structural ---
        "ifcbeam":            "beam",
        "ifccolumn":          "column",
        "ifcslab":            "slab",
        "ifcwall":            "wall",
        "ifcfooting":         "foundation",
        "ifcreinforcingbar":  "reinforcement",
        "ifcreinforcingmesh": "reinforcement",
        # --- MEP: HVAC ---
        "ifcductsegment":       "duct",
        "ifcductfitting":       "duct fitting",
        "ifcairterminal":       "air terminal",
        "ifcairterminalbox":    "vav terminal",
        "ifcunitaryequipment":  "air handling unit",
        "ifcfan":               "fan",
        "ifccoil":              "coil",
        "ifchumidifier":        "humidifier",
        # --- MEP: piping ---
        "ifcpipesegment":  "pipe",
        "ifcpipefitting":  "pipe fitting",
        "ifcvalve":        "valve",
        "ifcpump":         "pump",
        "ifctank":         "tank",
        # --- MEP: fire / safety ---
        "ifcfiresuppressionterminal": "fire suppression",
        "ifcsensor":                  "smoke detector",
        "ifcalarm":                   "fire alarm",
        # --- ELE ---
        "ifccablecarriersegment":     "cable tray",
        "ifccablecarrierfitting":     "cable tray fitting",
        "ifcelectricdistributionboard": "distribution board",
        "ifcjunctionbox":             "junction box",
        "ifclightfixture":            "luminaire",
        # --- SAN ---
        "ifcwasteterminal":           "floor waste",
        "ifcflowterminal":            "sanitary terminal",
        "ifcsanitaryterminal":        "sanitary fitting",
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
# HELPERS COMPARTIDOS
# -----------------------------------

# predefined_type values genéricos que no aportan info extra (ya cubiertos por el element)
_PT_SKIP = {
    "$", "notdefined", "userdefined",
    # structural generics
    "beam", "column", "slab", "wall", "footing",
    # MEP generics (redundante con el nombre del elemento)
    "pipe", "duct", "valve", "pump", "tank", "fan", "sensor",
    "rigidsegment", "connector", "cabletraysegment",
    # fitting/segment generics
    "entry", "exit", "transition", "bend", "tee",
}

# Predefined types compuestos → extraer solo la primera palabra significativa
_PT_SIMPLIFY = {
    "centrifugalbackwardinclinedcurved": "centrifugal",
    "centrifugalforwardcurved":          "centrifugal",
    "axialflow":                         "axial",
    "variableflowpressuredependant":     "variable flow",
    "variableflowpressureindependant":   "variable flow",
    "smokeandheatvent":                  "smoke heat",
    "naturaldraft":                      "natural draft",
    "mechanicaldraft":                   "mechanical draft",
    "airconditioningunit":               "air conditioning unit",
}

def _predefined_qualifier(data):
    """Devuelve el predefined_type normalizado si aporta info útil."""
    pt = (data.get("predefined_type", "") or "").lower().strip()
    if pt in _PT_SKIP:
        return ""
    # Simplificar compuestos verbosos
    if pt in _PT_SIMPLIFY:
        return _PT_SIMPLIFY[pt]
    return pt.replace("_", " ")


# -----------------------------------
# FRASE SS
# -----------------------------------

def _material_qualifier(data):
    """
    Devuelve el calificador de material para la frase SS.
    Acero estructural (perfiles laminados) → 'heavy steel'
    Hormigón armado                         → 'reinforced concrete'
    Sin material conocido                   → ''
    """
    mat = data.get("material_category", "")
    if mat == "steel":
        return "heavy steel"
    if mat == "concrete":
        return "reinforced concrete"
    return ""


def _mep_qualifier(data):
    """
    Devuelve el calificador de contexto MEP para la frase SS.
    Permite que el embedding encuentre sistemas MEP específicos.
    """
    ifc = data.get("ifc_type", "").lower()
    pt  = (data.get("predefined_type", "") or "").lower()
    name = (data.get("name", "") or "").lower()

    # Fire / PCI context: disciplina del modelo o keywords en el nombre
    fire_keywords = ("pci", "fire", "sprinkler", "suppression", "incendio")
    is_fire = data.get("discipline", "") == "fire" or any(k in name for k in fire_keywords)

    if ifc in {"ifcductsegment", "ifcductfitting"}:
        return "mechanical ventilation"

    if ifc == "ifcairterminalbox":
        return "variable air volume air conditioning"

    if ifc == "ifcairterminal":
        if "vav" in pt or "variableflow" in pt:
            return "variable air volume air conditioning"
        return "ventilation"

    if ifc in {"ifcunitaryequipment", "ifccoil", "ifchumidifier"}:
        return "air conditioning"

    if ifc == "ifcfan":
        return "mechanical ventilation"

    if ifc == "ifcfiresuppressionterminal":
        return "water fire suppression"

    if ifc == "ifcsensor":
        if "smoke" in pt or "heat" in pt:
            return "fire smoke detection"
        return "fire smoke detection"

    if ifc in {"ifcpipesegment", "ifcpipefitting"}:
        if is_fire:
            return "water fire suppression"
        return "heating cooling water"  # → "heating cooling water pipe system"

    if ifc in {"ifcvalve", "ifcpump", "ifctank"}:
        if is_fire:
            return "water fire suppression"
        disc = data.get("discipline", "")
        if disc == "sanitary":
            return "hot cold water supply"
        return "heating cooling"

    # ELE
    if ifc in {"ifccablecarriersegment", "ifccablecarrierfitting"}:
        return "low-voltage cable management"

    if ifc == "ifcelectricdistributionboard":
        return "low-voltage electricity distribution"

    if ifc == "ifcjunctionbox":
        return "small power supply"

    if ifc == "ifclightfixture":
        return "general space lighting"

    # SAN
    if ifc in {"ifcpipesegment", "ifcpipefitting"} and data.get("discipline", "") == "sanitary":
        return "hot cold water supply"

    if ifc == "ifcwasteterminal":
        return "wastewater drainage"

    if ifc in {"ifcflowterminal", "ifcsanitaryterminal"}:
        return "sanitary appliance"

    return ""


def build_phrase_ss(data):

    element = detect_element(data)

    # MEP elements use domain-context qualifier; structural use material qualifier
    ifc = data.get("ifc_type", "").lower()
    MEP_TYPES = {
        "ifcductsegment", "ifcductfitting", "ifcairterminal", "ifcairterminalbox",
        "ifcunitaryequipment", "ifcfan", "ifccoil", "ifchumidifier",
        "ifcpipesegment", "ifcpipefitting", "ifcvalve", "ifcpump", "ifctank",
        "ifcfiresuppressionterminal", "ifcsensor", "ifcalarm",
        "ifccablecarriersegment", "ifccablecarrierfitting",
        "ifcelectricdistributionboard", "ifcjunctionbox", "ifclightfixture",
        "ifcwasteterminal", "ifcflowterminal", "ifcsanitaryterminal",
    }
    if ifc in MEP_TYPES:
        qualifier = _mep_qualifier(data)
    else:
        qualifier = _material_qualifier(data)

    parts = []

    if qualifier:
        parts.append(qualifier)

    # predefined_type informativo (e.g. "strip footing", "solid wall")
    pt = _predefined_qualifier(data)
    if pt:
        parts.append(pt)

    if element != "$":
        parts.append(element)

    # load_bearing: refuerza que es sistema estructural portante
    if data.get("load_bearing") == "true":
        parts.append("load-bearing")

    # is_external: distingue sistema de fachada vs interior
    if data.get("is_external") == "true":
        parts.append("external")

    parts.append("system")

    if data.get("connected_to") and data["connected_to"] != ["$"]:
        parts.append("connected")

    return " ".join(parts)


# -----------------------------------
# FRASE PR
# -----------------------------------

def _clean_name_for_phrase(raw):
    """Strip del sufijo de ID de instancia IFC (e.g. 'BeamType:571431' → 'BeamType')."""
    if not raw or raw == "$":
        return ""
    parts = raw.rsplit(":", 1)
    if len(parts) == 2 and parts[1].strip().isdigit():
        raw = parts[0].strip()
    return raw


def build_phrase_pr(data):

    element = detect_element(data)
    material = data.get("material_category", "")
    name = _clean_name_for_phrase(data.get("name", ""))

    parts = []

    if material != "$":
        parts.append(material)

    # predefined_type informativo antes del elemento
    pt = _predefined_qualifier(data)
    if pt:
        parts.append(pt)

    if element != "$":
        parts.append(element)

    # load_bearing: producto estructural portante
    if data.get("load_bearing") == "true":
        parts.append("structural")

    # is_external: producto de fachada/exterior
    if data.get("is_external") == "true":
        parts.append("external")

    if name:
        parts.append(name)

    return " ".join(parts)