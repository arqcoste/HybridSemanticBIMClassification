import ifcopenshell
from collections import defaultdict

from engine.ifc.ifc_feature_extractor import extract_ifc_features
from engine.semantic.semantic_translator import translate_to_ef_phrase

# IFC
ifc_path = r"C:\Users\USER\OneDrive\Documentos\Maestría\IFC PRACTICAS\WBZ-UNIBIM-XXX-IFC-EST-003.ifc"

model = ifcopenshell.open(ifc_path)
elements = model.by_type("IfcElement")

groups = defaultdict(list)

print("===== GENERATING GROUPS =====")

for e in elements:

    data = extract_ifc_features(e)
    phrase = translate_to_ef_phrase(data)

    groups[phrase].append(data)

# -------------------------
# RESULTADOS
# -------------------------
print("\n===== GROUP SUMMARY =====")

for phrase, items in groups.items():
    print(f"\nPHRASE: {phrase}")
    print(f"COUNT: {len(items)}")