"""Seed data: currencies and chart of accounts."""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from .models.commodity import Commodity
from .models.account import Account, AccountType


CURRENCIES = [
    {"mnemonic": "USD", "name": "US Dollar", "fraction": 100},
    {"mnemonic": "EUR", "name": "Euro", "fraction": 100},
    {"mnemonic": "GBP", "name": "British Pound", "fraction": 100},
    {"mnemonic": "JPY", "name": "Japanese Yen", "fraction": 1},
    {"mnemonic": "INR", "name": "Indian Rupee", "fraction": 100},
    {"mnemonic": "CAD", "name": "Canadian Dollar", "fraction": 100},
    {"mnemonic": "AUD", "name": "Australian Dollar", "fraction": 100},
    {"mnemonic": "CHF", "name": "Swiss Franc", "fraction": 100},
]


def seed_currencies(db: Session) -> Dict[str, int]:
    """Seed currencies, return mnemonic → id map."""
    existing = {c.mnemonic: c.id for c in db.query(Commodity).all()}
    for c in CURRENCIES:
        if c["mnemonic"] not in existing:
            commodity = Commodity(**c)
            db.add(commodity)
    db.commit()
    return {c.mnemonic: c.id for c in db.query(Commodity).all()}


def _add_account(
    db: Session,
    name: str,
    account_type: AccountType,
    commodity_id: int,
    parent_id: Optional[int],
    placeholder: bool = False,
) -> Account:
    full_name = name
    if parent_id is not None:
        parent = db.get(Account, parent_id)
        if parent:
            full_name = f"{parent.full_name}:{name}"
    account = Account(
        name=name,
        full_name=full_name,
        account_type=account_type,
        commodity_id=commodity_id,
        parent_id=parent_id,
        placeholder=placeholder,
    )
    db.add(account)
    db.flush()
    return account


def seed_chart_of_accounts(db: Session, currency_map: Dict[str, int]) -> None:
    """Seed a standard chart of accounts."""
    usd = currency_map["USD"]

    # Assets
    assets = _add_account(db, "Assets", AccountType.ASSET, usd, None, placeholder=True)
    current = _add_account(db, "Current Assets", AccountType.ASSET, usd, assets.id, placeholder=True)
    _add_account(db, "Checking", AccountType.ASSET, usd, current.id)
    _add_account(db, "Savings", AccountType.ASSET, usd, current.id)

    # Liabilities
    liab = _add_account(db, "Liabilities", AccountType.LIABILITY, usd, None, placeholder=True)
    _add_account(db, "Credit Cards", AccountType.LIABILITY, usd, liab.id)
    _add_account(db, "Loans", AccountType.LIABILITY, usd, liab.id)

    # Equity
    equity = _add_account(db, "Equity", AccountType.EQUITY, usd, None, placeholder=True)
    _add_account(db, "Opening Balance", AccountType.EQUITY, usd, equity.id)

    # Income
    income = _add_account(db, "Income", AccountType.INCOME, usd, None, placeholder=True)
    _add_account(db, "Salary", AccountType.INCOME, usd, income.id)
    _add_account(db, "Other Income", AccountType.INCOME, usd, income.id)

    # Expenses
    expenses = _add_account(db, "Expenses", AccountType.EXPENSE, usd, None, placeholder=True)
    food = _add_account(db, "Food", AccountType.EXPENSE, usd, expenses.id, placeholder=True)
    _add_account(db, "Groceries", AccountType.EXPENSE, usd, food.id)
    _add_account(db, "Restaurants", AccountType.EXPENSE, usd, food.id)
    housing = _add_account(db, "Housing", AccountType.EXPENSE, usd, expenses.id, placeholder=True)
    _add_account(db, "Rent", AccountType.EXPENSE, usd, housing.id)
    _add_account(db, "Utilities", AccountType.EXPENSE, usd, housing.id)
    transport = _add_account(db, "Transportation", AccountType.EXPENSE, usd, expenses.id, placeholder=True)
    _add_account(db, "Gas", AccountType.EXPENSE, usd, transport.id)
    _add_account(db, "Public Transit", AccountType.EXPENSE, usd, transport.id)

    db.commit()


def run_seed(db: Session) -> None:
    """Run seed if database is empty."""
    account_count = db.query(Account).count()
    if account_count > 0:
        return

    currency_map = seed_currencies(db)
    seed_chart_of_accounts(db, currency_map)
