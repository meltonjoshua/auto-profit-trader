"""
Core Trading Engine for Auto Profit Trader
Orchestrates all trading strategies and components
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict

from exchanges.exchange_manager import ExchangeManager
from risk_management.portfolio_manager import PortfolioManager, RiskManager
from security.crypto_manager import SecurityManager
from strategies.trading_strategies import ArbitrageStrategy, MomentumStrategy

# Import our components
from utils.logger import log_trade, setup_logger


class TradingEngine:
    """Main trading engine that coordinates all strategies and components"""

    def __init__(self, config_manager, notifier):
        self.config_manager = config_manager
        self.notifier = notifier
        self.logger = setup_logger("trading_engine")

        # Core components
        self.security_manager = SecurityManager()
        self.exchange_manager = ExchangeManager(config_manager, self.security_manager)
        self.portfolio_manager = PortfolioManager(config_manager)
        self.risk_manager = RiskManager(config_manager, self.portfolio_manager)

        # Trading strategies
        self.arbitrage_strategy = None
        self.momentum_strategy = None

        # Configuration
        trading_config = config_manager.get_section("trading")
        self.enable_arbitrage = trading_config.get("enable_arbitrage", True)
        self.enable_momentum = trading_config.get("enable_momentum", True)
        self.daily_loss_limit = trading_config.get("daily_loss_limit", 100.0)

        # State tracking
        self.is_running = False
        self.start_time = None
        self.cycle_count = 0
        self.last_arbitrage_scan = None
        self.last_momentum_scan = None

        # Performance tracking from portfolio manager
        self.last_performance_report = None

    async def initialize(self):
        """Initialize the trading engine"""
        self.logger.info("🔧 Initializing Trading Engine...")

        try:
            # Initialize exchange connections
            await self.exchange_manager.initialize_exchanges()

            # Initialize strategies
            await self._initialize_strategies()

            # Initialize risk management
            await self._initialize_risk_management()

            # Initialize technical analysis
            await self._initialize_technical_analysis()

            self.logger.info("✅ Trading Engine initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Trading Engine initialization failed: {e}")
            raise

    async def _initialize_strategies(self):
        """Initialize trading strategies"""
        self.logger.info("📊 Initializing trading strategies...")

        if self.enable_arbitrage:
            self.arbitrage_strategy = ArbitrageStrategy(
                self.exchange_manager, self.config_manager
            )
            self.logger.info("✅ Arbitrage strategy enabled")

        if self.enable_momentum:
            self.momentum_strategy = MomentumStrategy(
                self.exchange_manager, self.config_manager
            )
            self.logger.info("✅ Momentum strategy enabled")

        if not (self.enable_arbitrage or self.enable_momentum):
            self.logger.warning("⚠️ No trading strategies enabled")

    async def _initialize_risk_management(self):
        """Initialize risk management system"""
        self.logger.info("🛡️ Initializing risk management...")

        risk_config = self.config_manager.get_section("risk_management")

        self.logger.info(
            f"📉 Stop loss: {risk_config.get('stop_loss_percentage', 0.02) * 100}%"
        )
        self.logger.info(
            f"📈 Take profit: {risk_config.get('take_profit_percentage', 0.05) * 100}%"
        )
        self.logger.info(
            f"🔢 Max trades/day: {risk_config.get('max_trades_per_day', 50)}"
        )
        self.logger.info(f"💰 Daily loss limit: ${self.daily_loss_limit}")

    async def _initialize_technical_analysis(self):
        """Initialize technical analysis tools"""
        self.logger.info("📈 Initializing technical analysis...")

        ta_config = self.config_manager.get_section("technical_analysis")

        self.logger.info(f"📊 RSI period: {ta_config.get('rsi_period', 14)}")
        macd_config = f"{ta_config.get('macd_fast', 12)}/{ta_config.get('macd_slow', 26)}/{ta_config.get('macd_signal', 9)}"
        self.logger.info(f"📈 MACD config: {macd_config}")
        self.logger.info(
            f"📊 Bollinger Bands: {ta_config.get('bollinger_period', 20)} period"
        )

    async def start_trading(self):
        """Start the main trading loop"""
        self.logger.info("🚀 Starting trading operations...")
        self.is_running = True
        self.start_time = datetime.now()

        try:
            # Send startup notification
            await self.notifier.send_system_alert(
                "startup",
                "Trading engine is now active and scanning for opportunities",
                "success",
            )

            # Main trading loop
            while self.is_running:
                await self._trading_cycle()
                await asyncio.sleep(5)  # 5 second cycle

        except Exception as e:
            self.logger.error(f"❌ Trading loop error: {e}")
            await self.notifier.send_system_alert(
                "error", f"Trading loop encountered an error: {e}", "error"
            )
            raise

    async def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            self.cycle_count += 1

            # Check for emergency shutdown
            if await self.risk_manager.emergency_shutdown_check():
                await self._emergency_shutdown()
                return

            # Check trading limits
            limits = await self.portfolio_manager.check_trading_limits()
            if not limits["can_trade"]:
                if self.cycle_count % 120 == 0:  # Log every 10 minutes
                    self.logger.info(
                        f"🛑 Trading paused: {', '.join(limits['reasons'])}"
                    )
                return

            # Execute arbitrage strategy
            if self.enable_arbitrage and self.arbitrage_strategy:
                await self._execute_arbitrage_cycle()

            # Execute momentum strategy
            if self.enable_momentum and self.momentum_strategy:
                await self._execute_momentum_cycle()

            # Check existing positions
            if self.momentum_strategy:
                position_actions = await self.momentum_strategy.check_positions()
                for action in position_actions:
                    await self._execute_trade_action(
                        action, "momentum_position_management"
                    )

            # Performance monitoring
            if self.cycle_count % 720 == 0:  # Every hour (720 * 5 seconds)
                await self._check_profit_milestones()
                await self._send_performance_update()

        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")

    async def _execute_arbitrage_cycle(self):
        """Execute arbitrage trading logic"""
        try:
            # Rate limit arbitrage scanning (every 30 seconds)
            now = datetime.now()
            if (
                self.last_arbitrage_scan
                and (now - self.last_arbitrage_scan).total_seconds() < 30
            ):
                return

            self.last_arbitrage_scan = now

            # Scan for arbitrage opportunities
            opportunities = await self.arbitrage_strategy.scan_opportunities()

            for opportunity in opportunities:
                # Evaluate risk
                risk_assessment = await self.risk_manager.evaluate_trade_risk(
                    {"confidence": 0.9, "strategy": "arbitrage"},
                    10000,  # Mock account balance
                )

                if risk_assessment["approved"]:
                    # Execute arbitrage trade
                    trade_result = await self.arbitrage_strategy.execute_opportunity(
                        opportunity
                    )
                    if trade_result:
                        await self._process_trade_result(trade_result)
                else:
                    warnings_msg = ", ".join(risk_assessment["warnings"])
                    self.logger.warning(f"Arbitrage trade rejected: {warnings_msg}")

        except Exception as e:
            self.logger.error(f"Error in arbitrage cycle: {e}")

    async def _execute_momentum_cycle(self):
        """Execute momentum trading logic"""
        try:
            # Rate limit momentum scanning (every 60 seconds)
            now = datetime.now()
            if (
                self.last_momentum_scan
                and (now - self.last_momentum_scan).total_seconds() < 60
            ):
                return

            self.last_momentum_scan = now

            # Scan for momentum signals
            signals = await self.momentum_strategy.scan_signals()

            for signal in signals:
                await self._execute_trade_action(signal, "momentum_signal")

        except Exception as e:
            self.logger.error(f"Error in momentum cycle: {e}")

    async def _execute_trade_action(self, signal: Dict, source: str):
        """Execute a trade action with risk management"""
        try:
            # Evaluate risk
            risk_assessment = await self.risk_manager.evaluate_trade_risk(signal, 10000)

            if not risk_assessment["approved"]:
                warnings_msg = ", ".join(risk_assessment["warnings"])
                self.logger.warning(f"Trade rejected ({source}): {warnings_msg}")
                return

            # Execute the trade
            trade_result = await self.momentum_strategy.execute_signal(signal)
            if trade_result:
                await self._process_trade_result(trade_result)

        except Exception as e:
            self.logger.error(f"Error executing trade action: {e}")

    async def _process_trade_result(self, trade_result: Dict):
        """Process a completed trade result"""
        try:
            # Record trade in portfolio
            await self.portfolio_manager.record_trade(trade_result)

            # Log the trade
            log_trade(
                trade_result.get("symbol", ""),
                trade_result.get("action", ""),
                trade_result.get("amount", 0),
                trade_result.get("price", 0)
                or trade_result.get("entry_price", 0)
                or trade_result.get("exit_price", 0),
                trade_result.get("profit", 0),
            )

            # Send trade notification
            symbol = trade_result.get("symbol", "")
            action = trade_result.get("action", "")
            amount = trade_result.get("amount", 0)
            price = (
                trade_result.get("price", 0)
                or trade_result.get("entry_price", 0)
                or trade_result.get("exit_price", 0)
            )
            profit = trade_result.get("profit", 0)

            await self.notifier.send_trade_alert(symbol, action, amount, price, profit)

            # Record losses for risk management
            if profit < 0:
                await self.risk_manager.record_loss(abs(profit))

            action = trade_result.get("action", "UNKNOWN")
            symbol = trade_result.get("symbol", "N/A")
            strategy = trade_result.get("strategy", "unknown")
            self.logger.info(f"✅ Trade processed: {strategy} {action} {symbol}")

        except Exception as e:
            self.logger.error(f"Error processing trade result: {e}")

    async def _check_profit_milestones(self):
        """Check for profit milestones and send notifications"""
        try:
            metrics = await self.portfolio_manager.get_performance_metrics()
            total_profit = metrics.get("total_profit", 0)
            daily_profit = metrics.get("daily_profit", 0)

            milestones = [50, 100, 250, 500, 1000, 2500, 5000]

            for milestone in milestones:
                attr_name = f"milestone_{milestone}_reached"
                if total_profit >= milestone and not hasattr(self, attr_name):
                    await self.notifier.send_profit_milestone(
                        daily_profit, total_profit
                    )
                    setattr(self, attr_name, True)
                    break

        except Exception as e:
            self.logger.error(f"Error checking profit milestones: {e}")

    async def _send_performance_update(self):
        """Send periodic performance update"""
        try:
            report = await self.portfolio_manager.generate_performance_report()

            # Send detailed report every 6 hours, summary every hour
            now = datetime.now()
            if (
                not self.last_performance_report
                or (now - self.last_performance_report).total_seconds() >= 21600
            ):  # 6 hours
                await self.notifier.send_system_alert("performance", report, "info")
                self.last_performance_report = now
            else:
                # Send brief summary
                metrics = await self.portfolio_manager.get_performance_metrics()
                daily_profit = metrics["daily_profit"]
                daily_trades = metrics["daily_trades"]
                win_rate = metrics["win_rate"]
                summary = (
                    f"Hourly Update - Profit: ${daily_profit:.2f} | "
                    f"Trades: {daily_trades} | Win Rate: {win_rate:.1f}%"
                )
                await self.notifier.send_system_alert("update", summary, "info")

        except Exception as e:
            self.logger.error(f"Error sending performance update: {e}")

    async def _emergency_shutdown(self):
        """Execute emergency shutdown"""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")
        self.is_running = False

        await self.notifier.send_system_alert(
            "emergency",
            "🚨 EMERGENCY SHUTDOWN: Trading has been halted due to risk conditions",
            "error",
        )

    async def shutdown(self):
        """Gracefully shutdown the trading engine"""
        self.logger.info("🛑 Shutting down Trading Engine...")
        self.is_running = False

        try:
            # Send final performance report
            metrics = await self.portfolio_manager.get_performance_metrics()

            if metrics["total_trades"] > 0:
                uptime = (
                    datetime.now() - self.start_time
                    if self.start_time
                    else timedelta(0)
                )

                final_report = f"""
Trading Session Summary:
• Duration: {uptime}
• Total Trades: {metrics['total_trades']}
• Win Rate: {metrics['win_rate']:.1f}%
• Daily P&L: ${metrics['daily_profit']:.2f}
• Total P&L: ${metrics['total_profit']:.2f}
• Trades per Hour: {metrics['trades_per_hour']:.1f}
                """.strip()

                await self.notifier.send_system_alert("shutdown", final_report, "info")

            # Shutdown exchange connections
            await self.exchange_manager.shutdown()

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

        self.logger.info("✅ Trading Engine shutdown complete")
