from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    projects_access = relationship("UserProject", back_populates="user")


from .project_model import Project
