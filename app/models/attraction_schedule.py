from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class AttractionSchedule(Base):
    __tablename__ = "attraction_schedule"

    id = Column(BigInteger, ForeignKey("attractions.id", ondelete="CASCADE"), primary_key=True)
    zi = Column(SmallInteger, primary_key=True, comment="0=Luni, 1=Marti, ..., 6=Duminica")
    ora_deschidere = Column(SmallInteger, nullable=False, comment="format HHMM")
    ora_inchidere = Column(SmallInteger, nullable=False, comment="0=non-stop, 2400=miezul noptii")

    attraction = relationship("Attraction", backref="schedule")