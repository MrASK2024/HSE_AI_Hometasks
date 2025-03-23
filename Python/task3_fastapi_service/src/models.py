from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, TIMESTAMP, Boolean

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(UUID, primary_key=True, index=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
