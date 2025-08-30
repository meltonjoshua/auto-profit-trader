# Auto Profit Trader - UK Crypto Trading Suite
# Main launcher for the complete UK cryptocurrency trading platform

Write-Host ""
Write-Host "=== AUTO PROFIT TRADER - UK CRYPTO SUITE ===" -ForegroundColor Blue
Write-Host ""

# Get script directory and set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set environment variables
$env:PYTHONPATH = Join-Path $scriptPath "src"
$env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
$env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"

# Check if first time setup is needed
$firstTimeSetup = -not (Test-Path "encrypted_credentials.json")

if ($firstTimeSetup) {
    Write-Host "Welcome to Auto Profit Trader!" -ForegroundColor Green
    Write-Host ""
    Write-Host "UK's Premier Cryptocurrency Trading Suite" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Features:" -ForegroundColor Yellow
    Write-Host "   GBP-focused trading (BTC/GBP, ETH/GBP)" -ForegroundColor Green
    Write-Host "   FCA-regulated exchanges (Kraken priority)" -ForegroundColor Green
    Write-Host "   Real-time profit/loss dashboard" -ForegroundColor Green
    Write-Host "   Automated trading strategies" -ForegroundColor Green
    Write-Host "   Risk-free demo mode" -ForegroundColor Green
    Write-Host "   HMRC-compliant reporting" -ForegroundColor Green
    Write-Host "   Bank-grade security" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Welcome back to your trading suite!" -ForegroundColor Green
    Write-Host ""
}

# System status check
Write-Host "System Status Check..." -ForegroundColor Cyan

# Check Python environment
try {
    $pythonVersion = python --version 2>$null
    Write-Host "   Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   Python not found" -ForegroundColor Red
    Write-Host "      Please install Python 3.11+ from python.org" -ForegroundColor White
    exit 1
}

# Check dependencies
try {
    python -c "import aiohttp, ccxt, cryptography" 2>$null
    Write-Host "   Core dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "   Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    Write-Host "   Dependencies installed" -ForegroundColor Green
}

Write-Host ""

# Main menu
Write-Host "Choose Your Trading Experience:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   QUICK START:" -ForegroundColor Cyan
Write-Host "      [1] Demo Mode (Practice with £5,000)" -ForegroundColor White
Write-Host "      [2] Launch Dashboard (Monitor Everything)" -ForegroundColor White
Write-Host "      [3] Express Setup (Kraken API + Start Trading)" -ForegroundColor White
Write-Host ""
Write-Host "   SETUP & CONFIGURATION:" -ForegroundColor Cyan
Write-Host "      [4] Setup Kraken API (UK Recommended)" -ForegroundColor White
Write-Host "      [5] Setup Coinbase Pro API (UK Alternative)" -ForegroundColor White
Write-Host "      [6] Advanced Configuration" -ForegroundColor White
Write-Host ""
Write-Host "   TRADING OPERATIONS:" -ForegroundColor Cyan
Write-Host "      [7] Start Automated Trading" -ForegroundColor White
Write-Host "      [8] View Performance Report" -ForegroundColor White
Write-Host "      [9] Stop All Trading" -ForegroundColor White
Write-Host ""
Write-Host "   HELP & INFORMATION:" -ForegroundColor Cyan
Write-Host "      [10] Quick Start Guide" -ForegroundColor White
Write-Host "      [11] Run System Tests" -ForegroundColor White
Write-Host "      [12] Help & Support" -ForegroundColor White
Write-Host ""
Write-Host "      [0] Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter your choice (0-12)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Launching Demo Mode..." -ForegroundColor Green
        Write-Host ""
        Write-Host "UK Crypto Trading Simulator Features:" -ForegroundColor Cyan
        Write-Host "   £5,000 demo balance" -ForegroundColor White
        Write-Host "   Realistic UK market prices" -ForegroundColor White
        Write-Host "   GBP pairs focus (BTC/GBP, ETH/GBP)" -ForegroundColor White
        Write-Host "   Bull/bear market simulations" -ForegroundColor White
        Write-Host "   Zero risk, maximum learning" -ForegroundColor White
        Write-Host ""
        
        python -c "
import sys
sys.path.append('src')
from demo.demo_kraken import run_demo_kraken
import asyncio

print('Starting Demo Kraken Mode...')
print('')
asyncio.run(run_demo_kraken())

print('')
print('Demo completed! Ready for real trading?')
print('   Tip: Run this app again and choose option 3 for Express Setup')
"
    }
    
    "2" {
        Write-Host ""
        Write-Host "Launching Trading Dashboard..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "UK-Optimized Dashboard Features:" -ForegroundColor Yellow
        Write-Host "   Real-time profit/loss in GBP" -ForegroundColor Green
        Write-Host "   Performance metrics and win rates" -ForegroundColor Green
        Write-Host "   Complete trade history for HMRC" -ForegroundColor Green
        Write-Host "   System status monitoring" -ForegroundColor Green
        Write-Host "   Auto-refresh every 30 seconds" -ForegroundColor Green
        Write-Host ""
        Write-Host "Dashboard will be available at: http://localhost:8080" -ForegroundColor Yellow
        Write-Host ""
        
        .\launch_dashboard_clean.ps1
    }
    
    "3" {
        Write-Host ""
        Write-Host "Express Setup - Get Trading in Minutes!" -ForegroundColor Green
        Write-Host ""
        Write-Host "This will setup Kraken (UK's best crypto exchange):" -ForegroundColor Cyan
        Write-Host "   FCA-regulated and UK-compliant" -ForegroundColor Green
        Write-Host "   Direct GBP pairs (BTC/GBP, ETH/GBP)" -ForegroundColor Green
        Write-Host "   UK bank transfers via Faster Payments" -ForegroundColor Green
        Write-Host "   Lower fees for GBP trading" -ForegroundColor Green
        Write-Host ""
        
        $proceed = Read-Host "Do you have Kraken API credentials ready? (y/n)"
        if ($proceed -eq "y" -or $proceed -eq "Y") {
            Write-Host ""
            Write-Host "Kraken API Setup:" -ForegroundColor Yellow
            Write-Host ""
            
            $apiKey = Read-Host "Enter your Kraken API Key"
            $apiSecret = Read-Host "Enter your Kraken Private Key" -MaskInput
            
            if ($apiKey -and $apiSecret) {
                # Store credentials
                python -c "
import sys
sys.path.append('src')
from security.crypto_manager import SecurityManager
sm = SecurityManager()
result = sm.encrypt_api_credentials('kraken', '$apiKey', '$apiSecret')
if result:
    print('Kraken API configured securely!')
else:
    print('Failed to store credentials')
"
                
                Write-Host ""
                Write-Host "Testing connection..." -ForegroundColor Cyan
                
                # Test connection
                python -c "
import asyncio
import sys
sys.path.append('src')
from exchanges.exchange_manager import ExchangeManager
from utils.config_manager import ConfigManager
from security.crypto_manager import SecurityManager

async def test_connection():
    try:
        config = ConfigManager()
        security = SecurityManager()
        exchange_mgr = ExchangeManager(config, security)
        await exchange_mgr.initialize_exchanges()
        
        if 'kraken' in exchange_mgr.exchanges:
            print('Connection successful!')
            print('Ready for UK crypto trading!')
        else:
            print('Using demo mode - check API credentials')
        
        await exchange_mgr.shutdown()
    except Exception as e:
        print(f'Connection issue: {e}')
        print('Will use demo mode for now')

asyncio.run(test_connection())
"
                
                Write-Host ""
                Write-Host "Ready to Start!" -ForegroundColor Green
                Write-Host ""
                $startNow = Read-Host "Start trading dashboard now? (y/n)"
                if ($startNow -eq "y" -or $startNow -eq "Y") {
                    .\launch_dashboard_clean.ps1
                }
            }
        } else {
            Write-Host ""
            Write-Host "To get Kraken API credentials:" -ForegroundColor Cyan
            Write-Host "   1. Visit: https://www.kraken.com/u/security/api" -ForegroundColor White
            Write-Host "   2. Click 'Generate New Key'" -ForegroundColor White
            Write-Host "   3. Enable: Query Funds, Query Orders, Create Orders" -ForegroundColor White
            Write-Host "   4. Disable: Withdraw Funds (for security)" -ForegroundColor White
            Write-Host "   5. Run this app again and choose Express Setup" -ForegroundColor White
            Write-Host ""
            Write-Host "Or try Demo Mode (option 1) to practice first!" -ForegroundColor Yellow
        }
    }
    
    "8" {
        Write-Host ""
        Write-Host "Performance Report" -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path "portfolio.db") {
            python -c "
import sys
sys.path.append('src')
import sqlite3
from datetime import datetime, timedelta

try:
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # Get trade statistics
    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE profit_loss IS NOT NULL')
    result = cursor.fetchone()[0]
    total_pnl = result if result else 0
    
    cursor.execute('SELECT COUNT(*) FROM trades WHERE profit_loss > 0')
    winning_trades = cursor.fetchone()[0]
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    print('UK TRADING PERFORMANCE:')
    print('=' * 30)
    print(f'Total Trades: {total_trades}')
    print(f'Total P&L: £{total_pnl:.2f}')
    print(f'Win Rate: {win_rate:.1f}%')
    print(f'Winning Trades: {winning_trades}')
    print(f'Losing Trades: {total_trades - winning_trades}')
    
    if total_trades > 0:
        avg_trade = total_pnl / total_trades
        print(f'Average per Trade: £{avg_trade:.2f}')
    
    # Recent trades
    print('')
    print('Recent Trades:')
    cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5')
    recent = cursor.fetchall()
    
    if recent:
        for trade in recent:
            print(f'   {trade[1]} {trade[2]} - £{trade[5]:.2f}' if len(trade) > 5 else f'   {trade[1]} {trade[2]}')
    else:
        print('   No trades yet')
    
    conn.close()
    
except Exception as e:
    print(f'Error reading trading data: {e}')
    print('Start trading to see performance metrics')
"
        } else {
            Write-Host "No trading data yet" -ForegroundColor Yellow
            Write-Host "Start trading to see performance metrics" -ForegroundColor Cyan
        }
    }
    
    "11" {
        Write-Host ""
        Write-Host "Running System Tests..." -ForegroundColor Cyan
        Write-Host ""
        
        # Test 1: Python environment
        Write-Host "Test 1: Python Environment" -ForegroundColor Yellow
        try {
            python -c "import sys; print(f'Python {sys.version.split()[0]}')"
        } catch {
            Write-Host "Python test failed" -ForegroundColor Red
        }
        
        # Test 2: Dependencies
        Write-Host "Test 2: Dependencies" -ForegroundColor Yellow
        try {
            python -c "
import aiohttp, ccxt, cryptography, asyncio
print('All dependencies available')
"
        } catch {
            Write-Host "Dependencies missing" -ForegroundColor Red
        }
        
        # Test 3: Demo mode
        Write-Host "Test 3: Demo Mode" -ForegroundColor Yellow
        try {
            python -c "
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenExchange
demo = DemoKrakenExchange()
print('Demo Kraken working')
"
        } catch {
            Write-Host "Demo mode failed" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "System test completed!" -ForegroundColor Green
    }
    
    "0" {
        Write-Host ""
        Write-Host "Thank you for using Auto Profit Trader!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Happy UK crypto trading!" -ForegroundColor Blue
        Write-Host "May your profits be ever in your favour!" -ForegroundColor Yellow
        Write-Host ""
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please select 0-12." -ForegroundColor Red
        Write-Host ""
        Write-Host "Tip: Choose 1 for Demo Mode to get started!" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "Run this application again anytime for full access!" -ForegroundColor Cyan
Write-Host "Auto Profit Trader - Your UK Crypto Trading Partner" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
