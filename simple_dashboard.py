"""
Simple Auto Profit Trader Dashboard
Basic real-time monitoring for UK crypto trading
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from aiohttp import web
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_dashboard")

class SimpleDashboard:
    def __init__(self):
        self.start_time = datetime.now()
        
    async def get_trading_stats(self):
        """Get basic trading statistics"""
        try:
            if not Path('portfolio.db').exists():
                return {
                    'total_trades': 0,
                    'total_profit': 0.0,
                    'today_trades': 0,
                    'today_profit': 0.0,
                    'win_rate': 0.0
                }
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            # Total statistics
            cursor.execute('SELECT COUNT(*) FROM trades')
            total_trades = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE profit_loss IS NOT NULL')
            result = cursor.fetchone()[0]
            total_profit = float(result) if result else 0.0
            
            cursor.execute('SELECT COUNT(*) FROM trades WHERE profit_loss > 0')
            winning_trades = cursor.fetchone()[0] or 0
            
            # Today's statistics
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = ?', (today,))
            today_trades = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE DATE(timestamp) = ? AND profit_loss IS NOT NULL', (today,))
            result = cursor.fetchone()[0]
            today_profit = float(result) if result else 0.0
            
            # Calculate win rate
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
            
            conn.close()
            
            return {
                'total_trades': total_trades,
                'total_profit': total_profit,
                'today_trades': today_trades,
                'today_profit': today_profit,
                'win_rate': win_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting trading stats: {e}")
            return {
                'total_trades': 0,
                'total_profit': 0.0,
                'today_trades': 0,
                'today_profit': 0.0,
                'win_rate': 0.0
            }
    
    async def get_recent_trades(self, limit=10):
        """Get recent trades"""
        try:
            if not Path('portfolio.db').exists():
                return []
                
            conn = sqlite3.connect('portfolio.db')
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT symbol, side, amount, price, profit_loss, timestamp FROM trades ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            trades = cursor.fetchall()
            conn.close()
            
            trade_list = []
            for trade in trades:
                if len(trade) >= 6:
                    trade_list.append({
                        'symbol': trade[0],
                        'side': trade[1],
                        'amount': trade[2],
                        'price': trade[3],
                        'profit_loss': trade[4],
                        'timestamp': trade[5]
                    })
            
            return trade_list
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []
    
    async def api_stats(self, request):
        """API endpoint for trading statistics"""
        stats = await self.get_trading_stats()
        return web.json_response(stats)
    
    async def api_trades(self, request):
        """API endpoint for recent trades"""
        trades = await self.get_recent_trades()
        return web.json_response(trades)
    
    async def dashboard_handler(self, request):
        """Serve the dashboard HTML"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇬🇧 Auto Profit Trader Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { font-size: 1.2em; opacity: 0.8; }
        
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { opacity: 0.8; }
        
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
        }
        
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
        }
        .refresh-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🇬🇧 Auto Profit Trader</h1>
            <p class="subtitle">UK Cryptocurrency Trading Dashboard</p>
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-profit">£0.00</div>
                <div class="stat-label">Total Profit</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="total-trades">0</div>
                <div class="stat-label">Total Trades</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="today-profit">£0.00</div>
                <div class="stat-label">Today's Profit</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="today-trades">0</div>
                <div class="stat-label">Today's Trades</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="win-rate">0%</div>
                <div class="stat-label">Win Rate</div>
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
                        <td colspan="6" style="text-align: center; opacity: 0.7;">Loading...</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="last-update">
            Last updated: <span id="last-update">Never</span>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('total-profit').textContent = `£${stats.total_profit.toFixed(2)}`;
                document.getElementById('total-trades').textContent = stats.total_trades;
                document.getElementById('today-profit').textContent = `£${stats.today_profit.toFixed(2)}`;
                document.getElementById('today-trades').textContent = stats.today_trades;
                document.getElementById('win-rate').textContent = `${stats.win_rate.toFixed(1)}%`;
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
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
                
                tbody.innerHTML = trades.map(trade => {
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
        
        async function loadData() {
            await loadStats();
            await loadTrades();
            document.getElementById('last-update').textContent = new Date().toLocaleString('en-GB');
        }
        
        // Load data initially
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')

async def create_simple_app():
    """Create the simple dashboard application"""
    dashboard = SimpleDashboard()
    
    app = web.Application()
    
    # Routes
    app.router.add_get('/', dashboard.dashboard_handler)
    app.router.add_get('/api/stats', dashboard.api_stats)
    app.router.add_get('/api/trades', dashboard.api_trades)
    
    return app

async def run_simple_dashboard():
    """Run the simple dashboard"""
    try:
        app = await create_simple_app()
        
        print("🇬🇧 AUTO PROFIT TRADER - SIMPLE DASHBOARD")
        print("=" * 45)
        print("🚀 Starting UK crypto trading dashboard...")
        print(f"🌐 Dashboard: http://localhost:8080")
        print(f"💷 Real-time UK trading metrics")
        print("=" * 45)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        print("✅ Dashboard is running!")
        print("💡 Press Ctrl+C to stop")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard...")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

if __name__ == "__main__":
    asyncio.run(run_simple_dashboard())
