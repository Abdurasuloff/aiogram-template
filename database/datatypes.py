from pydantic import BaseModel, Field


class UserType(BaseModel):
    id: int
    name: str
    language: str | None = None
    username: str | None = None
