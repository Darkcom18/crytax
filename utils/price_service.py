"""
Price service for getting cryptocurrency prices and converting to VND
"""

import requests
from typing import Optional, Dict
from datetime import datetime
import config


# Global variable for USD/VND rate
_usd_vnd_rate: Optional[float] = None


def get_current_usd_vnd_rate() -> float:
    """Get current USD/VND rate from global state or config default"""
    global _usd_vnd_rate
    if _usd_vnd_rate is not None:
        return _usd_vnd_rate
    return config.USD_VND_RATE


def set_usd_vnd_rate(rate: float) -> None:
    """Set USD/VND rate manually"""
    global _usd_vnd_rate
    _usd_vnd_rate = rate


def fetch_usd_vnd_rate_from_api() -> Optional[float]:
    """
    Fetch USD to VND exchange rate from free API
    Returns rate if successful, None if failed
    """
    try:
        url = config.BASE_URL_EXCHANGE_RATE_API
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = data.get("rates", {}).get("VND")
        if rate:
            return float(rate)
        return None
    except Exception as e:
        print(f"Error fetching USD/VND rate: {e}")
        return None


def refresh_usd_vnd_rate() -> tuple[float, bool]:
    """
    Refresh USD/VND rate from API
    Returns (rate, success) tuple
    """
    global _usd_vnd_rate
    rate = fetch_usd_vnd_rate_from_api()
    if rate:
        _usd_vnd_rate = rate
        return (rate, True)
    else:
        # Fallback to config default
        return (config.USD_VND_RATE, False)


class PriceService:
    """Service for fetching cryptocurrency prices"""

    def __init__(self, api_key: Optional[str] = None, use_db_cache: bool = True):
        self.api_key = api_key or config.COINGECKO_API_KEY
        self.base_url = config.COINGECKO_API_URL
        self._price_cache: Dict[str, Dict] = {}
        self._use_db_cache = use_db_cache
        self._db_cache = None
        self.base_url_currency_crypto_binance = config.BASE_URL_CURRENCY_CRYPTO_BINANCE

    def _get_db_cache(self):
        """Lazy load database cache"""
        if self._db_cache is None and self._use_db_cache:
            try:
                from utils.storage import get_price_cache

                self._db_cache = get_price_cache()
            except Exception:
                self._use_db_cache = False
        return self._db_cache

    def get_usd_to_vnd_rate(self) -> float:
        """
        Get USD to VND exchange rate
        Uses global rate if set, otherwise config default
        """
        return get_current_usd_vnd_rate()

    # def get_crypto_price_usd(
    #     self, token_symbol: str, date: Optional[datetime] = None
    # ) -> Optional[float]:
    #     """
    #     Get cryptocurrency price in USD

    #     Args:
    #         token_symbol: Token symbol (BTC, ETH, etc.)
    #         date: Optional date for historical price

    #     Returns:
    #         Price in USD or None if not found
    #     """
    #     # Map common token symbols to CoinGecko IDs
    #     token_map = {
    #         "BTC": "bitcoin",
    #         "ETH": "ethereum",
    #         "BNB": "binancecoin",
    #         "USDT": "tether",
    #         "USDC": "usd-coin",
    #         "MATIC": "matic-network",
    #         "SOL": "solana",
    #         "ADA": "cardano",
    #         "DOT": "polkadot",
    #         "AVAX": "avalanche-2",
    #     }

    #     coin_id = token_map.get(token_symbol.upper())

    #     if not coin_id:
    #         # Try using symbol directly
    #         coin_id = token_symbol.lower()

    #     cache_key = f"{coin_id}_{date.date() if date else 'latest'}"

    #     # Check memory cache first
    #     if cache_key in self._price_cache:
    #         return self._price_cache[cache_key].get("usd")

    #     # Check database cache for historical prices
    #     if date:
    #         db_cache = self._get_db_cache()
    #         if db_cache:
    #             date_str = date.strftime("%Y-%m-%d")
    #             cached = db_cache.get_price(token_symbol, date_str)
    #             if cached:
    #                 self._price_cache[cache_key] = {"usd": cached["price_usd"]}
    #                 return cached["price_usd"]

    #     try:
    #         if date:
    #             # Historical price
    #             date_str = date.strftime("%d-%m-%Y")
    #             url = f"{self.base_url}/coins/{coin_id}/history"
    #             params = {"date": date_str}
    #         else:
    #             # Current price
    #             url = f"{self.base_url}/simple/price"
    #             params = {"ids": coin_id, "vs_currencies": "usd"}

    #         if self.api_key:
    #             params["x_cg_demo_api_key"] = self.api_key

    #         response = requests.get(url, params=params, timeout=10)
    #         response.raise_for_status()
    #         data = response.json()

    #         if date:
    #             price = data.get("market_data", {}).get("current_price", {}).get("usd")
    #         else:
    #             price = data.get(coin_id, {}).get("usd")

    #         if price:
    #             self._price_cache[cache_key] = {"usd": price}

    #             # Save historical price to database cache
    #             if date:
    #                 db_cache = self._get_db_cache()
    #                 if db_cache:
    #                     vnd_rate = self.get_usd_to_vnd_rate()
    #                     db_cache.set_price(
    #                         token_symbol,
    #                         date.strftime("%Y-%m-%d"),
    #                         price,
    #                         price * vnd_rate,
    #                     )

    #             return price
    #         else:
    #             return None
    #     except Exception as e:
    #         print(f"Error fetching price for {token_symbol}: {e}")
    #         return None

    def get_crypto_price_usd(
        self, token_symbol: str, date: datetime
    ) -> Optional[float]:
        """
        Get cryptocurrency price in USD using Binance API

        Args:
            token_symbol: Token symbol (BTC, ETH, etc.)

        Returns:
            Price in USD or None if not found
        """
        # Binance uses trading pairs like ETHUSDT, BTCUSDT
        pair = f"{token_symbol.upper()}USDT"
        cache_key = f"{pair}_latest"

        # Check memory cache first
        if cache_key in self._price_cache:
            return self._price_cache[cache_key]

        try:
            url = f"{self.base_url_currency_crypto_binance}?symbol={pair}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            price = float(data.get("price", 0))

            return price

        except Exception as e:
            print(f"Error fetching price for {token_symbol}: {e}")
            return None

    def get_crypto_price_vnd(
        self, token_symbol: str, date: Optional[datetime] = None
    ) -> Optional[float]:
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

    def convert_value_to_vnd(
        self, token_symbol: str, amount: float, date: Optional[datetime] = None
    ) -> Optional[float]:
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
