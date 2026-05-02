from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.itinerary_schema import ItineraryRequest, ItineraryResponse
from app.schemas.attraction_schema import AttractionResponse
from app.services.recommender import recommend_for_user
from app.services.itinerary_service import build_itinerary

router = APIRouter(prefix="/itinerary", tags=["Itinerary"])

@router.post("/generate", response_model=ItineraryResponse)
def generate_itinerary(payload: ItineraryRequest, db: Session = Depends(get_db)):
    recommendations = recommend_for_user(db, payload.user_id, limit=20)
    selected, total = build_itinerary(recommendations, payload.available_minutes)

    return ItineraryResponse(
        total_minutes=total,
        attractions=[AttractionResponse.model_validate(a) for a in selected]
    )
