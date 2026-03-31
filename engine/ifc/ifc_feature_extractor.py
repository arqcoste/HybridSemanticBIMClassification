import ifcopenshell

# -----------------------------------
# HELPERS
# -----------------------------------

def safe_value(val):
    if val is None or val == "" or val == "NOTDEFINED":
        return "$"
    return str(val).lower()


def categorize_material(mat):

    if mat == "$":
        return "$"

    mat = mat.lower()

    if "steel" in mat or "s2" in mat or "s3" in mat:
        return "steel"

    if "concrete" in mat or "c2" in mat or "c3" in mat:
        return "concrete"

    if "wood" in mat or "timber" in mat:
        return "wood"

    return "$"


def get_pset_property(elem, pset_name, prop_name):

    if hasattr(elem, "IsDefinedBy"):
        for rel in elem.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):

                pset = rel.RelatingPropertyDefinition

                if pset.Name == pset_name:

                    for prop in pset.HasProperties:
                        if prop.Name == prop_name:
                            try:
                                return str(prop.NominalValue.wrappedValue).lower()
                            except:
                                return "$"

    return "$"


# -----------------------------------
# 🔥 SYSTEM / ASSEMBLY
# -----------------------------------

def get_system_role(elem):

    if hasattr(elem, "HasAssignments"):
        for rel in elem.HasAssignments:
            if rel.is_a("IfcRelAssignsToGroup"):
                return "system"

    return "$"


def get_assembly_context(elem):

    if hasattr(elem, "Decomposes"):
        for rel in elem.Decomposes:
            if rel.is_a("IfcRelAggregates"):
                parent = rel.RelatingObject

                if parent.is_a("IfcElementAssembly"):
                    return "assembly"

    return "$"


# -----------------------------------
# 🔥 CONNECTIONS (CLAVE)
# -----------------------------------

VALID_CONNECTIONS = [
    "ifcbeam",
    "ifccolumn",
    "ifcslab",
    "ifcwall",
    "ifcfooting"
]


def get_connected_elements(elem):

    connected = []

    # conexiones hacia otros
    if hasattr(elem, "ConnectedTo"):
        for rel in elem.ConnectedTo:
            try:
                other = rel.RelatedElement
                if other:
                    connected.append(other.is_a().lower())
            except:
                continue

    # conexiones desde otros
    if hasattr(elem, "ConnectedFrom"):
        for rel in elem.ConnectedFrom:
            try:
                other = rel.RelatingElement
                if other:
                    connected.append(other.is_a().lower())
            except:
                continue

    # limpiar + filtrar
    clean = []

    for c in connected:
        if c in VALID_CONNECTIONS:
            c = c.replace("ifc", "")
            if c not in clean:
                clean.append(c)

    return clean if clean else ["$"]


# -----------------------------------
# MAIN EXTRACTOR
# -----------------------------------

def extract_ifc_features(elem):

    data = {}

    # -------------------------
    # 1. IFC TYPE
    # -------------------------
    data["ifc_type"] = safe_value(elem.is_a())

    # -------------------------
    # 2. PREDEFINED TYPE
    # -------------------------
    data["predefined_type"] = safe_value(
        getattr(elem, "PredefinedType", None)
    )

    # -------------------------
    # 3. NAME
    # -------------------------
    data["name"] = safe_value(
        getattr(elem, "Name", None)
    )

    # -------------------------
    # 4. MATERIAL
    # -------------------------
    material = "$"

    if hasattr(elem, "HasAssociations"):
        for rel in elem.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):

                mat = rel.RelatingMaterial

                try:
                    material = mat.Name
                except:
                    material = str(mat)

    raw_mat = safe_value(material)

    data["material_raw"] = raw_mat
    data["material_category"] = categorize_material(raw_mat)

    # -------------------------
    # 5. SPATIAL (LEVEL)
    # -------------------------
    spatial = "$"

    if hasattr(elem, "ContainedInStructure"):
        for rel in elem.ContainedInStructure:
            structure = rel.RelatingStructure
            spatial = getattr(structure, "Name", None)

    data["spatial"] = safe_value(spatial)

    # -------------------------
    # 6. TYPE OBJECT
    # -------------------------
    type_obj = "$"

    if hasattr(elem, "IsTypedBy"):
        for rel in elem.IsTypedBy:
            type_obj = rel.RelatingType.Name

    data["type_object"] = safe_value(type_obj)

    # -------------------------
    # 7. PROPERTIES
    # -------------------------
    data["load_bearing"] = safe_value(
        get_pset_property(elem, "Pset_BuildingElementCommon", "LoadBearing")
    )

    data["is_external"] = safe_value(
        get_pset_property(elem, "Pset_BuildingElementCommon", "IsExternal")
    )

    # -------------------------
    # 8. SYSTEM
    # -------------------------
    data["system_role"] = get_system_role(elem)

    # -------------------------
    # 9. 🔥 ASSEMBLY CONTEXT
    # -------------------------
    data["assembly_context"] = get_assembly_context(elem)

    # -------------------------
    # 10. 🔥 CONNECTED ELEMENTS
    # -------------------------
    data["connected_to"] = get_connected_elements(elem)

    return data