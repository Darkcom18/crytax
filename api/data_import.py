"""
Data Import API
Handles importing transactions from various sources
"""

from typing import List, Optional, Any, BinaryIO
from datetime import datetime
from dataclasses import dataclass

from api.base import BaseAPI, APIResponse
from models.transaction import Transaction
from utils.exceptions import validate_wallet_address


@dataclass
class ImportResult:
    """Result of an import operation"""
    count: int
    source: str
    format_type: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class DataImportAPI(BaseAPI):
    """
    API for importing transaction data.
    Independent of any UI framework.
    """

    # Wallet imports

    def import_from_wallet(
        self,
        wallet_address: str,
        chain: str,
        api_key: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> APIResponse[ImportResult]:
        """
        Import transactions from blockchain wallet.

        Args:
            wallet_address: Wallet address
            chain: Blockchain name (ethereum, bsc, polygon)
            api_key: Optional API key for blockchain explorer
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        # Validate address
        is_valid, error_msg = validate_wallet_address(wallet_address, chain)
        if not is_valid:
            return APIResponse.validation_error([error_msg])

        try:
            from services.wallet_service import WalletService
            service = WalletService()

            transactions = service.fetch_transactions(
                wallet_address,
                chain.lower(),
                api_key,
                start_date,
                end_date
            )

            if transactions:
                # Add to transaction store
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(ImportResult(
                    count=len(transactions),
                    source=f"wallet:{chain}"
                ), f"Đã import {len(transactions)} giao dịch từ ví")
            else:
                return APIResponse.ok(ImportResult(
                    count=0,
                    source=f"wallet:{chain}",
                    warnings=["Không tìm thấy giao dịch trong khoảng thời gian này"]
                ))

        except Exception as e:
            return APIResponse.error(f"Lỗi khi lấy giao dịch từ ví: {str(e)}")

    # Exchange imports

    def import_from_binance(
        self,
        api_key: str,
        api_secret: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> APIResponse[ImportResult]:
        """
        Import transactions from Binance exchange.

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        if not api_key or not api_secret:
            return APIResponse.validation_error([
                "Vui lòng nhập API Key và Secret"
            ])

        try:
            from services.exchange_service import ExchangeService
            service = ExchangeService()

            transactions = service.fetch_binance_transactions(
                api_key,
                api_secret,
                start_date,
                end_date
            )

            if transactions:
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(ImportResult(
                    count=len(transactions),
                    source="exchange:binance"
                ), f"Đã import {len(transactions)} giao dịch từ Binance")
            else:
                return APIResponse.ok(ImportResult(
                    count=0,
                    source="exchange:binance",
                    warnings=["Không tìm thấy giao dịch"]
                ))

        except Exception as e:
            return APIResponse.error(f"Lỗi khi lấy giao dịch từ Binance: {str(e)}")

    def test_binance_connection(
        self,
        api_key: str,
        api_secret: str
    ) -> APIResponse[dict]:
        """
        Test Binance API connection.

        Returns account info if successful.
        """
        if not api_key or not api_secret:
            return APIResponse.validation_error([
                "Vui lòng nhập API Key và Secret"
            ])

        try:
            from utils.exchange_clients import create_binance_client
            client = create_binance_client(api_key, api_secret)
            account = client.client.get_account()

            return APIResponse.ok({
                "account_type": account.get("accountType", "N/A"),
                "can_trade": account.get("canTrade", False),
                "can_withdraw": account.get("canWithdraw", False),
            }, "Kết nối thành công")

        except Exception as e:
            return APIResponse.error(f"Lỗi kết nối: {str(e)}")

    # File imports

    def import_from_csv(
        self,
        file_content: Any,
        filename: str = ""
    ) -> APIResponse[ImportResult]:
        """
        Import transactions from CSV file.

        Args:
            file_content: File content (file object or string)
            filename: Optional filename for format detection
        """
        try:
            from utils.file_parser import parse_csv

            transactions, format_type = parse_csv(file_content, filename)

            if transactions:
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(ImportResult(
                    count=len(transactions),
                    source="file:csv",
                    format_type=format_type
                ), f"Đã import {len(transactions)} giao dịch từ CSV")
            else:
                return APIResponse.ok(ImportResult(
                    count=0,
                    source="file:csv",
                    format_type=format_type,
                    warnings=[f"Không tìm thấy giao dịch hợp lệ. Format: {format_type}"]
                ))

        except Exception as e:
            return APIResponse.error(f"Lỗi đọc file CSV: {str(e)}")

    def import_from_json(
        self,
        file_content: Any
    ) -> APIResponse[ImportResult]:
        """
        Import transactions from JSON file.

        Args:
            file_content: File content (file object or string)
        """
        try:
            from utils.file_parser import parse_json

            transactions, format_type = parse_json(file_content)

            if transactions:
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(ImportResult(
                    count=len(transactions),
                    source="file:json"
                ), f"Đã import {len(transactions)} giao dịch từ JSON")
            else:
                return APIResponse.ok(ImportResult(
                    count=0,
                    source="file:json",
                    warnings=[f"Không tìm thấy giao dịch hợp lệ. Error: {format_type}"]
                ))

        except Exception as e:
            return APIResponse.error(f"Lỗi đọc file JSON: {str(e)}")

    # Utilities

    def get_supported_chains(self) -> List[str]:
        """Get list of supported blockchain chains"""
        return ["Ethereum", "BSC", "Polygon"]

    def get_supported_exchanges(self) -> List[str]:
        """Get list of supported exchanges"""
        return ["Binance"]

    def get_sample_csv_format(self) -> str:
        """Get sample CSV format"""
        from utils.file_parser import get_sample_csv_format
        return get_sample_csv_format()

    def get_sample_json_format(self) -> str:
        """Get sample JSON format"""
        from utils.file_parser import get_sample_json_format
        return get_sample_json_format()
