from sqlalchemy import Column, BigInteger, String, Text, Double, Integer, Float
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
    estimated_visit_time = Column(Integer)
    rating = Column(Float)
    destination_id = Column(Integer)