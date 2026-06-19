import sys
from pathlib import Path

# Permite importul modulelor din app/ atunci când rulezi pytest din root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_loader import load_all_models, get_sentiment_model


def setup_module(module):
    """Se rulează o singură dată, înainte de toate testele din acest fișier."""
    load_all_models()


def test_sentiment_negativ_dezamagitor():
    model_data = get_sentiment_model()
    model = model_data["model"]
    vectorizer = model_data["vectorizer"]

    X = vectorizer.transform(["dezamagitor"])
    rezultat = model.predict(X)[0]

    assert rezultat == "negativ"


def test_sentiment_pozitiv_minunat():
    model_data = get_sentiment_model()
    model = model_data["model"]
    vectorizer = model_data["vectorizer"]

    X = vectorizer.transform(["minunat"])
    rezultat = model.predict(X)[0]

    assert rezultat == "pozitiv"


def test_sentiment_negativ_groaznic():
    model_data = get_sentiment_model()
    model = model_data["model"]
    vectorizer = model_data["vectorizer"]

    X = vectorizer.transform(["groaznic, nu recomand"])
    rezultat = model.predict(X)[0]

    assert rezultat == "negativ"