"""
Input validation utilities for Auto Profit Trader
"""

import re
from typing import Any, Dict, List, Optional, Union


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


class InputValidator:
    """Utility class for input validation and sanitization"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format

        Args:
            email: Email address to validate

        Returns:
            True if email is valid
        """
        if not email or not isinstance(email, str):
            return False

        # RFC 5322 compliant email validation (simplified)
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        # Check basic format
        if not re.match(pattern, email):
            return False

        # Reject consecutive dots
        if ".." in email:
            return False

        # Check for valid local and domain parts
        parts = email.split("@")
        if len(parts) != 2:
            return False

        local, domain = parts

        # Local part cannot be empty or start/end with dot
        if not local or local.startswith(".") or local.endswith("."):
            return False

        # Domain must have at least one dot and valid TLD
        if "." not in domain or domain.startswith(".") or domain.endswith("."):
            return False

        return True

    @staticmethod
    def validate_api_key(api_key: str, min_length: int = 16) -> bool:
        """
        Validate API key format

        Args:
            api_key: API key to validate
            min_length: Minimum length requirement

        Returns:
            True if API key is valid
        """
        if not api_key or not isinstance(api_key, str):
            return False

        return len(api_key.strip()) >= min_length

    @staticmethod
    def validate_amount(amount: Union[int, float], min_value: float = 0) -> bool:
        """
        Validate monetary amount

        Args:
            amount: Amount to validate
            min_value: Minimum allowed value

        Returns:
            True if amount is valid
        """
        try:
            amount_float = float(amount)
            return amount_float >= min_value
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_percentage(percentage: Union[int, float]) -> bool:
        """
        Validate percentage value (0-100)

        Args:
            percentage: Percentage to validate

        Returns:
            True if percentage is valid
        """
        try:
            pct_float = float(percentage)
            return 0 <= pct_float <= 100
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_trading_pair(symbol: str) -> bool:
        """
        Validate trading pair symbol format

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT' or 'btc/usdt')

        Returns:
            True if symbol is valid
        """
        if not symbol or not isinstance(symbol, str):
            return False

        # Check for common trading pair formats (case insensitive)
        pattern = r"^[A-Za-z0-9]{2,10}/[A-Za-z0-9]{2,10}$"
        return re.match(pattern, symbol) is not None

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255) -> str:
        """
        Sanitize string input

        Args:
            input_str: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return ""

        # Remove control characters and limit length
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", input_str)
        return sanitized[:max_length].strip()

    @staticmethod
    def validate_config_section(
        config: Dict[str, Any], required_fields: List[str]
    ) -> List[str]:
        """
        Validate configuration section

        Args:
            config: Configuration dictionary
            required_fields: List of required field names

        Returns:
            List of missing or invalid fields
        """
        errors = []

        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return errors

        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
            elif config[field] is None or config[field] == "":
                errors.append(f"Field cannot be empty: {field}")

        return errors

    @staticmethod
    def validate_exchange_config(exchange_config: Dict[str, Any]) -> List[str]:
        """
        Validate exchange configuration

        Args:
            exchange_config: Exchange configuration dictionary

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(exchange_config, dict):
            return ["Exchange configuration must be a dictionary"]

        # Check required fields
        required_fields = ["enabled", "api_key", "api_secret"]
        for field in required_fields:
            if field not in exchange_config:
                errors.append(f"Missing required field: {field}")

        # Validate API credentials if exchange is enabled
        if exchange_config.get("enabled", False):
            api_key = exchange_config.get("api_key", "")
            api_secret = exchange_config.get("api_secret", "")

            if not InputValidator.validate_api_key(api_key):
                errors.append("Invalid API key format")

            if not InputValidator.validate_api_key(api_secret):
                errors.append("Invalid API secret format")

        return errors

    @staticmethod
    def validate_risk_config(risk_config: Dict[str, Any]) -> List[str]:
        """
        Validate risk management configuration

        Args:
            risk_config: Risk configuration dictionary

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(risk_config, dict):
            return ["Risk configuration must be a dictionary"]

        # Validate stop loss percentage
        stop_loss = risk_config.get("stop_loss_percentage")
        if stop_loss is not None and not InputValidator.validate_amount(
            stop_loss, 0.001
        ):
            errors.append("Stop loss percentage must be a positive number >= 0.001")

        # Validate take profit percentage
        take_profit = risk_config.get("take_profit_percentage")
        if take_profit is not None and not InputValidator.validate_amount(
            take_profit, 0.001
        ):
            errors.append("Take profit percentage must be a positive number >= 0.001")

        # Validate max trades per day
        max_trades = risk_config.get("max_trades_per_day")
        if max_trades is not None:
            try:
                max_trades_int = int(max_trades)
                if max_trades_int <= 0 or max_trades_int > 1000:
                    errors.append("Max trades per day must be between 1 and 1000")
            except (ValueError, TypeError):
                errors.append("Max trades per day must be a valid integer")

        return errors

    @staticmethod
    def validate_trade_signal(signal: Dict[str, Any]) -> List[str]:
        """
        Validate trade signal data

        Args:
            signal: Trade signal dictionary

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(signal, dict):
            return ["Trade signal must be a dictionary"]

        # Validate required fields
        required_fields = ["action", "symbol", "amount"]
        for field in required_fields:
            if field not in signal:
                errors.append(f"Missing required field: {field}")

        # Validate action
        action = signal.get("action")
        if action not in ["BUY", "SELL", "buy", "sell"]:
            errors.append("Action must be BUY or SELL")

        # Validate symbol
        symbol = signal.get("symbol")
        if symbol and not InputValidator.validate_trading_pair(symbol):
            errors.append("Invalid trading pair symbol format")

        # Validate amount
        amount = signal.get("amount")
        if amount is not None and not InputValidator.validate_amount(amount, 0.000001):
            errors.append("Amount must be a positive number >= 0.000001")

        # Validate price if provided
        price = signal.get("price")
        if price is not None and not InputValidator.validate_amount(price, 0.01):
            errors.append("Price must be a positive number >= 0.01")

        # Validate confidence if provided
        confidence = signal.get("confidence")
        if confidence is not None:
            try:
                conf_float = float(confidence)
                if not 0 <= conf_float <= 1:
                    errors.append("Confidence must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("Confidence must be a valid number")

        return errors
