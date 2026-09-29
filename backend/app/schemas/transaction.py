from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from backend.app.schemas.category import CategoryResponse
from backend.app.schemas.money import Money

# Matches the Numeric(10, 2) column: positive, at most 2 decimal places.
Amount = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
TransactionTypeLiteral = Literal["expense", "income"]


class TransactionBase(BaseModel):
    type: TransactionTypeLiteral
    amount: Amount
    description: str | None = None
    # default_factory runs per request; a plain default would be evaluated once
    # at import time and every transaction would share that timestamp.
    date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    category_id: int


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: TransactionTypeLiteral | None = None
    amount: Amount | None = None
    description: str | None = None
    date: datetime | None = None
    category_id: int | None = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self):
        # Omitting a field keeps its value; sending null is only valid for
        # description, the one nullable column.
        for field in ("type", "amount", "date", "category_id"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TransactionResponse(TransactionBase):
    id: int
    amount: Money
    category: CategoryResponse

    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    balance: Money
    income_total: Money
    expense_total: Money
    # {category_id: percentage of the income/expense total}
    income_porcentage_by_category: dict[int, float]
    expense_porcentage_by_category: dict[int, float]
