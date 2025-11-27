"""
Exchange service for fetching transactions from exchanges
Currently supports Binance
"""

from typing import List, Optional
from datetime import datetime
from models.transaction import Transaction, TransactionType, TransactionSource
from utils.exchange_clients import BinanceClient, create_binance_client
from utils.price_service import get_price_service


class ExchangeService:
    """Service for fetching and processing exchange transactions"""
    
    def __init__(self):
        self.price_service = get_price_service()
    
    def fetch_binance_transactions(self, api_key: str, api_secret: str, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> List[Transaction]:
        """
        Fetch transactions from Binance
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of Transaction objects
        """
        try:
            client = create_binance_client(api_key, api_secret)
            transactions = []
            
            # Fetch trades
            # Note: get_trades() without symbol requires getting all symbols first
            # For MVP, we'll need to handle this differently
            # For now, return empty list and user can upload CSV
            trades = []  # client.get_trades() - needs symbol parameter
            # TODO: Implement getting all trades by iterating through symbols
            for trade in trades:
                tx = self._parse_binance_trade(trade)
                if tx:
                    transactions.append(tx)
            
            # Fetch deposits
            deposits = client.get_deposits()
            for deposit in deposits:
                tx = self._parse_binance_deposit(deposit)
                if tx:
                    transactions.append(tx)
            
            # Fetch withdrawals
            withdrawals = client.get_withdrawals()
            for withdrawal in withdrawals:
                tx = self._parse_binance_withdrawal(withdrawal)
                if tx:
                    transactions.append(tx)
            
            # Filter by date if provided
            if start_date or end_date:
                transactions = [
                    tx for tx in transactions
                    if (not start_date or tx.date >= start_date) and
                       (not end_date or tx.date <= end_date)
                ]
            
            return transactions
            
        except Exception as e:
            print(f"Error fetching Binance transactions: {e}")
            return []
    
    def _parse_binance_trade(self, trade: dict) -> Optional[Transaction]:
        """Parse Binance trade to Transaction"""
        try:
            symbol = trade.get("symbol", "")
            base_token = symbol.replace("USDT", "").replace("BUSD", "").replace("BTC", "").replace("ETH", "")
            quote_token = "USDT" if "USDT" in symbol else ("BUSD" if "BUSD" in symbol else "BTC")
            
            # Determine transaction type
            is_buyer = trade.get("isBuyer", False)
            tx_type = TransactionType.BUY if is_buyer else TransactionType.SELL
            
            # Get token and amount
            if is_buyer:
                token = base_token
                amount = trade.get("qty", 0)
            else:
                token = quote_token
                amount = trade.get("quoteQty", 0) / trade.get("price", 1)
            
            # Get price and value
            price = trade.get("price", 0)
            value = trade.get("quoteQty", 0)
            
            # Convert to VND
            price_vnd = self.price_service.get_crypto_price_vnd(
                token, 
                datetime.fromtimestamp(trade.get("time", 0) / 1000)
            ) or 0
            
            value_vnd = self.price_service.convert_value_to_vnd(
                quote_token,
                value,
                datetime.fromtimestamp(trade.get("time", 0) / 1000)
            ) or 0
            
            # Transaction date
            tx_date = datetime.fromtimestamp(trade.get("time", 0) / 1000)
            
            return Transaction(
                date=tx_date,
                type=tx_type,
                token=token,
                amount=float(amount),
                price_vnd=price_vnd,
                value_vnd=value_vnd,
                source=TransactionSource.EXCHANGE,
                exchange_name="Binance",
                chain="Binance",
                tx_hash=str(trade.get("id", "")),
                fee_vnd=self.price_service.convert_value_to_vnd(
                    trade.get("commissionAsset", "BNB"),
                    trade.get("commission", 0),
                    tx_date
                ) or 0
            )
        except Exception as e:
            print(f"Error parsing Binance trade: {e}")
            return None
    
    def _parse_binance_deposit(self, deposit: dict) -> Optional[Transaction]:
        """Parse Binance deposit to Transaction"""
        try:
            token = deposit.get("coin", "")
            amount = float(deposit.get("amount", 0))
            
            tx_date = datetime.fromtimestamp(deposit.get("insertTime", 0) / 1000)
            
            price_vnd = self.price_service.get_crypto_price_vnd(token, tx_date) or 0
            value_vnd = amount * price_vnd
            
            return Transaction(
                date=tx_date,
                type=TransactionType.DEPOSIT,
                token=token,
                amount=amount,
                price_vnd=price_vnd,
                value_vnd=value_vnd,
                source=TransactionSource.EXCHANGE,
                exchange_name="Binance",
                chain="Binance",
                tx_hash=deposit.get("txId", "")
            )
        except Exception as e:
            print(f"Error parsing Binance deposit: {e}")
            return None
    
    def _parse_binance_withdrawal(self, withdrawal: dict) -> Optional[Transaction]:
        """Parse Binance withdrawal to Transaction"""
        try:
            token = withdrawal.get("coin", "")
            amount = float(withdrawal.get("amount", 0))
            
            tx_date = datetime.fromtimestamp(withdrawal.get("applyTime", 0) / 1000)
            
            price_vnd = self.price_service.get_crypto_price_vnd(token, tx_date) or 0
            value_vnd = amount * price_vnd
            
            return Transaction(
                date=tx_date,
                type=TransactionType.WITHDRAWAL,
                token=token,
                amount=amount,
                price_vnd=price_vnd,
                value_vnd=value_vnd,
                source=TransactionSource.EXCHANGE,
                exchange_name="Binance",
                chain="Binance",
                tx_hash=withdrawal.get("txId", ""),
                fee_vnd=self.price_service.convert_value_to_vnd(
                    token,
                    float(withdrawal.get("transactionFee", 0)),
                    tx_date
                ) or 0
            )
        except Exception as e:
            print(f"Error parsing Binance withdrawal: {e}")
            return None

