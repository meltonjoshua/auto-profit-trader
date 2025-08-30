#!/usr/bin/env python3
"""
Auto Profit Trader Production Startup Script
Designed for autonomous 24/7 operation
"""

import asyncio
import signal
import sys
import os
import time
import subprocess
import warnings
from datetime import datetime
from pathlib import Path

# Suppress protobuf warnings before any imports that might trigger them
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.runtime_version")
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from core.trading_engine import TradingEngine
from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from notifications.notifier import Notifier


class AutoTraderDaemon:
    """Production daemon for autonomous trading"""
    
    def __init__(self):
        self.logger = setup_logger("daemon")
        self.config_manager = ConfigManager()
        self.notifier = Notifier(self.config_manager)
        self.trading_engine = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.last_restart_time = None
        
    async def startup_checks(self):
        """Perform pre-flight checks before starting trading"""
        self.logger.info("🔍 Performing startup checks...")
        
        checks_passed = True
        
        # Check if at least one exchange is enabled
        enabled_exchanges = self.config_manager.get_enabled_exchanges()
        if not enabled_exchanges:
            self.logger.warning("⚠️ No exchanges enabled - will run in paper trading mode")
        else:
            self.logger.info(f"✅ Enabled exchanges: {', '.join(enabled_exchanges)}")
        
        # Check notification settings
        notifications = self.config_manager.get_section("notifications")
        has_notifications = any(
            config.get("enabled", False) 
            for config in notifications.values()
        )
        
        if has_notifications:
            self.logger.info("✅ Notifications configured")
        else:
            self.logger.warning("⚠️ No notifications enabled - consider enabling for monitoring")
        
        # Check risk management settings
        risk_config = self.config_manager.get_section("risk_management")
        if risk_config.get("stop_loss_percentage", 0) > 0:
            self.logger.info("✅ Risk management configured")
        else:
            self.logger.warning("⚠️ Risk management not properly configured")
            checks_passed = False
        
        # Check if running with sufficient permissions
        if os.name != 'nt':  # Unix/Linux
            try:
                # Test file creation in current directory
                test_file = Path("test_permissions.tmp")
                test_file.touch()
                test_file.unlink()
                self.logger.info("✅ File permissions OK")
            except Exception as e:
                self.logger.error(f"❌ File permission issues: {e}")
                checks_passed = False
        
        return checks_passed
    
    async def start_trading_engine(self):
        """Start the trading engine with error handling"""
        try:
            self.logger.info("🚀 Starting trading engine...")
            
            # Create trading engine
            self.trading_engine = TradingEngine(self.config_manager, self.notifier)
            
            # Initialize engine
            await self.trading_engine.initialize()
            self.logger.info("✅ Trading engine initialized")
            
            # Send startup notification
            await self.notifier.send_notification(
                "🚀 Auto Profit Trader Started",
                f"Trading bot is now running autonomously in production mode.\n"
                f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Restart count: {self.restart_count}"
            )
            
            # Start trading
            self.running = True
            await self.trading_engine.start_trading()
            
        except Exception as e:
            self.logger.error(f"❌ Trading engine error: {e}")
            await self.notifier.send_notification(
                "❌ Trading Engine Error",
                f"Error occurred: {e}\nAttempting restart..."
            )
            raise
    
    async def monitor_and_restart(self):
        """Monitor the trading engine and restart if needed"""
        while self.restart_count < self.max_restarts:
            try:
                await self.start_trading_engine()
                
            except Exception as e:
                self.restart_count += 1
                current_time = datetime.now()
                
                self.logger.error(f"Trading engine crashed (restart {self.restart_count}/{self.max_restarts}): {e}")
                
                # Prevent rapid restarts
                if self.last_restart_time and (current_time - self.last_restart_time).seconds < 60:
                    wait_time = 60
                    self.logger.info(f"⏳ Waiting {wait_time} seconds before restart...")
                    await asyncio.sleep(wait_time)
                
                self.last_restart_time = current_time
                
                if self.restart_count < self.max_restarts:
                    self.logger.info(f"🔄 Attempting restart {self.restart_count + 1}/{self.max_restarts}...")
                    await asyncio.sleep(5)  # Brief pause
                else:
                    self.logger.critical("💀 Max restarts reached - shutting down permanently")
                    await self.notifier.send_notification(
                        "💀 Auto Trader Shutdown",
                        f"Maximum restart attempts ({self.max_restarts}) reached. Manual intervention required."
                    )
                    break
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Shutting down Auto Profit Trader...")
        self.running = False
        
        if self.trading_engine:
            try:
                await self.trading_engine.shutdown()
            except Exception as e:
                self.logger.error(f"Error during trading engine shutdown: {e}")
        
        await self.notifier.send_notification(
            "🛑 Auto Profit Trader Stopped",
            f"Trading bot has been shut down.\nTotal restarts during session: {self.restart_count}"
        )
        
        self.logger.info("✅ Shutdown complete")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"🛑 Received signal {signum} - initiating shutdown...")
        self.running = False
        # Create a task to handle async shutdown
        asyncio.create_task(self.shutdown())


async def main():
    """Main entry point for production daemon"""
    daemon = AutoTraderDaemon()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, daemon.signal_handler)
    signal.signal(signal.SIGTERM, daemon.signal_handler)
    
    try:
        # Perform startup checks
        checks_passed = await daemon.startup_checks()
        
        if not checks_passed:
            daemon.logger.error("❌ Startup checks failed - see warnings above")
            user_input = input("Continue anyway? (y/N): ").strip().lower()
            if user_input != 'y':
                daemon.logger.info("Startup aborted by user")
                return
        
        daemon.logger.info("🎯 All systems ready - Starting autonomous trading...")
        
        # Start monitoring and auto-restart loop
        await daemon.monitor_and_restart()
        
    except KeyboardInterrupt:
        daemon.logger.info("🛑 Received keyboard interrupt")
        await daemon.shutdown()
    except Exception as e:
        daemon.logger.error(f"❌ Fatal error: {e}")
        await daemon.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher required")
            sys.exit(1)
        
        # Check if running as module vs script
        if __package__ is None:
            print("🚀 Starting Auto Profit Trader in Production Mode...")
            print("📊 For monitoring, check the logs/ directory")
            print("🛑 Press Ctrl+C to stop\n")
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Auto Profit Trader stopped by user")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)