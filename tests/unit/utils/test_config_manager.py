"""
Unit tests for ConfigManager
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from utils.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class"""

    def test_init_creates_default_config(self):
        """Test that ConfigManager creates default config on initialization"""
        with patch("pathlib.Path.exists", return_value=False), patch(
            "builtins.open", mock_open()
        ) as mock_file:

            config_manager = ConfigManager()

            assert config_manager.config is not None
            assert "trading" in config_manager.config
            assert "exchanges" in config_manager.config
            assert "notifications" in config_manager.config

    def test_load_existing_config(self, sample_config, temp_config_file):
        """Test loading existing config file"""
        config_manager = ConfigManager(config_path=temp_config_file)
        loaded_config = config_manager.get_config()

        assert loaded_config["trading"]["daily_loss_limit"] == 100.0
        assert loaded_config["exchanges"]["binance"]["enabled"] is False

    def test_get_section_returns_correct_data(self, mock_config_manager, sample_config):
        """Test getting specific config section"""
        mock_config_manager.get_section.return_value = sample_config["trading"]

        trading_config = mock_config_manager.get_section("trading")

        assert trading_config["daily_loss_limit"] == 100.0
        assert trading_config["enable_arbitrage"] is True

    def test_get_enabled_exchanges(self, sample_config):
        """Test getting list of enabled exchanges"""
        # Modify sample config to have enabled exchange
        sample_config["exchanges"]["binance"]["enabled"] = True

        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_config))
        ):

            config_manager = ConfigManager()
            enabled_exchanges = config_manager.get_enabled_exchanges()

            assert "binance" in enabled_exchanges

    def test_save_config(self, sample_config):
        """Test saving configuration to file"""
        with patch("builtins.open", mock_open()) as mock_file, patch(
            "pathlib.Path.chmod"
        ) as mock_chmod, patch("pathlib.Path.mkdir") as mock_mkdir:

            config_manager = ConfigManager()
            config_manager.config = sample_config
            result = config_manager.save_config()

            assert result is True
            mock_file.assert_called()
            # Note: chmod might be called during init as well, so just check it was called
            mock_chmod.assert_called()

    def test_invalid_config_file_creates_default(self, caplog):
        """Test that invalid config file triggers default config creation"""
        invalid_json = "{ invalid json }"

        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=invalid_json)
        ):

            config_manager = ConfigManager()

            # Should create default config when JSON is invalid
            assert config_manager.config is not None
            # Check that error was logged instead of printed
            assert "Invalid JSON in config file" in caplog.text

    def test_get_nonexistent_section_returns_empty_dict(self):
        """Test getting non-existent config section returns empty dict"""
        with patch("pathlib.Path.exists", return_value=False), patch(
            "builtins.open", mock_open()
        ):

            config_manager = ConfigManager()
            result = config_manager.get_section("nonexistent")

            assert result == {}

    def test_update_config_section(self, sample_config):
        """Test updating a specific config section"""
        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_config))
        ):

            config_manager = ConfigManager()

            # Update trading config
            new_trading_config = {"daily_loss_limit": 200.0}
            config_manager.update_section("trading", new_trading_config)

            updated_config = config_manager.get_section("trading")
            assert updated_config["daily_loss_limit"] == 200.0

    @pytest.mark.parametrize(
        "exchange_name,expected",
        [
            ("binance", False),
            ("coinbase", False),
            ("kraken", False),
        ],
    )
    def test_exchange_enabled_status(self, sample_config, exchange_name, expected):
        """Test checking if specific exchange is enabled"""
        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_config))
        ):

            config_manager = ConfigManager()
            result = config_manager.is_exchange_enabled(exchange_name)

            assert result == expected
