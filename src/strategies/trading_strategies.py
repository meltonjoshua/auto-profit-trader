"""
Trading Strategies for Auto Profit Trader
Implements arbitrage and momentum trading strategies
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np

try:
    import talib

    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

from utils.logger import setup_logger


class ArbitrageStrategy:
    """Arbitrage trading strategy implementation"""

    def __init__(self, exchange_manager, config_manager):
        self.exchange_manager = exchange_manager
        self.config_manager = config_manager
        self.logger = setup_logger("arbitrage_strategy")
        self.min_profit_percentage = (
            config_manager.get_section("trading").get("target_profit_arbitrage", 0.005)
            * 100
        )
        self.max_position_size = config_manager.get_section("trading").get(
            "max_position_size", 0.02
        )

    async def scan_opportunities(self) -> List[Dict]:
        """Scan for arbitrage opportunities"""
        try:
            # Get tradeable symbols from all exchanges
            all_symbols = set()
            exchange_names = list(self.exchange_manager.exchanges.keys())

            for exchange_name in exchange_names:
                symbols = await self.exchange_manager.get_trading_symbols(exchange_name)
                all_symbols.update(symbols)

            # Filter to common symbols across exchanges (if multiple exchanges)
            if len(exchange_names) > 1:
                common_symbols = []
                for symbol in all_symbols:
                    count = 0
                    for exchange_name in exchange_names:
                        exchange_symbols = (
                            await self.exchange_manager.get_trading_symbols(
                                exchange_name
                            )
                        )
                        if symbol in exchange_symbols:
                            count += 1
                    if count >= 2:  # Symbol available on at least 2 exchanges
                        common_symbols.append(symbol)
                all_symbols = common_symbols[:10]  # Limit to top 10 for performance
            else:
                all_symbols = list(all_symbols)[:10]

            # Find arbitrage opportunities
            opportunities = await self.exchange_manager.find_arbitrage_opportunities(
                all_symbols
            )

            if opportunities:
                self.logger.info(
                    f"🔍 Found {len(opportunities)} arbitrage opportunities"
                )
                for opp in opportunities:
                    self.logger.info(
                        f"📈 {opp['symbol']}: {opp['profit_percentage']:.3f}% profit potential"
                    )

            return opportunities

        except Exception as e:
            self.logger.error(f"Error scanning arbitrage opportunities: {e}")
            return []

    async def execute_opportunity(self, opportunity: Dict) -> Optional[Dict]:
        """Execute an arbitrage opportunity"""
        try:
            symbol = opportunity["symbol"]
            buy_exchange = opportunity["buy_exchange"]
            sell_exchange = opportunity["sell_exchange"]
            buy_price = opportunity["buy_price"]
            sell_price = opportunity["sell_price"]

            # Calculate position size based on available balance
            buy_balance = await self.exchange_manager.get_balance(buy_exchange)
            sell_balance = await self.exchange_manager.get_balance(sell_exchange)

            if not buy_balance or not sell_balance:
                self.logger.warning(
                    f"Could not get balance for arbitrage trade {symbol}"
                )
                return None

            # Get base and quote currencies
            base_currency, quote_currency = symbol.split("/")

            # Calculate maximum position size
            available_quote = buy_balance.get(quote_currency, {}).get("free", 0)
            available_base = sell_balance.get(base_currency, {}).get("free", 0)

            max_buy_amount = (available_quote * self.max_position_size) / buy_price
            max_sell_amount = available_base * self.max_position_size

            # Use smaller of the two amounts
            trade_amount = min(max_buy_amount, max_sell_amount)

            if trade_amount < 0.001:  # Minimum trade size
                self.logger.warning(
                    f"Trade amount too small for {symbol}: {trade_amount}"
                )
                return None

            # Execute simultaneous buy and sell orders
            self.logger.info(
                f"🔄 Executing arbitrage: Buy {trade_amount:.6f} {symbol} on {buy_exchange} at ${buy_price:.4f}"
            )
            self.logger.info(
                f"🔄 Executing arbitrage: Sell {trade_amount:.6f} {symbol} on {sell_exchange} at ${sell_price:.4f}"
            )

            # Place orders simultaneously
            buy_task = self.exchange_manager.place_order(
                buy_exchange, symbol, "market", "buy", trade_amount
            )
            sell_task = self.exchange_manager.place_order(
                sell_exchange, symbol, "market", "sell", trade_amount
            )

            buy_order, sell_order = await asyncio.gather(
                buy_task, sell_task, return_exceptions=True
            )

            if isinstance(buy_order, Exception):
                self.logger.error(f"Buy order failed: {buy_order}")
                return None

            if isinstance(sell_order, Exception):
                self.logger.error(f"Sell order failed: {sell_order}")
                return None

            # Calculate actual profit
            buy_cost = buy_order.get("cost", trade_amount * buy_price)
            sell_revenue = sell_order.get("cost", trade_amount * sell_price)
            actual_profit = sell_revenue - buy_cost

            trade_result = {
                "strategy": "arbitrage",
                "symbol": symbol,
                "buy_exchange": buy_exchange,
                "sell_exchange": sell_exchange,
                "amount": trade_amount,
                "buy_price": buy_order.get("price", buy_price),
                "sell_price": sell_order.get("price", sell_price),
                "buy_cost": buy_cost,
                "sell_revenue": sell_revenue,
                "profit": actual_profit,
                "profit_percentage": (
                    (actual_profit / buy_cost) * 100 if buy_cost > 0 else 0
                ),
                "timestamp": datetime.now(),
                "buy_order_id": buy_order.get("id"),
                "sell_order_id": sell_order.get("id"),
            }

            self.logger.info(
                f"✅ Arbitrage executed: ${actual_profit:.4f} profit ({trade_result['profit_percentage']:.3f}%)"
            )
            return trade_result

        except Exception as e:
            self.logger.error(f"Error executing arbitrage opportunity: {e}")
            return None


class MomentumStrategy:
    """Momentum trading strategy using technical analysis"""

    def __init__(self, exchange_manager, config_manager):
        self.exchange_manager = exchange_manager
        self.config_manager = config_manager
        self.logger = setup_logger("momentum_strategy")
        self.ta_config = config_manager.get_section("technical_analysis")
        self.trading_config = config_manager.get_section("trading")
        self.risk_config = config_manager.get_section("risk_management")

        # Technical analysis parameters
        self.rsi_period = self.ta_config.get("rsi_period", 14)
        self.rsi_overbought = self.ta_config.get("rsi_overbought", 70)
        self.rsi_oversold = self.ta_config.get("rsi_oversold", 30)
        self.macd_fast = self.ta_config.get("macd_fast", 12)
        self.macd_slow = self.ta_config.get("macd_slow", 26)
        self.macd_signal = self.ta_config.get("macd_signal", 9)
        self.bb_period = self.ta_config.get("bollinger_period", 20)
        self.bb_std = self.ta_config.get("bollinger_std", 2)

        # Trading parameters
        self.target_profit = self.trading_config.get("target_profit_momentum", 0.02)
        self.max_position_size = self.trading_config.get("max_position_size", 0.02)
        self.stop_loss = self.risk_config.get("stop_loss_percentage", 0.02)

        # Price history storage
        self.price_history: Dict[str, List] = {}
        self.positions: Dict[str, Dict] = {}

    async def get_historical_data(
        self, exchange_name: str, symbol: str, timeframe: str = "1m", limit: int = 100
    ) -> Optional[np.ndarray]:
        """Get historical price data for technical analysis"""
        try:
            if exchange_name == "paper":
                # Generate mock historical data for paper trading
                import random

                base_prices = {"BTC/USDT": 45000, "ETH/USDT": 3000, "ADA/USDT": 0.5}
                base_price = base_prices.get(symbol, 100)

                prices = []
                current_price = base_price
                for i in range(limit):
                    # Add random walk with slight upward bias for momentum
                    change = random.uniform(-0.02, 0.025)
                    current_price *= 1 + change
                    prices.append(current_price)

                return np.array(prices)

            exchange = self.exchange_manager.exchanges.get(exchange_name)
            if exchange and hasattr(exchange, "fetch_ohlcv"):
                ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                closes = [candle[4] for candle in ohlcv]  # Close prices
                return np.array(closes)

        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")

        return None

    def calculate_technical_indicators(self, prices: np.ndarray) -> Dict:
        """Calculate technical indicators"""
        try:
            if len(prices) < max(self.rsi_period, self.macd_slow, self.bb_period):
                return {}

            if not TALIB_AVAILABLE:
                # Return mock indicators when TA-Lib is not available
                return {
                    "rsi": 50.0,
                    "macd": 0.0,
                    "macd_signal": 0.0,
                    "macd_histogram": 0.0,
                    "bb_upper": prices[-1] * 1.02,
                    "bb_middle": prices[-1],
                    "bb_lower": prices[-1] * 0.98,
                    "sma_20": prices[-1],
                    "sma_50": prices[-1],
                    "current_price": prices[-1],
                }

            # RSI
            rsi = talib.RSI(prices, timeperiod=self.rsi_period)

            # MACD
            macd, macd_signal, macd_hist = talib.MACD(
                prices,
                fastperiod=self.macd_fast,
                slowperiod=self.macd_slow,
                signalperiod=self.macd_signal,
            )

            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(
                prices,
                timeperiod=self.bb_period,
                nbdevup=self.bb_std,
                nbdevdn=self.bb_std,
            )

            # Simple Moving Average
            sma_20 = talib.SMA(prices, timeperiod=20)
            sma_50 = talib.SMA(prices, timeperiod=50)

            return {
                "rsi": rsi[-1] if not np.isnan(rsi[-1]) else 50,
                "macd": macd[-1] if not np.isnan(macd[-1]) else 0,
                "macd_signal": macd_signal[-1] if not np.isnan(macd_signal[-1]) else 0,
                "macd_histogram": macd_hist[-1] if not np.isnan(macd_hist[-1]) else 0,
                "bb_upper": bb_upper[-1] if not np.isnan(bb_upper[-1]) else prices[-1],
                "bb_middle": (
                    bb_middle[-1] if not np.isnan(bb_middle[-1]) else prices[-1]
                ),
                "bb_lower": bb_lower[-1] if not np.isnan(bb_lower[-1]) else prices[-1],
                "sma_20": sma_20[-1] if not np.isnan(sma_20[-1]) else prices[-1],
                "sma_50": sma_50[-1] if not np.isnan(sma_50[-1]) else prices[-1],
                "current_price": prices[-1],
            }

        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {e}")
            return {}

    def generate_signal(self, indicators: Dict) -> Dict:
        """Generate trading signal based on technical indicators"""
        if not indicators:
            return {
                "action": "hold",
                "confidence": 0,
                "reason": "No indicators available",
            }

        signals = []
        confidence_factors = []

        current_price = indicators["current_price"]
        rsi = indicators["rsi"]
        macd = indicators["macd"]
        macd_signal = indicators["macd_signal"]
        macd_hist = indicators["macd_histogram"]
        bb_upper = indicators["bb_upper"]
        bb_lower = indicators["bb_lower"]
        sma_20 = indicators["sma_20"]
        sma_50 = indicators["sma_50"]

        # RSI signals
        if rsi < self.rsi_oversold:
            signals.append("buy")
            confidence_factors.append(0.8)
        elif rsi > self.rsi_overbought:
            signals.append("sell")
            confidence_factors.append(0.8)

        # MACD signals
        if macd > macd_signal and macd_hist > 0:
            signals.append("buy")
            confidence_factors.append(0.7)
        elif macd < macd_signal and macd_hist < 0:
            signals.append("sell")
            confidence_factors.append(0.7)

        # Bollinger Bands signals
        if current_price <= bb_lower:
            signals.append("buy")
            confidence_factors.append(0.6)
        elif current_price >= bb_upper:
            signals.append("sell")
            confidence_factors.append(0.6)

        # Moving Average signals
        if current_price > sma_20 > sma_50:
            signals.append("buy")
            confidence_factors.append(0.5)
        elif current_price < sma_20 < sma_50:
            signals.append("sell")
            confidence_factors.append(0.5)

        # Determine final signal
        if not signals:
            return {"action": "hold", "confidence": 0, "reason": "No clear signal"}

        buy_signals = signals.count("buy")
        sell_signals = signals.count("sell")

        if buy_signals > sell_signals:
            action = "buy"
            confidence = (
                sum(confidence_factors[:buy_signals]) / len(confidence_factors)
                if confidence_factors
                else 0
            )
            reason = f"Buy signals: RSI={rsi:.1f}, MACD={macd:.4f}>{macd_signal:.4f}"
        elif sell_signals > buy_signals:
            action = "sell"
            confidence = (
                sum(confidence_factors[:sell_signals]) / len(confidence_factors)
                if confidence_factors
                else 0
            )
            reason = f"Sell signals: RSI={rsi:.1f}, MACD={macd:.4f}<{macd_signal:.4f}"
        else:
            action = "hold"
            confidence = 0.3
            reason = "Mixed signals"

        return {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "indicators": indicators,
        }

    async def scan_signals(self) -> List[Dict]:
        """Scan for momentum trading signals"""
        signals = []

        try:
            # Get first available exchange
            exchange_name = list(self.exchange_manager.exchanges.keys())[0]
            symbols = await self.exchange_manager.get_trading_symbols(exchange_name)

            # Limit to top symbols for performance
            top_symbols = symbols[:5] if symbols else []

            for symbol in top_symbols:
                try:
                    # Get historical data
                    prices = await self.get_historical_data(exchange_name, symbol)
                    if prices is None or len(prices) < 50:
                        continue

                    # Calculate indicators
                    indicators = self.calculate_technical_indicators(prices)
                    if not indicators:
                        continue

                    # Generate signal
                    signal = self.generate_signal(indicators)

                    if signal["action"] != "hold" and signal["confidence"] > 0.6:
                        signal.update(
                            {
                                "symbol": symbol,
                                "exchange": exchange_name,
                                "timestamp": datetime.now(),
                            }
                        )
                        signals.append(signal)

                        self.logger.info(
                            f"📊 {symbol}: {signal['action'].upper()} signal "
                            f"(confidence: {signal['confidence']:.2f}) - {signal['reason']}"
                        )

                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}")
                    continue

            if signals:
                self.logger.info(f"🎯 Found {len(signals)} momentum signals")

        except Exception as e:
            self.logger.error(f"Error scanning momentum signals: {e}")

        return signals

    async def execute_signal(self, signal: Dict) -> Optional[Dict]:
        """Execute a momentum trading signal"""
        try:
            symbol = signal["symbol"]
            exchange_name = signal["exchange"]
            action = signal["action"]

            # Check if we already have a position
            position_key = f"{exchange_name}_{symbol}"

            if action == "buy" and position_key not in self.positions:
                return await self._execute_buy(signal)
            elif action == "sell" and position_key in self.positions:
                return await self._execute_sell(signal)

        except Exception as e:
            self.logger.error(f"Error executing momentum signal: {e}")

        return None

    async def _execute_buy(self, signal: Dict) -> Optional[Dict]:
        """Execute a buy order"""
        try:
            symbol = signal["symbol"]
            exchange_name = signal["exchange"]

            # Get current price
            ticker = await self.exchange_manager.get_ticker(exchange_name, symbol)
            if not ticker:
                return None

            current_price = ticker["last"]

            # Calculate position size
            balance = await self.exchange_manager.get_balance(exchange_name)
            if not balance:
                return None

            quote_currency = symbol.split("/")[1]
            available_balance = balance.get(quote_currency, {}).get("free", 0)
            position_value = available_balance * self.max_position_size
            amount = position_value / current_price

            if amount < 0.001:  # Minimum trade size
                self.logger.warning(f"Position too small for {symbol}: {amount}")
                return None

            # Place buy order
            order = await self.exchange_manager.place_order(
                exchange_name, symbol, "market", "buy", amount
            )
            if not order:
                return None

            # Store position
            position_key = f"{exchange_name}_{symbol}"
            self.positions[position_key] = {
                "symbol": symbol,
                "exchange": exchange_name,
                "side": "long",
                "amount": amount,
                "entry_price": order.get("price", current_price),
                "entry_time": datetime.now(),
                "target_price": current_price * (1 + self.target_profit),
                "stop_price": current_price * (1 - self.stop_loss),
                "order_id": order.get("id"),
            }

            trade_result = {
                "strategy": "momentum",
                "action": "buy",
                "symbol": symbol,
                "exchange": exchange_name,
                "amount": amount,
                "price": order.get("price", current_price),
                "cost": order.get("cost", amount * current_price),
                "timestamp": datetime.now(),
                "order_id": order.get("id"),
                "signal_confidence": signal["confidence"],
            }

            self.logger.info(
                f"📈 Momentum BUY: {amount:.6f} {symbol} at ${current_price:.4f}"
            )
            return trade_result

        except Exception as e:
            self.logger.error(f"Error executing buy order: {e}")
            return None

    async def _execute_sell(self, signal: Dict) -> Optional[Dict]:
        """Execute a sell order"""
        try:
            symbol = signal["symbol"]
            exchange_name = signal["exchange"]
            position_key = f"{exchange_name}_{symbol}"

            position = self.positions.get(position_key)
            if not position:
                return None

            # Get current price
            ticker = await self.exchange_manager.get_ticker(exchange_name, symbol)
            if not ticker:
                return None

            current_price = ticker["last"]
            amount = position["amount"]

            # Place sell order
            order = await self.exchange_manager.place_order(
                exchange_name, symbol, "market", "sell", amount
            )
            if not order:
                return None

            # Calculate profit
            entry_cost = position["amount"] * position["entry_price"]
            exit_revenue = order.get("cost", amount * current_price)
            profit = exit_revenue - entry_cost
            profit_percentage = (profit / entry_cost) * 100 if entry_cost > 0 else 0

            # Remove position
            del self.positions[position_key]

            trade_result = {
                "strategy": "momentum",
                "action": "sell",
                "symbol": symbol,
                "exchange": exchange_name,
                "amount": amount,
                "entry_price": position["entry_price"],
                "exit_price": order.get("price", current_price),
                "entry_cost": entry_cost,
                "exit_revenue": exit_revenue,
                "profit": profit,
                "profit_percentage": profit_percentage,
                "hold_duration": datetime.now() - position["entry_time"],
                "timestamp": datetime.now(),
                "order_id": order.get("id"),
                "signal_confidence": signal["confidence"],
            }

            self.logger.info(
                f"📉 Momentum SELL: {amount:.6f} {symbol} at ${current_price:.4f} "
                f"(P&L: ${profit:.4f}, {profit_percentage:.2f}%)"
            )
            return trade_result

        except Exception as e:
            self.logger.error(f"Error executing sell order: {e}")
            return None

    async def check_positions(self) -> List[Dict]:
        """Check existing positions for stop-loss or take-profit"""
        actions = []

        for position_key, position in list(self.positions.items()):
            try:
                symbol = position["symbol"]
                exchange_name = position["exchange"]

                # Get current price
                ticker = await self.exchange_manager.get_ticker(exchange_name, symbol)
                if not ticker:
                    continue

                current_price = ticker["last"]

                # Check stop-loss
                if current_price <= position["stop_price"]:
                    self.logger.warning(
                        f"🛑 Stop-loss triggered for {symbol} at ${current_price:.4f}"
                    )
                    actions.append(
                        {
                            "action": "sell",
                            "symbol": symbol,
                            "exchange": exchange_name,
                            "reason": "stop_loss",
                            "current_price": current_price,
                            "confidence": 1.0,
                        }
                    )

                # Check take-profit
                elif current_price >= position["target_price"]:
                    self.logger.info(
                        f"🎯 Take-profit triggered for {symbol} at ${current_price:.4f}"
                    )
                    actions.append(
                        {
                            "action": "sell",
                            "symbol": symbol,
                            "exchange": exchange_name,
                            "reason": "take_profit",
                            "current_price": current_price,
                            "confidence": 1.0,
                        }
                    )

                # Check for time-based exit (hold for too long)
                elif datetime.now() - position["entry_time"] > timedelta(hours=24):
                    self.logger.info(f"⏰ Time-based exit for {symbol} after 24 hours")
                    actions.append(
                        {
                            "action": "sell",
                            "symbol": symbol,
                            "exchange": exchange_name,
                            "reason": "time_exit",
                            "current_price": current_price,
                            "confidence": 0.8,
                        }
                    )

            except Exception as e:
                self.logger.error(f"Error checking position {position_key}: {e}")

        return actions
