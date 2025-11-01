from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    documents = relationship(
        "Document", back_populates="project", cascade="all, delete"
    )
    users_access = relationship(
        "UserProject", back_populates="project", cascade="all, delete"
    )
