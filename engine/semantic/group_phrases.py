# -----------------------------------
# GROUP ELEMENTS (CLEAN VERSION 🔥)
# -----------------------------------

from collections import defaultdict
from engine.ifc.ifc_feature_extractor import extract_ifc_features


def build_group_key(data):
    """
    Genera una clave simple para agrupar elementos
    (sin lógica semántica compleja)
    """

    ifc = data.get("ifc_type", "")
    material = data.get("material_category", "")
    type_obj = data.get("type_object", "")

    parts = [ifc]

    if material != "$":
        parts.append(material)

    if type_obj != "$":
        parts.append(type_obj)

    return " | ".join(parts)


def group_elements(elements):

    groups = defaultdict(list)

    print("\n===== GENERATING GROUPS =====")

    for elem in elements:

        # 🔥 EXTRAER FEATURES (CLAVE)
        data = extract_ifc_features(elem)

        key = build_group_key(data)

        if not key:
            continue

        groups[key].append(data)

    print(f"🔹 Número de grupos: {len(groups)}")

    return groups