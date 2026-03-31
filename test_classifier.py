from engine.semantic.embedding_classifier import EmbeddingClassifier

clf = EmbeddingClassifier()

text = "steel structural beam plate"

results = clf.classify(text)

print("\nRESULTADOS:")
for r in results:
    print(r)