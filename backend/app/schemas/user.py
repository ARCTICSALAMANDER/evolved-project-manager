from pydantic import BaseModel, ConfigDict, SecretStr


class UserCreate(BaseModel):
    username: str
    password: SecretStr

    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    new_username: str

    model_config = ConfigDict(extra="forbid")