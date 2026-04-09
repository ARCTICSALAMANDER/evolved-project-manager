from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str

    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    user_id: int # TODO: брать из токена
    new_username: str

    model_config = ConfigDict(extra="forbid")