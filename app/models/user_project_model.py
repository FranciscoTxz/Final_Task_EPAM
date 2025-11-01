from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class UserProject(Base):
    __tablename__ = "users_projects"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    project_id = Column(
        Integer, ForeignKey("projects.id"), primary_key=True, nullable=False
    )
    is_owner = Column(Boolean, default=False, nullable=False)
    user = relationship("User", back_populates="projects_access")
    project = relationship("Project", back_populates="users_access")


from .user_model import User
from .project_model import Project
