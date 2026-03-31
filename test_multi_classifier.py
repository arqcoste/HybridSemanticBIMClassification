from engine.semantic.multi_table_classifier import MultiTableClassifier

clf = MultiTableClassifier()

text = "steel structural beam plate"

results = clf.classify(text)

for table, res in results.items():
    print(f"\n=== {table} ===")
    for r in res:
        print(r)