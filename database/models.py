from sqlalchemy import Column, Integer, String, Float, Boolean
from database.db_config import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, primary_key=False, index=True)
    username = Column(String, index=True, nullable=True)
    language = Column(String, nullable=True)

    def __repr__(self):
        return f"User: {self.name} | {self.id}"
