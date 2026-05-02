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
    estimated_visit_time: Optional[int] = None
    rating: Optional[float] = None
    destination_id: Optional[int] = None

    class Config:
        from_attributes = True