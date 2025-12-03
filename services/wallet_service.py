"""
Wallet service for fetching transactions from blockchain
Supports 60+ chains via Etherscan API V2
"""

from typing import List, Optional
from datetime import datetime
import config
from models.transaction import Transaction, TransactionType, TransactionSource
from utils.api_clients import get_client_for_chain, EtherscanV2Client, get_chain_info
from utils.price_service import get_price_service


class WalletService:
    """Service for fetching and processing wallet transactions"""

    def __init__(self):
        self.price_service = get_price_service()

    def fetch_transactions(
        self,
        wallet_address: str,
        chain: str,
        api_key: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = config.DEFAULT_PAGE_REQUEST_TRANSACTION,
        offset: int = config.DEFAULT_LIMIT_REQUEST_TRANSACTION,
    ) -> List[Transaction]:
        """
        Fetch transactions for a wallet address

        Args:
            wallet_address: Wallet address
            chain: Chain name (e.g., 'ethereum', 'polygon', 'arbitrum') or chain_id
            api_key: Optional API key for Etherscan V2 (single key works for all chains)
            start_date: Optional start date
            end_date: Optional end date
            page: Page number for pagination (1-indexed)
            offset: Number of transactions per page (default 20)

        Returns:
            List of Transaction objects
        """
        try:
            client = get_client_for_chain(chain, api_key)
            transactions = []

            # Get chain info for native token
            chain_info = get_chain_info(chain)
            native_token = (
                chain_info.get("native_token", "ETH") if chain_info else "ETH"
            )

            # Get transactions using Etherscan V2 API
            if isinstance(client, EtherscanV2Client):
                normal_txs = client.get_transactions(
                    wallet_address, page=page, offset=offset
                )
                for tx in normal_txs:
                    parsed = self._parse_normal_transaction(
                        tx, wallet_address, chain, native_token
                    )
                    if parsed:
                        transactions.append(parsed)

                # Get token transfers
                token_txs = client.get_token_transfers(
                    wallet_address, page=page, offset=offset
                )
                for tx in token_txs:
                    parsed = self._parse_token_transfer(tx, wallet_address, chain)
                    if parsed:
                        transactions.append(parsed)

            if start_date or end_date:
                transactions = [
                    tx
                    for tx in transactions
                    if (not start_date or tx.date >= start_date)
                    and (not end_date or tx.date <= end_date)
                ]

            return transactions

        except Exception as e:
            print(f"Error fetching wallet transactions: {e}")
            return []

    def _parse_normal_transaction(
        self, tx: dict, wallet_address: str, chain: str, native_token: str
    ) -> Optional[Transaction]:
        """Parse normal transaction (native token transfer)"""
        try:
            # Determine if it's incoming or outgoing
            from_address = tx.get("from", "").lower()
            to_address = tx.get("to", "").lower()
            wallet_lower = wallet_address.lower()

            if from_address == wallet_lower:
                tx_type = TransactionType.TRANSFER_OUT
                amount = float(tx.get("value", 0)) / 1e18  # Convert from wei
            elif to_address == wallet_lower:
                tx_type = TransactionType.TRANSFER_IN
                amount = float(tx.get("value", 0)) / 1e18
            else:
                return None

            # Use native token from chain info
            token = native_token

            # Transaction date
            tx_timestamp = int(tx.get("timeStamp", 0))
            tx_date = datetime.fromtimestamp(tx_timestamp)

            # Get price in VND
            price_vnd = self.price_service.get_crypto_price_vnd(token, tx_date) or 0
            value_vnd = amount * price_vnd

            # Gas fee
            gas_used = float(tx.get("gasUsed", 0))
            gas_price = float(tx.get("gasPrice", 0))
            fee_eth = (gas_used * gas_price) / 1e18
            fee_vnd = (
                self.price_service.convert_value_to_vnd(token, fee_eth, tx_date) or 0
            )

            return Transaction(
                date=tx_date,
                type=tx_type,
                token=token,
                amount=amount,
                price_vnd=price_vnd,
                value_vnd=value_vnd,
                source=TransactionSource.WALLET,
                wallet_address=wallet_address,
                chain=chain,
                tx_hash=tx.get("hash", ""),
                fee_vnd=fee_vnd,
            )
        except Exception as e:
            print(f"Error parsing normal transaction: {e}")
            return None

    def _parse_token_transfer(
        self, tx: dict, wallet_address: str, chain: str
    ) -> Optional[Transaction]:
        """Parse ERC-20/BEP-20 token transfer"""
        try:
            from_address = tx.get("from", "").lower()
            to_address = tx.get("to", "").lower()
            wallet_lower = wallet_address.lower()

            if from_address == wallet_lower:
                tx_type = TransactionType.TRANSFER_OUT
            elif to_address == wallet_lower:
                tx_type = TransactionType.TRANSFER_IN
            else:
                return None

            # Get token info
            token_symbol = tx.get("tokenSymbol", "")
            token_decimal = int(tx.get("tokenDecimal", 18))
            amount = float(tx.get("value", 0)) / (10**token_decimal)

            # Transaction date
            tx_timestamp = int(tx.get("timeStamp", 0))
            tx_date = datetime.fromtimestamp(tx_timestamp)

            # Get price in VND
            price_vnd = (
                self.price_service.get_crypto_price_vnd(token_symbol, tx_date) or 0
            )
            value_vnd = amount * price_vnd

            return Transaction(
                date=tx_date,
                type=tx_type,
                token=token_symbol,
                amount=amount,
                price_vnd=price_vnd,
                value_vnd=value_vnd,
                source=TransactionSource.WALLET,
                wallet_address=wallet_address,
                chain=chain,
                tx_hash=tx.get("hash", ""),
            )
        except Exception as e:
            print(f"Error parsing token transfer: {e}")
            return None
