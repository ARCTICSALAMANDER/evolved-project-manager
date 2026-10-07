from pydantic import BaseModel, ConfigDict
from datetime import datetime 


class ProjectIn(BaseModel):
    name: str
    description: str | None = None
    repository_url: str | None = None
    is_public: bool

    model_config = ConfigDict(extra="forbid")


class ProjectOut(BaseModel):
    name: str
    description: str | None = None 
    repository_url: str | None = None
    created_at: datetime
    is_public: bool


class ProjectUpdate(BaseModel):
    project_id: int
    name: str | None = None
    description: str | None = None
    repository_url: str | None = None
    is_public: bool | None = None

    model_config = ConfigDict(extra="forbid")


class ProjectMember(BaseModel):
    user_id: int
    project_id: int

    model_config = ConfigDict(extra="forbid")