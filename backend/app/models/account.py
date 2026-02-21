import enum
from typing import Optional, List
from sqlalchemy import Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class AccountType(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, default="")
    placeholder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    commodity_id: Mapped[int] = mapped_column(Integer, ForeignKey("commodities.id"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=True)

    commodity: Mapped["Commodity"] = relationship("Commodity", back_populates="accounts")  # noqa: F821
    parent: Mapped[Optional["Account"]] = relationship("Account", remote_side=[id], back_populates="children")
    children: Mapped[List["Account"]] = relationship("Account", back_populates="parent", cascade="all, delete-orphan")
    splits: Mapped[List["Split"]] = relationship("Split", back_populates="account")  # noqa: F821
