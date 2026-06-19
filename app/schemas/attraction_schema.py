from pydantic import BaseModel
from typing import Optional


class AttractionResponse(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    visit_time_min: Optional[int] = None
    rating: Optional[float] = None
    tip_spatiu: Optional[str] = None
    range_pret: Optional[int] = None
    image_url: Optional[str] = None
    opening_hours: str | None = None

    class Config:
        from_attributes = True