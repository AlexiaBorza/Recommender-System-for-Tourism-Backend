from pydantic import BaseModel
from typing import List, Optional
from app.schemas.attraction_schema import AttractionResponse


class ItineraryRequest(BaseModel):
    user_id: int
    categorii_preferate: List[str]
    buget_max: int = 2
    tip_spatiu: Optional[str] = None
    zi_saptamana: int
    ora_start: int
    cu_copii: bool = False
    lat_start: Optional[float] = None
    lon_start: Optional[float] = None
    timp_disponibil: int = 180
    saved_attraction_ids: list[int] = []


class ItineraryStopResponse(BaseModel):
    attraction: AttractionResponse
    ora_vizita: Optional[str] = None
    durata_minute: Optional[int] = None
    timp_tranzit_minute: Optional[int] = None


class ItineraryResponse(BaseModel):
    total_minutes: int
    stops: List[ItineraryStopResponse]