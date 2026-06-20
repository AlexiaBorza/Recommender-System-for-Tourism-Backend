from fastapi import FastAPI, HTTPException, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.sql.annotation import Annotated
import app.models.user as user
import app.models.attractions as attractions
from app.database.connection import engine, SessionLocal
from app.database.connection import get_db
from sqlalchemy.orm import Session
from app.routers import users, recommendations, itinerary, feedback, auth, attractions
from app.services.ai_loader import load_all_models
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    load_all_models()
@app.get("/")
def root():
    return {"message": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recommendations.router)
app.include_router(itinerary.router)
app.include_router(feedback.router)
app.include_router(attractions.router)
class User(BaseModel):
    email: str

db_dependency = Annotated[Session, Depends(get_db)]
