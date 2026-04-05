# -----------------------------------
# EF CLASSIFIER (DOMAIN-AWARE 🔥)
# -----------------------------------

# -------------------------
# HELPERS
# -------------------------

def _is_steel(data):
    return data.get("material_category", "") == "steel"

def _is_concrete(data):
    return data.get("material_category", "") == "concrete"

def _is_external(data):
    return data.get("is_external", "") == "true"

def _spatial_level(data):
    """Devuelve el nivel espacial normalizado en minúsculas."""
    return (data.get("spatial", "") or "").lower()

def _is_basement(data):
    level = _spatial_level(data)
    return any(k in level for k in ["b1", "b2", "b3", "basement", "sotano", "s1", "s2", "planta -"])

def _is_ground(data):
    level = _spatial_level(data)
    return any(k in level for k in ["p0", "ground", "planta 0", "pb", "baja", "level 0", "00"])


# -------------------------
# SUPERSTRUCTURE (ef_20_10)
# -------------------------

def _classify_superstructure(data):
    """
    ef_20_10_15  Composite structures  → acero + hormigón combinados
    ef_20_10_30  Framed structures     → acero o hormigón armado
    ef_20_10_80  Solid structures      → hormigón macizo / muros
    """
    ifc = data.get("ifc_type", "").lower()

    # Muros de hormigón → solid
    if ifc in ("ifcwall", "ifcwallstandardcase"):
        if _is_concrete(data):
            return "ef_20_10_80"
        return "ef_20_10_30"

    # Losas → framed (generalmente)
    if ifc == "ifcslab":
        if _is_concrete(data):
            return "ef_20_10_80"
        return "ef_20_10_30"

    # Vigas y columnas → framed (acero o HA)
    if _is_steel(data) or _is_concrete(data):
        return "ef_20_10_30"

    # Sin material conocido → nivel genérico
    return "ef_20_10"


# -------------------------
# WALLS (ef_25_10)
# -------------------------

def _classify_wall(data):
    """
    ef_25_10_25  External walls
    ef_25_10_27  External walls below DPC
    ef_25_10_28  External walls below ground
    ef_25_10_40  Internal walls
    """
    if _is_external(data):
        if _is_basement(data):
            return "ef_25_10_28"
        return "ef_25_10_25"

    return "ef_25_10_40"


# -------------------------
# FLOORS (ef_30_20)
# -------------------------

def _classify_floor(data):
    """
    ef_30_20_06  Basement floors
    ef_30_20_34  Ground floors
    ef_30_20_52  Mezzanine floors  (sin info → fallback)
    ef_30_20_93  Upper floors
    """
    if _is_basement(data):
        return "ef_30_20_06"
    if _is_ground(data):
        return "ef_30_20_34"
    # Si hay nivel espacial definido asumimos planta alta
    if _spatial_level(data) not in ("", "$"):
        return "ef_30_20_93"
    return "ef_30_20"


# -------------------------
# MAIN CLASSIFIER
# -------------------------

def get_ef_candidates(data, domain):

    ifc = data.get("ifc_type", "").lower()

    # -------------------------
    # STRUCTURE DOMAIN
    # -------------------------
    if domain == "structure":

        STRUCTURAL = {
            "ifcbeam", "ifccolumn", "ifcmember",
            "ifcreinforcingbar", "ifcreinforcingmesh",
            "ifctendon", "ifctendonanchor"
        }

        SUBSTRUCTURE = {"ifcfooting", "ifcpile"}

        WALLS = {"ifcwall", "ifcwallstandardcase"}

        FLOORS = {"ifcslab", "ifcroof"}

        CONNECTIONS = {"ifcelementassembly", "ifcfastener"}

        if ifc in STRUCTURAL:
            return [_classify_superstructure(data)]

        if ifc in SUBSTRUCTURE:
            return ["ef_20_05_30"]   # Foundations (nivel 3 directo)

        if ifc in WALLS:
            return [_classify_wall(data)]

        if ifc in FLOORS:
            return [_classify_floor(data)]

        if ifc in CONNECTIONS:
            return [_classify_superstructure(data)]

    # -------------------------
    # MEP DOMAIN
    # -------------------------
    elif domain == "mep":

        # Helper: detecta sistema de incendios por disciplina o por nombre
        def _is_fire(d):
            if d.get("discipline", "") == "fire":
                return True
            name = (d.get("name", "") or "").lower()
            return any(k in name for k in ["pci", "fire", "sprinkler", "suppression", "incendio"])

        # Conductos HVAC → Ventilation
        if ifc in {"ifcductsegment", "ifcductfitting"}:
            return ["ef_65_40"]

        # Caja de caudal variable → Air conditioning
        if ifc == "ifcairterminalbox":
            return ["ef_65_80"]

        # Difusor / rejilla → Ventilation; VAV → Air conditioning
        if ifc == "ifcairterminal":
            pt = data.get("predefined_type", "").lower()
            if "vav" in pt or "variableflow" in pt:
                return ["ef_65_80"]
            return ["ef_65_40"]

        # Climatizadores → Air conditioning
        if ifc in {"ifcunitaryequipment", "ifccoil", "ifchumidifier"}:
            return ["ef_65_80"]

        # Ventiladores → Ventilation
        if ifc == "ifcfan":
            return ["ef_65_40"]

        # Terminales de supresión de incendios → Safety and protection
        if ifc == "ifcfiresuppressionterminal":
            return ["ef_75_50"]

        # Sensores → Safety and protection
        if ifc == "ifcsensor":
            return ["ef_75_50"]

        disc = data.get("discipline", "")

        # Tuberías y accesorios: fuego → ef_75_50, SAN → ef_55_70_38, HVAC → ef_60_40
        if ifc in {"ifcpipesegment", "ifcpipefitting"}:
            if _is_fire(data):
                return ["ef_75_50"]
            if disc == "sanitary":
                return ["ef_55_70_38"]
            return ["ef_60_40"]

        # Válvulas, bombas, depósitos: fuego → ef_75_50, SAN → ef_55_70_38, HVAC → ef_60_40
        if ifc in {"ifcvalve", "ifcpump", "ifctank"}:
            if _is_fire(data):
                return ["ef_75_50"]
            if disc == "sanitary":
                return ["ef_55_70_38"]
            return ["ef_60_40"]

        # --- ELE: distribución eléctrica ---
        if ifc in {"ifcelectricdistributionboard", "ifcelectricflowstoragedevice"}:
            return ["ef_70_30_45"]   # Low-voltage electricity distribution

        # Bandejas y canalizaciones → Cable management
        if ifc in {"ifccablecarriersegment", "ifccablecarrierfitting"}:
            return ["ef_70_30_10"]   # Cable management

        # Cajas de paso → Small power supply
        if ifc == "ifcjunctionbox":
            return ["ef_70_30_80"]   # Small power supply

        # Luminarias → General space lighting
        if ifc == "ifclightfixture":
            return ["ef_70_80_33"]   # General space lighting

        # Terminales sanitarias → Water supply
        if ifc in {"ifcflowterminal", "ifcsanitaryterminal"}:
            return ["ef_55_70_38"]   # Hot and cold water supply

        # Desagüe → Above-ground drainage
        if ifc == "ifcwasteterminal":
            return ["ef_50_30_34"]   # Gravity above-ground drainage

        return ["ef_70"]  # fallback genérico MEP

    # -------------------------
    # ARCH DOMAIN
    # -------------------------
    elif domain == "architecture":

        if "wall" in ifc:
            return [_classify_wall(data)]

        if "door" in ifc:
            return ["ef_25_30_25"]   # Doors

        if "window" in ifc:
            return ["ef_25_30_97"]   # Windows

        return ["ef_30"]

    return ["ef_00"]
