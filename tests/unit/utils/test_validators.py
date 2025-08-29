"""
Unit tests for input validators
"""

import pytest

from utils.validators import InputValidator, ValidationError


@pytest.mark.unit
class TestInputValidator:
    """Test cases for InputValidator class"""

    def test_validate_email_valid_emails(self):
        """Test validation of valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "trader123@crypto-exchange.io",
            "support+trading@platform.org",
        ]

        for email in valid_emails:
            assert InputValidator.validate_email(email), f"Failed for {email}"

    def test_validate_email_invalid_emails(self):
        """Test validation of invalid email addresses"""
        invalid_emails = [
            "",
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            None,
            123,
        ]

        for email in invalid_emails:
            assert not InputValidator.validate_email(email), f"Should fail for {email}"

    def test_validate_api_key_valid_keys(self):
        """Test validation of valid API keys"""
        valid_keys = [
            "abcdef1234567890",  # 16 chars
            "very_long_api_key_1234567890abcdef",  # Long key
            "API-KEY-WITH-DASHES-123",
        ]

        for key in valid_keys:
            assert InputValidator.validate_api_key(key), f"Failed for {key}"

    def test_validate_api_key_invalid_keys(self):
        """Test validation of invalid API keys"""
        invalid_keys = [
            "",
            "short",  # Too short
            "   ",  # Only whitespace
            None,
            123,
        ]

        for key in invalid_keys:
            assert not InputValidator.validate_api_key(key), f"Should fail for {key}"

    def test_validate_amount_valid_amounts(self):
        """Test validation of valid monetary amounts"""
        valid_amounts = [
            0,
            0.01,
            100.50,
            1000000,
            "123.45",  # String numbers should work
        ]

        for amount in valid_amounts:
            assert InputValidator.validate_amount(amount), f"Failed for {amount}"

    def test_validate_amount_invalid_amounts(self):
        """Test validation of invalid monetary amounts"""
        invalid_amounts = [
            -1,
            -0.01,
            "invalid",
            None,
            [],
        ]

        for amount in invalid_amounts:
            assert not InputValidator.validate_amount(
                amount
            ), f"Should fail for {amount}"

    def test_validate_percentage_valid_percentages(self):
        """Test validation of valid percentages"""
        valid_percentages = [
            0,
            0.5,
            50,
            100,
            "75.5",  # String numbers should work
        ]

        for pct in valid_percentages:
            assert InputValidator.validate_percentage(pct), f"Failed for {pct}"

    def test_validate_percentage_invalid_percentages(self):
        """Test validation of invalid percentages"""
        invalid_percentages = [
            -1,
            101,
            150,
            "invalid",
            None,
        ]

        for pct in invalid_percentages:
            assert not InputValidator.validate_percentage(pct), f"Should fail for {pct}"

    def test_validate_trading_pair_valid_symbols(self):
        """Test validation of valid trading pair symbols"""
        valid_symbols = [
            "BTC/USDT",
            "ETH/BTC",
            "ADA/USD",
            "DOGE/EUR",
            "SHIB/BUSD",
            "btc/usdt",  # Lowercase should be valid
            "eth/btc",
        ]

        for symbol in valid_symbols:
            assert InputValidator.validate_trading_pair(symbol), f"Failed for {symbol}"

    def test_validate_trading_pair_invalid_symbols(self):
        """Test validation of invalid trading pair symbols"""
        invalid_symbols = [
            "",
            "BTC",
            "BTC-USDT",  # Wrong separator
            "BTC/",
            "/USDT",
            "BTC/USDT/ETH",  # Too many parts
            None,
            123,
        ]

        for symbol in invalid_symbols:
            assert not InputValidator.validate_trading_pair(
                symbol
            ), f"Should fail for {symbol}"

    def test_sanitize_string_normal_input(self):
        """Test string sanitization with normal input"""
        input_str = "Normal trading bot text"
        result = InputValidator.sanitize_string(input_str)
        assert result == input_str

    def test_sanitize_string_with_control_chars(self):
        """Test string sanitization with control characters"""
        input_str = "Text with\x00control\x1fchars\x7f"
        result = InputValidator.sanitize_string(input_str)
        assert result == "Text withcontrolchars"

    def test_sanitize_string_length_limit(self):
        """Test string sanitization with length limit"""
        long_string = "a" * 300
        result = InputValidator.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_non_string_input(self):
        """Test string sanitization with non-string input"""
        result = InputValidator.sanitize_string(123)
        assert result == ""

        result = InputValidator.sanitize_string(None)
        assert result == ""

    def test_validate_config_section_valid_config(self):
        """Test validation of valid configuration section"""
        config = {
            "daily_loss_limit": 100.0,
            "max_position_size": 0.02,
            "enable_arbitrage": True,
        }
        required_fields = ["daily_loss_limit", "max_position_size"]

        errors = InputValidator.validate_config_section(config, required_fields)
        assert errors == []

    def test_validate_config_section_missing_fields(self):
        """Test validation with missing required fields"""
        config = {
            "daily_loss_limit": 100.0,
        }
        required_fields = ["daily_loss_limit", "max_position_size"]

        errors = InputValidator.validate_config_section(config, required_fields)
        assert "Missing required field: max_position_size" in errors

    def test_validate_config_section_empty_fields(self):
        """Test validation with empty required fields"""
        config = {
            "daily_loss_limit": "",
            "max_position_size": None,
        }
        required_fields = ["daily_loss_limit", "max_position_size"]

        errors = InputValidator.validate_config_section(config, required_fields)
        assert len(errors) == 2
        assert any("cannot be empty" in error for error in errors)

    def test_validate_exchange_config_valid_disabled(self):
        """Test validation of valid disabled exchange config"""
        config = {
            "enabled": False,
            "api_key": "",
            "api_secret": "",
        }

        errors = InputValidator.validate_exchange_config(config)
        assert errors == []

    def test_validate_exchange_config_valid_enabled(self):
        """Test validation of valid enabled exchange config"""
        config = {
            "enabled": True,
            "api_key": "valid_api_key_123456",
            "api_secret": "valid_api_secret_789012",
        }

        errors = InputValidator.validate_exchange_config(config)
        assert errors == []

    def test_validate_exchange_config_invalid_keys(self):
        """Test validation with invalid API keys"""
        config = {
            "enabled": True,
            "api_key": "short",  # Too short
            "api_secret": "",  # Empty
        }

        errors = InputValidator.validate_exchange_config(config)
        assert len(errors) == 2
        assert any("Invalid API key" in error for error in errors)
        assert any("Invalid API secret" in error for error in errors)

    def test_validate_risk_config_valid(self):
        """Test validation of valid risk configuration"""
        config = {
            "stop_loss_percentage": 0.02,
            "take_profit_percentage": 0.05,
            "max_trades_per_day": 50,
        }

        errors = InputValidator.validate_risk_config(config)
        assert errors == []

    def test_validate_risk_config_invalid_values(self):
        """Test validation with invalid risk values"""
        config = {
            "stop_loss_percentage": -0.01,  # Negative
            "take_profit_percentage": 0,  # Too small
            "max_trades_per_day": 2000,  # Too large
        }

        errors = InputValidator.validate_risk_config(config)
        assert len(errors) == 3

    def test_validate_trade_signal_valid(self):
        """Test validation of valid trade signal"""
        signal = {
            "action": "BUY",
            "symbol": "BTC/USDT",
            "amount": 0.001,
            "price": 45000.0,
            "confidence": 0.8,
        }

        errors = InputValidator.validate_trade_signal(signal)
        assert errors == []

    def test_validate_trade_signal_missing_fields(self):
        """Test validation with missing required fields"""
        signal = {
            "action": "BUY",
            # Missing symbol and amount
        }

        errors = InputValidator.validate_trade_signal(signal)
        assert len(errors) >= 2
        assert any("Missing required field: symbol" in error for error in errors)
        assert any("Missing required field: amount" in error for error in errors)

    def test_validate_trade_signal_invalid_values(self):
        """Test validation with invalid trade signal values"""
        signal = {
            "action": "INVALID",
            "symbol": "BTC-USDT",  # Wrong format
            "amount": -0.001,  # Negative
            "price": 0,  # Too small
            "confidence": 1.5,  # Too large
        }

        errors = InputValidator.validate_trade_signal(signal)
        assert len(errors) >= 5
