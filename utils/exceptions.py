"""
Custom exceptions for Crypto Tax MVP
"""

from utils.api_clients import get_chain_info


class CryptoTaxError(Exception):
    """Base exception for Crypto Tax MVP"""

    pass


class InvalidWalletAddressError(CryptoTaxError):
    """Invalid wallet address format"""

    pass


class APIError(CryptoTaxError):
    """API call failed"""

    pass


class ExchangeAPIError(APIError):
    """Exchange API error"""

    pass


class BlockchainAPIError(APIError):
    """Blockchain explorer API error"""

    pass


class PriceServiceError(APIError):
    """Price service error"""

    pass


class ParseError(CryptoTaxError):
    """Error parsing data"""

    pass


class StorageError(CryptoTaxError):
    """Storage operation error"""

    pass


def validate_evm_address(address: str) -> bool:
    """
    Validate EVM (Ethereum/BSC/Polygon) wallet address

    Args:
        address: Wallet address to validate

    Returns:
        True if valid, False otherwise
    """
    if not address:
        return False

    # Must start with 0x
    if not address.startswith("0x"):
        return False

    # Must be 42 characters (0x + 40 hex chars)
    if len(address) != 42:
        return False

    # Must be valid hex
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def validate_wallet_address(address: str, chain: str) -> tuple[bool, str]:
    """
    Validate wallet address for a given chain

    Args:
        address: Wallet address
        chain: Blockchain name or chain_id

    Returns:
        (is_valid, error_message)
    """

    chain_lower = chain.lower().strip()

    # Handle Solana separately (non-EVM)
    if chain_lower == "solana":
        # Solana addresses are base58 encoded, 32-44 characters
        if not address:
            return False, "Vui lòng nhập địa chỉ ví"
        if len(address) < 32 or len(address) > 44:
            return False, "Địa chỉ Solana không hợp lệ"
        return True, ""

    # Check if chain is supported via Etherscan V2
    chain_info = get_chain_info(chain)

    if chain_info:
        # All Etherscan V2 supported chains use EVM addresses
        if not address:
            return False, "Vui lòng nhập địa chỉ ví"
        if not validate_evm_address(address):
            return (
                False,
                "Địa chỉ ví không hợp lệ. Địa chỉ EVM phải bắt đầu bằng 0x và có 42 ký tự",
            )
        return True, ""

    # Legacy support for known EVM chains
    evm_chains = [
        "ethereum",
        "bsc",
        "polygon",
        "arbitrum",
        "optimism",
        "base",
        "avalanche",
        "linea",
        "scroll",
        "zksync",
    ]
    if chain_lower in evm_chains:
        if not address:
            return False, "Vui lòng nhập địa chỉ ví"
        if not validate_evm_address(address):
            return (
                False,
                "Địa chỉ ví không hợp lệ. Địa chỉ EVM phải bắt đầu bằng 0x và có 42 ký tự",
            )
        return True, ""

    return False, f"Chain không được hỗ trợ: {chain}"
