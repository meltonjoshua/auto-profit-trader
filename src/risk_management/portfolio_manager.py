"""
Portfolio Manager for Auto Profit Trader
Tracks performance, manages positions, and maintains trading statistics
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import setup_logger


class PortfolioManager:
    """Manages portfolio tracking and performance metrics"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = setup_logger("portfolio_manager")
        self.db_path = Path("portfolio.db")
        self.performance_file = Path("performance.json")

        # Trading statistics
        self.daily_trades = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.daily_profit = 0.0
        self.total_profit = 0.0
        self.total_volume = 0.0
        self.largest_win = 0.0
        self.largest_loss = 0.0
        self.start_time = datetime.now()
        self.daily_loss_limit = config_manager.get_section("trading").get(
            "daily_loss_limit", 100.0
        )
        self.max_trades_per_day = config_manager.get_section("risk_management").get(
            "max_trades_per_day", 50
        )

        # Initialize database
        asyncio.create_task(self._initialize_database())

    async def _initialize_database(self):
        """Initialize SQLite database for trade storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create trades table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    action TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL NOT NULL,
                    cost REAL NOT NULL,
                    profit REAL DEFAULT 0,
                    profit_percentage REAL DEFAULT 0,
                    order_id TEXT,
                    signal_confidence REAL DEFAULT 0,
                    notes TEXT
                )
            """
            )

            # Create daily_stats table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    daily_profit REAL DEFAULT 0,
                    daily_volume REAL DEFAULT 0,
                    largest_win REAL DEFAULT 0,
                    largest_loss REAL DEFAULT 0
                )
            """
            )

            conn.commit()
            conn.close()

            self.logger.info("📊 Portfolio database initialized")

        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")

    async def record_trade(self, trade_data: Dict) -> bool:
        """Record a completed trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert trade record
            cursor.execute(
                """
                INSERT INTO trades (timestamp, strategy, symbol, exchange, action, amount, 
                                  price, cost, profit, profit_percentage, order_id, signal_confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    trade_data.get("timestamp", datetime.now()).isoformat(),
                    trade_data.get("strategy", "unknown"),
                    trade_data.get("symbol", ""),
                    trade_data.get("exchange", ""),
                    trade_data.get("action", ""),
                    trade_data.get("amount", 0),
                    trade_data.get("price", 0)
                    or trade_data.get("entry_price", 0)
                    or trade_data.get("exit_price", 0),
                    trade_data.get("cost", 0)
                    or trade_data.get("entry_cost", 0)
                    or trade_data.get("exit_revenue", 0),
                    trade_data.get("profit", 0),
                    trade_data.get("profit_percentage", 0),
                    trade_data.get("order_id", ""),
                    trade_data.get("signal_confidence", 0),
                    trade_data.get("reason", ""),
                ),
            )

            conn.commit()
            conn.close()

            # Update statistics
            await self._update_statistics(trade_data)

            self.logger.info(
                f"📝 Trade recorded: {trade_data.get('symbol')} {trade_data.get('action')}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error recording trade: {e}")
            return False

    async def _update_statistics(self, trade_data: Dict):
        """Update trading statistics"""
        try:
            profit = trade_data.get("profit", 0)
            volume = (
                trade_data.get("cost", 0)
                or trade_data.get("entry_cost", 0)
                or trade_data.get("exit_revenue", 0)
            )

            # Update counters
            self.total_trades += 1
            self.daily_trades += 1
            self.total_volume += abs(volume)

            # Update profit tracking
            if profit != 0:  # Only count completed trades (not just buys)
                self.daily_profit += profit
                self.total_profit += profit

                if profit > 0:
                    self.winning_trades += 1
                    if profit > self.largest_win:
                        self.largest_win = profit
                else:
                    self.losing_trades += 1
                    if profit < self.largest_loss:
                        self.largest_loss = profit

            # Save daily statistics to database
            await self._save_daily_stats()

            # Save performance to file
            await self._save_performance()

        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")

    async def _save_daily_stats(self):
        """Save daily statistics to database"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO daily_stats 
                (date, total_trades, winning_trades, losing_trades, daily_profit, 
                 daily_volume, largest_win, largest_loss)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    today,
                    self.daily_trades,
                    self.winning_trades,
                    self.losing_trades,
                    self.daily_profit,
                    self.total_volume,
                    self.largest_win,
                    self.largest_loss,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error saving daily stats: {e}")

    async def _save_performance(self):
        """Save performance metrics to file"""
        try:
            performance_data = {
                "last_updated": datetime.now().isoformat(),
                "start_time": self.start_time.isoformat(),
                "total_trades": self.total_trades,
                "daily_trades": self.daily_trades,
                "winning_trades": self.winning_trades,
                "losing_trades": self.losing_trades,
                "win_rate": (
                    self.winning_trades
                    / max(self.winning_trades + self.losing_trades, 1)
                )
                * 100,
                "daily_profit": self.daily_profit,
                "total_profit": self.total_profit,
                "total_volume": self.total_volume,
                "largest_win": self.largest_win,
                "largest_loss": self.largest_loss,
                "avg_profit_per_trade": self.total_profit / max(self.total_trades, 1),
                "daily_loss_limit": self.daily_loss_limit,
                "max_trades_per_day": self.max_trades_per_day,
            }

            with open(self.performance_file, "w") as f:
                json.dump(performance_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving performance: {e}")

    async def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        completed_trades = self.winning_trades + self.losing_trades
        win_rate = (self.winning_trades / max(completed_trades, 1)) * 100

        uptime = datetime.now() - self.start_time
        uptime_hours = uptime.total_seconds() / 3600

        return {
            "uptime_hours": uptime_hours,
            "total_trades": self.total_trades,
            "daily_trades": self.daily_trades,
            "completed_trades": completed_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": win_rate,
            "daily_profit": self.daily_profit,
            "total_profit": self.total_profit,
            "total_volume": self.total_volume,
            "largest_win": self.largest_win,
            "largest_loss": self.largest_loss,
            "avg_profit_per_trade": self.total_profit / max(completed_trades, 1),
            "trades_per_hour": self.total_trades / max(uptime_hours, 1),
            "profit_per_hour": self.total_profit / max(uptime_hours, 1),
            "remaining_daily_trades": max(
                0, self.max_trades_per_day - self.daily_trades
            ),
            "remaining_daily_loss_allowance": max(
                0, self.daily_loss_limit + self.daily_profit
            ),
        }

    async def check_trading_limits(self) -> Dict:
        """Check if trading limits have been reached"""
        metrics = await self.get_performance_metrics()

        limits = {"can_trade": True, "reasons": []}

        # Check daily trade limit
        if self.daily_trades >= self.max_trades_per_day:
            limits["can_trade"] = False
            limits["reasons"].append(
                f"Daily trade limit reached ({self.daily_trades}/{self.max_trades_per_day})"
            )

        # Check daily loss limit
        if self.daily_profit <= -self.daily_loss_limit:
            limits["can_trade"] = False
            limits["reasons"].append(
                f"Daily loss limit reached (${self.daily_profit:.2f}/${-self.daily_loss_limit:.2f})"
            )

        return limits

    async def get_trade_history(self, days: int = 7, limit: int = None) -> List[Dict]:
        """Get recent trade history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            query = """
                SELECT * FROM trades 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (start_date,))

            trades = []
            for row in cursor.fetchall():
                trades.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "strategy": row[2],
                        "symbol": row[3],
                        "exchange": row[4],
                        "action": row[5],
                        "amount": row[6],
                        "price": row[7],
                        "cost": row[8],
                        "profit": row[9],
                        "profit_percentage": row[10],
                        "order_id": row[11],
                        "signal_confidence": row[12],
                        "notes": row[13],
                    }
                )

            conn.close()
            return trades

        except Exception as e:
            self.logger.error(f"Error getting trade history: {e}")
            return []

    async def get_daily_summary(self, date: str = None) -> Dict:
        """Get daily trading summary"""
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (date,))
            row = cursor.fetchone()

            if row:
                return {
                    "date": row[0],
                    "total_trades": row[1],
                    "winning_trades": row[2],
                    "losing_trades": row[3],
                    "daily_profit": row[4],
                    "daily_volume": row[5],
                    "largest_win": row[6],
                    "largest_loss": row[7],
                    "win_rate": (row[2] / max(row[2] + row[3], 1)) * 100,
                }

            conn.close()

        except Exception as e:
            self.logger.error(f"Error getting daily summary: {e}")

        return {}

    async def reset_daily_stats(self):
        """Reset daily statistics (called at start of new day)"""
        self.daily_trades = 0
        self.daily_profit = 0.0
        self.logger.info("📅 Daily statistics reset for new trading day")

    async def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        try:
            metrics = await self.get_performance_metrics()
            recent_trades = await self.get_trade_history(7)

            report = f"""
📊 AUTO PROFIT TRADER PERFORMANCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🕐 UPTIME & ACTIVITY:
   • System Uptime: {metrics['uptime_hours']:.1f} hours
   • Total Trades: {metrics['total_trades']}
   • Trades Today: {metrics['daily_trades']}
   • Trades per Hour: {metrics['trades_per_hour']:.2f}

💰 PROFITABILITY:
   • Total Profit: ${metrics['total_profit']:.2f}
   • Daily Profit: ${metrics['daily_profit']:.2f}
   • Profit per Hour: ${metrics['profit_per_hour']:.2f}
   • Average per Trade: ${metrics['avg_profit_per_trade']:.2f}
   
📈 WIN/LOSS STATISTICS:
   • Win Rate: {metrics['win_rate']:.1f}%
   • Winning Trades: {metrics['winning_trades']}
   • Losing Trades: {metrics['losing_trades']}
   • Largest Win: ${metrics['largest_win']:.2f}
   • Largest Loss: ${metrics['largest_loss']:.2f}

💱 TRADING VOLUME:
   • Total Volume: ${metrics['total_volume']:.2f}
   • Remaining Daily Trades: {metrics['remaining_daily_trades']}
   • Daily Loss Allowance: ${metrics['remaining_daily_loss_allowance']:.2f}

📋 RECENT ACTIVITY ({len(recent_trades)} trades in last 7 days):
"""

            # Add recent trades summary
            for trade in recent_trades[:10]:  # Show last 10 trades
                timestamp = datetime.fromisoformat(trade["timestamp"]).strftime(
                    "%m-%d %H:%M"
                )
                profit_str = (
                    f"${trade['profit']:.2f}" if trade["profit"] != 0 else "N/A"
                )
                report += f"   • {timestamp} | {trade['symbol']} {trade['action'].upper()} | {profit_str}\n"

            return report.strip()

        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return f"Error generating report: {e}"


class RiskManager:
    """Advanced risk management system"""

    def __init__(self, config_manager, portfolio_manager):
        self.config_manager = config_manager
        self.portfolio_manager = portfolio_manager
        self.logger = setup_logger("risk_manager")
        self.risk_config = config_manager.get_section("risk_management")

        # Risk parameters
        self.stop_loss_percentage = self.risk_config.get("stop_loss_percentage", 0.02)
        self.take_profit_percentage = self.risk_config.get(
            "take_profit_percentage", 0.05
        )
        self.max_trades_per_day = self.risk_config.get("max_trades_per_day", 50)
        self.cooldown_after_loss = self.risk_config.get(
            "cooldown_after_loss", 300
        )  # seconds

        # Track recent losses for cooldown
        self.recent_losses = []
        self.last_loss_time = None

    async def evaluate_trade_risk(
        self, trade_signal: Dict, account_balance: float
    ) -> Dict:
        """Evaluate risk for a potential trade"""
        risk_assessment = {
            "approved": True,
            "risk_score": 0.0,
            "warnings": [],
            "position_size_adjustment": 1.0,
        }

        try:
            # Check trading limits
            limits = await self.portfolio_manager.check_trading_limits()
            if not limits["can_trade"]:
                risk_assessment["approved"] = False
                risk_assessment["warnings"].extend(limits["reasons"])
                return risk_assessment

            # Check cooldown after recent loss
            if self.last_loss_time and datetime.now() - self.last_loss_time < timedelta(
                seconds=self.cooldown_after_loss
            ):
                risk_assessment["approved"] = False
                risk_assessment["warnings"].append(
                    "Cooldown period active after recent loss"
                )
                return risk_assessment

            # Calculate risk score based on various factors
            risk_score = 0.0

            # Signal confidence factor
            confidence = trade_signal.get("confidence", 0.5)
            if confidence < 0.6:
                risk_score += 0.3
                risk_assessment["warnings"].append("Low signal confidence")

            # Recent performance factor
            metrics = await self.portfolio_manager.get_performance_metrics()
            if metrics["win_rate"] < 40 and metrics["completed_trades"] > 10:
                risk_score += 0.4
                risk_assessment["warnings"].append("Recent poor performance")
                risk_assessment["position_size_adjustment"] = (
                    0.5  # Reduce position size
                )

            # Daily loss factor
            if metrics["daily_profit"] < -50:  # If daily loss is significant
                risk_score += 0.3
                risk_assessment["warnings"].append("Significant daily losses")
                risk_assessment["position_size_adjustment"] *= 0.7

            # Account balance factor
            if account_balance < 1000:  # Small account
                risk_score += 0.2
                risk_assessment["warnings"].append("Small account balance")
                risk_assessment["position_size_adjustment"] *= 0.8

            risk_assessment["risk_score"] = min(risk_score, 1.0)

            # Deny trade if risk is too high
            if risk_score > 0.8:
                risk_assessment["approved"] = False
                risk_assessment["warnings"].append("Risk score too high")

        except Exception as e:
            self.logger.error(f"Error evaluating trade risk: {e}")
            risk_assessment["approved"] = False
            risk_assessment["warnings"].append(f"Risk evaluation error: {e}")

        return risk_assessment

    async def record_loss(self, loss_amount: float):
        """Record a trading loss for risk tracking"""
        self.recent_losses.append({"amount": loss_amount, "timestamp": datetime.now()})
        self.last_loss_time = datetime.now()

        # Keep only losses from last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        self.recent_losses = [
            loss for loss in self.recent_losses if loss["timestamp"] > cutoff
        ]

        self.logger.warning(
            f"💸 Loss recorded: ${loss_amount:.2f} - Activating {self.cooldown_after_loss}s cooldown"
        )

    async def emergency_shutdown_check(self) -> bool:
        """Check if emergency shutdown is needed"""
        try:
            metrics = await self.portfolio_manager.get_performance_metrics()

            # Emergency conditions
            emergency_conditions = []

            # Massive daily loss
            if metrics["daily_profit"] <= -500:
                emergency_conditions.append("Excessive daily losses")

            # Too many consecutive losses
            if len(self.recent_losses) >= 5:
                emergency_conditions.append("Too many recent losses")

            # System errors or connection issues could be added here

            if emergency_conditions:
                self.logger.critical(
                    f"🚨 EMERGENCY SHUTDOWN TRIGGERED: {', '.join(emergency_conditions)}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Error in emergency shutdown check: {e}")

        return False
