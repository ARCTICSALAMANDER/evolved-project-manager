from pydantic import BaseModel, ConfigDict, Field, SecretStr


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserCreate(BaseModel):
    username: str
    password: SecretStr
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN)
    tech_stack: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    new_username: str | None = None
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN)
    tech_stack: list[str] | None = None

    model_config = ConfigDict(extra="forbid")