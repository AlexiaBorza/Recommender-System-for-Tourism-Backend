from pydantic import BaseModel
from typing import List
from app.schemas.attraction_schema import AttractionResponse


class ItineraryRequest(BaseModel):
    user_id: int
    available_minutes: int


class ItineraryResponse(BaseModel):
    total_minutes: int
    attractions: List[AttractionResponse]