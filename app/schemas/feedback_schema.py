from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackRequest(BaseModel):
    user_id: int
    attraction_id: int
    rating: int
    comment: Optional[str] = None
    author: Optional[str] = None

class FeedbackResponse(BaseModel):
    message: str
    user_id: int
    attraction_id: int
    rating: int

class FeedbackItem(BaseModel):
    id: int
    user_id: int
    attraction_id: int
    rating: int
    comment: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True