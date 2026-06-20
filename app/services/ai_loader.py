import pickle
import dill
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODELS_DIR = Path(__file__).parent / "models"
CSV_PATH = Path(__file__).parent.parent.parent / "atractii_master_final.csv"

_cosine_model = None
_svd_model = None
_sentiment_model = None


def simple_tokenizer(text):
    return text.split()


category_tags = {
    "restaurant": "restaurant mancare masa dining",
    "fast_food":  "fast_food mancare rapid ieftin",
    "cafe":       "cafenea cafea relaxare",
    "bakery":     "cofetarie patiserie desert dulciuri",
    "bar":        "bar bautura socializare seara",
    "pub":        "pub bautura seara socializare",
    "nightclub":  "club noapte petrecere dans muzica",
    "park":       "parc natura aer_liber outdoor relaxare familie copii",
    "museum":     "muzeu cultura istorie arta educatie",
    "artwork":    "arta monument cultura exterior",
    "attraction": "atractie turism vizitare landmark",
    "zoo":        "zoo animale familie copii natura",
}

space_tags = {
    "indoor":  "interior acoperit vreme_rea",
    "outdoor": "exterior aer_liber vreme_buna",
}

price_tags = {
    1: "ieftin buget_mic accesibil",
    2: "mediu buget_mediu",
    3: "scump premium lux",
}


def _build_cosine_model():
    df = pd.read_csv(CSV_PATH)
    df = df[~df["category"].isin(["hotel", "guest_house"])].reset_index(drop=True)

    def build_tags(row):
        tags = []
        tags.append(category_tags.get(row["category"], row["category"]))
        tags.append(space_tags.get(row["tip_spatiu"], ""))
        tags.append(price_tags.get(row["range_pret"], ""))
        return " ".join(tags)

    df["tags"] = df.apply(build_tags, axis=1)

    tfidf = TfidfVectorizer(tokenizer=simple_tokenizer)
    tfidf_matrix = tfidf.fit_transform(df["tags"])

    return {
        "tfidf_vectorizer": tfidf,
        "tfidf_matrix":     tfidf_matrix,
        "dataframe":        df,
        "category_tags":    category_tags,
        "spatiu_tags":       space_tags,
        "pret_tags":         price_tags,
    }


def load_all_models():
    global _cosine_model, _svd_model, _sentiment_model

    svd_path       = MODELS_DIR / "svd_model.pkl"
    sentiment_path = MODELS_DIR / "sentiment_model.pkl"

    if not svd_path.exists():
        raise FileNotFoundError(f"svd_model.pkl negăsit în {MODELS_DIR}")
    if not sentiment_path.exists():
        raise FileNotFoundError(f"sentiment_model.pkl negăsit în {MODELS_DIR}")

    # Cosine model — re-antrenat din CSV (evităm problema de compatibilitate pkl)
    _cosine_model = _build_cosine_model()

    # SVD și sentiment — încărcate din pkl
    with open(svd_path, "rb") as f:
        _svd_model = dill.load(f)

    with open(sentiment_path, "rb") as f:
        _sentiment_model = dill.load(f)

    print(f"Modele AI încărcate cu succes ({len(_cosine_model['dataframe'])} atracții).")


def get_cosine_model():
    if _cosine_model is None:
        raise RuntimeError("Modelul cosine nu este încărcat.")
    return _cosine_model


def get_svd_model():
    if _svd_model is None:
        raise RuntimeError("Modelul SVD nu este încărcat.")
    return _svd_model


def get_sentiment_model():
    if _sentiment_model is None:
        raise RuntimeError("Modelul sentiment nu este încărcat.")
    return _sentiment_model