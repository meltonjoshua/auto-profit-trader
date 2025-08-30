"""
Enhanced Trading Dashboard with System Health Monitoring
Comprehensive real-time monitoring for UK crypto trading
"""

import asyncio
import json
import sqlite3
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from aiohttp import web, web_ws
import aiohttp_cors
import logging
import traceback
from typing import Dict, List, Optional

# Setup paths
import sys
sys.path.append('src')

from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from security.crypto_manager import SecurityManager
from exchanges.exchange_manager import ExchangeManager

class EnhancedDashboard:
    def __init__(self):
        self.logger = setup_logger("enhanced_dashboard")
        self.config = ConfigManager()
        self.security = SecurityManager()
        self.exchange_manager = None
        self.websockets = set()
        self.start_time = datetime.now()
        self.metrics = {
            'trades_today': 0,
            'profit_today': 0,
            'system_uptime': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
            'active_exchanges': 0,
            'portfolio_value': 0,
            'last_update': None
        }
        
    async def initialize(self):
        """Initialize the dashboard"""
        try:
            self.exchange_manager = ExchangeManager(self.config, self.security)
            await self.exchange_manager.initialize_exchanges()
            self.logger.info("🚀 Enhanced dashboard initialized")
        except Exception as e:
            self.logger.error(f"Dashboard initialization error: {e}")
    
    async def get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Trading metrics
            trades_today = await self.get_trades_today()
            profit_today = await self.get_profit_today()
            portfolio_value = await self.get_portfolio_value()
            
            # System uptime
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            uptime_hours = uptime_seconds / 3600
            
            # Active exchanges
            active_exchanges = len(self.exchange_manager.exchanges) if self.exchange_manager else 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'uptime_hours': round(uptime_hours, 2),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_free_gb': round(disk.free / (1024**3), 2),
                    'disk_percent': (disk.used / disk.total) * 100
                },
                'trading': {
                    'trades_today': trades_today,
                    'profit_today_gbp': profit_today,
                    'portfolio_value_gbp': portfolio_value,
                    'active_exchanges': active_exchanges,
                    'last_trade': await self.get_last_trade(),
                    'win_rate': await self.get_win_rate()
                },
                'health_status': await self.get_health_status()
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
    
    async def get_trades_today(self) -> int:
        """Get number of trades today"""
        try:
            if not Path('portfolio.db').exists():
                return 0
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = ?",
                (today,)
            )
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    async def get_profit_today(self) -> float:
        """Get profit/loss today"""
        try:
            if not Path('portfolio.db').exists():
                return 0.0
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT SUM(profit_loss) FROM trades WHERE DATE(timestamp) = ? AND profit_loss IS NOT NULL",
                (today,)
            )
            result = cursor.fetchone()[0]
            conn.close()
            return float(result) if result else 0.0
        except:
            return 0.0
    
    async def get_portfolio_value(self) -> float:
        """Get total portfolio value"""
        try:
            if not self.exchange_manager:
                return 0.0
                
            total_value = 0.0
            for exchange_name, exchange in self.exchange_manager.exchanges.items():
                try:
                    balance = await exchange.fetch_balance()
                    # Convert to GBP equivalent
                    for currency, amount in balance['total'].items():
                        if currency == 'GBP':
                            total_value += amount
                        elif currency in ['USD', 'EUR', 'BTC', 'ETH']:
                            # Simplified conversion - would need real rates
                            total_value += amount * 0.8  # Rough GBP conversion
                except:
                    continue
                    
            return round(total_value, 2)
        except:
            return 0.0
    
    async def get_last_trade(self) -> Optional[Dict]:
        """Get details of last trade"""
        try:
            if not Path('portfolio.db').exists():
                return None
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT symbol, side, amount, price, profit_loss, timestamp FROM trades ORDER BY timestamp DESC LIMIT 1"
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'symbol': result[0],
                    'side': result[1],
                    'amount': result[2],
                    'price': result[3],
                    'profit_loss': result[4],
                    'timestamp': result[5]
                }
            return None
        except:
            return None
    
    async def get_win_rate(self) -> float:
        """Get current win rate percentage"""
        try:
            if not Path('portfolio.db').exists():
                return 0.0
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM trades WHERE profit_loss > 0")
            winning_trades = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM trades WHERE profit_loss IS NOT NULL")
            total_trades = cursor.fetchone()[0]
            
            conn.close()
            
            if total_trades > 0:
                return round((winning_trades / total_trades) * 100, 1)
            return 0.0
        except:
            return 0.0
    
    async def get_health_status(self) -> Dict:
        """Get overall system health status"""
        try:
            health = {
                'overall': 'healthy',
                'issues': [],
                'warnings': []
            }
            
            # Check system resources
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            if cpu > 80:
                health['issues'].append('High CPU usage')
                health['overall'] = 'warning'
            
            if memory.percent > 85:
                health['issues'].append('High memory usage')
                health['overall'] = 'warning'
            
            # Check trading system
            if not self.exchange_manager:
                health['issues'].append('Exchange manager not initialized')
                health['overall'] = 'error'
            elif not self.exchange_manager.exchanges:
                health['warnings'].append('No exchanges connected')
                health['overall'] = 'warning'
            
            # Check database
            if not Path('portfolio.db').exists():
                health['warnings'].append('No trading database found')
            
            # Check API credentials
            if not Path('encrypted_credentials.json').exists():
                health['warnings'].append('No API credentials configured')
            
            return health
        except Exception as e:
            return {
                'overall': 'error',
                'issues': [f'Health check failed: {str(e)}'],
                'warnings': []
            }
    
    async def get_trading_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trading history"""
        try:
            if not Path('portfolio.db').exists():
                return []
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            trades = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts
            trade_list = []
            for trade in trades:
                if len(trade) >= 6:
                    trade_list.append({
                        'id': trade[0],
                        'symbol': trade[1],
                        'side': trade[2],
                        'amount': trade[3],
                        'price': trade[4],
                        'profit_loss': trade[5],
                        'timestamp': trade[6] if len(trade) > 6 else None
                    })
            
            return trade_list
        except Exception as e:
            self.logger.error(f"Error getting trading history: {e}")
            return []
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates"""
        ws = web_ws.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == web_ws.WSMsgType.TEXT:
                    # Handle client messages if needed
                    pass
                elif msg.type == web_ws.WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.websockets.discard(ws)
        
        return ws
    
    async def broadcast_metrics(self):
        """Broadcast metrics to all connected WebSocket clients"""
        if not self.websockets:
            return
            
        try:
            metrics = await self.get_system_metrics()
            message = json.dumps(metrics)
            
            # Send to all connected clients
            disconnected = set()
            for ws in self.websockets:
                try:
                    await ws.send_str(message)
                except:
                    disconnected.add(ws)
            
            # Remove disconnected clients
            self.websockets -= disconnected
            
        except Exception as e:
            self.logger.error(f"Error broadcasting metrics: {e}")
    
    async def metrics_handler(self, request):
        """API endpoint for system metrics"""
        try:
            metrics = await self.get_system_metrics()
            return web.json_response(metrics)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def trades_handler(self, request):
        """API endpoint for trading history"""
        try:
            limit = int(request.query.get('limit', 50))
            trades = await self.get_trading_history(limit)
            return web.json_response(trades)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def dashboard_handler(self, request):
        """Serve enhanced dashboard HTML"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇬🇧 Auto Profit Trader - UK Crypto Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header .subtitle { font-size: 1.2em; opacity: 0.8; }
        
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-card h3 { font-size: 1.4em; margin-bottom: 15px; }
        .metric-value { font-size: 2.2em; font-weight: bold; margin-bottom: 10px; }
        .metric-label { opacity: 0.8; font-size: 0.9em; }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-healthy { background: #4CAF50; }
        .status-warning { background: #FF9800; }
        .status-error { background: #F44336; }
        
        .trades-section { margin-top: 30px; }
        .trades-table {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        .trades-table th, .trades-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .trades-table th { background: rgba(255, 255, 255, 0.2); font-weight: bold; }
        
        .profit-positive { color: #4CAF50; }
        .profit-negative { color: #F44336; }
        
        .last-update {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        
        .uk-flag { font-size: 2em; margin-right: 10px; }
        
        @media (max-width: 768px) {
            .metrics-grid { grid-template-columns: 1fr; }
            .metric-value { font-size: 1.8em; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="uk-flag">🇬🇧</span>Auto Profit Trader</h1>
            <p class="subtitle">UK Cryptocurrency Trading Dashboard</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💷 Today's Profit</h3>
                <div class="metric-value" id="profit-today">£0.00</div>
                <div class="metric-label">British Pounds</div>
            </div>
            
            <div class="metric-card">
                <h3>📊 Trades Today</h3>
                <div class="metric-value" id="trades-today">0</div>
                <div class="metric-label">Executed Orders</div>
            </div>
            
            <div class="metric-card">
                <h3>🏦 Portfolio Value</h3>
                <div class="metric-value" id="portfolio-value">£0.00</div>
                <div class="metric-label">Total GBP Value</div>
            </div>
            
            <div class="metric-card">
                <h3>🎯 Win Rate</h3>
                <div class="metric-value" id="win-rate">0%</div>
                <div class="metric-label">Success Percentage</div>
            </div>
            
            <div class="metric-card">
                <h3>🔗 Active Exchanges</h3>
                <div class="metric-value" id="active-exchanges">0</div>
                <div class="metric-label">Connected APIs</div>
            </div>
            
            <div class="metric-card">
                <h3>⚡ System Health</h3>
                <div class="metric-value">
                    <span id="health-status" class="status-badge status-healthy">Healthy</span>
                </div>
                <div class="metric-label" id="health-details">All systems operational</div>
            </div>
            
            <div class="metric-card">
                <h3>🖥️ CPU Usage</h3>
                <div class="metric-value" id="cpu-usage">0%</div>
                <div class="metric-label">System Performance</div>
            </div>
            
            <div class="metric-card">
                <h3>💾 Memory Usage</h3>
                <div class="metric-value" id="memory-usage">0%</div>
                <div class="metric-label">RAM Utilization</div>
            </div>
            
            <div class="metric-card">
                <h3>⏱️ Uptime</h3>
                <div class="metric-value" id="uptime">0h</div>
                <div class="metric-label">System Runtime</div>
            </div>
        </div>
        
        <div class="trades-section">
            <h2>📋 Recent Trades</h2>
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Pair</th>
                        <th>Side</th>
                        <th>Amount</th>
                        <th>Price</th>
                        <th>P&L (£)</th>
                    </tr>
                </thead>
                <tbody id="trades-tbody">
                    <tr>
                        <td colspan="6" style="text-align: center; opacity: 0.7;">Loading trades...</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="last-update">
            Last updated: <span id="last-update">Never</span>
        </div>
    </div>

    <script>
        let ws = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function(event) {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function(event) {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(connectWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            if (data.error) {
                console.error('Dashboard error:', data.error);
                return;
            }
            
            // Update trading metrics
            if (data.trading) {
                document.getElementById('profit-today').textContent = 
                    `£${data.trading.profit_today_gbp?.toFixed(2) || '0.00'}`;
                document.getElementById('trades-today').textContent = 
                    data.trading.trades_today || 0;
                document.getElementById('portfolio-value').textContent = 
                    `£${data.trading.portfolio_value_gbp?.toFixed(2) || '0.00'}`;
                document.getElementById('win-rate').textContent = 
                    `${data.trading.win_rate || 0}%`;
                document.getElementById('active-exchanges').textContent = 
                    data.trading.active_exchanges || 0;
            }
            
            // Update system metrics
            if (data.system) {
                document.getElementById('cpu-usage').textContent = 
                    `${data.system.cpu_percent?.toFixed(1) || 0}%`;
                document.getElementById('memory-usage').textContent = 
                    `${data.system.memory_percent?.toFixed(1) || 0}%`;
                document.getElementById('uptime').textContent = 
                    `${data.system.uptime_hours?.toFixed(1) || 0}h`;
            }
            
            // Update health status
            if (data.health_status) {
                const healthElement = document.getElementById('health-status');
                const detailsElement = document.getElementById('health-details');
                
                healthElement.className = `status-badge status-${data.health_status.overall}`;
                healthElement.textContent = data.health_status.overall.toUpperCase();
                
                let details = 'All systems operational';
                if (data.health_status.issues.length > 0) {
                    details = data.health_status.issues.join(', ');
                } else if (data.health_status.warnings.length > 0) {
                    details = data.health_status.warnings.join(', ');
                }
                detailsElement.textContent = details;
            }
            
            // Update timestamp
            document.getElementById('last-update').textContent = 
                new Date().toLocaleString('en-GB');
        }
        
        async function loadTrades() {
            try {
                const response = await fetch('/api/trades');
                const trades = await response.json();
                
                const tbody = document.getElementById('trades-tbody');
                
                if (trades.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; opacity: 0.7;">No trades yet</td></tr>';
                    return;
                }
                
                tbody.innerHTML = trades.slice(0, 10).map(trade => {
                    const time = new Date(trade.timestamp).toLocaleString('en-GB');
                    const profitClass = trade.profit_loss > 0 ? 'profit-positive' : 'profit-negative';
                    
                    return `
                        <tr>
                            <td>${time}</td>
                            <td>${trade.symbol || 'N/A'}</td>
                            <td>${trade.side || 'N/A'}</td>
                            <td>${trade.amount || 'N/A'}</td>
                            <td>${trade.price || 'N/A'}</td>
                            <td class="${profitClass}">£${(trade.profit_loss || 0).toFixed(2)}</td>
                        </tr>
                    `;
                }).join('');
            } catch (error) {
                console.error('Error loading trades:', error);
            }
        }
        
        // Initialize dashboard
        connectWebSocket();
        loadTrades();
        
        // Refresh trades every minute
        setInterval(loadTrades, 60000);
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def start_background_tasks(self):
        """Start background tasks for metrics broadcasting"""
        while True:
            try:
                await self.broadcast_metrics()
                await asyncio.sleep(30)  # Broadcast every 30 seconds
            except Exception as e:
                self.logger.error(f"Background task error: {e}")
                await asyncio.sleep(30)

async def create_app():
    """Create and configure the web application"""
    dashboard = EnhancedDashboard()
    await dashboard.initialize()
    
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Routes
    app.router.add_get('/', dashboard.dashboard_handler)
    app.router.add_get('/ws', dashboard.websocket_handler)
    app.router.add_get('/api/metrics', dashboard.metrics_handler)
    app.router.add_get('/api/trades', dashboard.trades_handler)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    # Start background tasks
    asyncio.create_task(dashboard.start_background_tasks())
    
    return app

async def run_enhanced_dashboard():
    """Run the enhanced dashboard"""
    try:
        app = await create_app()
        
        print("🇬🇧 ENHANCED UK CRYPTO TRADING DASHBOARD")
        print("=" * 50)
        print("🚀 Starting enhanced monitoring system...")
        print(f"🌐 Dashboard: http://localhost:8080")
        print(f"📊 Real-time metrics and system health")
        print(f"💷 UK-optimized trading interface")
        print(f"⚡ WebSocket real-time updates")
        print("=" * 50)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        print("✅ Enhanced dashboard is running!")
        print("💡 Press Ctrl+C to stop")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down enhanced dashboard...")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_enhanced_dashboard())
