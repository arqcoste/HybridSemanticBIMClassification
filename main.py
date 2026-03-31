import numpy as np
import json

from engine.semantic.embedding_classifier import EmbeddingClassifier


# ----------------------------------
# 1. CARGAR VECTORES
# ----------------------------------

print("📂 Cargando vectores...")

vectors = np.load("data/embeddings/uniclass_vectors.npy")

with open("data/embeddings/uniclass_codes.json") as f:
    codes = json.load(f)

with open("data/embeddings/uniclass_metadata.json") as f:
    metadata = json.load(f)


# ----------------------------------
# 2. CREAR CLASIFICADOR
# ----------------------------------

classifier = EmbeddingClassifier(
    model_path="models/construction_embedding_model",
    vectors=vectors,
    codes=codes,
    metadata=metadata
)


# ----------------------------------
# 3. SIMULAR semantic_signature
# ----------------------------------

semantic_signature = "concrete load bearing external wall"


# ----------------------------------
# 4. PREDICCIÓN
# ----------------------------------

results = classifier.predict(semantic_signature)

print("\n🎯 RESULTADOS:")
for r in results:
    print(r)