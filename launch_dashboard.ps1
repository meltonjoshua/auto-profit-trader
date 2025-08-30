# Auto Profit Trader - Ultimate Dashboard Launcher
# This script handles all setup and launches your profit tracking dashboard

Write-Host ""
Write-Host "🚀 ======================================== 🚀" -ForegroundColor Green
Write-Host "    AUTO PROFIT TRADER DASHBOARD (UK)" -ForegroundColor Green
Write-Host "🚀 ======================================== 🚀" -ForegroundColor Green
Write-Host ""

# Get script directory and set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set all required environment variables
$env:PYTHONPATH = Join-Path $scriptPath "src"
$env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
$env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"

Write-Host "🔧 Setting up environment..." -ForegroundColor Cyan
Write-Host "   ✅ Python path configured" -ForegroundColor Green
Write-Host "   ✅ Protobuf warnings suppressed" -ForegroundColor Green

# Check if dependencies are installed
Write-Host ""
Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan

try {
    python -c "import aiohttp, aiohttp_cors" 2>$null
    Write-Host "   ✅ Dashboard dependencies ready" -ForegroundColor Green
} catch {
    Write-Host "   📥 Installing dashboard dependencies..." -ForegroundColor Yellow
    pip install aiohttp aiohttp-cors --quiet
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
}

# Check for database (indicates trader has been run)
if (Test-Path "portfolio.db") {
    Write-Host "   ✅ Portfolio database found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  No portfolio database found" -ForegroundColor Yellow
    Write-Host "      Dashboard will work but show no data until trader is run" -ForegroundColor White
}

# Check if trader is currently running
if (Test-Path "trader.pid") {
    Write-Host "   🟢 Trader status: RUNNING" -ForegroundColor Green
} else {
    Write-Host "   🔴 Trader status: STOPPED" -ForegroundColor Red
    Write-Host "      (You can start it with: .\start_trader_windows.ps1)" -ForegroundColor White
}

Write-Host ""
Write-Host "🌐 Starting dashboard server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Your dashboard will be available at:" -ForegroundColor Yellow
Write-Host "   🌍 http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard Features:" -ForegroundColor Yellow
Write-Host "   � Real-time profit/loss tracking (GBP focus)" -ForegroundColor White
Write-Host "   🇬🇧 UK-optimized exchange support (Kraken priority)" -ForegroundColor White
Write-Host "   📈 Performance metrics and win rates" -ForegroundColor White
Write-Host "   📋 Complete trade history for HMRC reporting" -ForegroundColor White
Write-Host "   🎯 System status monitoring" -ForegroundColor White
Write-Host "   🔄 Auto-refresh every 30 seconds" -ForegroundColor White
Write-Host "   📱 Mobile-friendly interface" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop the dashboard" -ForegroundColor Red
Write-Host ""

# Dashboard Options
Write-Host "🎛️ Dashboard Options:" -ForegroundColor Cyan
Write-Host "   [1] 🚀 Enhanced Dashboard (Full Features + System Monitoring)" -ForegroundColor White
Write-Host "   [2] 📱 Basic Dashboard (Lightweight)" -ForegroundColor White
Write-Host "   [3] 📊 Quick Analytics Report" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose dashboard (1-3, or press Enter for Enhanced)"

if ([string]::IsNullOrWhiteSpace($choice)) {
    $choice = "1"
}

# Start the dashboard
try {
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "🚀 Starting Enhanced Dashboard..." -ForegroundColor Green
            try {
                python enhanced_dashboard.py
            } catch {
                Write-Host "⚠️ Enhanced dashboard unavailable, starting simple dashboard..." -ForegroundColor Yellow
                python simple_dashboard.py
            }
        }
        "2" {
            Write-Host ""
            Write-Host "📱 Starting Simple Dashboard..." -ForegroundColor Blue
            python simple_dashboard.py
        }
        "3" {
            Write-Host ""
            Write-Host "📊 QUICK ANALYTICS REPORT" -ForegroundColor Purple
            Write-Host ("=" * 30)
            
            $analyticsScript = @"
import sys, os
sys.path.append('src')
import sqlite3
from datetime import datetime

try:
    if not os.path.exists('portfolio.db'):
        print('📊 No trading data available yet')
        print('💡 Start trading to see analytics')
        exit()
    
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute('SELECT COUNT(*), SUM(profit_loss), AVG(profit_loss) FROM trades WHERE profit_loss IS NOT NULL')
    total_trades, total_pnl, avg_pnl = cursor.fetchone()
    
    total_trades = total_trades or 0
    total_pnl = total_pnl or 0
    avg_pnl = avg_pnl or 0
    
    print(f'💷 TRADING PERFORMANCE:')
    print(f'   Total Trades: {total_trades}')
    print(f'   Total P&L: £{total_pnl:.2f}')
    if total_trades > 0:
        print(f'   Average per Trade: £{avg_pnl:.2f}')
    
    # Win rate
    cursor.execute('SELECT COUNT(*) FROM trades WHERE profit_loss > 0')
    winning_trades = cursor.fetchone()[0] or 0
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    print(f'   Win Rate: {win_rate:.1f}%')
    
    # Today
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*), SUM(profit_loss) FROM trades WHERE DATE(timestamp) = ?', (today,))
    today_trades, today_pnl = cursor.fetchone()
    today_trades = today_trades or 0
    today_pnl = today_pnl or 0
    
    print(f'')
    print(f'📅 TODAY: {today_trades} trades, £{today_pnl:.2f} P&L')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
"@
            
            python -c $analyticsScript
            Write-Host ""
            Write-Host "💡 For live dashboard, run this script again and choose option 1 or 2" -ForegroundColor Cyan
            Write-Host "Press any key to exit..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        default {
            Write-Host ""
            Write-Host "🚀 Starting Enhanced Dashboard..." -ForegroundColor Green
            python enhanced_dashboard.py
        }
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error starting dashboard: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting Tips:" -ForegroundColor Yellow
    Write-Host "   1. Make sure Python is installed and accessible" -ForegroundColor White
    Write-Host "   2. Try running: .\install.ps1" -ForegroundColor White
    Write-Host "   3. Ensure port 8080 is not in use by another application" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
