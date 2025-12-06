"""
Dependency Injection Container
Manages all service instances and their dependencies
"""

from typing import Optional
from dataclasses import dataclass, field
from api.transactions import TransactionAPI
from api.tax import TaxAPI
from api.exchange_rate import ExchangeRateAPI
from api.data_import import DataImportAPI
from utils.price_service import get_price_service
from utils.storage import get_storage
from services.tax_calculator import TaxCalculator


@dataclass
class Container:
    """
    Central container for all services and APIs.
    Provides dependency injection and lazy loading.
    """

    _transaction_api: Optional["TransactionAPI"] = field(default=None, repr=False)
    _tax_api: Optional["TaxAPI"] = field(default=None, repr=False)
    _exchange_rate_api: Optional["ExchangeRateAPI"] = field(default=None, repr=False)
    _data_import_api: Optional["DataImportAPI"] = field(default=None, repr=False)

    # Services
    _price_service: Optional[object] = field(default=None, repr=False)
    _storage: Optional[object] = field(default=None, repr=False)
    _tax_calculator: Optional[object] = field(default=None, repr=False)

    @property
    def transactions(self) -> "TransactionAPI":
        """Get TransactionAPI instance"""
        if self._transaction_api is None:

            self._transaction_api = TransactionAPI(self)
        return self._transaction_api

    @property
    def tax(self) -> "TaxAPI":
        """Get TaxAPI instance"""
        if self._tax_api is None:
            self._tax_api = TaxAPI(self)
        return self._tax_api

    @property
    def exchange_rate(self) -> "ExchangeRateAPI":
        """Get ExchangeRateAPI instance"""
        if self._exchange_rate_api is None:

            self._exchange_rate_api = ExchangeRateAPI(self)
        return self._exchange_rate_api

    @property
    def data_import(self) -> "DataImportAPI":
        """Get DataImportAPI instance"""
        if self._data_import_api is None:
            self._data_import_api = DataImportAPI(self)
        return self._data_import_api

    # Service accessors
    @property
    def price_service(self):
        """Get PriceService instance"""
        if self._price_service is None:
            self._price_service = get_price_service()
        return self._price_service

    @property
    def storage(self):
        """Get Storage instance"""
        if self._storage is None:
            self._storage = get_storage()
        return self._storage

    @property
    def tax_calculator(self):
        """Get TaxCalculator instance"""
        if self._tax_calculator is None:
            self._tax_calculator = TaxCalculator()
        return self._tax_calculator


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get global container instance"""
    global _container
    if _container is None:
        _container = Container()
    return _container


def reset_container() -> None:
    """Reset container (useful for testing)"""
    global _container
    _container = None
