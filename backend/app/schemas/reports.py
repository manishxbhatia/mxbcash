from pydantic import BaseModel


class PnLRow(BaseModel):
    account_id: int
    account_name: str
    account_type: str
    period: str  # e.g. "2024-01-01" (first of month)
    amount_minor: int
    reporting_currency: str


class PnLReport(BaseModel):
    rows: list[PnLRow]
    reporting_currency: str
    from_date: str
    to_date: str


class BalancePoint(BaseModel):
    period: str
    balance_minor: int
    reporting_currency: str


class BalanceHistory(BaseModel):
    account_id: int
    account_name: str
    points: list[BalancePoint]
    reporting_currency: str


class NetWorthSnapshot(BaseModel):
    assets_minor: int
    liabilities_minor: int
    net_worth_minor: int
    reporting_currency: str
