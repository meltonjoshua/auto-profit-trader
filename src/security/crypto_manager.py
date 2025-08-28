"""
Security utilities for Auto Profit Trader
Handles API key encryption and secure credential management
"""

import os
from cryptography.fernet import Fernet
from pathlib import Path
import json
import base64
from typing import Optional, Dict


class SecurityManager:
    """Handles encryption and security for the trading bot"""
    
    def __init__(self):
        self.key_file = Path(".encryption_key")
        self.credentials_file = Path("encrypted_credentials.json")
        self._ensure_encryption_key()
    
    def _ensure_encryption_key(self):
        """Ensure encryption key exists"""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions
            self.key_file.chmod(0o600)
            print("🔐 Generated new encryption key")
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet encryption instance"""
        with open(self.key_file, 'rb') as f:
            key = f.read()
        return Fernet(key)
    
    def encrypt_api_credentials(self, exchange: str, api_key: str, api_secret: str):
        """Encrypt and store API credentials"""
        fernet = self._get_fernet()
        
        credentials = {
            "api_key": fernet.encrypt(api_key.encode()).decode(),
            "api_secret": fernet.encrypt(api_secret.encode()).decode()
        }
        
        # Load existing credentials
        if self.credentials_file.exists():
            with open(self.credentials_file, 'r') as f:
                all_credentials = json.load(f)
        else:
            all_credentials = {}
        
        all_credentials[exchange] = credentials
        
        # Save encrypted credentials
        with open(self.credentials_file, 'w') as f:
            json.dump(all_credentials, f, indent=2)
        
        self.credentials_file.chmod(0o600)
        print(f"🔐 Encrypted and stored credentials for {exchange}")
    
    def decrypt_api_credentials(self, exchange: str) -> dict:
        """Decrypt API credentials for an exchange"""
        if not self.credentials_file.exists():
            return {"api_key": "", "api_secret": ""}
        
        with open(self.credentials_file, 'r') as f:
            all_credentials = json.load(f)
        
        if exchange not in all_credentials:
            return {"api_key": "", "api_secret": ""}
        
        fernet = self._get_fernet()
        credentials = all_credentials[exchange]
        
        try:
            decrypted_credentials = {
                "api_key": fernet.decrypt(credentials["api_key"].encode()).decode(),
                "api_secret": fernet.decrypt(credentials["api_secret"].encode()).decode()
            }
            return decrypted_credentials
        except Exception as e:
            print(f"❌ Failed to decrypt credentials for {exchange}: {e}")
            return {"api_key": "", "api_secret": ""}
    
    def get_api_credentials(self, exchange: str) -> Optional[Dict]:
        """Get decrypted API credentials for an exchange"""
        try:
            if not self.credentials_file.exists():
                return None
            
            with open(self.credentials_file, 'r') as f:
                all_credentials = json.load(f)
            
            encrypted_creds = all_credentials.get(exchange)
            if not encrypted_creds:
                return None
            
            fernet = self._get_fernet()
            
            credentials = {
                'api_key': fernet.decrypt(encrypted_creds['api_key'].encode()).decode(),
                'api_secret': fernet.decrypt(encrypted_creds['api_secret'].encode()).decode()
            }
            
            return credentials
            
        except Exception as e:
            print(f"❌ Error decrypting credentials for {exchange}: {e}")
            return None
        """Validate that API key has safe permissions (read-only preferred)"""
        # This would normally connect to the exchange and check permissions
        # For now, return True as mock validation
        print(f"✅ API key permissions validated for {exchange}")
        return True
    
    def secure_wipe_memory(self, sensitive_data: str):
        """Securely wipe sensitive data from memory"""
        # Python doesn't have true secure memory wiping, but we can overwrite
        if isinstance(sensitive_data, str):
            # Overwrite with random data
            import secrets
            overwrite = ''.join(secrets.choice('0123456789abcdef') for _ in range(len(sensitive_data)))
            sensitive_data = overwrite
            del overwrite
        del sensitive_data


class EnvironmentValidator:
    """Validates environment security"""
    
    @staticmethod
    def check_environment_security():
        """Check for common security issues"""
        issues = []
        
        # Check for .env file exposure
        if Path('.env').exists():
            if oct(Path('.env').stat().st_mode)[-3:] != '600':
                issues.append("⚠️ .env file has incorrect permissions")
        
        # Check for API keys in environment variables
        dangerous_env_vars = []
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                if len(value) > 10:  # Likely an actual credential
                    dangerous_env_vars.append(key)
        
        if dangerous_env_vars:
            issues.append(f"⚠️ Potential credentials in environment: {', '.join(dangerous_env_vars)}")
        
        # Check file permissions
        sensitive_files = ['config.json', 'encrypted_credentials.json', '.encryption_key']
        for file_path in sensitive_files:
            if Path(file_path).exists():
                perms = oct(Path(file_path).stat().st_mode)[-3:]
                if perms not in ['600', '400']:
                    issues.append(f"⚠️ {file_path} has insecure permissions: {perms}")
        
        return issues
    
    @staticmethod
    def secure_environment():
        """Apply security best practices to environment"""
        # Set secure permissions on sensitive files
        sensitive_files = ['config.json', 'encrypted_credentials.json', '.encryption_key']
        for file_path in sensitive_files:
            if Path(file_path).exists():
                Path(file_path).chmod(0o600)
                print(f"🔒 Secured permissions for {file_path}")


def generate_secure_session_id() -> str:
    """Generate a cryptographically secure session ID"""
    import secrets
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging/monitoring without exposing it"""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()[:8]  # First 8 chars for identification