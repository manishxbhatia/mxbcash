from typing import Optional, List
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True, default="")
    import_ref: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, unique=True)
    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("commodities.id"), nullable=False)

    currency: Mapped["Commodity"] = relationship("Commodity", back_populates="transactions")  # noqa: F821
    splits: Mapped[List["Split"]] = relationship(
        "Split", back_populates="transaction", cascade="all, delete-orphan"
    )


class Split(Base):
    __tablename__ = "splits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("transactions.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    value_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    memo: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, default="")
    reconciled: Mapped[str] = mapped_column(String(1), nullable=False, default="n")

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="splits")
    account: Mapped["Account"] = relationship("Account", back_populates="splits")  # noqa: F821
