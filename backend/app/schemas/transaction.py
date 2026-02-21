from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class SplitCreate(BaseModel):
    account_id: int
    value_minor: int
    quantity_minor: int
    memo: str = ""
    reconciled: str = "n"


class SplitRead(BaseModel):
    id: int
    transaction_id: int
    account_id: int
    value_minor: int
    quantity_minor: int
    memo: Optional[str] = None
    reconciled: str

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    date: date
    description: str = ""
    notes: str = ""
    import_ref: Optional[str] = None
    currency_id: int
    splits: List[SplitCreate]


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    currency_id: Optional[int] = None
    splits: Optional[List[SplitCreate]] = None


class TransactionRead(BaseModel):
    id: int
    date: date
    description: str
    notes: Optional[str] = None
    import_ref: Optional[str] = None
    currency_id: int
    splits: List[SplitRead] = []

    model_config = {"from_attributes": True}
