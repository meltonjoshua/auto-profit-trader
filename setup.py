#!/usr/bin/env python3
"""
Setup script for Auto Profit Trader
Interactive configuration wizard for first-time setup
"""

import json
import os
from pathlib import Path


def print_banner():
    """Print the setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Auto Profit Trader - Setup Wizard                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Welcome to Auto Profit Trader Setup!

This wizard will help you configure your automated trading bot.
You can modify settings later in the config.json file.
"""
    print(banner)


def get_user_input(prompt, default=None, input_type=str):
    """Get user input with default value"""
    if default is not None:
        prompt += f" [{default}]"
    prompt += ": "
    
    while True:
        value = input(prompt).strip()
        
        if not value and default is not None:
            return default
        
        if not value:
            print("Please enter a value or press Enter for default.")
            continue
        
        try:
            if input_type == bool:
                return value.lower() in ['y', 'yes', 'true', '1']
            elif input_type == float:
                return float(value)
            elif input_type == int:
                return int(value)
            else:
                return value
        except ValueError:
            print(f"Please enter a valid {input_type.__name__}.")


def configure_trading_settings():
    """Configure trading parameters"""
    print("\n💰 TRADING CONFIGURATION")
    print("=" * 50)
    
    daily_loss_limit = get_user_input(
        "Daily loss limit (USD)", 
        default=100.0, 
        input_type=float
    )
    
    max_position_size = get_user_input(
        "Maximum position size (% of account, e.g., 0.02 for 2%)", 
        default=0.02, 
        input_type=float
    )
    
    enable_arbitrage = get_user_input(
        "Enable arbitrage trading? (y/n)", 
        default="y", 
        input_type=bool
    )
    
    enable_momentum = get_user_input(
        "Enable momentum trading? (y/n)", 
        default="y", 
        input_type=bool
    )
    
    return {
        "daily_loss_limit": daily_loss_limit,
        "max_position_size": max_position_size,
        "enable_arbitrage": enable_arbitrage,
        "enable_momentum": enable_momentum,
        "target_profit_arbitrage": 0.005,
        "target_profit_momentum": 0.02
    }


def configure_exchanges():
    """Configure exchange settings"""
    print("\n🔗 EXCHANGE CONFIGURATION")
    print("=" * 50)
    print("Note: Leave API keys empty for demo mode")
    
    exchanges = {}
    
    for exchange in ["binance", "coinbase", "kraken"]:
        print(f"\n--- {exchange.upper()} ---")
        
        enabled = get_user_input(
            f"Enable {exchange}? (y/n)", 
            default="n", 
            input_type=bool
        )
        
        if enabled:
            api_key = get_user_input(f"{exchange} API Key", default="")
            api_secret = get_user_input(f"{exchange} API Secret", default="")
            
            exchanges[exchange] = {
                "enabled": True,
                "api_key": api_key,
                "api_secret": api_secret,
                "testnet": True  # Always start with testnet
            }
        else:
            exchanges[exchange] = {
                "enabled": False,
                "api_key": "",
                "api_secret": "",
                "testnet": True
            }
    
    return exchanges


def configure_notifications():
    """Configure notification settings"""
    print("\n📱 NOTIFICATION CONFIGURATION")
    print("=" * 50)
    print("Configure notifications to stay informed about trades")
    
    notifications = {}
    
    # Telegram
    print("\n--- TELEGRAM ---")
    telegram_enabled = get_user_input(
        "Enable Telegram notifications? (y/n)", 
        default="n", 
        input_type=bool
    )
    
    if telegram_enabled:
        bot_token = get_user_input("Telegram Bot Token", default="")
        chat_id = get_user_input("Telegram Chat ID", default="")
        
        notifications["telegram"] = {
            "enabled": True,
            "bot_token": bot_token,
            "chat_id": chat_id
        }
    else:
        notifications["telegram"] = {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        }
    
    # Discord
    print("\n--- DISCORD ---")
    discord_enabled = get_user_input(
        "Enable Discord notifications? (y/n)", 
        default="n", 
        input_type=bool
    )
    
    if discord_enabled:
        webhook_url = get_user_input("Discord Webhook URL", default="")
        
        notifications["discord"] = {
            "enabled": True,
            "webhook_url": webhook_url
        }
    else:
        notifications["discord"] = {
            "enabled": False,
            "webhook_url": ""
        }
    
    # Email
    print("\n--- EMAIL ---")
    email_enabled = get_user_input(
        "Enable Email notifications? (y/n)", 
        default="n", 
        input_type=bool
    )
    
    if email_enabled:
        smtp_server = get_user_input("SMTP Server", default="smtp.gmail.com")
        smtp_port = get_user_input("SMTP Port", default=587, input_type=int)
        username = get_user_input("Email Username", default="")
        password = get_user_input("Email Password", default="")
        to_email = get_user_input("Recipient Email", default="")
        
        notifications["email"] = {
            "enabled": True,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "to_email": to_email
        }
    else:
        notifications["email"] = {
            "enabled": False,
            "smtp_server": "",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "to_email": ""
        }
    
    return notifications


def configure_risk_management():
    """Configure risk management settings"""
    print("\n🛡️ RISK MANAGEMENT CONFIGURATION")
    print("=" * 50)
    
    stop_loss = get_user_input(
        "Stop loss percentage (e.g., 0.02 for 2%)", 
        default=0.02, 
        input_type=float
    )
    
    take_profit = get_user_input(
        "Take profit percentage (e.g., 0.05 for 5%)", 
        default=0.05, 
        input_type=float
    )
    
    max_trades_per_day = get_user_input(
        "Maximum trades per day", 
        default=50, 
        input_type=int
    )
    
    return {
        "stop_loss_percentage": stop_loss,
        "take_profit_percentage": take_profit,
        "max_trades_per_day": max_trades_per_day,
        "cooldown_after_loss": 300
    }


def save_configuration(config):
    """Save configuration to file"""
    config_path = Path("config.json")
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set secure permissions
    config_path.chmod(0o600)
    
    print(f"\n✅ Configuration saved to {config_path}")


def main():
    """Main setup function"""
    print_banner()
    
    print("This setup will create a config.json file with your preferences.")
    print("You can always modify these settings later.\n")
    
    # Check if config already exists
    if Path("config.json").exists():
        overwrite = get_user_input(
            "config.json already exists. Overwrite? (y/n)", 
            default="n", 
            input_type=bool
        )
        
        if not overwrite:
            print("Setup cancelled. Existing configuration preserved.")
            return
    
    # Gather configuration
    config = {
        "trading": configure_trading_settings(),
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
    save_configuration(config)
    
    print("\n🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Review your configuration in config.json")
    print("2. If using real exchanges, ensure API keys are configured correctly")
    print("3. Start with testnet/sandbox mode first")
    print("4. Run: python main.py")
    print("\n💰 Happy trading! 🚀")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("You can run the setup again or manually create config.json")