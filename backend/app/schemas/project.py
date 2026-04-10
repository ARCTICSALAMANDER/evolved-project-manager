from pydantic import BaseModel, ConfigDict
from datetime import datetime 


class ProjectIn(BaseModel):
    name: str
    description: str | None = None
    is_public: bool

    model_config = ConfigDict(extra="forbid")


class ProjectOut(BaseModel):
    name: str
    description: str | None = None 
    created_at: datetime
    is_public: bool


class ProjectUpdate(BaseModel):
    project_id: int
    name: str | None
    description: str | None
    is_public: bool | None

    model_config = ConfigDict(extra="forbid")