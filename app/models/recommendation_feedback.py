from sqlalchemy import Column, Integer, Text, String, BigInteger, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database.connection import Base


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    attraction_id = Column(BigInteger, ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False, comment="1-5")
    comment = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", backref="feedback")
    attraction = relationship("Attraction", backref="feedback")