"""
Custom exceptions for Crypto Tax MVP
"""


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
        chain: Blockchain name

    Returns:
        (is_valid, error_message)
    """
    chain_lower = chain.lower()

    if chain_lower in ["ethereum", "bsc", "polygon"]:
        if not address:
            return False, "Vui lòng nhập địa chỉ ví"
        if not validate_evm_address(address):
            return False, "Địa chỉ ví không hợp lệ. Địa chỉ EVM phải bắt đầu bằng 0x và có 42 ký tự"
        return True, ""

    elif chain_lower == "solana":
        # Solana addresses are base58 encoded, 32-44 characters
        if not address:
            return False, "Vui lòng nhập địa chỉ ví"
        if len(address) < 32 or len(address) > 44:
            return False, "Địa chỉ Solana không hợp lệ"
        return True, ""

    return False, f"Chain không được hỗ trợ: {chain}"
