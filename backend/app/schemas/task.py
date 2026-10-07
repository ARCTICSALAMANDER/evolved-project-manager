from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal


TaskStatus = Literal["not_started", "in_progress", "review", "completed"]


class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    status: TaskStatus = "not_started"
    commit_url: str | None = None
    task_executor: int | None = None
    deadline: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class TaskIn(BaseModel):
    task_id: int

    model_config = ConfigDict(extra="forbid")


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    task_executor: int | None = None
    deadline: datetime | None = None
    status: TaskStatus | None = None
    commit_url: str | None = None

    model_config = ConfigDict(extra="forbid")