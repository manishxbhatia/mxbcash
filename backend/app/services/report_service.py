from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.account import Account, AccountType
from ..models.transaction import Transaction, Split
from ..models.commodity import Commodity, Price
from ..schemas.reports import PnLRow, PnLReport, BalancePoint, BalanceHistory, NetWorthSnapshot


def _get_reporting_currency(db: Session, mnemonic: str) -> Commodity:
    c = db.query(Commodity).filter(Commodity.mnemonic == mnemonic).first()
    if c is None:
        raise ValueError(f"Unknown reporting currency: {mnemonic}")
    return c


def _convert_to_reporting(
    quantity_minor: int,
    account_commodity_id: int,
    reporting_currency_id: int,
    date_str: str,
    price_cache: dict,
    db: Session,
) -> int:
    """Convert quantity_minor in account's commodity to reporting currency minor units."""
    if account_commodity_id == reporting_currency_id:
        return quantity_minor

    key = (account_commodity_id, reporting_currency_id, date_str)
    if key not in price_cache:
        price = (
            db.query(Price)
            .filter(
                Price.commodity_id == account_commodity_id,
                Price.currency_id == reporting_currency_id,
                Price.date <= date_str,
            )
            .order_by(Price.date.desc())
            .first()
        )
        price_cache[key] = price

    price = price_cache[key]
    if price is None:
        # Try reverse lookup
        rev_key = (reporting_currency_id, account_commodity_id, date_str)
        if rev_key not in price_cache:
            rev_price = (
                db.query(Price)
                .filter(
                    Price.commodity_id == reporting_currency_id,
                    Price.currency_id == account_commodity_id,
                    Price.date <= date_str,
                )
                .order_by(Price.date.desc())
                .first()
            )
            price_cache[rev_key] = rev_price
        rev_price = price_cache[rev_key]
        if rev_price is None:
            return quantity_minor  # fallback: assume 1:1
        # Invert the rate
        rate = rev_price.denominator / rev_price.numerator
    else:
        rate = price.numerator / price.denominator

    return round(quantity_minor * rate)


def get_pnl(
    db: Session,
    from_date: str,
    to_date: str,
    group_by: str,
    reporting_currency_mnemonic: str,
) -> PnLReport:
    rc = _get_reporting_currency(db, reporting_currency_mnemonic)

    if group_by == "month":
        period_expr = func.strftime("%Y-%m-01", Transaction.date)
    elif group_by == "year":
        period_expr = func.strftime("%Y-01-01", Transaction.date)
    else:
        period_expr = func.strftime("%Y-%m-%d", Transaction.date)

    rows_raw = (
        db.query(
            Account.id,
            Account.full_name,
            Account.account_type,
            Account.commodity_id,
            period_expr.label("period"),
            func.sum(Split.quantity_minor).label("total_qty"),
        )
        .join(Split, Split.account_id == Account.id)
        .join(Transaction, Transaction.id == Split.transaction_id)
        .filter(
            Account.account_type.in_([AccountType.INCOME, AccountType.EXPENSE]),
            Transaction.date >= from_date,
            Transaction.date <= to_date,
        )
        .group_by(Account.id, Account.full_name, Account.account_type, Account.commodity_id, "period")
        .all()
    )

    price_cache: dict = {}
    pnl_rows: list[PnLRow] = []
    for row in rows_raw:
        converted = _convert_to_reporting(
            row.total_qty, row.commodity_id, rc.id, row.period, price_cache, db
        )
        pnl_rows.append(
            PnLRow(
                account_id=row.id,
                account_name=row.full_name,
                account_type=row.account_type.value,
                period=row.period,
                amount_minor=converted,
                reporting_currency=reporting_currency_mnemonic,
            )
        )

    return PnLReport(
        rows=pnl_rows,
        reporting_currency=reporting_currency_mnemonic,
        from_date=from_date,
        to_date=to_date,
    )


def get_balance_history(
    db: Session,
    account_id: int,
    from_date: str,
    to_date: str,
    group_by: str,
    reporting_currency_mnemonic: str,
) -> BalanceHistory:
    account = db.get(Account, account_id)
    if account is None:
        raise ValueError(f"Account {account_id} not found")

    rc = _get_reporting_currency(db, reporting_currency_mnemonic)

    if group_by == "month":
        period_expr = func.strftime("%Y-%m-01", Transaction.date)
    elif group_by == "year":
        period_expr = func.strftime("%Y-01-01", Transaction.date)
    else:
        period_expr = func.strftime("%Y-%m-%d", Transaction.date)

    # Opening balance before from_date
    opening = (
        db.query(func.coalesce(func.sum(Split.quantity_minor), 0))
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(Split.account_id == account_id, Transaction.date < from_date)
        .scalar()
        or 0
    )

    period_deltas = (
        db.query(period_expr.label("period"), func.sum(Split.quantity_minor).label("delta"))
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(
            Split.account_id == account_id,
            Transaction.date >= from_date,
            Transaction.date <= to_date,
        )
        .group_by("period")
        .order_by("period")
        .all()
    )

    price_cache: dict = {}
    points: list[BalancePoint] = []
    running = opening
    for row in period_deltas:
        running += row.delta
        converted = _convert_to_reporting(
            running, account.commodity_id, rc.id, row.period, price_cache, db
        )
        points.append(
            BalancePoint(
                period=row.period,
                balance_minor=converted,
                reporting_currency=reporting_currency_mnemonic,
            )
        )

    return BalanceHistory(
        account_id=account_id,
        account_name=account.full_name,
        points=points,
        reporting_currency=reporting_currency_mnemonic,
    )


def get_net_worth(db: Session, reporting_currency_mnemonic: str) -> NetWorthSnapshot:
    rc = _get_reporting_currency(db, reporting_currency_mnemonic)

    rows = (
        db.query(
            Account.id,
            Account.account_type,
            Account.commodity_id,
            func.coalesce(func.sum(Split.quantity_minor), 0).label("balance"),
        )
        .outerjoin(Split, Split.account_id == Account.id)
        .filter(Account.account_type.in_([AccountType.ASSET, AccountType.LIABILITY]))
        .group_by(Account.id, Account.account_type, Account.commodity_id)
        .all()
    )

    from datetime import date as date_cls
    today = date_cls.today().isoformat()
    price_cache: dict = {}
    assets = 0
    liabilities = 0

    for row in rows:
        converted = _convert_to_reporting(
            row.balance, row.commodity_id, rc.id, today, price_cache, db
        )
        if row.account_type == AccountType.ASSET:
            assets += converted
        else:
            liabilities += converted

    return NetWorthSnapshot(
        assets_minor=assets,
        liabilities_minor=liabilities,
        net_worth_minor=assets + liabilities,
        reporting_currency=reporting_currency_mnemonic,
    )
