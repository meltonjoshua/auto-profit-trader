"""
Integration tests for Auto Profit Trader system components
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from security.crypto_manager import SecurityManager
from utils.config_manager import ConfigManager
from utils.logger import setup_logger


@pytest.mark.integration
class TestSystemIntegration:
    """Test integration between system components"""

    def test_config_manager_security_integration(self):
        """Test integration between ConfigManager and SecurityManager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup components
            config_path = Path(temp_dir) / "test_config.json"
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            config_manager = ConfigManager(config_path=config_path)
            security_manager = SecurityManager(key_file, creds_file)

            # Test configuration loading
            config = config_manager.get_config()
            assert "trading" in config
            assert "exchanges" in config

            # Test security manager functionality
            exchanges = config_manager.get_enabled_exchanges()
            assert isinstance(exchanges, list)

            # Test credential storage and retrieval
            if exchanges:
                exchange = exchanges[0] if exchanges else "test_exchange"
                test_key = "test_api_key"
                test_secret = "test_api_secret"

                security_manager.encrypt_api_credentials(
                    exchange, test_key, test_secret
                )
                retrieved_creds = security_manager.get_api_credentials(exchange)

                assert retrieved_creds is not None
                assert retrieved_creds["api_key"] == test_key
                assert retrieved_creds["api_secret"] == test_secret

    def test_logger_config_integration(self):
        """Test integration between logger and configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config_manager = ConfigManager(config_path=config_path)

            # Setup logger
            logger = setup_logger("test_integration")
            assert logger is not None
            assert logger.name == "test_integration"

            # Test logging with config data
            config = config_manager.get_config()
            logger.info(f"Loaded config with {len(config)} sections")

            # This should not raise any exceptions
            assert True

    @pytest.mark.slow
    def test_full_system_components_loading(self):
        """Test that all system components can be loaded without errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup temporary files
            config_path = Path(temp_dir) / "test_config.json"
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            try:
                # Test all core components can be initialized
                config_manager = ConfigManager(config_path=config_path)
                security_manager = SecurityManager(key_file, creds_file)
                logger = setup_logger("integration_test")

                # Verify they work together
                config = config_manager.get_config()
                exchanges = security_manager.list_stored_exchanges()

                logger.info(
                    f"System integration test: {len(config)} config sections, {len(exchanges)} stored exchanges"
                )

                # Test configuration sections exist
                assert "trading" in config
                assert "exchanges" in config
                assert "notifications" in config
                assert "risk_management" in config

                # Test security manager basic functionality
                assert isinstance(exchanges, list)

                # This integration test passes if no exceptions are raised
                assert True

            except Exception as e:
                pytest.fail(f"System integration failed: {e}")
