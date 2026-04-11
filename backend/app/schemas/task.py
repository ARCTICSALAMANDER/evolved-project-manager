from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    name: str
    description: str | None
    project_id: int

    model_config = ConfigDict(extra="forbid")


class TaskIn(BaseModel):
    task_id: int
    project_id: int

    model_config = ConfigDict(extra="forbid")