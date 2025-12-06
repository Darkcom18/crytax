"""
Storage utilities for saving and loading transactions
"""

import sqlite3
import pandas as pd
from typing import List, Optional
from datetime import datetime
from models.transaction import Transaction, TransactionType, TransactionSource
import config


class TransactionStorage:
    """Storage for transactions"""

    def __init__(self, storage_type: str = None):
        self.storage_type = storage_type or config.STORAGE_TYPE
        self.db_path = config.DATABASE_PATH
        self.csv_path = config.CSV_PATH
        self._init_table()

    def _init_table(self):
        """Initialize price cache table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT,
                token TEXT,
                amount REAL,
                price_vnd REAL,
                value_vnd REAL,
                source TEXT,
                chain TEXT,
                wallet_address TEXT,
                exchange_name TEXT,
                tx_hash TEXT,
                fee_vnd REAL,
                cost_basis REAL,
                profit_loss REAL,
                tax_amount REAL,
                token_out TEXT,
                amount_out REAL,
                value_out_vnd REAL
            )
         """
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing price cache: {e}")

    def save_transactions(self, transactions: List[Transaction]):
        """Save transactions to storage"""
        if self.storage_type == "sqlite":
            self._save_to_sqlite(transactions)
        else:
            self._save_to_csv(transactions)

    def load_transactions(self) -> List[Transaction]:
        """Load transactions from storage"""
        if self.storage_type == "sqlite":
            return self._load_from_sqlite()
        else:
            return self._load_from_csv()

    def _save_to_sqlite(self, transactions: List[Transaction]):
        """Save to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert transactions
        for tx in transactions:
            cursor.execute(
                """
                INSERT INTO transactions (
                    date, type, token, amount, price_vnd, value_vnd,
                    source, chain, wallet_address, exchange_name,
                    tx_hash, fee_vnd, cost_basis, profit_loss, tax_amount,
                    token_out, amount_out, value_out_vnd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    tx.date.isoformat(),
                    tx.type.value,
                    tx.token,
                    tx.amount,
                    tx.price_vnd,
                    tx.value_vnd,
                    tx.source.value,
                    tx.chain,
                    tx.wallet_address,
                    tx.exchange_name,
                    tx.tx_hash,
                    tx.fee_vnd,
                    tx.cost_basis,
                    tx.profit_loss,
                    tx.tax_amount,
                    tx.token_out,
                    tx.amount_out,
                    tx.value_out_vnd,
                ),
            )

        conn.commit()
        conn.close()

    def _load_from_sqlite(self) -> List[Transaction]:
        """Load from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM transactions")
            rows = cursor.fetchall()

            transactions = []
            for row in rows:
                tx_dict = {
                    "date": row[1],
                    "type": row[2],
                    "token": row[3],
                    "amount": row[4],
                    "price_vnd": row[5],
                    "value_vnd": row[6],
                    "source": row[7],
                    "chain": row[8],
                    "wallet_address": row[9],
                    "exchange_name": row[10],
                    "tx_hash": row[11],
                    "fee_vnd": row[12],
                    "cost_basis": row[13],
                    "profit_loss": row[14],
                    "tax_amount": row[15],
                    "token_out": row[16] if len(row) > 16 else None,
                    "amount_out": row[17] if len(row) > 17 else None,
                    "value_out_vnd": row[18] if len(row) > 18 else None,
                }
                transactions.append(Transaction.from_dict(tx_dict))

            conn.close()
            return transactions
        except Exception as e:
            print(f"Error loading from SQLite: {e}")
            return []

    def _save_to_csv(self, transactions: List[Transaction]):
        """Save to CSV file"""
        if not transactions:
            return

        df = pd.DataFrame([tx.to_dict() for tx in transactions])
        df.to_csv(self.csv_path, index=False)

    def _load_from_csv(self) -> List[Transaction]:
        """Load from CSV file"""
        try:
            df = pd.read_csv(self.csv_path)
            transactions = []
            for _, row in df.iterrows():
                transactions.append(Transaction.from_dict(row.to_dict()))
            return transactions
        except Exception as e:
            print(f"Error loading from CSV: {e}")
            return []

    def clear_all(self):
        """Clear all transactions from storage"""
        if self.storage_type == "sqlite":
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions")
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error clearing SQLite: {e}")
        else:
            try:
                import os

                if os.path.exists(self.csv_path):
                    os.remove(self.csv_path)
            except Exception as e:
                print(f"Error clearing CSV: {e}")

    def has_data(self) -> bool:
        """Check if storage has any data"""
        if self.storage_type == "sqlite":
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM transactions")
                count = cursor.fetchone()[0]
                conn.close()
                return count > 0
            except Exception:
                return False
        else:
            try:
                import os

                return os.path.exists(self.csv_path)
            except Exception:
                return False


# Global storage instance
_storage: Optional[TransactionStorage] = None


def get_storage() -> TransactionStorage:
    """Get global storage instance"""
    global _storage
    if _storage is None:
        _storage = TransactionStorage()
    return _storage


class PriceCache:
    """Cache for cryptocurrency prices in SQLite"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self._init_table()

    def _init_table(self):
        """Initialize price cache table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS price_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL,
                    date TEXT NOT NULL,
                    price_usd REAL,
                    price_vnd REAL,
                    cached_at TEXT,
                    UNIQUE(token, date)
                )
            """
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing price cache: {e}")

    def get_price(self, token: str, date_str: str) -> Optional[dict]:
        """
        Get cached price for token on date

        Args:
            token: Token symbol (e.g., 'BTC')
            date_str: Date string (YYYY-MM-DD)

        Returns:
            {'price_usd': float, 'price_vnd': float} or None if not cached
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT price_usd, price_vnd FROM price_cache WHERE token = ? AND date = ?",
                (token.upper(), date_str),
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return {"price_usd": row[0], "price_vnd": row[1]}
            return None
        except Exception as e:
            print(f"Error getting cached price: {e}")
            return None

    def set_price(self, token: str, date_str: str, price_usd: float, price_vnd: float):
        """
        Cache price for token on date

        Args:
            token: Token symbol
            date_str: Date string (YYYY-MM-DD)
            price_usd: Price in USD
            price_vnd: Price in VND
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO price_cache (token, date, price_usd, price_vnd, cached_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    token.upper(),
                    date_str,
                    price_usd,
                    price_vnd,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error caching price: {e}")

    def clear_cache(self):
        """Clear all cached prices"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM price_cache")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error clearing price cache: {e}")


# Global price cache instance
_price_cache: Optional[PriceCache] = None


def get_price_cache() -> PriceCache:
    """Get global price cache instance"""
    global _price_cache
    if _price_cache is None:
        _price_cache = PriceCache()
    return _price_cache
