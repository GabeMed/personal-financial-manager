from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints

CategoryName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)
]


class CategoryBase(BaseModel):
    name: CategoryName


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
