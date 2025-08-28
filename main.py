#!/usr/bin/env python3
"""
Auto Profit Trader - Automated Cryptocurrency Trading Bot
Main entry point for the trading system
"""

import asyncio
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from core.trading_engine import TradingEngine
from utils.logger import setup_logger, log_trade, log_performance
from utils.config_manager import ConfigManager
from notifications.notifier import Notifier

# ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     $$$$$$\              $$\                                 ║
║    $$  __$$\             $$ |                                ║
║    $$ /  $$ |$$\   $$\ $$$$$$\    $$$$$$\                   ║
║    $$$$$$$$ |$$ |  $$ |\_$$  _|  $$  __$$\                  ║
║    $$  __$$ |$$ |  $$ |  $$ |    $$ /  $$ |                 ║
║    $$ |  $$ |$$ |  $$ |  $$ |$$\ $$ |  $$ |                 ║
║    $$ |  $$ |\$$$$$$  |  \$$$$  |\$$$$$$  |                 ║
║    \__|  \__| \______/    \____/  \______/                  ║
║                                                              ║
║    $$$$$$\                       $$$$$$\  $$\   $$\         ║
║    $$  __$$\                     $$  __$$\ \__|  $$ |        ║
║    $$ |  $$ |$$$$$$\   $$$$$$\   $$ /  \__|$$\ $$$$$$\      ║
║    $$$$$$$  |$$  __$$\ $$  __$$\  $$$$\    $$ |\_$$  _|     ║
║    $$  ____/ $$ |  \__|$$ /  $$ | $$  _|   $$ |  $$ |       ║
║    $$ |      $$ |      $$ |  $$ | $$ |     $$ |  $$ |$$\    ║
║    $$ |      $$ |      \$$$$$$  | $$ |     $$ |  \$$$$  |   ║
║    \__|      \__|       \______/  \__|     \__|   \____/    ║
║                                                              ║
║           Automated Cryptocurrency Trading Bot              ║
║                    v1.0.0 - Ready to Trade                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

💰 PROFIT STRATEGIES LOADED:
   ✅ Arbitrage Trading (0.1-2% per trade)
   ✅ Momentum Trading (Technical Analysis)
   ✅ Risk Management (Stop-loss & Position Limits)
   ✅ Multi-Exchange Support (Binance, Coinbase, Kraken)

🛡️  SAFETY FEATURES ACTIVE:
   ✅ API Key Encryption
   ✅ Daily Loss Limits
   ✅ Emergency Shutdown
   ✅ Real-time Monitoring

📱 NOTIFICATIONS ENABLED:
   ✅ Telegram Alerts
   ✅ Discord Updates
   ✅ Email Reports

🚀 STARTING YOUR MONEY-MAKING MACHINE...
"""

class AutoProfitTrader:
    def __init__(self):
        self.logger = setup_logger("main")
        self.config_manager = ConfigManager()
        self.notifier = Notifier(self.config_manager)
        self.trading_engine = None
        self.running = False
        
    async def startup(self):
        """Initialize the trading system"""
        print(BANNER)
        self.logger.info("🚀 Auto Profit Trader Starting Up...")
        
        try:
            # Load configuration
            config = self.config_manager.get_config()
            self.logger.info("✅ Configuration loaded successfully")
            
            # Initialize trading engine
            self.trading_engine = TradingEngine(self.config_manager, self.notifier)
            await self.trading_engine.initialize()
            self.logger.info("✅ Trading engine initialized")
            
            # Send startup notification
            await self.notifier.send_notification(
                "🚀 Auto Profit Trader Started!",
                "Your automated trading bot is now active and scanning for profitable opportunities."
            )
            
            self.running = True
            self.logger.info("💰 System ready - Starting to make money!")
            
        except Exception as e:
            self.logger.error(f"❌ Startup failed: {e}")
            await self.notifier.send_notification(
                "❌ Startup Failed",
                f"Auto Profit Trader failed to start: {e}"
            )
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the trading system"""
        self.logger.info("🛑 Shutting down Auto Profit Trader...")
        self.running = False
        
        if self.trading_engine:
            await self.trading_engine.shutdown()
            
        await self.notifier.send_notification(
            "🛑 Auto Profit Trader Stopped",
            "Trading bot has been safely shut down. All positions closed."
        )
        
        self.logger.info("✅ Shutdown complete")
    
    async def run(self):
        """Main trading loop"""
        await self.startup()
        
        try:
            # Start the trading engine
            await self.trading_engine.start_trading()
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Received shutdown signal")
        except Exception as e:
            self.logger.error(f"❌ Trading error: {e}")
            await self.notifier.send_notification(
                "❌ Trading Error",
                f"Auto Profit Trader encountered an error: {e}"
            )
        finally:
            await self.shutdown()

def signal_handler(signum, frame):
    """Handle shutdown signals""" 
    print("\n🛑 Received shutdown signal. Stopping trading...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the trader
    trader = AutoProfitTrader()
    
    try:
        asyncio.run(trader.run())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Auto Profit Trader stopped. Thank you for using our system!")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)