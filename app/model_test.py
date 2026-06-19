import dill
from pathlib import Path
from sklearn.base import clone
import pickle

cale_model = Path(__file__).parent / "services" / "models" / "sentiment_model.pkl"

with open(cale_model, "rb") as f:
    old = dill.load(f)

model = old["model"]
vectorizer = old["vectorizer"]


test_texts = ["dezamagitor", "foarte frumos", "groaznic", "minunat", "murdar"]
X_test = vectorizer.transform(test_texts)
predictions = model.predict(X_test)

for text, pred in zip(test_texts, predictions):
    print(f"'{text}' → {pred}")


with open(cale_model, "wb") as f:
    dill.dump({"model": model, "vectorizer": vectorizer}, f)

print("\nModelul re-salvat cu succes!")