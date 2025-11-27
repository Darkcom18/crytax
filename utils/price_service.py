"""
Price service for getting cryptocurrency prices and converting to VND
"""

import requests
from typing import Optional, Dict
from datetime import datetime
import config


class PriceService:
    """Service for fetching cryptocurrency prices"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.COINGECKO_API_KEY
        self.base_url = config.COINGECKO_API_URL
        self._price_cache: Dict[str, Dict] = {}
    
    def get_usd_to_vnd_rate(self) -> float:
        """
        Get USD to VND exchange rate
        Using CoinGecko or a fixed rate as fallback
        """
        # For MVP, use a fixed rate or fetch from CoinGecko
        # CoinGecko doesn't directly support VND, so we'll use a fixed rate
        # In production, you might want to use a currency API
        return 25000.0  # Approximate USD to VND rate
    
    def get_crypto_price_usd(self, token_symbol: str, date: Optional[datetime] = None) -> Optional[float]:
        """
        Get cryptocurrency price in USD
        
        Args:
            token_symbol: Token symbol (BTC, ETH, etc.)
            date: Optional date for historical price
            
        Returns:
            Price in USD or None if not found
        """
        # Map common token symbols to CoinGecko IDs
        token_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "BNB": "binancecoin",
            "USDT": "tether",
            "USDC": "usd-coin",
            "MATIC": "matic-network",
            "SOL": "solana",
            "ADA": "cardano",
            "DOT": "polkadot",
            "AVAX": "avalanche-2",
        }
        
        coin_id = token_map.get(token_symbol.upper())
        if not coin_id:
            # Try using symbol directly
            coin_id = token_symbol.lower()
        
        cache_key = f"{coin_id}_{date.date() if date else 'latest'}"
        if cache_key in self._price_cache:
            return self._price_cache[cache_key].get("usd")
        
        try:
            if date:
                # Historical price
                date_str = date.strftime("%d-%m-%Y")
                url = f"{self.base_url}/coins/{coin_id}/history"
                params = {"date": date_str}
            else:
                # Current price
                url = f"{self.base_url}/simple/price"
                params = {"ids": coin_id, "vs_currencies": "usd"}
            
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if date:
                price = data.get("market_data", {}).get("current_price", {}).get("usd")
            else:
                price = data.get(coin_id, {}).get("usd")
            
            if price:
                self._price_cache[cache_key] = {"usd": price}
                return price
            else:
                return None
        except Exception as e:
            print(f"Error fetching price for {token_symbol}: {e}")
            return None
    
    def get_crypto_price_vnd(self, token_symbol: str, date: Optional[datetime] = None) -> Optional[float]:
        """
        Get cryptocurrency price in VND
        
        Args:
            token_symbol: Token symbol
            date: Optional date for historical price
            
        Returns:
            Price in VND or None if not found
        """
        usd_price = self.get_crypto_price_usd(token_symbol, date)
        if usd_price is None:
            return None
        
        vnd_rate = self.get_usd_to_vnd_rate()
        return usd_price * vnd_rate
    
    def convert_value_to_vnd(self, token_symbol: str, amount: float, date: Optional[datetime] = None) -> Optional[float]:
        """
        Convert cryptocurrency amount to VND value
        
        Args:
            token_symbol: Token symbol
            amount: Token amount
            date: Optional date for historical price
            
        Returns:
            Value in VND or None if price not found
        """
        price_vnd = self.get_crypto_price_vnd(token_symbol, date)
        if price_vnd is None:
            return None
        
        return amount * price_vnd


# Global instance
_price_service = None


def get_price_service() -> PriceService:
    """Get global price service instance"""
    global _price_service
    if _price_service is None:
        _price_service = PriceService()
    return _price_service

