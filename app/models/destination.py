from sqlalchemy import Column, Integer, String, Text
from app.database.connection import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100))
    description = Column(Text)