"""
Data Import API
Handles importing transactions from various sources
"""

import time
from typing import List, Optional, Any, BinaryIO
from datetime import datetime, timezone
from dataclasses import dataclass

from api.base import BaseAPI, APIResponse
from models.transaction import Transaction
from utils.exceptions import validate_wallet_address
from utils.exchange_clients import create_binance_client
from services.wallet_service import WalletService
from utils.file_parser import parse_csv
from utils.file_parser import parse_json
from services.exchange_service import ExchangeService


@dataclass
class ImportResult:
    """Result of an import operation"""

    count: int
    source: str
    format_type: Optional[str] = None
    warnings: List[str] = None
    transactions: List[Transaction] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.transactions is None:
            self.transactions = []


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
        end_date: Optional[datetime] = None,
        page: int = 1,
        offset: int = 20,
    ) -> APIResponse[ImportResult]:
        """
        Import transactions from blockchain wallet.

        Args:
            wallet_address: Wallet address
            chain: Blockchain name (ethereum, bsc, polygon)
            api_key: Optional API key for blockchain explorer
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number for pagination (1-indexed)
            offset: Number of transactions per page (default 20)
        """
        # Validate address
        is_valid, error_msg = validate_wallet_address(wallet_address, chain)
        if not is_valid:
            return APIResponse.validation_error([error_msg])

        try:

            service = WalletService()

            transactions = service.fetch_transactions(
                wallet_address,
                chain.lower(),
                api_key,
                start_date,
                end_date,
                page,
                offset,
            )

            if transactions:
                # Add to transaction store
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(
                    ImportResult(
                        count=len(transactions),
                        transactions=transactions,
                        source=f"wallet:{chain}",
                    ),
                    f"Đã import {len(transactions)} giao dịch từ ví",
                )
            else:
                return APIResponse.ok(
                    ImportResult(
                        count=0,
                        source=f"wallet:{chain}",
                        warnings=[
                            "Không tìm thấy giao dịch trong khoảng thời gian này"
                        ],
                    )
                )

        except Exception as e:
            return APIResponse.error(f"Lỗi khi lấy giao dịch từ ví: {str(e)}")

    # Exchange imports

    def import_from_binance(
        self,
        api_key: str,
        api_secret: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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
            return APIResponse.validation_error(["Vui lòng nhập API Key và Secret"])

        try:

            service = ExchangeService()

            transactions = service.fetch_binance_transactions(
                api_key, api_secret, start_date, end_date
            )

            if transactions:
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(
                    ImportResult(count=len(transactions), source="exchange:binance"),
                    f"Đã import {len(transactions)} giao dịch từ Binance",
                )
            else:
                return APIResponse.ok(
                    ImportResult(
                        count=0,
                        source="exchange:binance",
                        warnings=["Không tìm thấy giao dịch"],
                    )
                )

        except Exception as e:
            return APIResponse.error(f"Lỗi khi lấy giao dịch từ Binance: {str(e)}")

    def test_binance_connection(
        self, api_key: str, api_secret: str
    ) -> APIResponse[dict]:
        """
        Test Binance API connection.

        Returns account info if successful.
        """
        if not api_key or not api_secret:
            return APIResponse.validation_error(["Vui lòng nhập API Key và Secret"])

        try:

            client = create_binance_client(api_key, api_secret)

            server = client.client.get_server_time()
            server_time_ms = server["serverTime"]

            # Get client current timestamp by UTC
            local_now = datetime.now()
            utc_now = local_now.astimezone(timezone.utc)
            utc_timestamp_ms = int(utc_now.timestamp() * 1000)

            # Offset between server and client ms
            client.client.timestamp_offset = server_time_ms - utc_timestamp_ms

            account = client.client.get_account(recvWindow=10000)

            return APIResponse.ok(
                {
                    "account_type": account.get("accountType", "N/A"),
                    "can_trade": account.get("canTrade", False),
                    "can_withdraw": account.get("canWithdraw", False),
                    "server_time_utc": datetime.fromtimestamp(
                        server_time_ms / 1000, tz=timezone.utc
                    ).isoformat(),
                    "local_time_utc": utc_now.isoformat(),
                    "timestamp_offset_ms": client.client.timestamp_offset,
                },
                "Kết nối thành công",
            )

        except Exception as e:
            return APIResponse.error(f"Lỗi kết nối: {str(e)}")

    # File imports

    def import_from_csv(
        self, file_content: Any, filename: str = ""
    ) -> APIResponse[ImportResult]:
        """
        Import transactions from CSV file.

        Args:
            file_content: File content (file object or string)
            filename: Optional filename for format detection
        """
        try:

            transactions, format_type = parse_csv(file_content, filename)

            if transactions:
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(
                    ImportResult(
                        count=len(transactions),
                        source="file:csv",
                        format_type=format_type,
                    ),
                    f"Đã import {len(transactions)} giao dịch từ CSV",
                )
            else:
                return APIResponse.ok(
                    ImportResult(
                        count=0,
                        source="file:csv",
                        format_type=format_type,
                        warnings=[
                            f"Không tìm thấy giao dịch hợp lệ. Format: {format_type}"
                        ],
                    )
                )

        except Exception as e:
            return APIResponse.error(f"Lỗi đọc file CSV: {str(e)}")

    def import_from_json(self, file_content: Any) -> APIResponse[ImportResult]:
        """
        Import transactions from JSON file.

        Args:
            file_content: File content (file object or string)
        """
        try:

            transactions, format_type = parse_json(file_content)

            if transactions:
                self.container.transactions.add_many(transactions)

                return APIResponse.ok(
                    ImportResult(count=len(transactions), source="file:json"),
                    f"Đã import {len(transactions)} giao dịch từ JSON",
                )
            else:
                return APIResponse.ok(
                    ImportResult(
                        count=0,
                        source="file:json",
                        warnings=[
                            f"Không tìm thấy giao dịch hợp lệ. Error: {format_type}"
                        ],
                    )
                )

        except Exception as e:
            return APIResponse.error(f"Lỗi đọc file JSON: {str(e)}")

    # Utilities

    def get_supported_chains(self) -> List[dict]:
        """
        Get list of supported blockchain chains with chain IDs

        Returns:
            List of dicts with chain info: name, chain_id, native_token, free_tier
        """
        from utils.api_clients import get_supported_chains

        chains = get_supported_chains()
        result = []
        for key, info in chains.items():
            result.append(
                {
                    "key": key,
                    "chain_id": info["chain_id"],
                    "name": info["name"],
                    "native_token": info["native_token"],
                    "free_tier": info["free_tier"],
                }
            )
        return sorted(result, key=lambda x: x["name"])

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
