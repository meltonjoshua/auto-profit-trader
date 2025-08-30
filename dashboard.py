"""
Auto Profit Trader - Web Dashboard
Real-time monitoring and performance tracking
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import aiohttp
from aiohttp import web, web_response
from aiohttp.web import Application, Request, Response
import aiohttp_cors

import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from risk_management.portfolio_manager import PortfolioManager
from utils.config_manager import ConfigManager
from utils.logger import setup_logger


class TradingDashboard:
    """Web-based dashboard for monitoring trading performance"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.logger = setup_logger("dashboard")
        self.config_manager = ConfigManager()
        self.portfolio_manager = None
        self.app = None
        
    async def initialize(self):
        """Initialize dashboard components"""
        try:
            # Initialize portfolio manager (read-only for dashboard)
            self.portfolio_manager = PortfolioManager(self.config_manager)
            await asyncio.sleep(1)  # Give it time to initialize
            
            # Create web application
            self.app = web.Application()
            
            # Setup CORS for local development
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Routes
            self.app.router.add_get('/', self.dashboard_home)
            self.app.router.add_get('/api/performance', self.api_performance)
            self.app.router.add_get('/api/trades', self.api_trades)
            self.app.router.add_get('/api/status', self.api_status)
            # Only add static route if directory exists
            static_dir = Path(__file__).parent / 'static'
            if static_dir.exists():
                self.app.router.add_static('/static', static_dir)
            
            # Add CORS to all routes
            for route in list(self.app.router.routes()):
                cors.add(route)
                
            self.logger.info(f"Dashboard initialized on port {self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {e}")
            raise
    
    async def dashboard_home(self, request: Request) -> Response:
        """Serve the main dashboard HTML"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    async def api_performance(self, request: Request) -> Response:
        """API endpoint for performance metrics"""
        try:
            if not self.portfolio_manager:
                return web.json_response({"error": "Portfolio manager not initialized"}, status=500)
                
            metrics = await self.portfolio_manager.get_performance_metrics()
            
            # Add additional calculated metrics
            metrics.update({
                "status": "running" if Path("trader.pid").exists() else "stopped",
                "last_updated": datetime.now().isoformat(),
                "daily_profit_formatted": f"${metrics['daily_profit']:.2f}",
                "total_profit_formatted": f"${metrics['total_profit']:.2f}",
                "win_rate_formatted": f"{metrics['win_rate']:.1f}%",
            })
            
            return web.json_response(metrics)
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_trades(self, request: Request) -> Response:
        """API endpoint for recent trades"""
        try:
            limit = int(request.query.get('limit', 50))
            trades = await self.portfolio_manager.get_trade_history(days=7, limit=limit)
            
            # Format trades for display
            formatted_trades = []
            for trade in trades:
                formatted_trades.append({
                    **trade,
                    "timestamp_formatted": datetime.fromisoformat(trade["timestamp"]).strftime("%m-%d %H:%M:%S"),
                    "profit_formatted": f"${trade['profit']:.2f}" if trade['profit'] != 0 else "N/A",
                    "profit_class": "profit-positive" if trade['profit'] > 0 else "profit-negative" if trade['profit'] < 0 else "profit-neutral"
                })
            
            return web.json_response(formatted_trades)
            
        except Exception as e:
            self.logger.error(f"Error getting trades: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_status(self, request: Request) -> Response:
        """API endpoint for system status"""
        try:
            # Check if trader is running
            trader_running = Path("trader.pid").exists()
            
            # Get recent log entries
            log_files = ["daemon.log", "trading_engine.log", "portfolio_manager.log"]
            recent_logs = []
            
            for log_file in log_files:
                log_path = Path("logs") / log_file
                if log_path.exists():
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_logs.extend(lines[-5:])  # Last 5 lines from each log
            
            # Sort by timestamp (assuming log format starts with timestamp)
            recent_logs.sort(reverse=True)
            recent_logs = recent_logs[:10]  # Keep only 10 most recent
            
            status = {
                "trader_running": trader_running,
                "dashboard_uptime": datetime.now().isoformat(),
                "recent_logs": [log.strip() for log in recent_logs],
                "database_size": self._get_database_size(),
                "log_files_count": len([f for f in Path("logs").glob("*.log") if f.exists()]),
            }
            
            return web.json_response(status)
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    def _get_database_size(self) -> str:
        """Get database file size"""
        try:
            db_path = Path("portfolio.db")
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            return "0 B"
        except Exception:
            return "Unknown"
    
    def _generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Profit Trader Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            min-height: 100vh;
        }
        
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin: 0 10px;
        }
        
        .status-running {
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        .status-stopped {
            background: #f44336;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-title {
            font-size: 1.1em;
            margin-bottom: 15px;
            opacity: 0.9;
        }
        
        .metric-value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .metric-subtext {
            font-size: 0.9em;
            opacity: 0.7;
        }
        
        .profit-positive {
            color: #4CAF50;
        }
        
        .profit-negative {
            color: #f44336;
        }
        
        .profit-neutral {
            color: #FFC107;
        }
        
        .trades-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .trades-table th,
        .trades-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .trades-table th {
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
        }
        
        .trades-table tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
        }
        
        .error {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid #f44336;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
        }
        
        .last-updated {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 0 10px;
        }
        
        .refresh-btn:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 Auto Profit Trader Dashboard</h1>
            <div id="status-indicators">
                <span class="status-badge status-stopped" id="trader-status">Loading...</span>
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
        </div>
        
        <div class="metrics-grid" id="metrics-grid">
            <div class="loading">Loading performance metrics...</div>
        </div>
        
        <div class="trades-section">
            <h2>📊 Recent Trades</h2>
            <div id="trades-content" class="loading">Loading recent trades...</div>
        </div>
        
        <div class="last-updated" id="last-updated">
            Dashboard started at: <span id="start-time"></span>
        </div>
    </div>

    <script>
        let updateInterval;
        
        async function fetchData(endpoint) {
            try {
                const response = await fetch(`/api/${endpoint}`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return await response.json();
            } catch (error) {
                console.error(`Error fetching ${endpoint}:`, error);
                return null;
            }
        }
        
        async function updatePerformanceMetrics() {
            const data = await fetchData('performance');
            const grid = document.getElementById('metrics-grid');
            
            if (!data) {
                grid.innerHTML = '<div class="error">Failed to load performance data</div>';
                return;
            }
            
            grid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-title">💰 Total Profit</div>
                    <div class="metric-value ${data.total_profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                        ${data.total_profit_formatted}
                    </div>
                    <div class="metric-subtext">Since inception</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">📈 Daily Profit</div>
                    <div class="metric-value ${data.daily_profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                        ${data.daily_profit_formatted}
                    </div>
                    <div class="metric-subtext">Today's performance</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">🎯 Win Rate</div>
                    <div class="metric-value">${data.win_rate_formatted}</div>
                    <div class="metric-subtext">${data.winning_trades}W / ${data.losing_trades}L</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">📊 Trade Volume</div>
                    <div class="metric-value">$${data.total_volume.toFixed(2)}</div>
                    <div class="metric-subtext">${data.total_trades} total trades</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">⏱️ Performance Rate</div>
                    <div class="metric-value">$${data.profit_per_hour.toFixed(2)}/hr</div>
                    <div class="metric-subtext">${data.trades_per_hour.toFixed(1)} trades/hr</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">🔥 Best/Worst Trade</div>
                    <div class="metric-value">
                        <span class="profit-positive">$${data.largest_win.toFixed(2)}</span> / 
                        <span class="profit-negative">$${data.largest_loss.toFixed(2)}</span>
                    </div>
                    <div class="metric-subtext">Highest gains/losses</div>
                </div>
            `;
        }
        
        async function updateTradesTable() {
            const data = await fetchData('trades?limit=20');
            const container = document.getElementById('trades-content');
            
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="error">No trades found or failed to load</div>';
                return;
            }
            
            const tableHTML = `
                <table class="trades-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Symbol</th>
                            <th>Action</th>
                            <th>Amount</th>
                            <th>Price</th>
                            <th>Profit</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(trade => `
                            <tr>
                                <td>${trade.timestamp_formatted}</td>
                                <td>${trade.symbol}</td>
                                <td>${trade.action.toUpperCase()}</td>
                                <td>${trade.amount}</td>
                                <td>$${trade.price}</td>
                                <td class="${trade.profit_class}">${trade.profit_formatted}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            container.innerHTML = tableHTML;
        }
        
        async function updateStatus() {
            const data = await fetchData('status');
            const statusElement = document.getElementById('trader-status');
            
            if (data && data.trader_running) {
                statusElement.textContent = '🟢 RUNNING';
                statusElement.className = 'status-badge status-running';
            } else {
                statusElement.textContent = '🔴 STOPPED';
                statusElement.className = 'status-badge status-stopped';
            }
        }
        
        async function refreshData() {
            await Promise.all([
                updatePerformanceMetrics(),
                updateTradesTable(),
                updateStatus()
            ]);
            
            document.getElementById('last-updated').innerHTML = 
                `Last updated: ${new Date().toLocaleString()}`;
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('start-time').textContent = new Date().toLocaleString();
            
            // Initial load
            refreshData();
            
            // Auto-refresh every 30 seconds
            updateInterval = setInterval(refreshData, 30000);
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            if (updateInterval) clearInterval(updateInterval);
        });
    </script>
</body>
</html>
        """
    
    async def start_server(self):
        """Start the dashboard web server"""
        try:
            await self.initialize()
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, 'localhost', self.port)
            await site.start()
            
            print(f"""
🌟 =============================================== 🌟
🚀 AUTO PROFIT TRADER DASHBOARD STARTED! 🚀
🌟 =============================================== 🌟

📊 Access your dashboard at: http://localhost:{self.port}

✨ Features Available:
   💰 Real-time profit/loss tracking
   📈 Performance metrics & statistics  
   📊 Recent trades history
   🎯 Win/loss rate monitoring
   ⏱️ Live system status
   🔄 Auto-refresh every 30 seconds

🛑 Press Ctrl+C to stop the dashboard
            """)
            
            # Keep the server running
            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                self.logger.info("Dashboard shutdown requested")
            finally:
                await runner.cleanup()
                
        except Exception as e:
            self.logger.error(f"Failed to start dashboard server: {e}")
            raise


async def main():
    """Main dashboard entry point"""
    dashboard = TradingDashboard(port=8080)
    await dashboard.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
