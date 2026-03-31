from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import pandas as pd


# 🔥 1. CARGAR MODELO BASE
model = SentenceTransformer('all-MiniLM-L6-v2')


# 🔥 2. CARGAR DATASET
df = pd.read_csv("data/raw/bim_training_dataset_clean.csv")


# 🔥 3. CREAR PARES SEMÁNTICOS
train_examples = []

for _, row in df.iterrows():

    text1 = str(row["text1"])
    text2 = str(row["text2"])
    label = float(row["label"])  # 1 similar, 0 no similar

    train_examples.append(InputExample(texts=[text1, text2], label=label))


# 🔥 4. DATALOADER
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)


# 🔥 5. FUNCIÓN DE PÉRDIDA
train_loss = losses.CosineSimilarityLoss(model)


# 🔥 6. ENTRENAMIENTO
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=2,
    warmup_steps=100
)


# 🔥 7. GUARDAR MODELO
model.save("models/construction_embedding_model")