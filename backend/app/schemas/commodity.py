from datetime import date
from pydantic import BaseModel


class CommodityRead(BaseModel):
    id: int
    mnemonic: str
    name: str
    fraction: int

    model_config = {"from_attributes": True}


class PriceCreate(BaseModel):
    date: date
    commodity_id: int
    currency_id: int
    numerator: int
    denominator: int = 1
    source: str = "user"


class PriceRead(BaseModel):
    id: int
    date: date
    commodity_id: int
    currency_id: int
    numerator: int
    denominator: int
    source: str

    model_config = {"from_attributes": True}
