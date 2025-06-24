from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True)
    display_name = Column(String)
    email = Column(String, unique=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
