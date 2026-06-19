from app.services.auth_service import hash_password
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.user_preferences import UserPreference
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    PreferencesCreate,
    PreferenceResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/{user_id}/preferences", response_model=list[PreferenceResponse])
def create_preferences(user_id: int, payload: PreferencesCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(UserPreference).filter(UserPreference.user_id == user_id).delete()

    created_preferences = []
    for pref in payload.preferences:
        db_pref = UserPreference(
            user_id=user_id,
            preference_type=pref.preference_type,
            preference_value=pref.preference_value
        )
        db.add(db_pref)
        created_preferences.append(db_pref)

    db.commit()

    for pref in created_preferences:
        db.refresh(pref)

    return created_preferences


@router.get("/{user_id}/preferences", response_model=list[PreferenceResponse])
def get_preferences(user_id: int, db: Session = Depends(get_db)):
    preferences = db.query(UserPreference).filter(UserPreference.user_id == user_id).all()
    return preferences