from fastapi import FastAPI, HTTPException, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.sql.annotation import Annotated
import app.models.user as user
import app.models.attractions as attractions
import app.models.destination as destinations
from app.database.connection import engine, SessionLocal
from app.database.connection import get_db
from sqlalchemy.orm import Session
from app.routers import users, recommendations, itinerary

app = FastAPI()
@app.get("/")
def root():
    return {"message": "ok"}

class User(BaseModel):
    email: str

db_dependency = Annotated[Session, Depends(get_db)]
