"""
File parser for CSV and JSON transaction files
Supports Binance export format and custom format
"""

import pandas as pd
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from models.transaction import Transaction, TransactionType, TransactionSource
from utils.price_service import get_price_service


# Column mappings for different CSV formats
BINANCE_COLUMNS = {
    "Date(UTC)": "date",
    "Pair": "symbol",
    "Side": "side",
    "Price": "price",
    "Executed": "amount",
    "Amount": "total",
    "Fee": "fee",
}

CUSTOM_COLUMNS = {
    "date": "date",
    "type": "type",
    "token": "token",
    "amount": "amount",
    "price": "price",
    "value": "value",
    "source": "source",
    "chain": "chain",
}


def detect_csv_format(df: pd.DataFrame) -> str:
    """Detect CSV format based on columns"""
    columns = set(df.columns)

    # Check for Binance format
    binance_required = {"Date(UTC)", "Pair", "Side", "Price", "Executed"}
    if binance_required.issubset(columns):
        return "binance"

    # Check for custom format
    custom_required = {"date", "type", "token", "amount"}
    if custom_required.issubset(columns):
        return "custom"

    return "unknown"


def parse_binance_csv(df: pd.DataFrame, exchange_name: str = "Binance") -> List[Transaction]:
    """Parse Binance trade history CSV export"""
    transactions = []
    price_service = get_price_service()

    for _, row in df.iterrows():
        try:
            # Parse date
            date_str = row.get("Date(UTC)", "")
            if isinstance(date_str, str):
                tx_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            else:
                tx_date = pd.to_datetime(date_str).to_pydatetime()

            # Parse symbol and determine tokens
            symbol = row.get("Pair", "")
            side = row.get("Side", "").upper()

            # Common quote currencies
            quote_currencies = ["USDT", "BUSD", "BTC", "ETH", "BNB", "USD"]
            base_token = symbol
            quote_token = "USDT"

            for quote in quote_currencies:
                if symbol.endswith(quote):
                    base_token = symbol[:-len(quote)]
                    quote_token = quote
                    break

            # Determine transaction type
            if side == "BUY":
                tx_type = TransactionType.BUY
                token = base_token
                amount = float(row.get("Executed", 0))
            else:
                tx_type = TransactionType.SELL
                token = base_token
                amount = float(row.get("Executed", 0))

            # Get price and value
            price = float(row.get("Price", 0))
            total = float(row.get("Amount", 0)) if "Amount" in row else price * amount

            # Convert to VND
            price_vnd = price_service.get_crypto_price_vnd(quote_token, tx_date)
            if price_vnd is None:
                price_vnd = price_service.get_usd_to_vnd_rate()  # Assume quote is USD-pegged

            value_vnd = total * (price_vnd / price) if price > 0 else total * price_service.get_usd_to_vnd_rate()
            token_price_vnd = value_vnd / amount if amount > 0 else 0

            # Fee
            fee = float(row.get("Fee", 0)) if "Fee" in row else 0
            fee_vnd = fee * price_service.get_usd_to_vnd_rate()

            tx = Transaction(
                date=tx_date,
                type=tx_type,
                token=token,
                amount=amount,
                price_vnd=token_price_vnd,
                value_vnd=value_vnd,
                source=TransactionSource.EXCHANGE,
                exchange_name=exchange_name,
                chain="Binance",
                fee_vnd=fee_vnd,
            )
            transactions.append(tx)

        except Exception as e:
            print(f"Error parsing row: {e}")
            continue

    return transactions


def parse_custom_csv(df: pd.DataFrame) -> List[Transaction]:
    """Parse custom format CSV"""
    transactions = []
    price_service = get_price_service()

    for _, row in df.iterrows():
        try:
            # Parse date
            date_val = row.get("date", "")
            if isinstance(date_val, str):
                # Try multiple date formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]:
                    try:
                        tx_date = datetime.strptime(date_val, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    tx_date = datetime.now()
            else:
                tx_date = pd.to_datetime(date_val).to_pydatetime()

            # Parse type
            type_str = str(row.get("type", "")).lower()
            type_mapping = {
                "buy": TransactionType.BUY,
                "sell": TransactionType.SELL,
                "swap": TransactionType.SWAP,
                "transfer_in": TransactionType.TRANSFER_IN,
                "transfer_out": TransactionType.TRANSFER_OUT,
                "staking": TransactionType.STAKING_REWARD,
                "staking_reward": TransactionType.STAKING_REWARD,
                "airdrop": TransactionType.AIRDROP,
                "farming": TransactionType.FARMING,
                "deposit": TransactionType.DEPOSIT,
                "withdrawal": TransactionType.WITHDRAWAL,
            }
            tx_type = type_mapping.get(type_str, TransactionType.BUY)

            # Parse other fields
            token = str(row.get("token", ""))
            amount = float(row.get("amount", 0))

            # Value - use provided or calculate
            if "value_vnd" in row and pd.notna(row["value_vnd"]):
                value_vnd = float(row["value_vnd"])
            elif "value" in row and pd.notna(row["value"]):
                value_vnd = float(row["value"])
            else:
                # Try to get price
                value_vnd = price_service.convert_value_to_vnd(token, amount, tx_date) or 0

            price_vnd = value_vnd / amount if amount > 0 else 0

            # Source
            source_str = str(row.get("source", "exchange")).lower()
            source = TransactionSource.WALLET if source_str == "wallet" else TransactionSource.EXCHANGE

            # Chain
            chain = str(row.get("chain", "Unknown"))

            # Create transaction based on source
            if source == TransactionSource.WALLET:
                tx = Transaction(
                    date=tx_date,
                    type=tx_type,
                    token=token,
                    amount=amount,
                    price_vnd=price_vnd,
                    value_vnd=value_vnd,
                    source=source,
                    wallet_address=str(row.get("wallet_address", "imported")),
                    chain=chain,
                )
            else:
                tx = Transaction(
                    date=tx_date,
                    type=tx_type,
                    token=token,
                    amount=amount,
                    price_vnd=price_vnd,
                    value_vnd=value_vnd,
                    source=source,
                    exchange_name=str(row.get("exchange_name", "Imported")),
                    chain=chain,
                )

            transactions.append(tx)

        except Exception as e:
            print(f"Error parsing row: {e}")
            continue

    return transactions


def parse_csv(file_content: Any, filename: str = "") -> tuple[List[Transaction], str]:
    """
    Parse CSV file and return transactions

    Returns:
        (transactions, format_detected)
    """
    try:
        df = pd.read_csv(file_content)

        if df.empty:
            return [], "empty"

        format_type = detect_csv_format(df)

        if format_type == "binance":
            transactions = parse_binance_csv(df)
        elif format_type == "custom":
            transactions = parse_custom_csv(df)
        else:
            # Try custom format as fallback
            transactions = parse_custom_csv(df)
            format_type = "custom (guessed)"

        return transactions, format_type

    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return [], f"error: {str(e)}"


def parse_json(file_content: Any) -> tuple[List[Transaction], str]:
    """
    Parse JSON file and return transactions

    Expects format:
    {
        "transactions": [
            {"date": "...", "type": "...", "token": "...", ...}
        ]
    }
    or just an array of transactions
    """
    try:
        if hasattr(file_content, 'read'):
            data = json.load(file_content)
        else:
            data = json.loads(file_content)

        # Handle both formats
        if isinstance(data, list):
            tx_list = data
        elif isinstance(data, dict) and "transactions" in data:
            tx_list = data["transactions"]
        else:
            return [], "invalid format"

        transactions = []
        for tx_data in tx_list:
            try:
                tx = Transaction.from_dict(tx_data)
                transactions.append(tx)
            except Exception as e:
                print(f"Error parsing transaction: {e}")
                continue

        return transactions, "json"

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return [], f"error: {str(e)}"


def get_sample_csv_format() -> str:
    """Return sample CSV format for users"""
    return """date,type,token,amount,value_vnd,source,chain,exchange_name
2024-01-15 10:30:00,buy,BTC,0.5,500000000,exchange,Binance,Binance
2024-01-20 14:00:00,sell,BTC,0.25,275000000,exchange,Binance,Binance
2024-02-01 09:00:00,staking_reward,ETH,0.1,5000000,wallet,Ethereum,
2024-02-10 16:30:00,swap,ETH,1.0,50000000,wallet,Ethereum,"""


def get_sample_json_format() -> str:
    """Return sample JSON format for users"""
    return """{
  "transactions": [
    {
      "date": "2024-01-15T10:30:00",
      "type": "buy",
      "token": "BTC",
      "amount": 0.5,
      "price_vnd": 1000000000,
      "value_vnd": 500000000,
      "source": "exchange",
      "chain": "Binance",
      "exchange_name": "Binance"
    }
  ]
}"""
