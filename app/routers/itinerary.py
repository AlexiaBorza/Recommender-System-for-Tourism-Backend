from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.itinerary_schema import ItineraryRequest, ItineraryResponse, ItineraryStopResponse
from app.schemas.attraction_schema import AttractionResponse
from app.services.itinerary_service import build_itinerary

router = APIRouter(prefix="/itinerary", tags=["Itinerary"])

@router.post("/generate", response_model=ItineraryResponse)
def generate_itinerary(payload: ItineraryRequest, db: Session = Depends(get_db)):

    lat = payload.lat_start or 45.7489
    lon = payload.lon_start or 21.2087
    stops, total_minutes = build_itinerary(
        db=db,
        categorii_preferate=payload.categorii_preferate,
        buget_max=payload.buget_max,
        tip_spatiu=payload.tip_spatiu,
        zi_saptamana=payload.zi_saptamana,
        ora_start=payload.ora_start,
        cu_copii=payload.cu_copii,
        lat_start=lat,
        lon_start=lon,
        timp_disponibil=payload.timp_disponibil,
        user_id=payload.user_id,
        saved_attraction_ids=payload.saved_attraction_ids,
    )

    if not stops:
        raise HTTPException(
            status_code=404,
            detail="Nu s-a putut genera un itinerariu cu parametrii dați."
        )

    return ItineraryResponse(
        total_minutes=total_minutes,
        stops=[
            ItineraryStopResponse(
                attraction=AttractionResponse.model_validate(s["attraction"]),
                ora_vizita=s["ora_vizita"],
                durata_minute=s["durata_minute"],
                timp_tranzit_minute=s["timp_tranzit_minute"],
            )
            for s in stops
        ],
    )

