from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.recommendation_schema import RecommendationRequest, RecommendationResponse
from app.schemas.attraction_schema import AttractionResponse
from app.services.recommender import get_recommendations
from app.models.attraction_schedule import AttractionSchedule

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest, db: Session = Depends(get_db)):
    if payload.buget_max not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="buget_max trebuie să fie 1, 2 sau 3")
    if payload.zi_saptamana not in range(7):
        raise HTTPException(status_code=400, detail="zi_saptamana trebuie să fie între 0 și 6")
    if payload.tip_spatiu and payload.tip_spatiu not in ["indoor", "outdoor"]:
        raise HTTPException(status_code=400, detail="tip_spatiu trebuie să fie indoor sau outdoor")

    results = get_recommendations(
        db=db,
        categorii_preferate=payload.categorii_preferate,
        buget_max=payload.buget_max,
        tip_spatiu=payload.tip_spatiu,
        zi_saptamana=payload.zi_saptamana,
        ora_start_minute=payload.ora_start,
        user_id=payload.user_id,
        top_n=payload.top_n,
    )

    def format_hour(hhmm: int) -> str:
        if hhmm == 0:
            return "00:00"
        if hhmm == 2400:
            return "24:00"
        return f"{hhmm // 100:02d}:{hhmm % 100:02d}"

    recommendations = []
    for a in results:
        schedule = db.query(AttractionSchedule).filter(
            AttractionSchedule.id == a.id,
            AttractionSchedule.zi == payload.zi_saptamana
        ).first()

        opening_hours = None
        if schedule:
            if schedule.ora_inchidere == 0:
                opening_hours = "Open 24h"
            else:
                deschidere = format_hour(schedule.ora_deschidere)
                inchidere = format_hour(schedule.ora_inchidere)
                opening_hours = f"{deschidere} - {inchidere}"
        else:
            print(f"  NO SCHEDULE FOUND for id {a.id}, zi {payload.zi_saptamana}")

        attraction_data = AttractionResponse(
            id=a.id,
            name=a.name,
            type=a.type,
            category=a.category,
            description=a.description,
            latitude=a.latitude,
            longitude=a.longitude,
            visit_time_min=a.visit_time_min,
            rating=a.rating,
            tip_spatiu=a.tip_spatiu,
            range_pret=a.range_pret,
            image_url=a.image_url,
            opening_hours=opening_hours,
        )

        recommendations.append(attraction_data)

    return RecommendationResponse(
        total=len(recommendations),
        recommendations=recommendations,
    )


@router.get("/accommodations")
def get_accommodations(db: Session = Depends(get_db)):
    """Returnează lista hotelurilor și pensiunilor pentru selectare punct de start."""
    from app.models.attractions import Attraction
    accommodations = db.query(Attraction).filter(
        Attraction.category.in_(["hotel", "guest_house"])
    ).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "latitude": a.latitude,
            "longitude": a.longitude,
        }
        for a in accommodations
        if a.latitude and a.longitude
    ]