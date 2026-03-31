from engine.ifc.extractor import extract_elements
from engine.semantic.signature_builder import build_signature

ifc_path = r"C:\Users\USER\OneDrive\Documentos\Maestría\IFC PRACTICAS\Tekla_muestra.ifc"

elements = extract_elements(ifc_path)

print("----- ELEMENTOS -----")
for e in elements[:5]:
    print(e)

print("\n----- SIGNATURES -----")
for e in elements[:5]:
    sig = build_signature(e)
    print("SIGNATURE:", sig)