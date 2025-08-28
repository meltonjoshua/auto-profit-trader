"""
Configuration management for Auto Profit Trader
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages configuration settings for the trading bot"""
    
    def __init__(self):
        self.config_path = Path("config.json")
        self.default_config = {
            "trading": {
                "daily_loss_limit": 100.0,  # USD
                "max_position_size": 0.02,  # 2% of account
                "enable_arbitrage": True,
                "enable_momentum": True,
                "target_profit_arbitrage": 0.005,  # 0.5% minimum profit
                "target_profit_momentum": 0.02,    # 2% target profit
            },
            "exchanges": {
                "binance": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True
                },
                "coinbase": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "sandbox": True
                },
                "kraken": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True
                }
            },
            "notifications": {
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_id": ""
                },
                "discord": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_email": ""
                }
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
                "bollinger_std": 2
            }
        }
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load existing config or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self._merge_with_defaults()
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                print("🔄 Creating default configuration...")
                self.config = self.default_config.copy()
                self.save_config()
        else:
            self.config = self.default_config.copy()
            self.save_config()
            print("✅ Created default configuration file: config.json")
    
    def _merge_with_defaults(self):
        """Merge loaded config with defaults to ensure all keys exist"""
        def merge_dicts(default: dict, loaded: dict) -> dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(value, dict) and isinstance(result[key], dict):
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
    
    def get_value(self, path: str, default=None):
        """Get a configuration value using dot notation (e.g., 'trading.daily_loss_limit')"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_value(self, path: str, value: Any):
        """Set a configuration value using dot notation"""
        keys = path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def validate_api_keys(self) -> bool:
        """Validate that at least one exchange has API keys configured"""
        exchanges = self.config.get("exchanges", {})
        
        for exchange_name, exchange_config in exchanges.items():
            if (exchange_config.get("enabled", False) and 
                exchange_config.get("api_key") and 
                exchange_config.get("api_secret")):
                return True
        
        return False
    
    def get_enabled_exchanges(self) -> list:
        """Get list of enabled exchanges"""
        exchanges = self.config.get("exchanges", {})
        return [name for name, config in exchanges.items() if config.get("enabled", False)]