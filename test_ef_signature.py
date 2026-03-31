import ifcopenshell

from engine.ifc.ifc_feature_extractor import extract_ifc_features
from engine.semantic.ef_signature_builder import build_ef_ae_signature

ifc_path = r"C:\Users\USER\OneDrive\Documentos\Maestría\IFC PRACTICAS\Tekla_muestra.ifc"

model = ifcopenshell.open(ifc_path)

elements = model.by_type("IfcElement")

print("----- EF SIGNATURES -----")

for e in elements[:10]:
    data = extract_ifc_features(e)
    sig = build_ef_ae_signature(data)

    print(sig)

    from engine.ifc.ifc_feature_extractor import extract_ifc_features
from engine.semantic.ef_signature_builder import build_ef_ae_signature

for e in elements[:5]:

    data = extract_ifc_features(e)

    sig = build_ef_ae_signature(data)

    print(sig)