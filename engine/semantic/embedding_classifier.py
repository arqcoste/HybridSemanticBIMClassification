from sentence_transformers import SentenceTransformer
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingClassifier:

    def __init__(self, model_path, vectors_path, metadata_path):

        print(f"🔹 Cargando modelo desde {model_path}...")
        self.model = SentenceTransformer(model_path)

        print("🔹 Cargando vectores...")
        self.vectors = np.load(vectors_path)

        print("🔹 Cargando metadata...")
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    # -----------------------------------
    # CLASIFICAR
    # -----------------------------------
    def classify(self, text, top_k=5, ef=None, data=None):

        # 1. embedding
        query_vec = self.model.encode([text])

        # 2. similitud
        sims = cosine_similarity(query_vec, self.vectors)[0]

        # 3. ranking bruto
        top_idx = np.argsort(sims)[::-1][:top_k * 3]

        results = []

        for idx in top_idx:
            results.append({
                "code": self.metadata[idx]["code"],
                "text": self.metadata[idx]["text"],
                "score": float(sims[idx])
            })

        # 🔥 FILTROS AVANZADOS
        results = self._apply_filters(results, ef, data)

        return results[:top_k]

    # -----------------------------------
    # FILTROS INTELIGENTES 🔥
    # -----------------------------------
    def _apply_filters(self, results, ef, data):

        if not data:
            return results

        ifc = data.get("ifc_type", "").lower()

        # -------------------------
        # KEYWORDS ESTRUCTURALES
        # -------------------------
        STRUCTURAL_KEYWORDS = [
            "beam", "column", "slab", "wall",
            "foundation", "reinforcement",
            "bar", "mesh", "steel", "concrete"
        ]

        # -------------------------
        # FILTRO POR IFC
        # -------------------------
        if ifc == "ifcbeam":
            return [r for r in results if "beam" in r["text"].lower()]

        if ifc == "ifccolumn":
            return [r for r in results if "column" in r["text"].lower()]

        if ifc == "ifcslab":
            return [r for r in results if "slab" in r["text"].lower()]

        if ifc == "ifcwall":
            return [r for r in results if "wall" in r["text"].lower()]

        if ifc == "ifcfooting":
            return [r for r in results if "foundation" in r["text"].lower()]

        if ifc in ["ifcreinforcingbar", "ifcreinforcingmesh"]:
            return [
                r for r in results
                if any(k in r["text"].lower() for k in ["reinforcement", "bar", "mesh"])
            ]

        # -------------------------
        # FILTRO POR EF
        # -------------------------
        if ef == "ef_20_10":  # estructura
            return [
                r for r in results
                if any(k in r["text"].lower() for k in STRUCTURAL_KEYWORDS)
            ]

        # fallback
        return results