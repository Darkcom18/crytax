"""
API clients for blockchain explorers
Etherscan API V2 (Unified multichain API)
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import config


# Etherscan API V2 Supported Chains with Chain IDs
# Reference: https://docs.etherscan.io/supported-chains
SUPPORTED_CHAINS = {
    # Ethereum
    "ethereum": {
        "chain_id": 1,
        "name": "Ethereum",
        "native_token": "ETH",
        "free_tier": True,
    },
    "sepolia": {
        "chain_id": 11155111,
        "name": "Sepolia Testnet",
        "native_token": "ETH",
        "free_tier": True,
    },
    # "holesky": {
    #     "chain_id": 17000,
    #     "name": "Holesky Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "hoodi": {
    #     "chain_id": 560048,
    #     "name": "Hoodi Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Abstract
    # "abstract": {
    #     "chain_id": 2741,
    #     "name": "Abstract Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "abstract_sepolia": {
    #     "chain_id": 11124,
    #     "name": "Abstract Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # ApeChain
    # "apechain_curtis": {
    #     "chain_id": 33111,
    #     "name": "ApeChain Curtis Testnet",
    #     "native_token": "APE",
    #     "free_tier": True,
    # },
    # "apechain": {
    #     "chain_id": 33139,
    #     "name": "ApeChain Mainnet",
    #     "native_token": "APE",
    #     "free_tier": True,
    # },
    # Arbitrum
    # "arbitrum_nova": {
    #     "chain_id": 42170,
    #     "name": "Arbitrum Nova Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "arbitrum": {
    #     "chain_id": 42161,
    #     "name": "Arbitrum One Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "arbitrum_sepolia": {
    #     "chain_id": 421614,
    #     "name": "Arbitrum Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Avalanche
    # "avalanche": {
    #     "chain_id": 43114,
    #     "name": "Avalanche C-Chain",
    #     "native_token": "AVAX",
    #     "free_tier": False,
    # },
    # "avalanche_fuji": {
    #     "chain_id": 43113,
    #     "name": "Avalanche Fuji Testnet",
    #     "native_token": "AVAX",
    #     "free_tier": False,
    # },
    # Base
    "base": {
        "chain_id": 8453,
        "name": "Base Mainnet",
        "native_token": "ETH",
        "free_tier": False,
    },
    "base_sepolia": {
        "chain_id": 84532,
        "name": "Base Sepolia Testnet",
        "native_token": "ETH",
        "free_tier": False,
    },
    # Berachain
    # "berachain_bepolia": {
    #     "chain_id": 80069,
    #     "name": "Berachain Bepolia Testnet",
    #     "native_token": "BERA",
    #     "free_tier": True,
    # },
    # "berachain": {
    #     "chain_id": 80094,
    #     "name": "Berachain Mainnet",
    #     "native_token": "BERA",
    #     "free_tier": True,
    # },
    # BitTorrent
    # "bittorrent": {
    #     "chain_id": 199,
    #     "name": "BitTorrent Chain Mainnet",
    #     "native_token": "BTT",
    #     "free_tier": True,
    # },
    # "bittorrent_testnet": {
    #     "chain_id": 1029,
    #     "name": "BitTorrent Chain Testnet",
    #     "native_token": "BTT",
    #     "free_tier": True,
    # },
    # Blast
    # "blast": {
    #     "chain_id": 81457,
    #     "name": "Blast Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "blast_sepolia": {
    #     "chain_id": 168587773,
    #     "name": "Blast Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # BNB Smart Chain (BSC)
    "bsc": {
        "chain_id": 56,
        "name": "BNB Smart Chain Mainnet",
        "native_token": "BNB",
        "free_tier": False,
    },
    "bsc_testnet": {
        "chain_id": 97,
        "name": "BNB Smart Chain Testnet",
        "native_token": "BNB",
        "free_tier": False,
    },
    # Celo
    # "celo": {
    #     "chain_id": 42220,
    #     "name": "Celo Mainnet",
    #     "native_token": "CELO",
    #     "free_tier": True,
    # },
    # "celo_sepolia": {
    #     "chain_id": 11142220,
    #     "name": "Celo Sepolia Testnet",
    #     "native_token": "CELO",
    #     "free_tier": True,
    # },
    # Fraxtal
    # "fraxtal": {
    #     "chain_id": 252,
    #     "name": "Fraxtal Mainnet",
    #     "native_token": "frxETH",
    #     "free_tier": True,
    # },
    # "fraxtal_hoodi": {
    #     "chain_id": 2523,
    #     "name": "Fraxtal Hoodi Testnet",
    #     "native_token": "frxETH",
    #     "free_tier": True,
    # },
    # Gnosis
    # "gnosis": {
    #     "chain_id": 100,
    #     "name": "Gnosis",
    #     "native_token": "xDAI",
    #     "free_tier": True,
    # },
    # HyperEVM
    "hyperevm": {
        "chain_id": 999,
        "name": "HyperEVM Mainnet",
        "native_token": "ETH",
        "free_tier": True,
    },
    # Katana
    # "katana_bokuto": {
    #     "chain_id": 737373,
    #     "name": "Katana Bokuto",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "katana": {
    #     "chain_id": 747474,
    #     "name": "Katana Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Linea
    # "linea": {
    #     "chain_id": 59144,
    #     "name": "Linea Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "linea_sepolia": {
    #     "chain_id": 59141,
    #     "name": "Linea Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Mantle
    # "mantle": {
    #     "chain_id": 5000,
    #     "name": "Mantle Mainnet",
    #     "native_token": "MNT",
    #     "free_tier": True,
    # },
    # "mantle_sepolia": {
    #     "chain_id": 5003,
    #     "name": "Mantle Sepolia Testnet",
    #     "native_token": "MNT",
    #     "free_tier": True,
    # },
    # Memecore
    # "memecore_testnet": {
    #     "chain_id": 43521,
    #     "name": "Memecore Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # # Monad
    # "monad": {
    #     "chain_id": 143,
    #     "name": "Monad Mainnet",
    #     "native_token": "MON",
    #     "free_tier": True,
    # },
    # "monad_testnet": {
    #     "chain_id": 10143,
    #     "name": "Monad Testnet",
    #     "native_token": "MON",
    #     "free_tier": True,
    # },
    # Moonbeam
    # "moonbase_alpha": {
    #     "chain_id": 1287,
    #     "name": "Moonbase Alpha Testnet",
    #     "native_token": "DEV",
    #     "free_tier": True,
    # },
    # "moonbeam": {
    #     "chain_id": 1284,
    #     "name": "Moonbeam Mainnet",
    #     "native_token": "GLMR",
    #     "free_tier": True,
    # },
    # "moonriver": {
    #     "chain_id": 1285,
    #     "name": "Moonriver Mainnet",
    #     "native_token": "MOVR",
    #     "free_tier": True,
    # },
    # Optimism
    # "optimism": {
    #     "chain_id": 10,
    #     "name": "OP Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": False,
    # },
    # "optimism_sepolia": {
    #     "chain_id": 11155420,
    #     "name": "OP Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": False,
    # },
    # opBNB
    # "opbnb": {
    #     "chain_id": 204,
    #     "name": "opBNB Mainnet",
    #     "native_token": "BNB",
    #     "free_tier": True,
    # },
    # "opbnb_testnet": {
    #     "chain_id": 5611,
    #     "name": "opBNB Testnet",
    #     "native_token": "BNB",
    #     "free_tier": True,
    # },
    # Polygon
    # "polygon_amoy": {
    #     "chain_id": 80002,
    #     "name": "Polygon Amoy Testnet",
    #     "native_token": "POL",
    #     "free_tier": True,
    # },
    # "polygon": {
    #     "chain_id": 137,
    #     "name": "Polygon Mainnet",
    #     "native_token": "POL",
    #     "free_tier": True,
    # },
    # Scroll
    # "scroll": {
    #     "chain_id": 534352,
    #     "name": "Scroll Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "scroll_sepolia": {
    #     "chain_id": 534351,
    #     "name": "Scroll Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Sei
    # "sei": {
    #     "chain_id": 1329,
    #     "name": "Sei Mainnet",
    #     "native_token": "SEI",
    #     "free_tier": True,
    # },
    # "sei_testnet": {
    #     "chain_id": 1328,
    #     "name": "Sei Testnet",
    #     "native_token": "SEI",
    #     "free_tier": True,
    # },
    # Sonic
    # "sonic": {
    #     "chain_id": 146,
    #     "name": "Sonic Mainnet",
    #     "native_token": "S",
    #     "free_tier": True,
    # },
    # "sonic_testnet": {
    #     "chain_id": 14601,
    #     "name": "Sonic Testnet",
    #     "native_token": "S",
    #     "free_tier": True,
    # },
    # Stable
    # "stable": {
    #     "chain_id": 988,
    #     "name": "Stable Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "stable_testnet": {
    #     "chain_id": 2201,
    #     "name": "Stable Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Swellchain
    # "swellchain": {
    #     "chain_id": 1923,
    #     "name": "Swellchain Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "swellchain_testnet": {
    #     "chain_id": 1924,
    #     "name": "Swellchain Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Taiko
    # "taiko_hoodi": {
    #     "chain_id": 167013,
    #     "name": "Taiko Hoodi",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "taiko": {
    #     "chain_id": 167000,
    #     "name": "Taiko Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # Unichain
    # "unichain": {
    #     "chain_id": 130,
    #     "name": "Unichain Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "unichain_sepolia": {
    #     "chain_id": 1301,
    #     "name": "Unichain Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # World
    # "world": {
    #     "chain_id": 480,
    #     "name": "World Mainnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # "world_sepolia": {
    #     "chain_id": 4801,
    #     "name": "World Sepolia Testnet",
    #     "native_token": "ETH",
    #     "free_tier": True,
    # },
    # # XDC
    # "xdc_apothem": {
    #     "chain_id": 51,
    #     "name": "XDC Apothem Testnet",
    #     "native_token": "XDC",
    #     "free_tier": True,
    # },
    # "xdc": {
    #     "chain_id": 50,
    #     "name": "XDC Mainnet",
    #     "native_token": "XDC",
    #     "free_tier": True,
    # },
    # zkSync
    "zksync": {
        "chain_id": 324,
        "name": "zkSync Mainnet",
        "native_token": "ETH",
        "free_tier": True,
    },
    "zksync_sepolia": {
        "chain_id": 300,
        "name": "zkSync Sepolia Testnet",
        "native_token": "ETH",
        "free_tier": True,
    },
}

# Mapping chain_id to chain key for reverse lookup
CHAIN_ID_TO_KEY = {v["chain_id"]: k for k, v in SUPPORTED_CHAINS.items()}


def get_supported_chains() -> Dict[str, Dict]:
    """Get all supported chains with their details"""
    return SUPPORTED_CHAINS


def get_chain_info(chain: str) -> Optional[Dict]:
    """
    Get chain information by chain name or chain_id

    Args:
        chain: Chain name (e.g., 'ethereum', 'polygon') or chain_id as string

    Returns:
        Chain info dict or None if not found
    """
    chain_lower = chain.lower().strip()

    # Try direct lookup by name
    if chain_lower in SUPPORTED_CHAINS:
        return SUPPORTED_CHAINS[chain_lower]

    # Try lookup by chain_id
    try:
        chain_id = int(chain)
        if chain_id in CHAIN_ID_TO_KEY:
            return SUPPORTED_CHAINS[CHAIN_ID_TO_KEY[chain_id]]
    except ValueError:
        pass

    # Handle legacy chain names (backward compatibility)
    legacy_mapping = {
        "binance smart chain": "bsc",
        "bnb": "bsc",
        "matic": "polygon",
        "op": "optimism",
        "arb": "arbitrum",
    }
    if chain_lower in legacy_mapping:
        return SUPPORTED_CHAINS.get(legacy_mapping[chain_lower])

    return None


class EtherscanV2Client:
    """
    Unified client for Etherscan API V2
    Supports 60+ chains with a single API endpoint and API key
    Reference: https://docs.etherscan.io/v2-migration
    """

    # Etherscan API V2 base URL
    BASE_URL = "https://api.etherscan.io/v2/api"

    def __init__(self, chain_id: int, api_key: Optional[str] = None):
        """
        Initialize Etherscan V2 client

        Args:
            chain_id: The chain ID for the target network
            api_key: Etherscan API key (single key works for all chains)
        """
        self.chain_id = chain_id
        self.api_key = api_key or config.ETHERSCAN_API_KEY

        # Get chain info for native token
        chain_key = CHAIN_ID_TO_KEY.get(chain_id)
        self.chain_info = SUPPORTED_CHAINS.get(chain_key, {})
        self.native_token = self.chain_info.get("native_token", "ETH")

    def _make_request(self, params: Dict) -> Dict:
        """
        Make API request with chain_id

        Args:
            params: Request parameters

        Returns:
            API response data
        """
        # Add chainid and apikey to params
        params["chainid"] = self.chain_id
        params["apikey"] = self.api_key

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making Etherscan V2 API request: {e}")
            return {"status": "0", "message": "ERROR", "result": str(e)}

    def get_transactions(
        self, address: str, start_block: int = 0, end_block: int = 99999999
    ) -> List[Dict]:
        """
        Get normal transactions for an address

        Args:
            address: Wallet address
            start_block: Start block number
            end_block: End block number

        Returns:
            List of transaction dictionaries
        """
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        }

        data = self._make_request(params)

        if data.get("status") == "1" and data.get("message") == "OK":
            return data.get("result", [])
        else:
            error_msg = data.get("result", data.get("message", "Unknown error"))
            print(f"Etherscan V2 API error (chain_id={self.chain_id}): {error_msg}")
            return []

    def get_token_transfers(
        self, address: str, contract_address: Optional[str] = None
    ) -> List[Dict]:
        """
        Get ERC-20/BEP-20 token transfers for an address

        Args:
            address: Wallet address
            contract_address: Optional token contract address to filter

        Returns:
            List of token transfer dictionaries
        """
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": "asc",
        }

        if contract_address:
            params["contractaddress"] = contract_address

        data = self._make_request(params)

        if data.get("status") == "1" and data.get("message") == "OK":
            return data.get("result", [])
        else:
            error_msg = data.get("result", data.get("message", "Unknown error"))
            print(f"Etherscan V2 API error (chain_id={self.chain_id}): {error_msg}")
            return []

    def get_internal_transactions(
        self, address: str, start_block: int = 0, end_block: int = 99999999
    ) -> List[Dict]:
        """
        Get internal transactions for an address

        Args:
            address: Wallet address
            start_block: Start block number
            end_block: End block number

        Returns:
            List of internal transaction dictionaries
        """
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        }

        data = self._make_request(params)

        if data.get("status") == "1" and data.get("message") == "OK":
            return data.get("result", [])
        else:
            return []

    def get_balance(self, address: str) -> str:
        """
        Get native token balance for an address

        Args:
            address: Wallet address

        Returns:
            Balance in wei as string
        """
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
        }

        data = self._make_request(params)

        if data.get("status") == "1" and data.get("message") == "OK":
            return data.get("result", "0")
        else:
            return "0"

    def get_nft_transfers(
        self, address: str, contract_address: Optional[str] = None
    ) -> List[Dict]:
        """
        Get ERC-721 NFT transfers for an address

        Args:
            address: Wallet address
            contract_address: Optional NFT contract address to filter

        Returns:
            List of NFT transfer dictionaries
        """
        params = {
            "module": "account",
            "action": "tokennfttx",
            "address": address,
            "sort": "asc",
        }

        if contract_address:
            params["contractaddress"] = contract_address

        data = self._make_request(params)

        if data.get("status") == "1" and data.get("message") == "OK":
            return data.get("result", [])
        else:
            return []


# Legacy client aliases for backward compatibility
class EtherscanClient(EtherscanV2Client):
    """Legacy alias for Ethereum - uses Etherscan V2 API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(chain_id=1, api_key=api_key)  # Ethereum Mainnet


class BSCScanClient(EtherscanV2Client):
    """Legacy alias for BSC - uses Etherscan V2 API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(chain_id=56, api_key=api_key)  # BNB Smart Chain Mainnet


class PolygonScanClient(EtherscanV2Client):
    """Legacy alias for Polygon - uses Etherscan V2 API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(chain_id=137, api_key=api_key)  # Polygon Mainnet


class SolanaClient:
    """Client for Solana blockchain (using RPC)"""

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or config.SOLANA_RPC_URL

    def get_transactions(self, address: str, limit: int = 1000) -> List[Dict]:
        """
        Get transactions for a Solana address

        Note: Solana RPC requires more complex setup with solana-py library
        This is a simplified version that would need proper implementation
        """
        # TODO: Implement proper Solana transaction fetching using solana-py
        # For now, return empty list
        print("Solana transaction fetching not yet fully implemented")
        return []


def get_client_for_chain(chain: str, api_key: Optional[str] = None):
    """
    Get appropriate API client for a chain

    Args:
        chain: Chain name (e.g., 'ethereum', 'polygon', 'arbitrum') or chain_id as string
        api_key: Optional API key (single Etherscan API key works for all EVM chains)

    Returns:
        API client instance
    """
    chain_lower = chain.lower().strip()

    # Handle Solana separately (not EVM)
    if chain_lower == "solana":
        return SolanaClient()

    # Get chain info
    chain_info = get_chain_info(chain)

    if chain_info:
        return EtherscanV2Client(chain_id=chain_info["chain_id"], api_key=api_key)

    # Fallback to legacy handling for backward compatibility
    legacy_chain_ids = {
        "ethereum": 1,
        "bsc": 56,
        "binance smart chain": 56,
        "polygon": 137,
        "matic": 137,
    }

    if chain_lower in legacy_chain_ids:
        return EtherscanV2Client(
            chain_id=legacy_chain_ids[chain_lower], api_key=api_key
        )

    raise ValueError(
        f"Unsupported chain: {chain}. Use get_supported_chains() to see available chains."
    )
