from sqlalchemy import Column, BigInteger, Numeric, Integer, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database.connection import Base


class AttractionSentiment(Base):
    __tablename__ = "attraction_sentiment"

    attraction_id = Column(BigInteger, ForeignKey("attractions.id", ondelete="CASCADE"), primary_key=True)
    sentiment_score = Column(Numeric(4, 3), nullable=False, default=1.000)
    rata_pozitiv = Column(Numeric(4, 3), nullable=False, default=0.500)
    nr_recenzii = Column(Integer, nullable=False, default=0)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    attraction = relationship("Attraction", backref="sentiment")