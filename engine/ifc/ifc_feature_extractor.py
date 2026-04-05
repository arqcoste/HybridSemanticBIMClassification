import re

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

    if "steel" in mat or "acero" in mat:
        return "steel"

    # Grados de acero: S235/S275/S355, A36/A572, 350W/400W, Gr50/Gr60
    if re.search(r'\bs\d{3}', mat) or re.search(r'\ba\d{2,3}\b', mat):
        return "steel"
    if re.search(r'\b\d{3}w\b', mat):   # 350W, 300W, 400W (CAN/CSA)
        return "steel"
    if re.search(r'\bgr\s?\d{2}', mat): # Gr50, Gr 60
        return "steel"

    if "concrete" in mat or "hormig" in mat:
        return "concrete"

    # Grados de hormigón: C20/C25/C30/C35/C40/C45/C50 o fc=3000 psi (2000–9000)
    if re.search(r'\bc\d{2}', mat):
        return "concrete"
    if re.search(r'\b[2-9]\d{3}\b', mat):  # 3000, 4000, 5000 psi
        return "concrete"

    if "wood" in mat or "timber" in mat or "madera" in mat:
        return "wood"

    return "$"


def _extract_material_name(mat):
    """Extrae el nombre de material sea cual sea el tipo IFC."""
    try:
        ifc_type = mat.is_a()

        # Caso simple
        if ifc_type == "IfcMaterial":
            return mat.Name or "$"

        # IfcMaterialProfileSetUsage → ForProfileSet → MaterialProfiles
        if ifc_type == "IfcMaterialProfileSetUsage":
            for profile in mat.ForProfileSet.MaterialProfiles or []:
                if profile.Material:
                    return profile.Material.Name or "$"

        # IfcMaterialLayerSetUsage → ForLayerSet → MaterialLayers
        if ifc_type == "IfcMaterialLayerSetUsage":
            for layer in mat.ForLayerSet.MaterialLayers or []:
                if layer.Material:
                    return layer.Material.Name or "$"

        # IfcMaterialLayerSet directo
        if ifc_type == "IfcMaterialLayerSet":
            for layer in mat.MaterialLayers or []:
                if layer.Material:
                    return layer.Material.Name or "$"

        # IfcMaterialConstituentSet
        if ifc_type == "IfcMaterialConstituentSet":
            for constituent in mat.MaterialConstituents or []:
                if constituent.Material:
                    return constituent.Material.Name or "$"

        # IfcMaterialList
        if ifc_type == "IfcMaterialList":
            for m in mat.Materials or []:
                return m.Name or "$"

        # Fallback: intentar .Name directamente
        return getattr(mat, "Name", None) or "$"

    except Exception:
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
                material = _extract_material_name(mat)

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