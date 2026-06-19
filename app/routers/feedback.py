from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.feedback_schema import FeedbackRequest, FeedbackResponse, FeedbackItem
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.user import User
from app.models.attractions import Attraction
from app.services.sentiment_service import analyze_and_update_sentiment
from app.models.review import Review

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    if payload.rating not in range(1, 6):
        raise HTTPException(status_code=400, detail="Rating trebuie sa fie intre 1 si 5")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User negasit")

    attraction = db.query(Attraction).filter(Attraction.id == payload.attraction_id).first()
    if not attraction:
        raise HTTPException(status_code=404, detail="Atractie negasita")

    feedback = RecommendationFeedback(
        user_id=payload.user_id,
        attraction_id=payload.attraction_id,
        rating=payload.rating,
        comment=payload.comment,
        author=payload.author,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    if payload.comment:
        analyze_and_update_sentiment(payload.attraction_id, payload.comment, db)

        if payload.comment:
            print(f"[SENTIMENT] Analizez comentariul: {payload.comment}")
            result = analyze_and_update_sentiment(payload.attraction_id, payload.comment, db)
            print(f"[SENTIMENT] Scor nou: {result}")

    return FeedbackResponse(
        message="Feedback salvat cu succes",
        user_id=payload.user_id,
        attraction_id=payload.attraction_id,
        rating=payload.rating,
    )

@router.get("/{user_id}")
def get_user_feedback(user_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(RecommendationFeedback).filter(
        RecommendationFeedback.user_id == user_id
    ).all()
    return feedbacks

@router.get("/reviews/{attraction_id}")
def get_attraction_reviews(attraction_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        Review.locatie_id == attraction_id
    ).order_by(Review.timestamp.desc()).all()
    return [
        {
            "id": f"{r.locatie_id}_{r.timestamp}",
            "author": r.nume or "Anonymous",
            "rating": r.nota_rating,
            "comment": r.text_recenzie,
            "createdAt": r.timestamp,
        }
        for r in reviews
    ]

@router.get("/user-reviews/{attraction_id}")
def get_user_reviews(attraction_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(RecommendationFeedback).filter(
        RecommendationFeedback.attraction_id == attraction_id
    ).order_by(RecommendationFeedback.created_at.desc()).all()
    return [
        {
            "id": str(f.id),
            "author": f.author or "Anonymous",
            "rating": f.rating,
            "comment": f.comment,
            "createdAt": f.created_at.isoformat() if f.created_at else None,
        }
        for f in feedbacks
    ]


@router.post("/admin/recalculare-sentiment")
def recalculeaza_toate_recenziile(db: Session = Depends(get_db)):
    """
    Ruta administrativa pentru recalcularea intregii baze de date
    folosind noul model de AI (utila dupa reantrenarea modelului).
    """
    try:

        recenzii = db.query(Review).filter(Review.text_recenzie.isnot(None)).all()

        if not recenzii:
            raise HTTPException(status_code=404, detail="Nu s-au gasit recenzii in baza de date")

        print(f"[ADMIN] Am gasit {len(recenzii)} recenzii pentru recalculare...")

        # 2. Le trecem pe rand prin functia ta existenta din proiect
        # Aceasta functie va folosi noul model .pkl (pe care l-ai înlocuit deja)
        # si va face update-ul automat in tabelul 'attraction_sentiment'
        count = 0
        for r in recenzii:
            if r.locatie_id and r.text_recenzie.strip():
                # Apelam functia ta nativa din proiect
                analyze_and_update_sentiment(r.locatie_id, r.text_recenzie, db)
                count += 1

        return {
            "status": "succes",
            "message": f"Baza de date a fost actualizata cu noul model de AI. Au fost reprocesate {count} recenzii."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Eroare la recalculare: {str(e)}")
