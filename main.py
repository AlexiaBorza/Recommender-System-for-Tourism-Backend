from fastapi import FastAPI, HTTPException, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy.sql.annotation import Annotated

import app.models.user as user
import app.models.attractions as attractions
import app.models.destination as destinations
from app.database.connection import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

class User(BaseModel):
    email: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated(SessionLocal, Depends(get_db))

