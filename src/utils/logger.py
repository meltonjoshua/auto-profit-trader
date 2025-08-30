"""
Logging utilities for Auto Profit Trader
"""

import logging
import sys
import platform
import re
from datetime import datetime
from pathlib import Path


class WindowsConsoleFormatter(logging.Formatter):
    """Custom formatter that removes emojis for Windows console compatibility"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_windows = platform.system() == "Windows"
        # Regex pattern to match emoji characters
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
    
    def format(self, record):
        formatted = super().format(record)
        if self.is_windows:
            # Remove emojis for Windows console
            formatted = self.emoji_pattern.sub('', formatted)
            # Clean up extra spaces
            formatted = re.sub(r'\s+', ' ', formatted).strip()
        return formatted


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with professional formatting"""
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Create console handler with Windows-compatible encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Use Windows-compatible formatter for console
    console_formatter = WindowsConsoleFormatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create file handler with full emoji support
    file_handler = logging.FileHandler(
        log_dir / f"{name}.log", 
        encoding='utf-8'  # Ensure UTF-8 encoding for file logs
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Use regular formatter for file logs (keeps emojis)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def log_trade(symbol: str, side: str, amount: float, price: float, profit: float = 0):
    """Log a trade execution"""
    logger = logging.getLogger("trades")
    if not logger.handlers:
        setup_logger("trades")

    timestamp = datetime.now().isoformat()
    logger.info(
        f"TRADE | {timestamp} | {symbol} | {side} | Amount: {amount} | Price: ${price:.4f} | Profit: ${profit:.4f}"
    )


def log_performance(daily_profit: float, total_profit: float, win_rate: float):
    """Log performance metrics"""
    logger = logging.getLogger("performance")
    if not logger.handlers:
        setup_logger("performance")

    timestamp = datetime.now().isoformat()
    logger.info(
        f"PERFORMANCE | {timestamp} | Daily: ${daily_profit:.2f} | Total: ${total_profit:.2f} | Win Rate: {win_rate:.1f}%"
    )
