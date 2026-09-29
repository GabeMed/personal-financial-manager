from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints
from backend.app.schemas.money import Money


class UserCreate(BaseModel):
    # Same limits as the frontend zod schema (src/schemas/auth.ts).
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)
    ]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=6, max_length=128)]


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    balance: Money

    model_config = ConfigDict(from_attributes=True)


##TODO add user update, just like I did with the other entities
