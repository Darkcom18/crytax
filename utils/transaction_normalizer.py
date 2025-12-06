"""
Transaction normalizer
Normalizes transactions from different sources (wallet, exchange) to a unified format
"""

from typing import List
from models.transaction import Transaction, TransactionType, TransactionSource
import pandas as pd


class TransactionNormalizer:
    """Normalize transactions from different sources"""

    @staticmethod
    def normalize(transactions: List[Transaction]) -> pd.DataFrame:
        """
        Normalize transactions to DataFrame

        Args:
            transactions: List of Transaction objects

        Returns:
            DataFrame with normalized transactions
        """
        if not transactions:
            return pd.DataFrame()

        # Convert to list of dicts
        data = [tx.to_dict() for tx in transactions]

        # Create DataFrame
        df = pd.DataFrame(data)

        # Ensure date is datetime
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        # Sort by date
        df = df.sort_values("date")

        return df

    @staticmethod
    def classify_transaction_type(transaction: Transaction) -> str:
        """
        Classify transaction for tax purposes

        Returns:
            'transfer' for buy/sell/swap, 'other_income' for staking/airdrop/farming
        """
        if transaction.type in [
            TransactionType.BUY,
            TransactionType.SELL,
            TransactionType.SWAP,
        ]:
            return "transfer"
        elif transaction.type in [
            TransactionType.STAKING_REWARD,
            TransactionType.AIRDROP,
            TransactionType.FARMING,
        ]:
            return "other_income"
        else:
            return "transfer"  # Default

    @staticmethod
    def filter_taxable_transactions(
        transactions: List[Transaction],
    ) -> List[Transaction]:
        """
        Filter transactions that are taxable

        Returns:
            List of taxable transactions
        """
        taxable_types = [
            TransactionType.BUY,
            TransactionType.SELL,
            TransactionType.SWAP,
            TransactionType.STAKING_REWARD,
            TransactionType.AIRDROP,
            TransactionType.FARMING,
        ]

        return [tx for tx in transactions if tx.type in taxable_types]
