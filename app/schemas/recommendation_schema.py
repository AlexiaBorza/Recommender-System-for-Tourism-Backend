from pydantic import BaseModel
from typing import List, Optional
from app.schemas.attraction_schema import AttractionResponse


class RecommendationRequest(BaseModel):
    user_id: Optional[int] = None
    categorii_preferate: List[str]
    buget_max: int = 2
    tip_spatiu: Optional[str] = None
    zi_saptamana: int
    ora_start: int
    top_n: int = 10


class RecommendationResponse(BaseModel):
    total: int
    recommendations: List[AttractionResponse]