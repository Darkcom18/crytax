"""
Configuration file for Crypto Tax MVP
Contains tax rates, API endpoints, and other settings
"""

# Tax rates according to Vietnam regulations (Nghị quyết 05/2025)
TAX_RATES = {
    "transfer": 0.001,  # 0.1% for transfer transactions (buy/sell/swap)
    "other_income": 0.10,  # 10% for other income (staking, airdrop, farming)
    "futures_min": 0.05,  # 5% minimum for futures (progressive tax)
    "futures_max": 0.35,  # 35% maximum for futures (progressive tax)
}

# API Keys (should be set via environment variables or .env file)
# Users will input their own API keys in the app
ETHERSCAN_API_KEY = ""  # Get from https://etherscan.io/apis
BSCSCAN_API_KEY = ""  # Get from https://bscscan.com/apis
POLYGONSCAN_API_KEY = ""  # Get from https://polygonscan.com/apis
COINGECKO_API_KEY = ""  # Optional, free tier available

# API Endpoints
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
BSCSCAN_API_URL = "https://api.bscscan.com/api"
POLYGONSCAN_API_URL = "https://api.polygonscan.com/api"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Solana RPC (public endpoints, can be replaced with private RPC)
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

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

# Supported chains
SUPPORTED_CHAINS = {
    "ethereum": "Ethereum",
    "bsc": "BSC (Binance Smart Chain)",
    "polygon": "Polygon",
    "solana": "Solana",
}

# Supported exchanges
SUPPORTED_EXCHANGES = {
    "binance": "Binance",
    # Can be extended: "coinbase", "okx", "bybit"
}

# Storage
STORAGE_TYPE = "sqlite"  # or "csv"
DATABASE_PATH = "transactions.db"
CSV_PATH = "transactions.csv"

