"""
Test configuration and fixtures for Auto Profit Trader
"""

import asyncio
import json

# Add src to path for imports
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest

sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.config_manager import ConfigManager

# Note: Import Notifier only when needed to avoid dependency issues


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for testing"""
    return {
        "trading": {
            "daily_loss_limit": 100.0,
            "max_position_size": 0.02,
            "enable_arbitrage": True,
            "enable_momentum": True,
            "target_profit_arbitrage": 0.005,
            "target_profit_momentum": 0.02,
        },
        "exchanges": {
            "binance": {
                "enabled": False,
                "api_key": "test_key",
                "api_secret": "test_secret",
                "testnet": True,
            }
        },
        "notifications": {
            "telegram": {"enabled": False, "bot_token": "", "chat_id": ""}
        },
        "risk_management": {
            "stop_loss_percentage": 0.02,
            "take_profit_percentage": 0.05,
            "max_trades_per_day": 50,
            "cooldown_after_loss": 300,
        },
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_config, f, indent=2)
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_config_manager(sample_config):
    """Mock ConfigManager for testing"""
    mock = Mock(spec=ConfigManager)
    mock.get_config.return_value = sample_config
    mock.get_section.return_value = sample_config["trading"]
    mock.get_enabled_exchanges.return_value = ["binance"]
    return mock


@pytest.fixture
def mock_notifier():
    """Mock Notifier for testing"""
    # Create mock without importing the actual class to avoid dependencies
    mock = Mock()
    mock.send_notification = AsyncMock()
    mock.send_trade_alert = AsyncMock()
    mock.send_system_alert = AsyncMock()
    mock.send_profit_milestone = AsyncMock()
    return mock


@pytest.fixture
def mock_exchange_response():
    """Mock exchange API response"""
    return {
        "symbol": "BTC/USDT",
        "bid": 45000.0,
        "ask": 45010.0,
        "last": 45005.0,
        "volume": 1234.56,
        "timestamp": 1234567890000,
    }


@pytest.fixture
def sample_trade_signal():
    """Sample trade signal for testing"""
    return {
        "action": "BUY",
        "symbol": "BTC/USDT",
        "amount": 0.001,
        "price": 45000.0,
        "confidence": 0.8,
        "strategy": "arbitrage",
        "timestamp": 1234567890000,
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {
        "total_balance": 10000.0,
        "available_balance": 8000.0,
        "positions": [
            {
                "symbol": "BTC/USDT",
                "side": "long",
                "amount": 0.001,
                "entry_price": 44000.0,
                "current_price": 45000.0,
                "unrealized_pnl": 1.0,
            }
        ],
        "daily_profit": 25.50,
        "total_profit": 150.75,
        "win_rate": 68.5,
        "completed_trades": 42,
    }
