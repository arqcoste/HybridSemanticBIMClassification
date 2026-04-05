# -----------------------------------
# DOMAIN CLASSIFIER (IFC-BASED 🔥)
# -----------------------------------

def detect_domain_from_ifc(elements):

    counts = {
        "structure": 0,
        "mep": 0,
        "architecture": 0
    }

    # -------------------------
    # LISTAS ONTOLÓGICAS
    # -------------------------

    STRUCTURAL = {
        "ifcbeam",
        "ifccolumn",
        "ifcmember",
        "ifcfooting",
        "ifcpile",
        "ifcslab",
        "ifcreinforcingbar",
        "ifcreinforcingmesh",
        "ifctendon",
        "ifctendonanchor"
    }

    MEP = {
        "ifcflowsegment",
        "ifcflowfitting",
        "ifcflowterminal",
        "ifcflowcontroller",
        "ifcflowstorage",
        "ifcflowmovingdevice",
        "ifcflowtreatmentdevice",
        "ifcflowmeter",
        "ifcductsegment",
        "ifcpipesegment",
        "ifccablecarriersegment"
    }

    ARCH = {
        "ifcwall",
        "ifcwallstandardcase",
        "ifcdoor",
        "ifcwindow",
        "ifccovering",
        "ifccurtainwall",
        "ifcroof",
        "ifcspace"
    }

    # -------------------------
    # CONTAR
    # -------------------------

    for elem in elements:
        ifc = elem.is_a().lower()

        if ifc in STRUCTURAL:
            counts["structure"] += 1
        elif ifc in MEP:
            counts["mep"] += 1
        elif ifc in ARCH:
            counts["architecture"] += 1

    # -------------------------
    # DECISIÓN
    # -------------------------

    print("\n🔹 DOMAIN DETECTION:")
    print(counts)

    if max(counts.values()) == 0:
        print("⚠️  No se reconoció ningún tipo IFC — dominio por defecto: architecture")
        return "architecture"

    domain = max(counts, key=counts.get)
    print("➡️ Dominio detectado:", domain)

    return domain