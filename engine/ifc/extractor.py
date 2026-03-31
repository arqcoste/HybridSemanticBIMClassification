import ifcopenshell

def extract_elements(ifc_path):

    model = ifcopenshell.open(ifc_path)

    elements = []

    for elem in model.by_type("IfcElement"):

        data = {}

        data["guid"] = elem.GlobalId
        data["ifc_type"] = elem.is_a()
        data["name"] = getattr(elem, "Name", None)
        data["description"] = getattr(elem, "Description", None)

        material = None

        if hasattr(elem, "HasAssociations"):
            for rel in elem.HasAssociations:
                if rel.is_a("IfcRelAssociatesMaterial"):
                    material = str(rel.RelatingMaterial)

        data["material"] = material

        elements.append(data)

    return elements