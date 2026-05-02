from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    preference_type = Column(String(100), nullable=False)
    preference_value = Column(String(100), nullable=False)