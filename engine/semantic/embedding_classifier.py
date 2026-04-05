from sentence_transformers import SentenceTransformer
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingClassifier:

    def __init__(self, model_path, vectors_path, metadata_path):

        print(f"Cargando modelo desde {model_path}...")
        self.model = SentenceTransformer(model_path)

        print("Cargando vectores...")
        self.vectors = np.load(vectors_path)

        print("Cargando metadata...")
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        # phrase → encoded vector (populated by encode_batch or lazily on first classify)
        self._vec_cache = {}

    # -----------------------------------
    # BATCH PRE-ENCODE
    # -----------------------------------
    def encode_batch(self, phrases):
        """Encode a list of phrases in one forward pass and store in cache."""
        unique = [p for p in set(phrases) if p not in self._vec_cache]
        if not unique:
            return
        vecs = self.model.encode(unique, batch_size=64, show_progress_bar=False)
        for phrase, vec in zip(unique, vecs):
            self._vec_cache[phrase] = vec

    # -----------------------------------
    # CLASIFICAR
    # -----------------------------------
    def classify(self, text, top_k=5, ef=None, data=None):

        # 1. embedding (cache hit avoids re-encoding)
        if text in self._vec_cache:
            query_vec = self._vec_cache[text].reshape(1, -1)
        else:
            query_vec = self.model.encode([text])
            self._vec_cache[text] = query_vec[0]

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
        ifc_keyword_map = {
            "ifcbeam":           ["beam"],
            "ifccolumn":         ["column"],
            "ifcslab":           ["slab"],
            "ifcwall":           ["wall"],
            "ifcfooting":        ["foundation"],
            "ifcreinforcingbar": ["reinforcement", "bar", "mesh"],
            "ifcreinforcingmesh":["reinforcement", "bar", "mesh"],
        }

        if ifc in ifc_keyword_map:
            keywords = ifc_keyword_map[ifc]
            filtered = [r for r in results if any(k in r["text"].lower() for k in keywords)]
            return filtered if filtered else results

        # -------------------------
        # FILTRO POR EF
        # -------------------------
        if ef == "ef_20_10":  # estructura
            filtered = [r for r in results if any(k in r["text"].lower() for k in STRUCTURAL_KEYWORDS)]
            return filtered if filtered else results

        # fallback
        return results