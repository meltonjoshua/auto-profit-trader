#!/usr/bin/env python3
"""
Production Setup Script for Auto Profit Trader
Configures the bot for real autonomous trading
"""

import json
import os
import sys
from pathlib import Path
from getpass import getpass

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from security.crypto_manager import SecurityManager
from utils.config_manager import ConfigManager


def print_banner():
    """Print setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        Auto Profit Trader - Production Setup Wizard         ║
║                                                              ║
║              Configure for Real Autonomous Trading          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

⚠️  IMPORTANT: This setup configures REAL trading with REAL money!
💰 Only proceed if you understand the risks and have tested thoroughly.
🔐 Your API keys will be encrypted and stored securely.

"""
    print(banner)


def get_user_input(prompt, default=None, input_type=str, required=True):
    """Get user input with validation"""
    while True:
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        try:
            if input_type == bool:
                value = input(full_prompt).strip().lower()
                if not value and default is not None:
                    return default
                return value in ['y', 'yes', 'true', '1']
            elif input_type == float:
                value = input(full_prompt).strip()
                if not value and default is not None:
                    return default
                return float(value)
            elif input_type == int:
                value = input(full_prompt).strip()
                if not value and default is not None:
                    return default
                return int(value)
            else:
                value = input(full_prompt).strip()
                if not value and default is not None:
                    return default
                if not value and required:
                    print("❌ This field is required.")
                    continue
                return value
        except ValueError:
            print(f"❌ Invalid {input_type.__name__} value. Please try again.")
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user.")
            sys.exit(0)


def configure_production_trading():
    """Configure production trading settings"""
    print("\n📊 TRADING CONFIGURATION")
    print("Configure your trading parameters for autonomous operation.\n")
    
    daily_loss_limit = get_user_input(
        "Daily loss limit (USD)", 
        default=100.0, 
        input_type=float
    )
    
    max_position_size = get_user_input(
        "Maximum position size (% of balance, 0.01 = 1%)", 
        default=0.02, 
        input_type=float
    )
    
    enable_arbitrage = get_user_input(
        "Enable arbitrage trading (y/n)", 
        default=True, 
        input_type=bool
    )
    
    enable_momentum = get_user_input(
        "Enable momentum trading (y/n)", 
        default=True, 
        input_type=bool
    )
    
    target_profit_arbitrage = get_user_input(
        "Minimum arbitrage profit (%, 0.005 = 0.5%)", 
        default=0.005, 
        input_type=float
    )
    
    target_profit_momentum = get_user_input(
        "Target momentum profit (%, 0.02 = 2%)", 
        default=0.02, 
        input_type=float
    )
    
    return {
        "daily_loss_limit": daily_loss_limit,
        "max_position_size": max_position_size,
        "enable_arbitrage": enable_arbitrage,
        "enable_momentum": enable_momentum,
        "target_profit_arbitrage": target_profit_arbitrage,
        "target_profit_momentum": target_profit_momentum
    }


def configure_exchange(exchange_name, exchange_info):
    """Configure a specific exchange"""
    print(f"\n🏢 CONFIGURING {exchange_name.upper()}")
    print(f"Setting up {exchange_info['name']} for real trading.\n")
    
    enabled = get_user_input(
        f"Enable {exchange_name} trading (y/n)", 
        default=False, 
        input_type=bool
    )
    
    if not enabled:
        return {
            "enabled": False,
            "api_key": "",
            "api_secret": "",
            "testnet": True
        }
    
    print(f"\n⚠️  LIVE TRADING WARNING:")
    print(f"You are about to configure {exchange_name} for REAL trading!")
    print(f"Make sure your API keys have appropriate permissions.")
    print(f"Recommended: Spot trading only, NO withdrawal permissions.\n")
    
    confirm = get_user_input(
        f"Continue with LIVE {exchange_name} setup? (y/n)", 
        default=False, 
        input_type=bool
    )
    
    if not confirm:
        return {
            "enabled": False,
            "api_key": "",
            "api_secret": "",
            "testnet": True
        }
    
    api_key = get_user_input(f"{exchange_name} API Key")
    api_secret = getpass(f"{exchange_name} API Secret (hidden): ")
    
    # Ask about testnet/sandbox
    use_testnet = get_user_input(
        f"Use testnet/sandbox for {exchange_name} (HIGHLY RECOMMENDED for first run) (y/n)", 
        default=True, 
        input_type=bool
    )
    
    return {
        "enabled": True,
        "api_key": api_key,
        "api_secret": api_secret,
        "testnet": use_testnet if exchange_name in ["binance", "kraken"] else False,
        "sandbox": use_testnet if exchange_name == "coinbase" else False
    }


def configure_exchanges():
    """Configure all exchanges"""
    print("\n🔗 EXCHANGE CONFIGURATION")
    print("Configure your cryptocurrency exchanges for trading.\n")
    
    exchanges_info = {
        "binance": {"name": "Binance", "testnet": True},
        "coinbase": {"name": "Coinbase Pro", "sandbox": True},
        "kraken": {"name": "Kraken", "testnet": True}
    }
    
    exchanges = {}
    
    for exchange_name, exchange_info in exchanges_info.items():
        exchanges[exchange_name] = configure_exchange(exchange_name, exchange_info)
    
    return exchanges


def configure_notifications():
    """Configure notification settings"""
    print("\n📱 NOTIFICATION CONFIGURATION")
    print("Configure notifications to monitor your trading bot.\n")
    
    # Telegram
    telegram_enabled = get_user_input(
        "Enable Telegram notifications (y/n)", 
        default=False, 
        input_type=bool
    )
    
    telegram_config = {"enabled": False, "bot_token": "", "chat_id": ""}
    if telegram_enabled:
        telegram_config = {
            "enabled": True,
            "bot_token": get_user_input("Telegram Bot Token"),
            "chat_id": get_user_input("Telegram Chat ID")
        }
    
    # Discord
    discord_enabled = get_user_input(
        "Enable Discord notifications (y/n)", 
        default=False, 
        input_type=bool
    )
    
    discord_config = {"enabled": False, "webhook_url": ""}
    if discord_enabled:
        discord_config = {
            "enabled": True,
            "webhook_url": get_user_input("Discord Webhook URL")
        }
    
    # Email
    email_enabled = get_user_input(
        "Enable Email notifications (y/n)", 
        default=False, 
        input_type=bool
    )
    
    email_config = {
        "enabled": False,
        "smtp_server": "",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "to_email": ""
    }
    
    if email_enabled:
        email_config = {
            "enabled": True,
            "smtp_server": get_user_input("SMTP Server", default="smtp.gmail.com"),
            "smtp_port": get_user_input("SMTP Port", default=587, input_type=int),
            "username": get_user_input("Email Username"),
            "password": getpass("Email Password (hidden): "),
            "to_email": get_user_input("Notification Email Address")
        }
    
    return {
        "telegram": telegram_config,
        "discord": discord_config,
        "email": email_config
    }


def configure_risk_management():
    """Configure risk management settings"""
    print("\n🛡️ RISK MANAGEMENT CONFIGURATION")
    print("Configure safety parameters for autonomous trading.\n")
    
    stop_loss = get_user_input(
        "Stop loss percentage (0.02 = 2%)", 
        default=0.02, 
        input_type=float
    )
    
    take_profit = get_user_input(
        "Take profit percentage (0.05 = 5%)", 
        default=0.05, 
        input_type=float
    )
    
    max_trades_per_day = get_user_input(
        "Maximum trades per day", 
        default=50, 
        input_type=int
    )
    
    cooldown_after_loss = get_user_input(
        "Cooldown after loss (seconds)", 
        default=300, 
        input_type=int
    )
    
    return {
        "stop_loss_percentage": stop_loss,
        "take_profit_percentage": take_profit,
        "max_trades_per_day": max_trades_per_day,
        "cooldown_after_loss": cooldown_after_loss
    }


def save_configuration(config, security_manager):
    """Save configuration and encrypt API credentials"""
    print("\n💾 SAVING CONFIGURATION")
    
    # Extract and encrypt API credentials
    exchanges_config = config["exchanges"].copy()
    
    for exchange_name, exchange_config in exchanges_config.items():
        if exchange_config.get("enabled") and exchange_config.get("api_key"):
            print(f"🔐 Encrypting {exchange_name} credentials...")
            
            # Encrypt credentials
            security_manager.encrypt_api_credentials(
                exchange_name,
                exchange_config["api_key"],
                exchange_config["api_secret"]
            )
            
            # Remove from main config (will be stored encrypted separately)
            exchanges_config[exchange_name]["api_key"] = ""
            exchanges_config[exchange_name]["api_secret"] = ""
    
    config["exchanges"] = exchanges_config
    
    # Save main configuration
    config_path = Path("config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    config_path.chmod(0o600)  # Restrict permissions
    print(f"✅ Configuration saved to {config_path}")


def final_checklist():
    """Display final pre-trading checklist"""
    print("\n🎯 FINAL CHECKLIST")
    print("Before starting autonomous trading, verify:\n")
    
    checklist = [
        "✅ All API keys are for TESTNET/SANDBOX (recommended for first run)",
        "✅ API keys have NO withdrawal permissions",
        "✅ Daily loss limit is set to an acceptable amount",
        "✅ Position sizes are appropriate for your account",
        "✅ Notifications are configured for monitoring",
        "✅ You understand this is REAL trading with REAL money",
        "✅ You have tested the system thoroughly"
    ]
    
    for item in checklist:
        print(f"   {item}")
    
    print(f"\n🚀 To start autonomous trading, run:")
    print(f"   python trader_daemon.py")
    print(f"\n📊 Monitor performance in the logs/ directory")
    print(f"🛑 Stop trading anytime with Ctrl+C")


def main():
    """Main setup function"""
    print_banner()
    
    # Check if config already exists
    if Path("config.json").exists():
        overwrite = get_user_input(
            "Configuration already exists. Overwrite? (y/n)", 
            default=False, 
            input_type=bool
        )
        
        if not overwrite:
            print("Setup cancelled. Existing configuration preserved.")
            return
    
    # Initialize security manager
    security_manager = SecurityManager()
    
    # Gather configuration
    print("🔧 Starting production configuration wizard...")
    
    config = {
        "trading": configure_production_trading(),
        "exchanges": configure_exchanges(),
        "notifications": configure_notifications(),
        "risk_management": configure_risk_management(),
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
    
    # Save configuration
    save_configuration(config, security_manager)
    
    # Show final checklist
    final_checklist()
    
    print("\n✅ Production setup complete!")
    print("💰 Your automated trading bot is ready for autonomous operation.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("You can run the setup again or manually create config.json")