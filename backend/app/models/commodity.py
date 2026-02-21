from typing import List
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Commodity(Base):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mnemonic: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    fraction: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="commodity")  # noqa: F821
    prices_from: Mapped[List["Price"]] = relationship(
        "Price", foreign_keys="Price.commodity_id", back_populates="commodity"
    )
    prices_to: Mapped[List["Price"]] = relationship(
        "Price", foreign_keys="Price.currency_id", back_populates="currency"
    )
    transactions: Mapped[List["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="currency"
    )


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    commodity_id: Mapped[int] = mapped_column(Integer, ForeignKey("commodities.id"), nullable=False)
    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("commodities.id"), nullable=False)
    numerator: Mapped[int] = mapped_column(Integer, nullable=False)
    denominator: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="user")

    commodity: Mapped["Commodity"] = relationship(
        "Commodity", foreign_keys=[commodity_id], back_populates="prices_from"
    )
    currency: Mapped["Commodity"] = relationship(
        "Commodity", foreign_keys=[currency_id], back_populates="prices_to"
    )
