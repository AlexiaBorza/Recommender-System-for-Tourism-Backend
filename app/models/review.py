from sqlalchemy import Column, BigInteger, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Review(Base):
    __tablename__ = "reviews"

    locatie_id = Column(BigInteger, ForeignKey("attractions.id", ondelete="CASCADE"), primary_key=True)
    nume = Column(String(255))
    tip = Column(String(100))
    nota_rating = Column(Integer)
    text_recenzie = Column(Text)
    timestamp = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    attraction = relationship("Attraction", backref="reviews")
    user = relationship("User", backref="reviews")


