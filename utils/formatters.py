"""
Formatting utilities for displaying data
"""

from datetime import datetime
from typing import Optional


def format_vnd(amount: float) -> str:
    """Format VND amount with thousand separators"""
    if amount is None:
        return "0 ₫"
    return f"{amount:,.0f} ₫"


def format_crypto(amount: float, decimals: int = 8) -> str:
    """Format cryptocurrency amount"""
    if amount is None:
        return "0"
    return f"{amount:,.{decimals}f}"


def format_date(date: datetime) -> str:
    """Format date for display"""
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    return date.strftime("%d/%m/%Y %H:%M")


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage"""
    if value is None:
        return "0%"
    return f"{value * 100:.{decimals}f}%"


def format_tax_type(tax_type: str) -> str:
    """Format tax type for display"""
    tax_types = {
        "transfer": "Chuyển nhượng (0.1%)",
        "other_income": "Thu nhập khác (10%)",
        "futures": "Futures (5-35%)",
    }
    return tax_types.get(tax_type, tax_type)

