from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth_schema import LoginRequest, TokenResponse, RegisterRequest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email deja înregistrat")

    existing_username = db.query(User).filter(User.name == payload.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username deja folosit")

    existing_username = db.query(User).filter(User.name == payload.username).first()
    db_user = User(
        name=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_access_token({"sub": str(db_user.id)})

    return TokenResponse(
        access_token=token,
        user_id=db_user.id,
        username=db_user.name,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email sau parolă incorectă",
        )

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.name,
    )


@router.get("/me")
def get_me(token: str, db: Session = Depends(get_db)):
    from app.services.auth_service import get_current_user
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalid sau expirat")
    return {"id": user.id, "username": user.name, "email": user.email}