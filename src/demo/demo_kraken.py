"""
Demo Kraken Mode for Auto Profit Trader
Simulates realistic UK cryptocurrency trading with live-like data
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.utils.logger import setup_logger


class DemoKrakenExchange:
    """Demo Kraken exchange with realistic UK trading simulation"""

    def __init__(self):
        self.logger = setup_logger("demo_kraken")
        self.id = "demo_kraken"
        self.name = "Kraken Demo (UK)"
        
        # Realistic UK crypto prices (August 2025)
        self.base_prices = {
            "BTC/GBP": 36500.0,  # Bitcoin in British Pounds
            "ETH/GBP": 2450.0,   # Ethereum in British Pounds
            "ADA/GBP": 0.385,    # Cardano in British Pounds
            "DOT/GBP": 4.25,     # Polkadot in British Pounds
            "MATIC/GBP": 0.52,   # Polygon in British Pounds
            "LINK/GBP": 11.80,   # Chainlink in British Pounds
            "XRP/GBP": 0.48,     # Ripple in British Pounds
            "SOL/GBP": 142.50,   # Solana in British Pounds
            "AVAX/GBP": 18.60,   # Avalanche in British Pounds
            "UNI/GBP": 5.95,     # Uniswap in British Pounds
            
            # USDT pairs for arbitrage
            "BTC/USDT": 46000.0,
            "ETH/USDT": 3100.0,
            "ADA/USDT": 0.485,
            "DOT/USDT": 5.35,
            "MATIC/USDT": 0.655,
        }
        
        # Demo account balance (realistic starting amounts)
        self.demo_balance = {
            "GBP": 5000.0,   # £5,000 starting balance
            "USDT": 2000.0,  # $2,000 for arbitrage
            "BTC": 0.0,
            "ETH": 0.0,
            "ADA": 0.0,
            "DOT": 0.0,
            "MATIC": 0.0,
            "LINK": 0.0,
            "XRP": 0.0,
            "SOL": 0.0,
            "AVAX": 0.0,
            "UNI": 0.0,
        }
        
        # Price movement simulation
        self.price_trends = {}
        self.last_update = time.time()
        self.trade_history = []
        self.order_id_counter = 1000
        
        # Market hours simulation (more volatility during UK hours)
        self.uk_market_hours = (8, 17)  # 8 AM to 5 PM GMT
        
        self.logger.info("🇬🇧 Demo Kraken initialized with UK focus")
        self.logger.info(f"💷 Starting balance: £{self.demo_balance['GBP']:,.2f}")

    def _is_uk_market_hours(self) -> bool:
        """Check if it's UK market hours for increased volatility"""
        uk_hour = datetime.now().hour
        return self.uk_market_hours[0] <= uk_hour <= self.uk_market_hours[1]

    def _simulate_market_movement(self, symbol: str) -> float:
        """Simulate realistic market price movements"""
        base_price = self.base_prices.get(symbol, 100.0)
        
        # Different volatility for different assets
        if "BTC" in symbol:
            volatility = 0.02  # 2% max movement
        elif "ETH" in symbol:
            volatility = 0.025  # 2.5% max movement
        elif symbol in ["ADA/GBP", "DOT/GBP", "MATIC/GBP"]:
            volatility = 0.035  # 3.5% max movement (altcoins more volatile)
        else:
            volatility = 0.03  # 3% max movement
        
        # Increase volatility during UK market hours
        if self._is_uk_market_hours():
            volatility *= 1.5
        
        # Add some trending behavior
        if symbol not in self.price_trends:
            self.price_trends[symbol] = random.choice([-1, 0, 1])  # bearish, sideways, bullish
        
        # Occasionally change trend
        if random.random() < 0.05:  # 5% chance to change trend
            self.price_trends[symbol] = random.choice([-1, 0, 1])
        
        # Generate price movement
        trend_influence = self.price_trends[symbol] * 0.001  # Small trend bias
        random_movement = random.uniform(-volatility, volatility)
        total_movement = trend_influence + random_movement
        
        new_price = base_price * (1 + total_movement)
        
        # Update base price occasionally for persistence
        if random.random() < 0.1:  # 10% chance to update base
            self.base_prices[symbol] = new_price
        
        return new_price

    async def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch realistic ticker data"""
        try:
            current_price = self._simulate_market_movement(symbol)
            
            # Add realistic bid/ask spread
            if "GBP" in symbol:
                spread = 0.001  # 0.1% spread for GBP pairs
            else:
                spread = 0.0015  # 0.15% spread for USDT pairs
            
            bid = current_price * (1 - spread)
            ask = current_price * (1 + spread)
            
            return {
                "symbol": symbol,
                "last": current_price,
                "bid": bid,
                "ask": ask,
                "high": current_price * 1.025,
                "low": current_price * 0.975,
                "volume": random.uniform(1000, 50000),
                "timestamp": int(time.time() * 1000),
                "datetime": datetime.now().isoformat(),
                "change": random.uniform(-3.0, 3.0),  # % change
            }
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    async def fetch_balance(self) -> Dict:
        """Fetch demo account balance"""
        balance = {}
        for currency, amount in self.demo_balance.items():
            balance[currency] = {
                "total": amount,
                "free": amount * 0.95,  # 95% available for trading
                "used": amount * 0.05,   # 5% in open orders
            }
        return balance

    async def create_market_order(self, symbol: str, side: str, amount: float) -> Dict:
        """Simulate market order execution"""
        try:
            ticker = await self.fetch_ticker(symbol)
            if not ticker:
                raise Exception(f"Could not get price for {symbol}")
            
            # Use bid for sells, ask for buys (realistic execution)
            execution_price = ticker["ask"] if side.lower() == "buy" else ticker["bid"]
            
            base, quote = symbol.split("/")
            cost = amount * execution_price
            
            # Add realistic slippage for larger orders
            if cost > 1000:  # Large order
                slippage = random.uniform(0.001, 0.003)  # 0.1-0.3% slippage
                execution_price *= (1 + slippage) if side.lower() == "buy" else (1 - slippage)
                cost = amount * execution_price
            
            # Update demo balance
            if side.lower() == "buy":
                if self.demo_balance.get(quote, 0) < cost:
                    raise Exception(f"Insufficient {quote} balance")
                self.demo_balance[quote] -= cost
                self.demo_balance[base] = self.demo_balance.get(base, 0) + amount
            else:  # sell
                if self.demo_balance.get(base, 0) < amount:
                    raise Exception(f"Insufficient {base} balance")
                self.demo_balance[base] -= amount
                self.demo_balance[quote] = self.demo_balance.get(quote, 0) + cost
            
            # Create order record
            order = {
                "id": f"DEMO_{self.order_id_counter}",
                "symbol": symbol,
                "type": "market",
                "side": side,
                "amount": amount,
                "price": execution_price,
                "cost": cost,
                "status": "closed",
                "filled": amount,
                "timestamp": int(time.time() * 1000),
                "datetime": datetime.now().isoformat(),
                "fee": {
                    "cost": cost * 0.0026,  # Kraken's 0.26% fee
                    "currency": quote,
                },
            }
            
            self.order_id_counter += 1
            self.trade_history.append(order)
            
            # Log the trade
            self.logger.info(
                f"🇬🇧 Demo Trade: {side.upper()} {amount:.4f} {base} "
                f"at £{execution_price:.2f} = £{cost:.2f}"
            )
            
            return order
            
        except Exception as e:
            self.logger.error(f"Demo order failed: {e}")
            raise

    async def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Generate realistic order book"""
        ticker = await self.fetch_ticker(symbol)
        if not ticker:
            return {}
        
        mid_price = ticker["last"]
        
        # Generate realistic order book
        bids = []
        asks = []
        
        for i in range(1, limit + 1):
            # Bids (decreasing prices)
            bid_price = mid_price * (1 - i * 0.001)
            bid_size = random.uniform(0.1, 10.0)
            bids.append([bid_price, bid_size])
            
            # Asks (increasing prices)
            ask_price = mid_price * (1 + i * 0.001)
            ask_size = random.uniform(0.1, 10.0)
            asks.append([ask_price, ask_size])
        
        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": int(time.time() * 1000),
            "datetime": datetime.now().isoformat(),
        }

    def get_trading_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        return list(self.base_prices.keys())

    def get_gbp_pairs(self) -> List[str]:
        """Get GBP trading pairs (UK focus)"""
        return [symbol for symbol in self.base_prices.keys() if "/GBP" in symbol]

    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trade history"""
        return self.trade_history[-limit:]

    async def simulate_market_conditions(self, condition: str = "normal"):
        """Simulate different market conditions"""
        if condition == "bull_run":
            # Simulate bull market
            for symbol in self.base_prices:
                self.price_trends[symbol] = 1  # All trending up
                self.base_prices[symbol] *= 1.02  # 2% pump
        
        elif condition == "bear_market":
            # Simulate bear market
            for symbol in self.base_prices:
                self.price_trends[symbol] = -1  # All trending down
                self.base_prices[symbol] *= 0.98  # 2% dump
        
        elif condition == "high_volatility":
            # Simulate high volatility
            for symbol in self.base_prices:
                movement = random.uniform(-0.05, 0.05)  # 5% random movements
                self.base_prices[symbol] *= (1 + movement)
        
        elif condition == "uk_market_open":
            # Simulate UK market opening (higher activity)
            for symbol in self.get_gbp_pairs():
                movement = random.uniform(-0.02, 0.03)  # Slight bullish bias
                self.base_prices[symbol] *= (1 + movement)
        
        self.logger.info(f"🎭 Market condition changed to: {condition}")

    def get_demo_stats(self) -> Dict:
        """Get demo trading statistics"""
        total_trades = len(self.trade_history)
        
        if total_trades == 0:
            return {"message": "No trades yet in demo mode"}
        
        profits = []
        for trade in self.trade_history:
            if trade["side"] == "sell":
                # Calculate profit (simplified)
                profit = trade["cost"] - (trade["amount"] * self.base_prices.get(trade["symbol"], 0))
                profits.append(profit)
        
        total_profit = sum(profits) if profits else 0
        win_rate = (len([p for p in profits if p > 0]) / len(profits) * 100) if profits else 0
        
        return {
            "total_trades": total_trades,
            "total_profit_gbp": total_profit,
            "win_rate": win_rate,
            "current_balance_gbp": self.demo_balance["GBP"],
            "demo_mode": True,
            "uk_optimized": True,
        }


class DemoKrakenManager:
    """Manager for demo Kraken trading"""

    def __init__(self):
        self.logger = setup_logger("demo_kraken_manager")
        self.demo_exchange = DemoKrakenExchange()
        self.is_running = False

    async def start_demo_mode(self):
        """Start demo trading mode"""
        self.is_running = True
        self.logger.info("🇬🇧 Starting Demo Kraken Mode")
        self.logger.info("💷 UK-focused cryptocurrency demo trading")
        
        # Display available pairs
        gbp_pairs = self.demo_exchange.get_gbp_pairs()
        self.logger.info(f"📊 Available GBP pairs: {', '.join(gbp_pairs)}")
        
        return self.demo_exchange

    async def demo_trading_session(self, duration_minutes: int = 5):
        """Run a demo trading session"""
        self.logger.info(f"🎮 Starting {duration_minutes}-minute demo session")
        
        end_time = time.time() + (duration_minutes * 60)
        trade_count = 0
        
        while time.time() < end_time and self.is_running:
            try:
                # Random demo trade
                symbol = random.choice(self.demo_exchange.get_gbp_pairs())
                side = random.choice(["buy", "sell"])
                amount = random.uniform(0.01, 0.1)  # Small demo amounts
                
                if side == "buy" and self.demo_exchange.demo_balance["GBP"] > 100:
                    await self.demo_exchange.create_market_order(symbol, side, amount)
                    trade_count += 1
                elif side == "sell" and self.demo_exchange.demo_balance.get(symbol.split("/")[0], 0) > amount:
                    await self.demo_exchange.create_market_order(symbol, side, amount)
                    trade_count += 1
                
                # Random market condition changes
                if random.random() < 0.1:  # 10% chance
                    condition = random.choice(["normal", "bull_run", "bear_market", "high_volatility"])
                    await self.demo_exchange.simulate_market_conditions(condition)
                
                await asyncio.sleep(2)  # 2 seconds between actions
                
            except Exception as e:
                self.logger.error(f"Demo trading error: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"🏁 Demo session completed! Executed {trade_count} trades")
        return self.demo_exchange.get_demo_stats()

    def stop_demo_mode(self):
        """Stop demo trading"""
        self.is_running = False
        self.logger.info("🛑 Demo Kraken mode stopped")


# Example usage functions
async def run_demo_kraken():
    """Quick demo run"""
    demo_manager = DemoKrakenManager()
    demo_exchange = await demo_manager.start_demo_mode()
    
    # Show initial prices
    print("\n🇬🇧 UK CRYPTO PRICES (DEMO):")
    for symbol in demo_exchange.get_gbp_pairs()[:5]:
        ticker = await demo_exchange.fetch_ticker(symbol)
        print(f"   {symbol}: £{ticker['last']:,.2f}")
    
    # Run demo session
    stats = await demo_manager.demo_trading_session(1)  # 1 minute demo
    
    print(f"\n📊 Demo Results:")
    print(f"   Trades: {stats.get('total_trades', 0)}")
    print(f"   Profit: £{stats.get('total_profit_gbp', 0):.2f}")
    print(f"   Balance: £{stats.get('current_balance_gbp', 0):,.2f}")
    
    return demo_exchange


if __name__ == "__main__":
    asyncio.run(run_demo_kraken())
