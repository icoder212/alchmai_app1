"""Helper functions for validation and data processing"""
import re
from typing import Optional


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or len(symbol) < 1 or len(symbol) > 10:
        return False
    
    # Check characters (letters, numbers, dots, hyphens allowed)
    if not re.match(r'^[A-Za-z0-9.\-]+$', symbol):
        return False
    
    return True


def normalize_symbol(symbol: str) -> str:
    """
    Normalize symbol to uppercase standard format
    
    Args:
        symbol: Symbol to normalize (e.g., "Apple", "aapl", "AAPL")
        
    Returns:
        Normalized symbol (e.g., "AAPL")
    """
    if not symbol:
        return ""
    
    # Remove whitespace and convert to uppercase
    normalized = symbol.strip().upper()
    
    # Common symbol mappings
    symbol_map = {
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "GOOGLE": "GOOGL",
        "AMAZON": "AMZN",
        "TESLA": "TSLA",
        "GOLD": "XAUUSD",
        "SILVER": "XAGUSD",
        "CRUDE": "CL",
        "OIL": "CL",
    }
    
    return symbol_map.get(normalized, normalized)


def get_asset_class(symbol: str) -> str:
    """
    Determine asset class from symbol
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Asset class: "stock", "forex", "commodity", "crypto", or "unknown"
    """
    symbol_upper = symbol.upper()
    
    # Commodities - CHECK FIRST (XAU, XAG are commodities, not forex!)
    commodity_symbols = ["XAU", "XAG", "CL", "NG", "GC", "SI"]
    if any(symbol_upper.startswith(comm) for comm in commodity_symbols):
        return "commodity"
    
    # Forex pairs (typically 6 characters, contains currency codes)
    forex_patterns = [
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"
    ]
    if len(symbol_upper) == 6 and any(
        symbol_upper.startswith(fx) or symbol_upper.endswith(fx) 
        for fx in forex_patterns
    ):
        return "forex"
    
    # Crypto (common patterns)
    crypto_patterns = ["BTC", "ETH", "USDT", "USDC"]
    if any(symbol_upper.startswith(crypto) for crypto in crypto_patterns):
        return "crypto"
    
    # Default to stock (most common)
    return "stock"
