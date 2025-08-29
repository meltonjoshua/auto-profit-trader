"""
Configuration management for Auto Profit Trader
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration settings for the trading bot"""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize ConfigManager

        Args:
            config_path: Optional path to config file, defaults to config.json
        """
        self.config_path = config_path or Path("config.json")
        self.config: Dict[str, Any] = {}
        self.default_config: Dict[str, Any] = {
            "trading": {
                "daily_loss_limit": 100.0,  # USD
                "max_position_size": 0.02,  # 2% of account
                "enable_arbitrage": True,
                "enable_momentum": True,
                "target_profit_arbitrage": 0.005,  # 0.5% minimum profit
                "target_profit_momentum": 0.02,  # 2% target profit
            },
            "exchanges": {
                "binance": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True,
                },
                "coinbase": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "sandbox": True,
                },
                "kraken": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True,
                },
            },
            "notifications": {
                "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
                "discord": {"enabled": False, "webhook_url": ""},
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_email": "",
                },
            },
            "risk_management": {
                "stop_loss_percentage": 0.02,  # 2% stop loss
                "take_profit_percentage": 0.05,  # 5% take profit
                "max_trades_per_day": 50,
                "cooldown_after_loss": 300,  # 5 minutes
            },
            "technical_analysis": {
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bollinger_period": 20,
                "bollinger_std": 2,
            },
        }
        self._load_or_create_config()

    def _load_or_create_config(self) -> None:
        """Load existing config or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self._merge_with_defaults()
                logger.info(
                    "Configuration loaded successfully from %s", self.config_path
                )
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON in config file: %s", e)
                self._create_default_config()
            except FileNotFoundError:
                logger.warning("Config file not found, creating default")
                self._create_default_config()
            except Exception as e:
                logger.error("Unexpected error loading config: %s", e)
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self) -> None:
        """Create default configuration"""
        self.config = self.default_config.copy()
        self.save_config()
        logger.info("Created default configuration file: %s", self.config_path)

    def _merge_with_defaults(self) -> None:
        """Merge loaded config with defaults to ensure all keys exist"""

        def merge_dicts(
            default: Dict[str, Any], loaded: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Recursively merge dictionaries"""
            result = default.copy()
            for key, value in loaded.items():
                if (
                    key in result
                    and isinstance(value, dict)
                    and isinstance(result[key], dict)
                ):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result

        self.config = merge_dicts(self.default_config, self.config)

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a specific configuration section"""
        return self.config.get(section, {})

    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation

        Args:
            path: Dot-separated path (e.g., 'trading.daily_loss_limit')
            default: Default value if path not found

        Returns:
            Configuration value or default
        """
        if not path:
            return default

        keys = path.split(".")
        value = self.config

        try:
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except (TypeError, KeyError):
            return default

    def set_value(self, path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation

        Args:
            path: Dot-separated path (e.g., 'trading.daily_loss_limit')
            value: Value to set
        """
        if not path:
            logger.warning("Empty path provided to set_value")
            return

        keys = path.split(".")
        config = self.config

        try:
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                elif not isinstance(config[key], dict):
                    logger.warning(
                        "Cannot set nested value, parent is not dict: %s", key
                    )
                    return
                config = config[key]

            config[keys[-1]] = value
            self.save_config()
            logger.debug("Set config value: %s = %s", path, value)
        except Exception as e:
            logger.error("Error setting config value %s: %s", path, e)

    def save_config(self) -> bool:
        """
        Save configuration to file

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)

            # Set secure permissions (readable/writable by owner only)
            self.config_path.chmod(0o600)
            logger.debug("Configuration saved to %s", self.config_path)
            return True
        except Exception as e:
            logger.error("Error saving config to %s: %s", self.config_path, e)
            return False

    def validate_api_keys(self) -> bool:
        """
        Validate that at least one exchange has API keys configured

        Returns:
            True if at least one exchange has valid API keys
        """
        exchanges = self.config.get("exchanges", {})

        for exchange_name, exchange_config in exchanges.items():
            if (
                exchange_config.get("enabled", False)
                and exchange_config.get("api_key")
                and exchange_config.get("api_secret")
            ):
                return True

        return False

    def get_enabled_exchanges(self) -> List[str]:
        """
        Get list of enabled exchanges

        Returns:
            List of enabled exchange names
        """
        exchanges = self.config.get("exchanges", {})
        return [
            name for name, config in exchanges.items() if config.get("enabled", False)
        ]

    def is_exchange_enabled(self, exchange_name: str) -> bool:
        """
        Check if a specific exchange is enabled

        Args:
            exchange_name: Name of the exchange to check

        Returns:
            True if exchange is enabled
        """
        exchanges = self.config.get("exchanges", {})
        return exchanges.get(exchange_name, {}).get("enabled", False)

    def update_section(self, section: str, updates: Dict[str, Any]) -> None:
        """
        Update a configuration section with new values

        Args:
            section: Configuration section name
            updates: Dictionary of updates to apply
        """
        if section not in self.config:
            self.config[section] = {}

        self.config[section].update(updates)
        self.save_config()
        logger.debug("Updated config section %s", section)
