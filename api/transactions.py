"""
Transaction API
Handles all transaction-related operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from api.base import BaseAPI, APIResponse
from models.transaction import Transaction, TransactionType, TransactionSource


@dataclass
class TransactionFilter:
    """Filter criteria for transactions"""

    source: Optional[TransactionSource] = None
    token: Optional[str] = None
    tx_type: Optional[TransactionType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class TransactionStats:
    """Transaction statistics"""

    total_count: int
    by_source: Dict[str, int]
    by_token: Dict[str, int]
    by_type: Dict[str, int]
    total_value_vnd: float


class TransactionAPI(BaseAPI):
    """
    API for transaction management.
    Independent of any UI framework.
    """

    def __init__(self, container):
        super().__init__(container)
        self._transactions: List[Transaction] = []
        self._loaded = False

    def _ensure_loaded(self):
        """Load transactions from storage if not already loaded"""
        if not self._loaded:
            stored = self.container.storage.load_transactions()
            self._transactions = stored
            self._loaded = True

    # CRUD Operations

    def get_all(self) -> APIResponse[List[Transaction]]:
        """Get all transactions"""
        self._ensure_loaded()
        return APIResponse.ok(self._transactions.copy())

    def get_filtered(self, filter: TransactionFilter) -> APIResponse[List[Transaction]]:
        """Get transactions with filter"""
        self._ensure_loaded()

        filtered = self._transactions.copy()

        if filter.source:
            filtered = [tx for tx in filtered if tx.source == filter.source]

        if filter.token:
            filtered = [tx for tx in filtered if tx.token == filter.token]

        if filter.tx_type:
            filtered = [tx for tx in filtered if tx.type == filter.tx_type]

        if filter.start_date:
            filtered = [tx for tx in filtered if tx.date >= filter.start_date]

        if filter.end_date:
            filtered = [tx for tx in filtered if tx.date <= filter.end_date]

        return APIResponse.ok(filtered)

    def add(self, transaction: Transaction) -> APIResponse[Transaction]:
        """Add a single transaction"""
        self._ensure_loaded()
        self._transactions.append(transaction)
        return APIResponse.ok(transaction, "Transaction added")

    def add_many(self, transactions: List[Transaction]) -> APIResponse[int]:
        """Add multiple transactions"""
        self._ensure_loaded()
        self._transactions.extend(transactions)
        return APIResponse.ok(
            len(transactions), f"Added {len(transactions)} transactions"
        )

    def clear_all(self) -> APIResponse[None]:
        """Clear all transactions"""
        self._transactions = []
        self.container.storage.clear_all()
        return APIResponse.ok(message="All transactions cleared")

    def get_count(self) -> int:
        """Get total transaction count"""
        self._ensure_loaded()
        return len(self._transactions)

    # Persistence
    def save(self) -> APIResponse[None]:
        """Save transactions to storage"""
        try:
            self.container.storage.save_transactions(self._transactions)
            return APIResponse.ok(message="Transactions saved")
        except Exception as e:
            return APIResponse.error(f"Failed to save: {str(e)}")

    def reload(self) -> APIResponse[int]:
        """Reload transactions from storage"""
        try:
            self._transactions = self.container.storage.load_transactions()
            self._loaded = True
            return APIResponse.ok(len(self._transactions), "Transactions reloaded")
        except Exception as e:
            return APIResponse.error(f"Failed to reload: {str(e)}")

    # Statistics

    def get_stats(self) -> APIResponse[TransactionStats]:
        """Get transaction statistics"""
        self._ensure_loaded()

        by_source = {}
        by_token = {}
        by_type = {}
        total_value = 0.0

        for tx in self._transactions:
            # By source
            source_key = tx.source.value
            by_source[source_key] = by_source.get(source_key, 0) + 1

            # By token
            by_token[tx.token] = by_token.get(tx.token, 0) + 1

            # By type
            type_key = tx.type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Total value
            total_value += tx.value_vnd or 0

        stats = TransactionStats(
            total_count=len(self._transactions),
            by_source=by_source,
            by_token=by_token,
            by_type=by_type,
            total_value_vnd=total_value,
        )

        return APIResponse.ok(stats)

    def get_unique_tokens(self) -> List[str]:
        """Get list of unique tokens"""
        self._ensure_loaded()
        return list(set(tx.token for tx in self._transactions))

    def get_unique_types(self) -> List[str]:
        """Get list of unique transaction types"""
        self._ensure_loaded()
        return list(set(tx.type.value for tx in self._transactions))
