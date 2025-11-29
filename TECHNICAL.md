# Crypto Tax Vietnam - Technical Documentation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (api/)                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ TransactionAPI│ │   TaxAPI    │ │  ExchangeRateAPI    │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  DataImportAPI                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│    Services     │ │     Utils       │ │      Models         │
│ - TaxCalculator │ │ - PriceService  │ │ - Transaction       │
│ - WalletService │ │ - Storage       │ │ - TransactionType   │
│ - ExchangeServ  │ │ - FileParser    │ │ - TransactionSource │
│ - PDFGenerator  │ │ - APIClients    │ │                     │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  SQLite DB      │
                    │ - transactions  │
                    │ - price_cache   │
                    └─────────────────┘
```

## Project Structure

```
tax_project/
├── app.py                 # Streamlit UI entry point
├── config.py              # Configuration constants
├── api/                   # API layer (framework-agnostic)
│   ├── __init__.py
│   ├── base.py            # APIResponse, BaseAPI
│   ├── container.py       # Dependency injection
│   ├── transactions.py    # Transaction CRUD
│   ├── tax.py             # Tax calculations
│   ├── exchange_rate.py   # USD/VND rate
│   └── data_import.py     # Import from sources
├── models/
│   └── transaction.py     # Transaction dataclass
├── services/
│   ├── tax_calculator.py  # FIFO tax calculation
│   ├── wallet_service.py  # Blockchain fetching
│   ├── exchange_service.py# Binance integration
│   └── pdf_generator.py   # PDF reports
├── utils/
│   ├── api_clients.py     # Blockchain explorers
│   ├── exchange_clients.py# Binance client
│   ├── price_service.py   # CoinGecko + rates
│   ├── storage.py         # SQLite persistence
│   ├── file_parser.py     # CSV/JSON parsing
│   └── exceptions.py      # Validation helpers
└── data/
    └── crypto_tax.db      # SQLite database
```

## API Layer

### Container Pattern

```python
from api import get_container

api = get_container()

# Transaction operations
api.transactions.get_all()
api.transactions.add(transaction)
api.transactions.save()

# Tax calculations
api.tax.calculate_summary()
api.tax.calculate_by_period(period="month")

# Exchange rate
api.exchange_rate.get_rate()
api.exchange_rate.refresh_from_api()
api.exchange_rate.set_manual(25000)

# Data import
api.data_import.import_from_wallet(address, chain)
api.data_import.import_from_binance(api_key, secret)
api.data_import.import_from_csv(file_content)
```

### APIResponse Pattern

All API methods return `APIResponse[T]`:

```python
@dataclass
class APIResponse(Generic[T]):
    status: StatusCode      # SUCCESS, ERROR, VALIDATION_ERROR
    data: Optional[T]       # Response data
    message: str            # User-friendly message
    errors: List[str]       # Validation errors

    @property
    def success(self) -> bool:
        return self.status == StatusCode.SUCCESS
```

Usage:
```python
result = api.transactions.get_all()
if result.success:
    transactions = result.data
else:
    print(result.message)
```

## Data Models

### Transaction

```python
@dataclass
class Transaction:
    id: str
    date: datetime
    type: TransactionType
    token: str
    amount: float
    price_usd: Optional[float]
    value_vnd: Optional[float]
    source: TransactionSource
    tx_hash: Optional[str]

    # SWAP specific
    token_out: Optional[str]      # Token received
    amount_out: Optional[float]   # Amount received
    value_out_vnd: Optional[float]# Value in VND
```

### TransactionType

```python
class TransactionType(Enum):
    BUY = "buy"
    SELL = "sell"
    SWAP = "swap"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    STAKING = "staking"
    AIRDROP = "airdrop"
    FARMING = "farming"
    REWARD = "reward"
    FEE = "fee"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    OTHER = "other"
```

## Tax Calculation

### FIFO Implementation

```python
class FIFOCalculator:
    def __init__(self):
        self.inventory: Dict[str, List[Purchase]] = {}

    def add_purchase(self, token, amount, price, date):
        """Add to FIFO queue"""

    def calculate_cost_basis(self, token, amount) -> Tuple[float, float]:
        """
        Calculate cost basis using FIFO
        Returns: (cost_basis, remaining_amount)
        """
```

### Tax Rates

```python
# config.py
TRANSFER_TAX_RATE = 0.001    # 0.1% for buy/sell/swap
OTHER_INCOME_TAX_RATE = 0.10 # 10% for staking/airdrop/farming
```

## External APIs

### Blockchain Explorers

| Chain | API | Endpoint |
|-------|-----|----------|
| Ethereum | Etherscan | api.etherscan.io |
| BSC | BSCScan | api.bscscan.com |
| Polygon | PolygonScan | api.polygonscan.com |

```python
# utils/api_clients.py
class BlockchainClient:
    def get_transactions(self, address, start_block=0):
        """Fetch normal transactions"""

    def get_token_transfers(self, address):
        """Fetch ERC20 transfers"""
```

### Price APIs

```python
# CoinGecko (crypto prices)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Exchange rate
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
```

## Binance Integration

### Setup

1. Get API Key from Binance (Read Only permission)
2. Use in app or set in environment

### How to Get Binance API Key

#### Step 1: Login to Binance
1. Go to [binance.com](https://www.binance.com)
2. Login to your account

#### Step 2: API Management
1. Click profile icon (top right)
2. Select "API Management"
3. Complete security verification

#### Step 3: Create API
1. Click "Create API"
2. Choose "System generated"
3. Name it (e.g., "Crypto Tax App")

#### Step 4: Set Permissions (IMPORTANT!)

**ONLY enable Read Only permission:**

| Permission | Enable? |
|------------|---------|
| Read Only | YES |
| Enable Spot & Margin Trading | NO |
| Enable Withdrawals | NO |
| Enable Futures | NO |

#### Step 5: Save Keys
- **API Key**: Copy and save securely
- **Secret Key**: Copy immediately (shown once only!)

### Implementation

```python
# utils/exchange_clients.py
class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)

    def get_all_trades(self, start_time, end_time) -> List[Dict]:
        """
        Fetch all trades from Binance

        Logic:
        1. Get account assets with balance
        2. Build trading pairs (asset + quote currencies)
        3. Fetch trades for each valid pair
        """
        # Get assets
        balances = self.client.get_account()["balances"]
        assets = [b["asset"] for b in balances if float(b["free"]) > 0]

        # Build symbols
        quotes = ["USDT", "BUSD", "BTC", "ETH", "BNB"]
        symbols_to_check = []
        for asset in assets:
            for quote in quotes:
                symbols_to_check.append(f"{asset}{quote}")
                symbols_to_check.append(f"{quote}{asset}")

        # Fetch trades
        all_trades = []
        for symbol in symbols_to_check:
            if symbol in valid_symbols:
                trades = self.client.get_my_trades(symbol=symbol)
                all_trades.extend(trades)

        return all_trades
```

### Troubleshooting

| Error | Solution |
|-------|----------|
| Invalid API Key | Check key/secret are correct, no extra spaces |
| No permission | Enable "Read Only" in API settings |
| IP not whitelisted | Add your IP or disable IP restriction |
| No trades found | Check date range, ensure trades exist |

## Database Schema

### transactions table

```sql
CREATE TABLE transactions (
    id TEXT PRIMARY KEY,
    date TEXT,
    type TEXT,
    token TEXT,
    amount REAL,
    price_usd REAL,
    value_vnd REAL,
    source TEXT,
    tx_hash TEXT,
    fee REAL,
    fee_token TEXT,
    notes TEXT,
    token_out TEXT,
    amount_out REAL,
    value_out_vnd REAL
);
```

### price_cache table

```sql
CREATE TABLE price_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL,
    date TEXT NOT NULL,
    price_usd REAL,
    price_vnd REAL,
    cached_at TEXT,
    UNIQUE(token, date)
);
```

## Running the Application

### Requirements

```bash
pip install streamlit pandas python-binance requests
```

### Environment Variables

```bash
# .env
ETHERSCAN_API_KEY=your_key
BSCSCAN_API_KEY=your_key
POLYGONSCAN_API_KEY=your_key
COINGECKO_API_KEY=your_key  # optional
```

### Start

```bash
streamlit run app.py
```

## Extending the Application

### Adding New Exchange

1. Create client in `utils/exchange_clients.py`:
```python
class NewExchangeClient:
    def get_trades(self, start, end) -> List[Dict]:
        pass
```

2. Add service method in `services/exchange_service.py`:
```python
def fetch_newexchange_transactions(self, api_key, secret, ...):
    pass
```

3. Add API endpoint in `api/data_import.py`:
```python
def import_from_newexchange(self, ...):
    pass
```

### Adding New Blockchain

1. Add client in `utils/api_clients.py`:
```python
class NewChainClient(BlockchainClient):
    BASE_URL = "https://api.newchain.io/api"
```

2. Add to `services/wallet_service.py`
3. Update `get_supported_chains()` in `api/data_import.py`

### Adding New Tax Type

1. Add to `TransactionType` enum
2. Update `TaxCalculator.calculate_transaction_tax()`
3. Update `TaxSummary` if needed

## Testing

```bash
# Test Binance connection
python -c "
from utils.exchange_clients import create_binance_client
client = create_binance_client('API_KEY', 'SECRET')
print(client.client.get_account())
"

# Test blockchain client
python -c "
from utils.api_clients import EtherscanClient
client = EtherscanClient('API_KEY')
txs = client.get_transactions('0x...')
print(len(txs))
"
```
