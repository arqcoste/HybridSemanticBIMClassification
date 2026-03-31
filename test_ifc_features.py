import ifcopenshell
from engine.ifc.ifc_feature_extractor import extract_ifc_features

ifc_path = r"C:\Users\USER\OneDrive\Documentos\Maestría\IFC PRACTICAS\Tekla_muestra.ifc"

model = ifcopenshell.open(ifc_path)

elements = model.by_type("IfcElement")

print("----- IFC FEATURES -----")

for e in elements[:10]:
    data = extract_ifc_features(e)
    print(data)