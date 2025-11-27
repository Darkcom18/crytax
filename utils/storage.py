"""
Storage utilities for saving and loading transactions
"""

import sqlite3
import json
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
        
        # Create table if not exists
        cursor.execute("""
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
                tax_amount REAL
            )
        """)
        
        # Clear existing data (for MVP, we'll replace all)
        cursor.execute("DELETE FROM transactions")
        
        # Insert transactions
        for tx in transactions:
            cursor.execute("""
                INSERT INTO transactions (
                    date, type, token, amount, price_vnd, value_vnd,
                    source, chain, wallet_address, exchange_name,
                    tx_hash, fee_vnd, cost_basis, profit_loss, tax_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            ))
        
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

