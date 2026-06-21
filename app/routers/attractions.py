from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.attractions import Attraction
from app.models.attraction_schedule import AttractionSchedule

router = APIRouter(prefix="/attractions", tags=["Attractions"])

DAY_NAMES = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]


def format_hour(hhmm: int) -> str:
    if hhmm == 0:
        return "00:00"
    if hhmm == 2400:
        return "24:00"
    return f"{hhmm // 100:02d}:{hhmm % 100:02d}"


@router.get("/{attraction_id}")
def get_attraction(attraction_id: int, db: Session = Depends(get_db)):
    attraction = db.query(Attraction).filter(Attraction.id == attraction_id).first()
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")

    schedule_rows = db.query(AttractionSchedule).filter(
        AttractionSchedule.id == attraction_id
    ).all()
    schedule_by_day = {row.zi: row for row in schedule_rows}

    weekly_hours = {}
    for day_index, day_name in enumerate(DAY_NAMES):
        row = schedule_by_day.get(day_index)
        if not row:
            weekly_hours[day_name] = None
        elif row.ora_inchidere == 0:
            weekly_hours[day_name] = "Non-stop"
        else:
            weekly_hours[day_name] = f"{format_hour(row.ora_deschidere)} - {format_hour(row.ora_inchidere)}"

    return {
        "id": attraction.id,
        "name": attraction.name,
        "type": attraction.type,
        "category": attraction.category,
        "description": attraction.description,
        "latitude": attraction.latitude,
        "longitude": attraction.longitude,
        "visit_time_min": attraction.visit_time_min,
        "rating": attraction.rating,
        "tip_spatiu": attraction.tip_spatiu,
        "range_pret": attraction.range_pret,
        "image_url": attraction.image_url,
        "opening_hours": weekly_hours,
    }