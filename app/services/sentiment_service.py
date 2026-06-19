from sqlalchemy.orm import Session
from app.services.ai_loader import get_sentiment_model
from app.models.attraction_sentiment import AttractionSentiment


def analyze_and_update_sentiment(attraction_id: int, text_recenzie: str, db: Session):
    model_data = get_sentiment_model()
    model      = model_data["model"]
    vectorizer = model_data["vectorizer"]

    X = vectorizer.transform([text_recenzie])
    sentiment = model.predict(X)[0]
    print(f"[DEBUG] Text: '{text_recenzie}' → clasificat ca: '{sentiment}'")  # adaugă asta
    este_pozitiv = 1 if sentiment == "pozitiv" else 0


    sentiment_row = db.query(AttractionSentiment).filter(
        AttractionSentiment.attraction_id == attraction_id
    ).first()

    if sentiment_row:
        total_vechi = sentiment_row.nr_recenzii
        rata_veche  = float(sentiment_row.rata_pozitiv)

        nr_nou   = total_vechi + 1
        rata_nou = ((rata_veche * total_vechi) + este_pozitiv) / nr_nou

        sentiment_row.nr_recenzii  = nr_nou
        sentiment_row.rata_pozitiv = round(rata_nou, 3)
        sentiment_row.sentiment_score = round(rata_nou * 4 + 1, 3)
    else:
        sentiment_row = AttractionSentiment(
            attraction_id=attraction_id,
            sentiment_score=round(este_pozitiv * 4 + 1, 3),
            rata_pozitiv=float(este_pozitiv),
            nr_recenzii=1,
        )
        db.add(sentiment_row)

    db.commit()
    return sentiment_row.sentiment_score


def get_sentiment_score(attraction_id: int, db: Session) -> float:
    """
    Returnează scorul de sentiment pentru o atracție.
    Default 3.0 dacă nu există recenzii.
    """
    row = db.query(AttractionSentiment).filter(
        AttractionSentiment.attraction_id == attraction_id
    ).first()
    return float(row.sentiment_score) if row else 3.0