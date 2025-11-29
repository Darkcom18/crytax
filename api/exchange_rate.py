"""
Exchange Rate API
Handles USD/VND exchange rate operations
"""

from dataclasses import dataclass
from typing import Optional

from api.base import BaseAPI, APIResponse
from utils.price_service import (
    get_current_usd_vnd_rate,
    set_usd_vnd_rate,
    refresh_usd_vnd_rate,
    fetch_usd_vnd_rate_from_api
)
import config


@dataclass
class ExchangeRateInfo:
    """Exchange rate information"""
    current_rate: float
    is_from_api: bool
    default_rate: float


class ExchangeRateAPI(BaseAPI):
    """
    API for exchange rate management.
    Independent of any UI framework.
    """

    def __init__(self, container):
        super().__init__(container)
        self._last_api_rate: Optional[float] = None

    def get_current(self) -> APIResponse[ExchangeRateInfo]:
        """Get current exchange rate info"""
        current = get_current_usd_vnd_rate()
        return APIResponse.ok(ExchangeRateInfo(
            current_rate=current,
            is_from_api=self._last_api_rate is not None and current == self._last_api_rate,
            default_rate=config.USD_VND_RATE
        ))

    def get_rate(self) -> float:
        """Get current rate value directly"""
        return get_current_usd_vnd_rate()

    def set_manual(self, rate: float) -> APIResponse[float]:
        """
        Set exchange rate manually.

        Args:
            rate: New exchange rate
        """
        if rate < 20000 or rate > 30000:
            return APIResponse.validation_error([
                "Tỷ giá phải trong khoảng 20,000 - 30,000 VND"
            ])

        set_usd_vnd_rate(rate)
        self._last_api_rate = None
        return APIResponse.ok(rate, f"Đã cập nhật tỷ giá: {rate:,.0f} VND")

    def refresh_from_api(self) -> APIResponse[float]:
        """
        Fetch latest exchange rate from API.
        """
        rate, success = refresh_usd_vnd_rate()

        if success:
            self._last_api_rate = rate
            return APIResponse.ok(rate, f"Đã cập nhật từ API: {rate:,.0f} VND")
        else:
            return APIResponse.error(
                f"Không thể lấy tỷ giá từ API. Sử dụng mặc định: {rate:,.0f} VND"
            )

    def reset_to_default(self) -> APIResponse[float]:
        """Reset to default configured rate"""
        set_usd_vnd_rate(config.USD_VND_RATE)
        self._last_api_rate = None
        return APIResponse.ok(
            config.USD_VND_RATE,
            f"Đã reset về mặc định: {config.USD_VND_RATE:,.0f} VND"
        )
