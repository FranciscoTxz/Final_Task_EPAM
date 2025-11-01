from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DocumentBase(BaseModel):
    name: str
    url: str


class DocumentGet(DocumentBase):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProjectInfo(BaseModel):
    id: int
    name: str
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
