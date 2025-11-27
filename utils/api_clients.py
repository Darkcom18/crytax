"""
API clients for blockchain explorers
Etherscan, BSCScan, PolygonScan, Solana
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import config


class EtherscanClient:
    """Client for Etherscan API (Ethereum)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.ETHERSCAN_API_KEY
        self.base_url = config.ETHERSCAN_API_URL
    
    def get_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict]:
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
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                return data["result"]
            else:
                return []
        except Exception as e:
            print(f"Error fetching Etherscan transactions: {e}")
            return []
    
    def get_token_transfers(self, address: str, contract_address: Optional[str] = None) -> List[Dict]:
        """
        Get ERC-20 token transfers for an address
        
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
            "apikey": self.api_key
        }
        
        if contract_address:
            params["contractaddress"] = contract_address
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                return data["result"]
            else:
                return []
        except Exception as e:
            print(f"Error fetching Etherscan token transfers: {e}")
            return []


class BSCScanClient:
    """Client for BSCScan API (Binance Smart Chain)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.BSCSCAN_API_KEY
        self.base_url = config.BSCSCAN_API_URL
    
    def get_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict]:
        """Get normal transactions for an address"""
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                return data["result"]
            else:
                return []
        except Exception as e:
            print(f"Error fetching BSCScan transactions: {e}")
            return []
    
    def get_token_transfers(self, address: str, contract_address: Optional[str] = None) -> List[Dict]:
        """Get BEP-20 token transfers for an address"""
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": "asc",
            "apikey": self.api_key
        }
        
        if contract_address:
            params["contractaddress"] = contract_address
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                return data["result"]
            else:
                return []
        except Exception as e:
            print(f"Error fetching BSCScan token transfers: {e}")
            return []


class PolygonScanClient:
    """Client for PolygonScan API (Polygon)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.POLYGONSCAN_API_KEY
        self.base_url = config.POLYGONSCAN_API_URL
    
    def get_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict]:
        """Get normal transactions for an address"""
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                return data["result"]
            else:
                return []
        except Exception as e:
            print(f"Error fetching PolygonScan transactions: {e}")
            return []
    
    def get_token_transfers(self, address: str, contract_address: Optional[str] = None) -> List[Dict]:
        """Get ERC-20 token transfers for an address"""
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": "asc",
            "apikey": self.api_key
        }
        
        if contract_address:
            params["contractaddress"] = contract_address
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                return data["result"]
            else:
                return []
        except Exception as e:
            print(f"Error fetching PolygonScan token transfers: {e}")
            return []


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
        chain: Chain name (ethereum, bsc, polygon, solana)
        api_key: Optional API key
        
    Returns:
        API client instance
    """
    chain_lower = chain.lower()
    
    if chain_lower == "ethereum":
        return EtherscanClient(api_key)
    elif chain_lower == "bsc" or chain_lower == "binance smart chain":
        return BSCScanClient(api_key)
    elif chain_lower == "polygon":
        return PolygonScanClient(api_key)
    elif chain_lower == "solana":
        return SolanaClient()
    else:
        raise ValueError(f"Unsupported chain: {chain}")

