"""
Transaction data model
Represents a cryptocurrency transaction from wallet or exchange
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionType(Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"
    SWAP = "swap"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    STAKING_REWARD = "staking_reward"
    AIRDROP = "airdrop"
    FARMING = "farming"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class TransactionSource(Enum):
    """Transaction source"""
    WALLET = "wallet"
    EXCHANGE = "exchange"


@dataclass
class Transaction:
    """
    Transaction data model
    
    Attributes:
        date: Transaction date and time
        type: Transaction type (buy, sell, swap, etc.)
        token: Token symbol (BTC, ETH, USDT, etc.)
        amount: Token amount
        price_vnd: Price per token in VND at transaction time
        value_vnd: Total transaction value in VND
        source: Source of transaction (wallet or exchange)
        wallet_address: Wallet address (if source is wallet)
        exchange_name: Exchange name (if source is exchange)
        chain: Blockchain name (Ethereum, BSC, etc.) or exchange name
        tx_hash: Transaction hash (for blockchain transactions)
        fee_vnd: Transaction fee in VND (optional)
        cost_basis: Cost basis for FIFO calculation (optional)
        profit_loss: Profit/loss in VND (optional)
        tax_amount: Tax amount in VND (optional)
    """
    date: datetime
    type: TransactionType
    token: str
    amount: float
    price_vnd: float
    value_vnd: float
    source: TransactionSource
    chain: str
    wallet_address: Optional[str] = None
    exchange_name: Optional[str] = None
    tx_hash: Optional[str] = None
    fee_vnd: Optional[float] = None
    cost_basis: Optional[float] = None
    profit_loss: Optional[float] = None
    tax_amount: Optional[float] = None
    
    def __post_init__(self):
        """Validate transaction data"""
        if self.source == TransactionSource.WALLET and not self.wallet_address:
            raise ValueError("wallet_address is required for wallet transactions")
        if self.source == TransactionSource.EXCHANGE and not self.exchange_name:
            raise ValueError("exchange_name is required for exchange transactions")
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            "date": self.date.isoformat(),
            "type": self.type.value,
            "token": self.token,
            "amount": self.amount,
            "price_vnd": self.price_vnd,
            "value_vnd": self.value_vnd,
            "source": self.source.value,
            "chain": self.chain,
            "wallet_address": self.wallet_address,
            "exchange_name": self.exchange_name,
            "tx_hash": self.tx_hash,
            "fee_vnd": self.fee_vnd,
            "cost_basis": self.cost_basis,
            "profit_loss": self.profit_loss,
            "tax_amount": self.tax_amount,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create transaction from dictionary"""
        return cls(
            date=datetime.fromisoformat(data["date"]),
            type=TransactionType(data["type"]),
            token=data["token"],
            amount=float(data["amount"]),
            price_vnd=float(data["price_vnd"]),
            value_vnd=float(data["value_vnd"]),
            source=TransactionSource(data["source"]),
            chain=data["chain"],
            wallet_address=data.get("wallet_address"),
            exchange_name=data.get("exchange_name"),
            tx_hash=data.get("tx_hash"),
            fee_vnd=data.get("fee_vnd"),
            cost_basis=data.get("cost_basis"),
            profit_loss=data.get("profit_loss"),
            tax_amount=data.get("tax_amount"),
        )

