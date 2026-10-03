from sqlalchemy import Column, UUID, String, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Item(Base):
    __tablename__ = 'item'
    id = Column(UUID, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(UUID, ForeignKey('user.id'), nullable=False)
