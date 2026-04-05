# Hybrid Semantic BIM Classification Engine

Classifies IFC building elements against the **Uniclass 2015** taxonomy (EF, Ss, Pr tables) using a hybrid approach: deterministic rules first, sentence-embedding cosine-similarity fallback.

---

## Architecture

```
IFC Model
    │
    ▼
[Feature Extractor]          ifc_feature_extractor.py
    │  ifc_type, material, predefined_type,
    │  load_bearing, is_external, spatial level…
    │
    ▼
[Group by key]               group_phrases.py
    │  ifc_type | material | type_object
    │
    ├──▶ [EF Classifier]     ef_classifier.py
    │       100% deterministic rules
    │       → EF code  (e.g. ef_20_10_30)
    │
    ├──▶ [SS Classifier]     ss_classifier.py + embedding_classifier.py
    │       Deterministic rules → embedding fallback
    │       → Ss code  (e.g. ss_20_20_75)
    │
    └──▶ [PR Classifier]     pr_classifier.py + embedding_classifier.py
            Deterministic rules → embedding fallback
            → Pr code  (e.g. pr_20_76_51_90)
```

### Classification strategy

| Table | Method | Confidence |
|-------|--------|------------|
| **EF** — Elements to form | 100% rule-based (IFC type + material + spatial level) | Fixed |
| **Ss** — Systems | Rules for all MEP with known discipline; embedding fallback for structural/arch | Rule: 95% / Embedding: cosine score |
| **Pr** — Products | Rules for all typed structural and MEP; embedding fallback for untyped | Rule: 95% / Embedding: cosine score |

Overall confidence per row = `min(ss_confidence, pr_confidence)`. Rows below **75%** are flagged `Revisar`.

---

## Project structure

```
├── multi_classifier.py              # Main entry point — processes N IFC files → CSV
│
├── engine/
│   ├── ifc/
│   │   └── ifc_feature_extractor.py # Extracts features from IfcElement objects
│   ├── rules/
│   │   ├── domain_classifier.py     # Detects domain (structure / mep / architecture)
│   │   ├── ef_classifier.py         # EF deterministic classifier
│   │   ├── ss_classifier.py         # Ss hybrid classifier
│   │   └── pr_classifier.py         # Pr hybrid classifier
│   └── semantic/
│       ├── semantic_translator.py   # Builds text phrases for embedding lookup
│       ├── group_phrases.py         # Groups IFC elements by classification key
│       └── embedding_classifier.py  # SentenceTransformer cosine-similarity lookup
│
├── data/
│   ├── processed/                   # Pre-built vector indices (committed)
│   │   ├── ss_vectors.npy           # Ss embeddings  (2 712 official codes)
│   │   ├── ss_metadata.json
│   │   ├── pr_vectors.npy           # Pr embeddings  (8 441 official codes)
│   │   └── pr_metadata.json
│   ├── uniclass/                    # NOT committed — user must supply
│   │   ├── Uniclass2015_EF_v1_16.xlsx
│   │   ├── Uniclass2015_Ss_v1_40.xlsx
│   │   └── Uniclass2015_Pr_v1_40.xlsx
│   └── embeddings/
│       └── rebuild_pr_index.py      # Rebuilds Pr vector index from Excel
│
├── models/
│   └── construction_embedding_model/ # Weights NOT committed — see Setup
│
└── training/
    └── train_embedding_model.py     # Fine-tuning script (all-MiniLM-L6-v2 base)
```

---

## Setup

### 1. Install dependencies

```bash
pip install ifcopenshell sentence-transformers scikit-learn numpy openpyxl
```

### 2. Provide the embedding model

The engine uses a fine-tuned `all-MiniLM-L6-v2` model stored at `models/construction_embedding_model/`.

**Option A — use the base model directly** (lower accuracy on construction terms):
```python
# In multi_classifier.py, change model_path to:
model_path = "sentence-transformers/all-MiniLM-L6-v2"
```

**Option B — fine-tune your own** (recommended):
```bash
# Place your training data at data/raw/bim_training_dataset_clean.csv
python training/train_embedding_model.py
```

### 3. Provide Uniclass Excel tables

Place the official Uniclass 2015 Excel files in `data/uniclass/`:
- `Uniclass2015_EF_v1_16.xlsx`
- `Uniclass2015_Ss_v1_40.xlsx`
- `Uniclass2015_Pr_v1_40.xlsx`

Available from [uniclass.thenbs.com](https://uniclass.thenbs.com).

### 4. (Optional) Rebuild vector indices

The pre-built indices in `data/processed/` are ready to use. If you update the Uniclass tables or change the model:

```bash
python data/embeddings/rebuild_pr_index.py
```

---

## Usage

Edit the `IFC_FILES` list at the top of [multi_classifier.py](multi_classifier.py):

```python
IFC_FILES = [
    r"path/to/your/model_EST.ifc",
    r"path/to/your/model_HVAC.ifc",
    # ...
]
```

The discipline is auto-detected from the filename (e.g. `IFC-HVAC-001.ifc` → `hvac`).

Run:

```bash
python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('multi_classifier.py', encoding='utf-8').read())"
```

Output: `classification_results_multi.csv`

---

## Output format

| Column | Description |
|--------|-------------|
| `model` | Source IFC discipline (extracted from filename) |
| `domain` | Detected domain: `structure`, `mep`, `architecture` |
| `phrase` | Group key used for classification |
| `count` | Number of elements in the group |
| `element_names` | Element names with counts |
| `ef_code` / `ef_text` | Uniclass EF classification |
| `ss_code` / `ss_text` / `ss_source` | Uniclass Ss classification + source (`rule` / `embedding`) |
| `pr_code` / `pr_text` / `pr_source` | Uniclass Pr classification + source (`rule` / `embedding`) |
| `confidence` | Overall confidence percentage |
| `flag` | `OK` (≥ 75%) or `Revisar` (< 75%) |

---

## How confidence works

- **Rule match** → fixed confidence of **95%**
- **Embedding fallback** → cosine similarity score between the generated phrase and the best-matching Uniclass title in the vector index
- **Overall** = `min(ss_confidence, pr_confidence)` — weakest link wins
- Rows flagged `Revisar` typically indicate: unknown IFC types, missing material/discipline data, or elements outside current rule coverage
