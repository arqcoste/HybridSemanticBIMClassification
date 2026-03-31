from sentence_transformers import SentenceTransformer
import numpy as np
import json

print("🚀 Script iniciado")

# -----------------------------------
# 1. CARGAR TU MODELO 🔥
# -----------------------------------
model = SentenceTransformer("models/construction_embedding_model")


# -----------------------------------
# 2. CARGAR SYNONYMS
# -----------------------------------
def load_synonyms(file_path):
    data = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")

            code = parts[0].strip()
            terms = [p.strip() for p in parts[1:]]

            for term in terms:
                if term:
                    data.append({
                        "code": code,
                        "text": term
                    })

    return data


# -----------------------------------
# 3. CARGAR ARCHIVOS
# -----------------------------------
ss_data = load_synonyms("data/raw/ss_synonyms_clean.txt")
ef_data = load_synonyms("data/raw/ef_synonyms_clean.txt")
pr_data = load_synonyms("data/raw/pr_synonyms_clean.txt")

print("SS:", len(ss_data))
print("EF:", len(ef_data))
print("PR:", len(pr_data))
# -----------------------------------
# 4. UNIFICAR
# -----------------------------------
all_data = ss_data + ef_data + pr_data

texts = [item["text"] for item in all_data]

print("Total textos:", len(texts))
# -----------------------------------
# 5. GENERAR EMBEDDINGS 🔥
# -----------------------------------
vectors = model.encode(texts, show_progress_bar=True)


# -----------------------------------
# 6. GUARDAR
# -----------------------------------
np.save("data/processed/domain_vectors.npy", vectors)

with open("data/processed/domain_metadata.json", "w") as f:
    json.dump(all_data, f, indent=2)


print("✅ Embeddings generados correctamente")