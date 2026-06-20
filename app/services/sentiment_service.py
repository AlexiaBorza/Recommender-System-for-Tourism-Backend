from sqlalchemy.orm import Session
from app.services.ai_loader import get_sentiment_model
from app.models.attraction_sentiment import AttractionSentiment


def analyze_and_update_sentiment(attraction_id: int, review_text: str, db: Session):
    model_data = get_sentiment_model()
    model = model_data["model"]
    vectorizer = model_data["vectorizer"]

    X = vectorizer.transform([review_text])
    sentiment = model.predict(X)[0]
    is_positive = 1 if sentiment == "pozitiv" else 0

    sentiment_row = db.query(AttractionSentiment).filter(
        AttractionSentiment.attraction_id == attraction_id
    ).first()

    if sentiment_row:
        old_total = sentiment_row.nr_recenzii
        old_rate = float(sentiment_row.rata_pozitiv)

        new_total = old_total + 1
        new_rate = ((old_rate * old_total) + is_positive) / new_total

        sentiment_row.nr_recenzii = new_total
        sentiment_row.rata_pozitiv = round(new_rate, 3)
        sentiment_row.sentiment_score = round(new_rate * 4 + 1, 3)
    else:
        sentiment_row = AttractionSentiment(
            attraction_id=attraction_id,
            sentiment_score=round(is_positive * 4 + 1, 3),
            rata_pozitiv=float(is_positive),
            nr_recenzii=1,
        )
        db.add(sentiment_row)

    db.commit()
    return sentiment_row.sentiment_score


def get_sentiment_score(attraction_id: int, db: Session) -> float:
    row = db.query(AttractionSentiment).filter(
        AttractionSentiment.attraction_id == attraction_id
    ).first()
    return float(row.sentiment_score) if row else 3.0