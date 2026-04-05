# -----------------------------------
# REBUILD PR INDEX FROM OFFICIAL UNICLASS CATALOG
# One entry per official code, using exact official title text.
# -----------------------------------

import openpyxl
import numpy as np
import json
from sentence_transformers import SentenceTransformer

EXCEL_PATH  = "data/uniclass/Uniclass2015_Pr_v1_40.xlsx"
OUT_VECTORS = "data/processed/pr_vectors.npy"
OUT_META    = "data/processed/pr_metadata.json"
MODEL_PATH  = "models/construction_embedding_model"

print("Loading Uniclass PR table...")
wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
ws = wb.active

entries = []
for row in ws.iter_rows(min_row=4, values_only=True):
    code  = str(row[0] or "").strip()
    title = str(row[6] or "").strip()
    if code.startswith("Pr_") and title:
        entries.append({"code": code.lower(), "text": title})

wb.close()
print(f"Official PR entries: {len(entries)}")

print("Loading model...")
model = SentenceTransformer(MODEL_PATH)

texts = [e["text"] for e in entries]
print(f"Encoding {len(texts)} phrases...")
vectors = model.encode(texts, batch_size=64, show_progress_bar=True)

np.save(OUT_VECTORS, vectors)
with open(OUT_META, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f"PR index rebuilt: {len(entries)} entries -> {OUT_VECTORS}")
