"""
Unit tests for SecurityManager
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from security.crypto_manager import (
    EnvironmentValidator,
    SecurityError,
    SecurityManager,
    generate_secure_session_id,
    hash_sensitive_data,
)


@pytest.mark.unit
class TestSecurityManager:
    """Test cases for SecurityManager class"""

    def test_init_creates_encryption_key(self):
        """Test that SecurityManager creates encryption key on initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            assert key_file.exists()
            assert oct(key_file.stat().st_mode)[-3:] == "600"

    def test_encrypt_decrypt_credentials_roundtrip(self):
        """Test encrypting and decrypting credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Test data
            exchange = "binance"
            api_key = "test_api_key_12345"
            api_secret = "test_api_secret_67890"

            # Encrypt credentials
            result = security_manager.encrypt_api_credentials(
                exchange, api_key, api_secret
            )
            assert result is True

            # Decrypt credentials
            decrypted = security_manager.decrypt_api_credentials(exchange)
            assert decrypted["api_key"] == api_key
            assert decrypted["api_secret"] == api_secret

    def test_encrypt_invalid_credentials(self):
        """Test encryption with invalid inputs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Test empty values
            result = security_manager.encrypt_api_credentials("", "key", "secret")
            assert result is False

            result = security_manager.encrypt_api_credentials("binance", "", "secret")
            assert result is False

            result = security_manager.encrypt_api_credentials("binance", "key", "")
            assert result is False

    def test_decrypt_nonexistent_exchange(self):
        """Test decrypting credentials for non-existent exchange"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Try to decrypt non-existent exchange
            result = security_manager.decrypt_api_credentials("nonexistent")
            assert result == {"api_key": "", "api_secret": ""}

    def test_decrypt_corrupted_credentials(self):
        """Test decrypting corrupted credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Create corrupted credentials file
            corrupted_creds = {
                "binance": {"api_key": "corrupted_data", "api_secret": "also_corrupted"}
            }

            with open(creds_file, "w") as f:
                json.dump(corrupted_creds, f)

            result = security_manager.decrypt_api_credentials("binance")
            assert result == {"api_key": "", "api_secret": ""}

    def test_get_api_credentials_existing(self):
        """Test getting existing API credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Store credentials
            exchange = "coinbase"
            api_key = "coinbase_key"
            api_secret = "coinbase_secret"

            security_manager.encrypt_api_credentials(exchange, api_key, api_secret)

            # Get credentials
            result = security_manager.get_api_credentials(exchange)
            assert result is not None
            assert result["api_key"] == api_key
            assert result["api_secret"] == api_secret

    def test_get_api_credentials_nonexistent(self):
        """Test getting non-existent API credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            result = security_manager.get_api_credentials("nonexistent")
            assert result is None

    def test_list_stored_exchanges(self):
        """Test listing stored exchanges"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Initially empty
            exchanges = security_manager.list_stored_exchanges()
            assert exchanges == []

            # Add some exchanges
            security_manager.encrypt_api_credentials("binance", "key1", "secret1")
            security_manager.encrypt_api_credentials("coinbase", "key2", "secret2")

            exchanges = security_manager.list_stored_exchanges()
            assert set(exchanges) == {"binance", "coinbase"}

    def test_remove_credentials(self):
        """Test removing stored credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # Add credentials
            security_manager.encrypt_api_credentials("binance", "key", "secret")

            # Verify they exist
            assert security_manager.get_api_credentials("binance") is not None

            # Remove them
            result = security_manager.remove_credentials("binance")
            assert result is True

            # Verify they're gone
            assert security_manager.get_api_credentials("binance") is None

    def test_validate_api_permissions(self):
        """Test API permissions validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # This is a mock implementation, should always return True
            result = security_manager.validate_api_permissions("binance")
            assert result is True

    def test_secure_wipe_memory(self):
        """Test secure memory wiping"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            creds_file = Path(temp_dir) / "test_creds.json"

            security_manager = SecurityManager(key_file, creds_file)

            # This should not raise an exception
            sensitive_data = "super_secret_key"
            security_manager.secure_wipe_memory(sensitive_data)

    def test_security_error_on_key_failure(self):
        """Test SecurityError is raised when key operations fail"""
        with patch("pathlib.Path.exists", return_value=False), patch(
            "builtins.open", side_effect=PermissionError("Access denied")
        ):

            with pytest.raises(SecurityError):
                SecurityManager()


class TestEnvironmentValidator:
    """Test cases for EnvironmentValidator class"""

    def test_check_environment_security_no_issues(self):
        """Test environment security check with no issues"""
        with patch("pathlib.Path.exists", return_value=False), patch("os.environ", {}):

            issues = EnvironmentValidator.check_environment_security()
            assert issues == []

    def test_check_environment_security_with_issues(self):
        """Test environment security check with issues"""
        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.stat"
        ) as mock_stat, patch("os.environ", {"API_KEY": "very_long_api_key_12345"}):

            # Mock file with insecure permissions
            mock_stat.return_value.st_mode = 0o644  # Readable by others

            issues = EnvironmentValidator.check_environment_security()
            assert len(issues) > 0
            assert any("credentials in environment" in issue for issue in issues)

    def test_secure_environment(self):
        """Test environment security hardening"""
        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.chmod"
        ) as mock_chmod:

            EnvironmentValidator.secure_environment()

            # Should call chmod for each sensitive file that exists
            assert mock_chmod.called


class TestUtilityFunctions:
    """Test cases for utility functions"""

    def test_generate_secure_session_id(self):
        """Test secure session ID generation"""
        session_id = generate_secure_session_id()

        assert isinstance(session_id, str)
        assert len(session_id) > 30  # Should be reasonably long

        # Should be unique
        session_id2 = generate_secure_session_id()
        assert session_id != session_id2

    def test_hash_sensitive_data(self):
        """Test sensitive data hashing"""
        data = "sensitive_api_key_12345"
        hash_result = hash_sensitive_data(data)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 8  # Should return first 8 chars

        # Should be deterministic
        hash_result2 = hash_sensitive_data(data)
        assert hash_result == hash_result2

        # Different data should produce different hash
        hash_different = hash_sensitive_data("different_data")
        assert hash_result != hash_different
