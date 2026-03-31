from sentence_transformers import SentenceTransformer
import numpy as np
import json


model = SentenceTransformer("models/construction_embedding_model")


def load_synonyms(file_path):
    data = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]

            code = parts[0]
            terms = parts[1:]

            for term in terms:
                if term:
                    data.append({
                        "code": code,
                        "text": term
                    })

    return data


def process(file_path, name):

    data = load_synonyms(file_path)
    texts = [d["text"] for d in data]

    print(f"Procesando {name}: {len(texts)} textos")

    vectors = model.encode(texts, show_progress_bar=True)

    np.save(f"data/processed/{name}_vectors.npy", vectors)

    with open(f"data/processed/{name}_metadata.json", "w") as f:
        json.dump(data, f, indent=2)


# -------------------------
# EJECUCIÓN
# -------------------------
process("data/raw/ss_synonyms_clean.txt", "ss")
process("data/raw/ef_synonyms_clean.txt", "ef")
process("data/raw/pr_synonyms_clean.txt", "pr")

print("✅ Embeddings por tabla generados")