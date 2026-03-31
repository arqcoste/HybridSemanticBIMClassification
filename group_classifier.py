import ifcopenshell
import csv

from engine.semantic.group_phrases import group_elements
from engine.semantic.embedding_classifier import EmbeddingClassifier

from engine.rules.domain_classifier import detect_domain_from_ifc
from engine.rules.ef_classifier import get_ef_candidates
from engine.rules.pr_classifier import classify_pr

from engine.semantic.semantic_translator import (
    build_phrase_ss,
    build_phrase_pr
)

# -------------------------
# 1. IFC
# -------------------------

ifc_path = r"C:\Users\USER\OneDrive\Documentos\Maestría\IFC PRACTICAS\WBZ-UNIBIM-XXX-IFC-EST-003.ifc"

print("🔹 Abriendo IFC...")
model = ifcopenshell.open(ifc_path)
elements = model.by_type("IfcElement")

print(f"🔹 Elementos encontrados: {len(elements)}")

# -------------------------
# 2. DOMAIN
# -------------------------

domain = detect_domain_from_ifc(elements)

# -------------------------
# 3. GROUPS
# -------------------------

print("\n===== GENERATING GROUPS =====")
groups = group_elements(elements)

print(f"🔹 Número de grupos: {len(groups)}")

# -------------------------
# 4. CLASSIFIERS
# -------------------------

print("\n🔹 Cargando clasificadores...")

classifier_ss = EmbeddingClassifier(
    model_path="models/construction_embedding_model",
    vectors_path="data/processed/ss_vectors.npy",
    metadata_path="data/processed/ss_metadata.json"
)

classifier_pr = EmbeddingClassifier(
    model_path="models/construction_embedding_model",
    vectors_path="data/processed/pr_vectors.npy",
    metadata_path="data/processed/pr_metadata.json"
)

# -------------------------
# 5. FILTER SKIP
# -------------------------

def should_skip_element(data, ef_candidates):

    # 1. EF inválido
    if not ef_candidates or ef_candidates == ["ef_00"]:
        return True

    ifc = data.get("ifc_type", "").lower()

    IFC_IGNORE = {
        "ifcopeningelement",
        "ifcspace",
        "ifcvirtualelement",
        "ifcannotation",
        "ifcelementassembly"  # 🔥 AÑADIDO
    }

    if ifc in IFC_IGNORE:
        return True

    return False

# -------------------------
# 6. CLASSIFICATION
# -------------------------

results = []

print("\n===== GROUP CLASSIFICATION =====")

for phrase, items in groups.items():

    print("\n---------------------------")
    print("PHRASE:", phrase)
    print("COUNT:", len(items))

    data = items[0]

    # -------------------------
    # EF
    # -------------------------

    ef_candidates = get_ef_candidates(data, domain)

    if should_skip_element(data, ef_candidates):
        print("⛔ SKIPPED")
        continue

    ef_main = ef_candidates[0]

    print("\n--- EF ---")
    print(ef_candidates)

    # -------------------------
    # SS
    # -------------------------

    phrase_ss = build_phrase_ss(data)

    ss_results = classifier_ss.classify(phrase_ss, top_k=3)

    print("\n--- SS ---")
    for r in ss_results:
        print(r)

    # -------------------------
    # PR (🔥 FINAL)
    # -------------------------

    phrase_pr = build_phrase_pr(data)

    pr_raw = classifier_pr.classify(
        phrase_pr,
        top_k=5,
        ef=ef_main,
        data=data
    )

    pr_final = classify_pr(data, pr_raw)

    print("\n--- PR FINAL ---")
    print(pr_final)

    # -------------------------
    # SAVE CSV
    # -------------------------

    results.append({
        "phrase": phrase,
        "count": len(items),
        "domain": domain,
        "ef_candidates": ",".join(ef_candidates),
        "ss_top1": ss_results[0]["code"] if ss_results else "",
        "pr_top1": pr_final["code"]
    })

# -------------------------
# 7. EXPORT CSV
# -------------------------

csv_path = "classification_results_final.csv"

with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "phrase", "count", "domain",
        "ef_candidates", "ss_top1", "pr_top1"
    ])

    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ CSV guardado en: {csv_path}")