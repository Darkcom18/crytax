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
        Get all trades from all symbols that user has balance or traded

        Note: This iterates through symbols with non-zero balance
        """
        all_trades = []

        try:
            # Get account info to find assets with balance
            account_info = self.client.get_account()
            balances = account_info.get("balances", [])

            # Find assets with non-zero balance (free or locked)
            assets_with_balance = []
            for balance in balances:
                free = float(balance.get("free", 0))
                locked = float(balance.get("locked", 0))
                if free > 0 or locked > 0:
                    assets_with_balance.append(balance.get("asset"))

            # Common quote currencies to try
            quote_currencies = ["USDT", "BUSD", "BTC", "ETH", "BNB"]

            # Build list of symbols to check
            symbols_to_check = set()
            for asset in assets_with_balance:
                if asset in quote_currencies:
                    continue  # Skip quote currencies themselves
                for quote in quote_currencies:
                    symbols_to_check.add(f"{asset}{quote}")

            # Also add some common pairs for assets that might have zero balance now
            common_assets = ["BTC", "ETH", "BNB", "SOL", "ADA", "DOT", "AVAX", "MATIC"]
            for asset in common_assets:
                for quote in ["USDT", "BUSD"]:
                    symbols_to_check.add(f"{asset}{quote}")

            # Get exchange info to validate symbols exist
            exchange_info = self.client.get_exchange_info()
            valid_symbols = {s["symbol"] for s in exchange_info.get("symbols", [])}

            # Fetch trades for each valid symbol
            for symbol in symbols_to_check:
                if symbol not in valid_symbols:
                    continue

                try:
                    params = {"symbol": symbol}
                    if start_time:
                        params["startTime"] = int(start_time.timestamp() * 1000)
                    if end_time:
                        params["endTime"] = int(end_time.timestamp() * 1000)

                    trades = self.client.get_my_trades(**params)

                    for trade in trades:
                        all_trades.append({
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
                except BinanceAPIException:
                    # Symbol might not exist or no trades - skip
                    continue
                except Exception:
                    continue

            # Sort by time
            all_trades.sort(key=lambda x: x.get("time", 0))

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

