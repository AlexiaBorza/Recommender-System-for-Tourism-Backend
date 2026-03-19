from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Attraction

router = APIRouter()

@router.get("/attractions")
def get_attractions(db: Session = Depends(get_db)):
    attractions = db.query(Attraction).limit(20).all()
    return attractions