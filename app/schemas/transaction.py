from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    transaction_type: str
    category: str
    description: str | None = None
    transaction_date: date