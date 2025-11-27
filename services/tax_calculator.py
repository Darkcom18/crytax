"""
Tax calculator for cryptocurrency transactions
Implements FIFO method and Vietnam tax regulations
"""

from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict, deque
from models.transaction import Transaction, TransactionType, TransactionSource
from utils.transaction_normalizer import TransactionNormalizer
import config
import pandas as pd


class FIFOCostBasis:
    """FIFO cost basis tracker for each token"""
    
    def __init__(self):
        # Dictionary: token -> deque of (amount, price, date)
        self.inventory: Dict[str, deque] = defaultdict(deque)
    
    def add_purchase(self, token: str, amount: float, price: float, date: datetime):
        """Add a purchase to inventory"""
        self.inventory[token].append((amount, price, date))
    
    def calculate_cost_basis(self, token: str, sell_amount: float) -> tuple:
        """
        Calculate cost basis for a sale using FIFO
        
        Args:
            token: Token symbol
            sell_amount: Amount being sold
            
        Returns:
            (cost_basis, remaining_amount) where remaining_amount is unsold
        """
        if token not in self.inventory or not self.inventory[token]:
            # No inventory, assume cost basis is 0 (airdrop, etc.)
            return (0.0, sell_amount)
        
        cost_basis = 0.0
        remaining = sell_amount
        
        while remaining > 0 and self.inventory[token]:
            amount, price, _ = self.inventory[token][0]
            
            if amount <= remaining:
                # Use entire lot
                cost_basis += amount * price
                remaining -= amount
                self.inventory[token].popleft()
            else:
                # Use partial lot
                cost_basis += remaining * price
                self.inventory[token][0] = (amount - remaining, price, _)
                remaining = 0
        
        return (cost_basis, remaining)
    
    def get_remaining_inventory(self, token: str) -> float:
        """Get remaining inventory for a token"""
        if token not in self.inventory:
            return 0.0
        return sum(amount for amount, _, _ in self.inventory[token])


class TaxCalculator:
    """Calculate taxes for cryptocurrency transactions"""
    
    def __init__(self):
        self.fifo = FIFOCostBasis()
        self.normalizer = TransactionNormalizer()
    
    def calculate_taxes(self, transactions: List[Transaction]) -> pd.DataFrame:
        """
        Calculate taxes for all transactions
        
        Args:
            transactions: List of Transaction objects
            
        Returns:
            DataFrame with transactions and calculated taxes
        """
        # Filter taxable transactions
        taxable_txs = self.normalizer.filter_taxable_transactions(transactions)
        
        # Sort by date
        taxable_txs.sort(key=lambda x: x.date)
        
        # Process each transaction
        results = []
        
        for tx in taxable_txs:
            result = self._process_transaction(tx)
            if result:
                results.append(result)
        
        # Create DataFrame
        if results:
            df = pd.DataFrame(results)
            return df
        else:
            return pd.DataFrame()
    
    def _process_transaction(self, tx: Transaction) -> Optional[Dict]:
        """Process a single transaction and calculate tax"""
        try:
            tx_class = self.normalizer.classify_transaction_type(tx)
            
            if tx.type == TransactionType.BUY:
                # Add to inventory
                self.fifo.add_purchase(tx.token, tx.amount, tx.price_vnd, tx.date)
                return {
                    "transaction": tx,
                    "cost_basis": tx.value_vnd,
                    "profit_loss": 0.0,
                    "tax_amount": 0.0,
                    "tax_type": "transfer",
                }
            
            elif tx.type == TransactionType.SELL:
                # Calculate cost basis using FIFO
                cost_basis, remaining = self.fifo.calculate_cost_basis(tx.token, tx.amount)
                
                if remaining > 0:
                    # Partial sale, adjust
                    actual_amount = tx.amount - remaining
                    actual_value = (actual_amount / tx.amount) * tx.value_vnd
                    cost_basis = (actual_amount / tx.amount) * cost_basis
                else:
                    actual_value = tx.value_vnd
                
                profit_loss = actual_value - cost_basis
                tax_amount = actual_value * config.TAX_RATES["transfer"]
                
                return {
                    "transaction": tx,
                    "cost_basis": cost_basis,
                    "profit_loss": profit_loss,
                    "tax_amount": tax_amount,
                    "tax_type": "transfer",
                }
            
            elif tx.type == TransactionType.SWAP:
                # Swap: sell token A, buy token B
                # First, calculate sale of token A
                # For simplicity, assume we know which token is being sold
                # In practice, you'd need to parse swap details
                
                # For MVP, treat swap as sell + buy
                # This is simplified - real swaps need more complex logic
                cost_basis = 0.0  # Would need to determine from swap details
                profit_loss = 0.0  # Would need to calculate
                tax_amount = tx.value_vnd * config.TAX_RATES["transfer"]
                
                return {
                    "transaction": tx,
                    "cost_basis": cost_basis,
                    "profit_loss": profit_loss,
                    "tax_amount": tax_amount,
                    "tax_type": "transfer",
                }
            
            elif tx.type in [TransactionType.STAKING_REWARD, TransactionType.AIRDROP, TransactionType.FARMING]:
                # Other income: 10% tax
                tax_amount = tx.value_vnd * config.TAX_RATES["other_income"]
                
                return {
                    "transaction": tx,
                    "cost_basis": 0.0,
                    "profit_loss": tx.value_vnd,  # Full amount is profit
                    "tax_amount": tax_amount,
                    "tax_type": "other_income",
                }
            
            else:
                return None
                
        except Exception as e:
            print(f"Error processing transaction: {e}")
            return None
    
    def get_tax_summary(self, transactions: List[Transaction]) -> Dict:
        """
        Get tax summary for all transactions
        
        Returns:
            Dictionary with tax summary
        """
        df = self.calculate_taxes(transactions)
        
        if df.empty:
            return {
                "total_transactions": 0,
                "total_transfer_tax": 0.0,
                "total_other_income_tax": 0.0,
                "total_tax": 0.0,
                "total_profit_loss": 0.0,
            }
        
        transfer_tax = df[df["tax_type"] == "transfer"]["tax_amount"].sum()
        other_income_tax = df[df["tax_type"] == "other_income"]["tax_amount"].sum()
        total_profit_loss = df["profit_loss"].sum()
        
        # Group by token for summary
        by_token = {}
        for _, row in df.iterrows():
            token = row["transaction"].token
            if token not in by_token:
                by_token[token] = 0.0
            by_token[token] += row["tax_amount"]
        
        return {
            "total_transactions": len(df),
            "total_transfer_tax": float(transfer_tax),
            "total_other_income_tax": float(other_income_tax),
            "total_tax": float(transfer_tax + other_income_tax),
            "total_profit_loss": float(total_profit_loss),
            "by_token": by_token,
        }
    
    def get_tax_by_period(self, transactions: List[Transaction], period: str = "month") -> pd.DataFrame:
        """
        Get tax breakdown by time period
        
        Args:
            transactions: List of transactions
            period: 'month', 'quarter', or 'year'
            
        Returns:
            DataFrame with tax by period
        """
        df = self.calculate_taxes(transactions)
        
        if df.empty:
            return pd.DataFrame()
        
        # Add period column
        if period == "month":
            df["period"] = df["transaction"].apply(lambda x: x.date.strftime("%Y-%m"))
        elif period == "quarter":
            df["period"] = df["transaction"].apply(
                lambda x: f"{x.date.year}-Q{(x.date.month-1)//3 + 1}"
            )
        elif period == "year":
            df["period"] = df["transaction"].apply(lambda x: str(x.date.year))
        
        # Group by period
        summary = df.groupby("period").agg({
            "tax_amount": "sum",
            "profit_loss": "sum",
        }).reset_index()
        
        return summary

