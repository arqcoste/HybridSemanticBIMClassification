# -----------------------------------
# EF CLASSIFIER (DOMAIN-AWARE 🔥)
# -----------------------------------

def get_ef_candidates(data, domain):

    ifc = data.get("ifc_type", "").lower()

    # -------------------------
    # STRUCTURE DOMAIN
    # -------------------------
    if domain == "structure":

        STRUCTURAL = {
            "ifcbeam",
            "ifccolumn",
            "ifcmember",
            "ifcreinforcingbar",
            "ifcreinforcingmesh",
            "ifctendon",
            "ifctendonanchor"
        }

        SUBSTRUCTURE = {
            "ifcfooting",
            "ifcpile"
        }

        WALLS = {
            "ifcwall",
            "ifcwallstandardcase"
        }

        FLOORS = {
            "ifcslab",
            "ifcroof"
        }

        CONNECTIONS = {
            "ifcelementassembly",
            "ifcfastener"
        }

        if ifc in STRUCTURAL:
            return ["ef_20_10"]

        if ifc in SUBSTRUCTURE:
            return ["ef_20_05"]

        if ifc in WALLS:
            return ["ef_25_10"]

        if ifc in FLOORS:
            return ["ef_30_20"]

        if ifc in CONNECTIONS:
            return ["ef_20_10"]

    # -------------------------
    # MEP DOMAIN
    # -------------------------
    elif domain == "mep":

        return ["ef_70_00"]  # servicios / instalaciones

    # -------------------------
    # ARCH DOMAIN
    # -------------------------
    elif domain == "architecture":

        if "wall" in ifc:
            return ["ef_25_10"]

        if "door" in ifc or "window" in ifc:
            return ["ef_30_10"]

        return ["ef_30_00"]

    return ["ef_00"]