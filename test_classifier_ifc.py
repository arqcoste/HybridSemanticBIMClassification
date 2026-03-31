import ifcopenshell

from engine.ifc.ifc_feature_extractor import extract_ifc_features
from engine.semantic.multi_table_classifier import MultiTableClassifier
from engine.semantic.semantic_translator import build_semantic_phrases, translate_to_ef_phrase

# IFC
ifc_path = r"C:\Users\USER\OneDrive\Documentos\Maestría\IFC PRACTICAS\Tekla_muestra.ifc"

model = ifcopenshell.open(ifc_path)
elements = model.by_type("IfcElement")

classifier = MultiTableClassifier()

print("===== CLASSIFICATION RESULTS =====")

for e in elements[:10]:

    # 1. FEATURES
    data = extract_ifc_features(e)

    # 2. FRASE SEMÁNTICA 🔥
    phrase = translate_to_ef_phrase(data)

    print("\nPHRASE:", phrase)

    # 3. CLASIFICACIÓN
    phrases = build_semantic_phrases(data)

    ef_res = classifier.classify(phrases["EF"])
    ss_res = classifier.classify(phrases["SS"])
    pr_res = classifier.classify(phrases["PR"])