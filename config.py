"""
Configuration file for Crypto Tax MVP
Contains tax rates, API endpoints, and other settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Tax rates according to Vietnam regulations (Nghị quyết 05/2025)
TAX_RATES = {
    "transfer": 0.001,  # 0.1% for transfer transactions (buy/sell/swap)
    "other_income": 0.10,  # 10% for other income (staking, airdrop, farming)
    "futures_min": 0.05,  # 5% minimum for futures (progressive tax)
    "futures_max": 0.35,  # 35% maximum for futures (progressive tax)
}

# API Keys (can be set via environment variables or .env file)
# Users can also input their own API keys in the app
# Note: With Etherscan API V2, a single API key works for all supported chains
ETHERSCAN_API_KEY = os.getenv(
    "ETHERSCAN_API_KEY", ""
)  # Get from https://etherscan.io/apis - works for ALL chains with V2 API
# Legacy keys (deprecated - use ETHERSCAN_API_KEY for all chains with V2 API)
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")  # Deprecated: use ETHERSCAN_API_KEY
POLYGONSCAN_API_KEY = os.getenv(
    "POLYGONSCAN_API_KEY", ""
)  # Deprecated: use ETHERSCAN_API_KEY
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")  # Optional, free tier available

# API Endpoints
# Reference: https://docs.etherscan.io/v2-migration
ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"
BSCSCAN_API_URL = "https://api.etherscan.io/v2/api"
POLYGONSCAN_API_URL = "https://api.etherscan.io/v2/api"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Solana RPC (public endpoints, can be replaced with private RPC)
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

BASE_URL_EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"

BASE_URL_CURRENCY_CRYPTO_BINANCE = "https://api.binance.com/api/v3/ticker/price"
# Transaction types
TRANSACTION_TYPES = {
    "buy": "Mua",
    "sell": "Bán",
    "swap": "Swap",
    "transfer_in": "Nhận",
    "transfer_out": "Gửi",
    "staking_reward": "Staking Reward",
    "airdrop": "Airdrop",
    "farming": "Farming",
    "deposit": "Nạp tiền",
    "withdrawal": "Rút tiền",
}

# Supported chains (legacy - see utils/api_clients.py for full list with 60+ chains)
# Using Etherscan API V2, all chains are supported with a single API key
SUPPORTED_CHAINS = {
    "ethereum": "Ethereum Mainnet",
    "bsc": "BNB Smart Chain Mainnet",
    "polygon": "Polygon Mainnet",
    "arbitrum": "Arbitrum One Mainnet",
    "optimism": "OP Mainnet",
    "base": "Base Mainnet",
    "avalanche": "Avalanche C-Chain",
    "linea": "Linea Mainnet",
    "scroll": "Scroll Mainnet",
    "zksync": "zkSync Mainnet",
    "solana": "Solana",
}

# Supported exchanges
SUPPORTED_EXCHANGES = {
    "binance": "Binance",
}

# Storage
STORAGE_TYPE = "sqlite"  # or "csv"
DATABASE_PATH = "transactions.db"
CSV_PATH = "transactions.csv"

# Exchange rate
USD_VND_RATE = 25450.0  # Default USD to VND rate (can be updated via API)


DEFAULT_LIMIT_REQUEST_TRANSACTION = 20
DEFAULT_PAGE_REQUEST_TRANSACTION = 1
