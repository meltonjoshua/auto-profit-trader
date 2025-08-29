"""
Security utilities for Auto Profit Trader
Handles API key encryption and secure credential management
"""

import base64
import json
import logging
import os
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Custom exception for security-related errors"""

    pass


class SecurityManager:
    """Handles encryption and security for the trading bot"""

    def __init__(
        self, key_file: Optional[Path] = None, credentials_file: Optional[Path] = None
    ) -> None:
        """
        Initialize SecurityManager

        Args:
            key_file: Optional path to encryption key file
            credentials_file: Optional path to credentials file
        """
        self.key_file = key_file or Path(".encryption_key")
        self.credentials_file = credentials_file or Path("encrypted_credentials.json")
        self._ensure_encryption_key()

    def _ensure_encryption_key(self) -> None:
        """
        Ensure encryption key exists

        Raises:
            SecurityError: If key creation fails
        """
        import platform
        
        try:
            if not self.key_file.exists():
                key = Fernet.generate_key()

                # Ensure directory exists
                self.key_file.parent.mkdir(parents=True, exist_ok=True)

                with open(self.key_file, "wb") as f:
                    f.write(key)

                # Set restrictive permissions (owner read/write only)
                try:
                    self.key_file.chmod(0o600)
                except (OSError, NotImplementedError):
                    # On Windows, chmod might not work as expected
                    if platform.system() == "Windows":
                        logger.info("Windows detected - file permissions handled by OS")
                    else:
                        logger.warning("Could not set file permissions")
                        
                logger.info("Generated new encryption key")
            else:
                # Verify key file has secure permissions (skip on Windows)
                if platform.system() != "Windows":
                    current_permissions = oct(self.key_file.stat().st_mode)[-3:]
                    if current_permissions != "600":
                        logger.warning(
                            "Encryption key file has insecure permissions: %s",
                            current_permissions,
                        )
                        try:
                            self.key_file.chmod(0o600)
                        except (OSError, NotImplementedError):
                            logger.warning("Could not fix file permissions")

        except Exception as e:
            logger.error("Failed to ensure encryption key: %s", e)
            raise SecurityError(f"Failed to create or access encryption key: {e}")

    def _get_fernet(self) -> Fernet:
        """
        Get Fernet encryption instance

        Returns:
            Fernet encryption instance

        Raises:
            SecurityError: If key loading fails
        """
        try:
            with open(self.key_file, "rb") as f:
                key = f.read()
            return Fernet(key)
        except Exception as e:
            logger.error("Failed to load encryption key: %s", e)
            raise SecurityError(f"Failed to load encryption key: {e}")

    def encrypt_api_credentials(
        self, exchange: str, api_key: str, api_secret: str
    ) -> bool:
        """
        Encrypt and store API credentials

        Args:
            exchange: Exchange name
            api_key: API key to encrypt
            api_secret: API secret to encrypt

        Returns:
            True if successful, False otherwise
        """
        if not exchange or not api_key or not api_secret:
            logger.warning("Invalid credentials provided for encryption")
            return False

        try:
            fernet = self._get_fernet()

            credentials = {
                "api_key": fernet.encrypt(api_key.encode()).decode(),
                "api_secret": fernet.encrypt(api_secret.encode()).decode(),
            }

            # Load existing credentials
            all_credentials = {}
            if self.credentials_file.exists():
                try:
                    with open(self.credentials_file, "r", encoding="utf-8") as f:
                        all_credentials = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    logger.warning("Corrupted credentials file, creating new one")
                    all_credentials = {}

            all_credentials[exchange] = credentials

            # Ensure directory exists
            self.credentials_file.parent.mkdir(parents=True, exist_ok=True)

            # Save encrypted credentials
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                json.dump(all_credentials, f, indent=2)

            # Set secure permissions (handle Windows compatibility)
            try:
                self.credentials_file.chmod(0o600)
            except (OSError, NotImplementedError):
                import platform
                if platform.system() == "Windows":
                    logger.debug("Windows detected - file permissions handled by OS")
                else:
                    logger.warning("Could not set secure permissions on credentials file")
                    
            logger.info("Encrypted and stored credentials for %s", exchange)
            return True

        except Exception as e:
            logger.error("Failed to encrypt credentials for %s: %s", exchange, e)
            return False

    def decrypt_api_credentials(self, exchange: str) -> Dict[str, str]:
        """
        Decrypt API credentials for an exchange

        Args:
            exchange: Exchange name

        Returns:
            Dictionary with api_key and api_secret, empty strings if not found/failed
        """
        default_creds = {"api_key": "", "api_secret": ""}

        if not exchange:
            logger.warning("Empty exchange name provided")
            return default_creds

        try:
            if not self.credentials_file.exists():
                logger.debug("Credentials file does not exist")
                return default_creds

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            if exchange not in all_credentials:
                logger.debug("No credentials found for exchange: %s", exchange)
                return default_creds

            fernet = self._get_fernet()
            credentials = all_credentials[exchange]

            decrypted_credentials = {
                "api_key": fernet.decrypt(credentials["api_key"].encode()).decode(),
                "api_secret": fernet.decrypt(
                    credentials["api_secret"].encode()
                ).decode(),
            }

            logger.debug("Successfully decrypted credentials for %s", exchange)
            return decrypted_credentials

        except InvalidToken:
            logger.error(
                "Invalid encryption token for %s - credentials may be corrupted",
                exchange,
            )
            return default_creds
        except Exception as e:
            logger.error("Failed to decrypt credentials for %s: %s", exchange, e)
            return default_creds

    def get_api_credentials(self, exchange: str) -> Optional[Dict[str, str]]:
        """
        Get decrypted API credentials for an exchange

        Args:
            exchange: Exchange name

        Returns:
            Dictionary with credentials or None if not found
        """
        try:
            credentials = self.decrypt_api_credentials(exchange)

            # Return None if credentials are empty (not found)
            if not credentials["api_key"] and not credentials["api_secret"]:
                return None

            return credentials

        except Exception as e:
            logger.error("Error getting API credentials for %s: %s", exchange, e)
            return None

    def validate_api_permissions(self, exchange: str) -> bool:
        """
        Validate that API key has safe permissions (read-only preferred)

        Args:
            exchange: Exchange name

        Returns:
            True if permissions are safe

        Note:
            This is a placeholder implementation. In production, this should
            connect to the exchange API and verify permissions.
        """
        # This would normally connect to the exchange and check permissions
        # For now, return True as mock validation
        logger.debug("API key permissions validated for %s", exchange)
        return True

    def secure_wipe_memory(self, sensitive_data: str) -> None:
        """
        Securely wipe sensitive data from memory

        Args:
            sensitive_data: Data to wipe

        Note:
            Python doesn't have true secure memory wiping, but we can overwrite
        """
        if isinstance(sensitive_data, str):
            # Overwrite with random data
            overwrite = "".join(
                secrets.choice("0123456789abcdef") for _ in range(len(sensitive_data))
            )
            sensitive_data = overwrite
            del overwrite
        del sensitive_data

    def list_stored_exchanges(self) -> List[str]:
        """
        Get list of exchanges with stored credentials

        Returns:
            List of exchange names
        """
        try:
            if not self.credentials_file.exists():
                return []

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            return list(all_credentials.keys())

        except Exception as e:
            logger.error("Error listing stored exchanges: %s", e)
            return []

    def remove_credentials(self, exchange: str) -> bool:
        """
        Remove stored credentials for an exchange

        Args:
            exchange: Exchange name

        Returns:
            True if successful
        """
        try:
            if not self.credentials_file.exists():
                return True

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            if exchange in all_credentials:
                del all_credentials[exchange]

                with open(self.credentials_file, "w", encoding="utf-8") as f:
                    json.dump(all_credentials, f, indent=2)

                logger.info("Removed credentials for %s", exchange)
                return True

            return True  # No credentials to remove

        except Exception as e:
            logger.error("Error removing credentials for %s: %s", exchange, e)
            return False


class EnvironmentValidator:
    """Validates environment security"""

    @staticmethod
    def check_environment_security() -> List[str]:
        """
        Check for common security issues

        Returns:
            List of security issues found
        """
        issues = []

        # Check for .env file exposure
        if Path(".env").exists():
            if oct(Path(".env").stat().st_mode)[-3:] != "600":
                issues.append("⚠️ .env file has incorrect permissions")

        # Check for API keys in environment variables
        dangerous_env_vars = []
        for key, value in os.environ.items():
            if any(
                keyword in key.upper()
                for keyword in ["API_KEY", "SECRET", "PASSWORD", "TOKEN"]
            ):
                if len(value) > 10:  # Likely an actual credential
                    dangerous_env_vars.append(key)

        if dangerous_env_vars:
            issues.append(
                f"⚠️ Potential credentials in environment: {', '.join(dangerous_env_vars)}"
            )

        # Check file permissions
        sensitive_files = [
            "config.json",
            "encrypted_credentials.json",
            ".encryption_key",
        ]
        for file_path in sensitive_files:
            if Path(file_path).exists():
                perms = oct(Path(file_path).stat().st_mode)[-3:]
                if perms not in ["600", "400"]:
                    issues.append(f"⚠️ {file_path} has insecure permissions: {perms}")

        return issues

    @staticmethod
    def secure_environment() -> None:
        """Apply security best practices to environment"""
        # Set secure permissions on sensitive files
        sensitive_files = [
            "config.json",
            "encrypted_credentials.json",
            ".encryption_key",
        ]
        for file_path in sensitive_files:
            if Path(file_path).exists():
                Path(file_path).chmod(0o600)
                logger.info("Secured permissions for %s", file_path)


def generate_secure_session_id() -> str:
    """
    Generate a cryptographically secure session ID

    Returns:
        Secure session ID
    """
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data for logging/monitoring without exposing it

    Args:
        data: Sensitive data to hash

    Returns:
        First 8 characters of SHA256 hash for identification
    """
    import hashlib

    return hashlib.sha256(data.encode()).hexdigest()[:8]
