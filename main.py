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
from typing import Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from core.trading_engine import TradingEngine
from notifications.notifier import Notifier
from utils.config_manager import ConfigManager
from utils.logger import setup_logger, log_performance, log_trade

# ASCII Art Banner
BANNER = r"""
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
    """Main auto profit trader class that orchestrates the entire trading system"""

    def __init__(self) -> None:
        """Initialize the Auto Profit Trader"""
        self.logger = setup_logger("main")
        self.config_manager = ConfigManager()
        self.notifier = Notifier(self.config_manager)
        self.trading_engine: Optional[TradingEngine] = None
        self.running = False

    async def startup(self) -> None:
        """
        Initialize the trading system
        
        Raises:
            Exception: If startup fails
        """
        print(BANNER)
        self.logger.info("🚀 Auto Profit Trader Starting Up...")

        try:
            # Load and validate configuration
            config = self.config_manager.get_config()
            if not config:
                raise ValueError("Configuration is empty or invalid")
            
            self.logger.info("✅ Configuration loaded successfully")

            # Initialize trading engine
            self.trading_engine = TradingEngine(self.config_manager, self.notifier)
            await self.trading_engine.initialize()
            self.logger.info("✅ Trading engine initialized")

            # Send startup notification
            await self.notifier.send_notification(
                "🚀 Auto Profit Trader Started!",
                "Your automated trading bot is now active and scanning for profitable opportunities.",
            )

            self.running = True
            self.logger.info("💰 System ready - Starting to make money!")

        except Exception as e:
            self.logger.error("❌ Startup failed: %s", e)
            await self.notifier.send_notification(
                "❌ Startup Failed", f"Auto Profit Trader failed to start: {e}"
            )
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the trading system"""
        self.logger.info("🛑 Shutting down Auto Profit Trader...")
        self.running = False

        if self.trading_engine:
            try:
                await self.trading_engine.shutdown()
            except Exception as e:
                self.logger.error("Error during trading engine shutdown: %s", e)

        try:
            await self.notifier.send_notification(
                "🛑 Auto Profit Trader Stopped",
                "Trading bot has been safely shut down. All positions closed.",
            )
        except Exception as e:
            self.logger.error("Error sending shutdown notification: %s", e)

        self.logger.info("✅ Shutdown complete")

    async def run(self) -> None:
        """Main trading loop"""
        try:
            await self.startup()

            # Start the trading engine
            if self.trading_engine:
                await self.trading_engine.start_trading()
            else:
                raise RuntimeError("Trading engine not initialized")

        except KeyboardInterrupt:
            self.logger.info("🛑 Received shutdown signal")
        except Exception as e:
            self.logger.error("❌ Trading error: %s", e)
            try:
                await self.notifier.send_notification(
                    "❌ Trading Error",
                    f"Auto Profit Trader encountered an error: {e}",
                )
            except Exception as notify_error:
                self.logger.error("Failed to send error notification: %s", notify_error)
        finally:
            await self.shutdown()

def signal_handler(signum: int, frame) -> None:
    """
    Handle shutdown signals
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    print("\n🛑 Received shutdown signal. Stopping trading...")
    sys.exit(0)


async def main() -> None:
    """Main entry point"""
    # Create and run the trader
    trader = AutoProfitTrader()

    try:
        await trader.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Auto Profit Trader stopped. Thank you for using our system!")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)