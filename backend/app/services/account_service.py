from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from ..models.account import Account
from ..models.transaction import Split
from ..schemas.account import AccountCreate, AccountUpdate, AccountTreeNode


def _compute_full_name(db: Session, account: Account) -> str:
    parts = [account.name]
    current = account
    while current.parent_id is not None:
        parent = db.get(Account, current.parent_id)
        if parent is None:
            break
        parts.append(parent.name)
        current = parent
    return ":".join(reversed(parts))


def create_account(db: Session, data: AccountCreate) -> Account:
    account = Account(
        name=data.name,
        full_name="",  # set below
        account_type=data.account_type,
        description=data.description,
        placeholder=data.placeholder,
        commodity_id=data.commodity_id,
        parent_id=data.parent_id,
    )
    db.add(account)
    db.flush()  # get id
    account.full_name = _compute_full_name(db, account)
    db.commit()
    db.refresh(account)
    return account


def get_account(db: Session, account_id: int) -> Account:
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def list_accounts(db: Session) -> List[Account]:
    return db.query(Account).order_by(Account.full_name).all()


def update_account(db: Session, account_id: int, data: AccountUpdate) -> Account:
    account = get_account(db, account_id)
    if data.name is not None:
        account.name = data.name
    if data.description is not None:
        account.description = data.description
    if data.placeholder is not None:
        account.placeholder = data.placeholder
    if data.parent_id is not None:
        account.parent_id = data.parent_id
    db.flush()
    # Recompute full_name for this account and all descendants
    _recompute_subtree_full_names(db, account)
    db.commit()
    db.refresh(account)
    return account


def _recompute_subtree_full_names(db: Session, account: Account) -> None:
    account.full_name = _compute_full_name(db, account)
    for child in account.children:
        _recompute_subtree_full_names(db, child)


def delete_account(db: Session, account_id: int) -> None:
    account = get_account(db, account_id)
    if account.children:
        raise HTTPException(status_code=400, detail="Cannot delete account with children")
    split_count = db.query(func.count(Split.id)).filter(Split.account_id == account_id).scalar()
    if split_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete account with transactions")
    db.delete(account)
    db.commit()


def get_balance(db: Session, account_id: int) -> int:
    """Returns sum of quantity_minor for all splits in this account (native commodity)."""
    result = (
        db.query(func.coalesce(func.sum(Split.quantity_minor), 0))
        .filter(Split.account_id == account_id)
        .scalar()
    )
    return result or 0


def get_register(db: Session, account_id: int, limit: int = 100, offset: int = 0):
    """Returns splits with transaction info, ordered by date."""
    from ..models.transaction import Transaction

    splits = (
        db.query(Split)
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(Split.account_id == account_id)
        .order_by(Transaction.date, Transaction.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    # Compute running balance
    total_before = (
        db.query(func.coalesce(func.sum(Split.quantity_minor), 0))
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(Split.account_id == account_id)
        .filter(
            (Transaction.date < db.query(Transaction.date)
             .filter(Transaction.id == splits[0].transaction_id)
             .scalar_subquery()) if splits else False
        )
        .scalar()
        or 0
    ) if splits else 0

    running = total_before
    result = []
    for split in splits:
        running += split.quantity_minor
        result.append({"split": split, "running_balance": running})
    return result


def build_tree(accounts: List[Account]) -> List[AccountTreeNode]:
    """Build a forest of AccountTreeNode from a flat list."""
    by_id: dict = {}
    for acc in accounts:
        node = AccountTreeNode.model_validate(acc)
        node.children = []  # reset — we rebuild children ourselves below
        by_id[acc.id] = node

    roots: List[AccountTreeNode] = []
    for node in by_id.values():
        if node.parent_id is None:
            roots.append(node)
        elif node.parent_id in by_id:
            by_id[node.parent_id].children.append(node)

    return sorted(roots, key=lambda n: n.full_name)
