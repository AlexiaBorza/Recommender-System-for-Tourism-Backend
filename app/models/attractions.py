from sqlalchemy import Column, Enum, BigInteger, String, Text, Double, Integer, Float
from app.database.connection import Base


class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255))
    type = Column(String(100))
    category = Column(String(100))
    description = Column(Text)
    latitude = Column(Double)
    longitude = Column(Double)
    visit_time_min = Column(Integer)
    rating = Column(Float)
    destination_id = Column(Integer)
    tip_spatiu = Column(Enum("indoor", "outdoor"), nullable=False, default="outdoor")
    range_pret = Column(Integer, nullable=False, default=1)
    image_url = Column(String(500), nullable=True)