from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    name: str
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class TaskIn(BaseModel):
    task_id: int

    model_config = ConfigDict(extra="forbid")


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    task_executor: int | None = None
    deadline: str | None = None

    model_config = ConfigDict(extra="forbid")