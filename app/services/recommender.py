from sqlalchemy.orm import Session
from app.models.attractions import Attraction
from app.models.user_preference import UserPreference
import math


def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


def get_user_preferences(db: Session, user_id: int):
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).all()


def recommend_for_user(db, user_id, user_lat=45.7489, user_lon=21.2087, limit=10):
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == user_id
    ).all()

    preferred_types = [p.preference_value for p in preferences]

    attractions = db.query(Attraction).all()

    scored = []

    for a in attractions:
        score = 0

        if a.type in preferred_types:
            score += 5

        if a.rating:
            score += a.rating

        if a.latitude and a.longitude:
            dist = distance(user_lat, user_lon, a.latitude, a.longitude)
            score += max(0, 5 - dist)  # mai aproape = scor mai mare

        scored.append((a, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [a for a, _ in scored[:limit]]