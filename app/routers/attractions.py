from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.attractions import Attraction

router = APIRouter(prefix="/attractions", tags=["Attractions"])

@router.get("/{attraction_id}")
def get_attraction(attraction_id: int, db: Session = Depends(get_db)):
    attraction = db.query(Attraction).filter(Attraction.id == attraction_id).first()
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return attraction