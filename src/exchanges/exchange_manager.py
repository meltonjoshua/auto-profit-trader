"""
Exchange Manager for Auto Profit Trader
Manages connections to multiple cryptocurrency exchanges using CCXT
"""

import time
from datetime import datetime
from typing import Dict, List, Optional

import ccxt.async_support as ccxt

from security.crypto_manager import SecurityManager
from utils.logger import setup_logger


class ExchangeManager:
    """Manages connections and operations across multiple exchanges"""

    def __init__(self, config_manager, security_manager: SecurityManager):
        self.config_manager = config_manager
        self.security_manager = security_manager
        self.logger = setup_logger("exchange_manager")
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.market_data: Dict[str, Dict] = {}
        self.tickers: Dict[str, Dict] = {}
        self.last_update = {}

    async def initialize_exchanges(self):
        """Initialize all enabled exchanges"""
        self.logger.info("🔗 Initializing exchange connections...")

        exchange_configs = self.config_manager.get_section("exchanges")

        for exchange_name, config in exchange_configs.items():
            if config.get("enabled", False):
                try:
                    await self._initialize_exchange(exchange_name, config)
                    self.logger.info(f"✅ Connected to {exchange_name}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to connect to {exchange_name}: {e}")

        if not self.exchanges:
            self.logger.warning("⚠️ No exchanges connected - using paper trading mode")
            await self._initialize_paper_trading()

        self.logger.info(f"🔗 Connected to {len(self.exchanges)} exchanges")

    async def _initialize_exchange(self, exchange_name: str, config: Dict):
        """Initialize a specific exchange"""
        # Get encrypted credentials
        credentials = self.security_manager.get_api_credentials(exchange_name)

        if not credentials:
            self.logger.warning(f"No credentials found for {exchange_name}")
            return

        # Create exchange instance
        exchange_class = getattr(ccxt, exchange_name)

        params = {
            "apiKey": credentials["api_key"],
            "secret": credentials["api_secret"],
            "enableRateLimit": True,
            "options": {
                "defaultType": "spot",
            },
        }

        # Add sandbox/testnet support
        if config.get("testnet", False) or config.get("sandbox", False):
            if exchange_name == "binance" and config.get("testnet"):
                params["sandbox"] = True
            elif exchange_name == "coinbase" and config.get("sandbox"):
                params["sandbox"] = True

        exchange = exchange_class(params)

        # Test connection
        await exchange.load_markets()
        balance = await exchange.fetch_balance()

        self.exchanges[exchange_name] = exchange
        usdt_balance = balance.get("USDT", {}).get("total", 0)
        self.logger.info(f"Connected to {exchange_name} - Balance: ${usdt_balance:.2f}")

    async def _initialize_paper_trading(self):
        """Initialize paper trading mode for testing"""
        self.logger.info("📄 Initializing paper trading mode...")

        # Create a mock exchange for paper trading
        paper_exchange = type(
            "PaperExchange",
            (),
            {
                "id": "paper",
                "has": {
                    "fetchTicker": True,
                    "fetchOrderBook": True,
                    "createOrder": True,
                },
                "markets": {
                    "BTC/USDT": {
                        "id": "BTCUSDT",
                        "symbol": "BTC/USDT",
                        "base": "BTC",
                        "quote": "USDT",
                    },
                    "ETH/USDT": {
                        "id": "ETHUSDT",
                        "symbol": "ETH/USDT",
                        "base": "ETH",
                        "quote": "USDT",
                    },
                    "ADA/USDT": {
                        "id": "ADAUSDT",
                        "symbol": "ADA/USDT",
                        "base": "ADA",
                        "quote": "USDT",
                    },
                },
                "paper_balance": {"USDT": 10000.0, "BTC": 0.0, "ETH": 0.0, "ADA": 0.0},
            },
        )()

        self.exchanges["paper"] = paper_exchange

    async def get_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """Get current ticker data for a symbol"""
        try:
            if exchange_name == "paper":
                # Mock ticker data for paper trading
                base_prices = {"BTC/USDT": 45000, "ETH/USDT": 3000, "ADA/USDT": 0.5}
                base_price = base_prices.get(symbol, 100)
                # Add some random variation
                import random

                price_variation = random.uniform(-0.02, 0.02)
                current_price = base_price * (1 + price_variation)

                return {
                    "symbol": symbol,
                    "last": current_price,
                    "bid": current_price * 0.999,
                    "ask": current_price * 1.001,
                    "timestamp": int(time.time() * 1000),
                    "datetime": datetime.now().isoformat(),
                }

            exchange = self.exchanges.get(exchange_name)
            if exchange:
                ticker = await exchange.fetch_ticker(symbol)
                return ticker

        except Exception as e:
            self.logger.error(
                f"Error fetching ticker {symbol} from {exchange_name}: {e}"
            )

        return None

    async def get_order_book(
        self, exchange_name: str, symbol: str, limit: int = 20
    ) -> Optional[Dict]:
        """Get order book for a symbol"""
        try:
            if exchange_name == "paper":
                # Mock order book
                ticker = await self.get_ticker(exchange_name, symbol)
                if ticker:
                    mid_price = ticker["last"]
                    return {
                        "symbol": symbol,
                        "bids": [
                            [mid_price * (1 - i * 0.001), 10.0]
                            for i in range(1, limit + 1)
                        ],
                        "asks": [
                            [mid_price * (1 + i * 0.001), 10.0]
                            for i in range(1, limit + 1)
                        ],
                        "timestamp": int(time.time() * 1000),
                    }

            exchange = self.exchanges.get(exchange_name)
            if exchange:
                order_book = await exchange.fetch_order_book(symbol, limit)
                return order_book

        except Exception as e:
            self.logger.error(
                f"Error fetching order book {symbol} from {exchange_name}: {e}"
            )

        return None

    async def place_order(
        self,
        exchange_name: str,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: float = None,
    ) -> Optional[Dict]:
        """Place an order on the exchange"""
        try:
            if exchange_name == "paper":
                # Mock order execution for paper trading
                ticker = await self.get_ticker(exchange_name, symbol)
                if ticker:
                    execution_price = price if price else ticker["last"]

                    # Update paper balance
                    exchange = self.exchanges[exchange_name]
                    base, quote = symbol.split("/")

                    if side.lower() == "buy":
                        cost = amount * execution_price
                        if exchange.paper_balance.get(quote, 0) >= cost:
                            exchange.paper_balance[quote] -= cost
                            exchange.paper_balance[base] = (
                                exchange.paper_balance.get(base, 0) + amount
                            )
                        else:
                            raise Exception("Insufficient balance")
                    else:  # sell
                        if exchange.paper_balance.get(base, 0) >= amount:
                            exchange.paper_balance[base] -= amount
                            exchange.paper_balance[quote] = exchange.paper_balance.get(
                                quote, 0
                            ) + (amount * execution_price)
                        else:
                            raise Exception("Insufficient balance")

                    return {
                        "id": f"paper_{int(time.time())}",
                        "symbol": symbol,
                        "type": order_type,
                        "side": side,
                        "amount": amount,
                        "price": execution_price,
                        "cost": amount * execution_price,
                        "status": "closed",
                        "filled": amount,
                        "timestamp": int(time.time() * 1000),
                    }

            exchange = self.exchanges.get(exchange_name)
            if exchange:
                if order_type.lower() == "market":
                    order = await exchange.create_market_order(symbol, side, amount)
                else:
                    order = await exchange.create_limit_order(
                        symbol, side, amount, price
                    )
                return order

        except Exception as e:
            self.logger.error(f"Error placing order {symbol} on {exchange_name}: {e}")
            raise

        return None

    async def get_balance(self, exchange_name: str) -> Optional[Dict]:
        """Get account balance"""
        try:
            if exchange_name == "paper":
                exchange = self.exchanges[exchange_name]
                balance = {}
                for currency, amount in exchange.paper_balance.items():
                    balance[currency] = {"total": amount, "free": amount, "used": 0.0}
                return balance

            exchange = self.exchanges.get(exchange_name)
            if exchange:
                balance = await exchange.fetch_balance()
                return balance

        except Exception as e:
            self.logger.error(f"Error fetching balance from {exchange_name}: {e}")

        return None

    async def get_trading_symbols(self, exchange_name: str) -> List[str]:
        """Get list of tradeable symbols"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if exchange:
                if exchange_name == "paper":
                    return list(exchange.markets.keys())
                markets = await exchange.load_markets()
                return [symbol for symbol in markets.keys() if "/USDT" in symbol]
        except Exception as e:
            self.logger.error(f"Error getting symbols from {exchange_name}: {e}")

        return []

    async def find_arbitrage_opportunities(self, symbols: List[str]) -> List[Dict]:
        """Find arbitrage opportunities across exchanges"""
        opportunities = []

        if len(self.exchanges) < 2:
            return opportunities

        for symbol in symbols:
            try:
                prices = {}

                # Get prices from all exchanges
                for exchange_name in self.exchanges.keys():
                    ticker = await self.get_ticker(exchange_name, symbol)
                    if ticker:
                        prices[exchange_name] = {
                            "bid": ticker["bid"],
                            "ask": ticker["ask"],
                            "last": ticker["last"],
                        }

                if len(prices) >= 2:
                    # Find highest bid and lowest ask
                    highest_bid = max(prices.items(), key=lambda x: x[1]["bid"])
                    lowest_ask = min(prices.items(), key=lambda x: x[1]["ask"])

                    if highest_bid[1]["bid"] > lowest_ask[1]["ask"]:
                        profit_amount = highest_bid[1]["bid"] - lowest_ask[1]["ask"]
                        profit_percentage = (profit_amount / lowest_ask[1]["ask"]) * 100

                        # Only consider opportunities with significant profit
                        min_profit = (
                            self.config_manager.get_section("trading").get(
                                "target_profit_arbitrage", 0.005
                            )
                            * 100
                        )
                        if profit_percentage >= min_profit:
                            opportunities.append(
                                {
                                    "symbol": symbol,
                                    "buy_exchange": lowest_ask[0],
                                    "sell_exchange": highest_bid[0],
                                    "buy_price": lowest_ask[1]["ask"],
                                    "sell_price": highest_bid[1]["bid"],
                                    "profit_amount": profit_amount,
                                    "profit_percentage": profit_percentage,
                                    "timestamp": datetime.now(),
                                }
                            )

            except Exception as e:
                self.logger.error(f"Error checking arbitrage for {symbol}: {e}")

        return opportunities

    async def shutdown(self):
        """Shutdown all exchange connections"""
        self.logger.info("🛑 Shutting down exchange connections...")

        for exchange_name, exchange in self.exchanges.items():
            try:
                if hasattr(exchange, "close"):
                    await exchange.close()
                self.logger.info(f"✅ Disconnected from {exchange_name}")
            except Exception as e:
                self.logger.error(f"Error closing {exchange_name}: {e}")

        self.exchanges.clear()
        self.logger.info("✅ All exchange connections closed")
