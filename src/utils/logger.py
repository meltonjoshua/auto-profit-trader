"""
Logging utilities for Auto Profit Trader
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with professional formatting"""
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create file handler
    file_handler = logging.FileHandler(log_dir / f"{name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
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
