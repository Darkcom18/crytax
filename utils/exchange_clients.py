"""
Exchange API clients
Binance and other exchanges
"""

from typing import List, Dict, Optional
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException


class BinanceClient:
    """Client for Binance API"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Binance client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet (default: False)
        """
        self.client = Client(api_key, api_secret, testnet=testnet)
    
    def get_trades(self, symbol: Optional[str] = None, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Get all trades (spot)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT'), None for all
            start_time: Start time
            end_time: End time
            
        Returns:
            List of trade dictionaries
        """
        try:
            if symbol:
                trades = self.client.get_my_trades(symbol=symbol)
            else:
                # Get all account trades
                # Note: This requires getting all symbols first
                trades = []
                # For MVP, we'll need to specify symbols or get from account
                # This is a simplified version
                pass
            
            # Convert to standard format
            result = []
            for trade in trades:
                result.append({
                    "id": trade.get("id"),
                    "symbol": trade.get("symbol"),
                    "price": float(trade.get("price", 0)),
                    "qty": float(trade.get("qty", 0)),
                    "quoteQty": float(trade.get("quoteQty", 0)),
                    "time": trade.get("time"),
                    "isBuyer": trade.get("isBuyer"),
                    "commission": float(trade.get("commission", 0)),
                    "commissionAsset": trade.get("commissionAsset"),
                })
            
            return result
        except BinanceAPIException as e:
            print(f"Binance API error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching Binance trades: {e}")
            return []
    
    def get_all_trades(self, start_time: Optional[datetime] = None, 
                       end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Get all trades from all symbols
        
        Note: This is expensive and may hit rate limits
        For MVP, consider limiting to specific symbols or time ranges
        """
        all_trades = []
        
        try:
            # Get account info to get all trading pairs
            account_info = self.client.get_account()
            
            # Get balances to find which symbols user has traded
            balances = account_info.get("balances", [])
            
            # For each balance, try to get trades
            # This is simplified - in production, you'd want to cache and optimize
            symbols_traded = set()
            
            # Get recent trades to determine which symbols were traded
            # This is a workaround - ideally Binance would provide a list of all traded symbols
            # For MVP, we'll need user to specify symbols or use a different approach
            
            return all_trades
        except Exception as e:
            print(f"Error fetching all Binance trades: {e}")
            return []
    
    def get_deposits(self, start_time: Optional[datetime] = None, 
                     end_time: Optional[datetime] = None) -> List[Dict]:
        """Get deposit history"""
        try:
            deposits = self.client.get_deposit_history()
            return deposits
        except Exception as e:
            print(f"Error fetching Binance deposits: {e}")
            return []
    
    def get_withdrawals(self, start_time: Optional[datetime] = None, 
                        end_time: Optional[datetime] = None) -> List[Dict]:
        """Get withdrawal history"""
        try:
            withdrawals = self.client.get_withdraw_history()
            return withdrawals
        except Exception as e:
            print(f"Error fetching Binance withdrawals: {e}")
            return []
    
    def get_staking_rewards(self) -> List[Dict]:
        """Get staking rewards"""
        try:
            # Binance staking rewards might be in different endpoints
            # This is a placeholder - actual implementation depends on Binance API
            return []
        except Exception as e:
            print(f"Error fetching Binance staking rewards: {e}")
            return []


def create_binance_client(api_key: str, api_secret: str, testnet: bool = False) -> BinanceClient:
    """Create a Binance client instance"""
    return BinanceClient(api_key, api_secret, testnet)

