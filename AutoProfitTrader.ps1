# 🇬🇧 Auto Profit Trader - Ultimate UK Crypto Trading Suite
# Your complete cryptocurrency trading solution optimized for the United Kingdom

Write-Host ""
Write-Host "💷 ============================================== 💷" -ForegroundColor Blue
Write-Host "    AUTO PROFIT TRADER - UK CRYPTO SUITE" -ForegroundColor Blue  
Write-Host "💷 ============================================== 💷" -ForegroundColor Blue
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
    Write-Host "🎉 WELCOME TO AUTO PROFIT TRADER!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🇬🇧 UK's Premier Cryptocurrency Trading Suite" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✨ WHAT YOU GET:" -ForegroundColor Yellow
    Write-Host "   💷 GBP-focused trading (BTC/GBP, ETH/GBP)" -ForegroundColor Green
    Write-Host "   🏦 FCA-regulated exchanges (Kraken priority)" -ForegroundColor Green
    Write-Host "   📊 Real-time profit/loss dashboard" -ForegroundColor Green
    Write-Host "   🤖 Automated trading strategies" -ForegroundColor Green
    Write-Host "   🎮 Risk-free demo mode" -ForegroundColor Green
    Write-Host "   📋 HMRC-compliant reporting" -ForegroundColor Green
    Write-Host "   🛡️ Bank-grade security" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "🇬🇧 WELCOME BACK TO YOUR TRADING SUITE!" -ForegroundColor Green
    Write-Host ""
}

# System status check
Write-Host "🔍 SYSTEM STATUS CHECK..." -ForegroundColor Cyan

# Check Python environment
try {
    $pythonVersion = python --version 2>$null
    Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found" -ForegroundColor Red
    Write-Host "      Please install Python 3.11+ from python.org" -ForegroundColor White
    exit 1
}

# Check dependencies
try {
    python -c "import aiohttp, ccxt, cryptography" 2>$null
    Write-Host "   ✅ Core dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "   📦 Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
}

# Check API credentials
if (Test-Path "encrypted_credentials.json") {
    try {
        python -c "
import sys
sys.path.append('src')
from security.crypto_manager import SecurityManager
sm = SecurityManager()
exchanges = sm.list_stored_exchanges()
if exchanges:
    print(f'   ✅ API credentials: {len(exchanges)} exchange(s) configured')
else:
    print('   ⚠️  No API credentials configured')
" 2>$null
    } catch {
        Write-Host "   ⚠️  API credentials status unknown" -ForegroundColor Yellow
    }
} else {
    Write-Host "   📝 No API credentials yet (demo mode available)" -ForegroundColor Yellow
}

# Check portfolio database
if (Test-Path "portfolio.db") {
    Write-Host "   ✅ Trading database found" -ForegroundColor Green
} else {
    Write-Host "   📊 Trading database will be created on first trade" -ForegroundColor Yellow
}

Write-Host ""

# Main menu
Write-Host "🚀 CHOOSE YOUR TRADING EXPERIENCE:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   🎯 QUICK START:" -ForegroundColor Cyan
Write-Host "      [1] 🎮 Demo Mode (Practice with £5,000)" -ForegroundColor White
Write-Host "      [2] 📊 Launch Dashboard (Monitor Everything)" -ForegroundColor White
Write-Host "      [3] ⚡ Express Setup (Kraken API + Start Trading)" -ForegroundColor White
Write-Host ""
Write-Host "   🔧 SETUP & CONFIGURATION:" -ForegroundColor Cyan
Write-Host "      [4] 🇬🇧 Setup Kraken API (UK Recommended)" -ForegroundColor White
Write-Host "      [5] 🔵 Setup Coinbase Pro API (UK Alternative)" -ForegroundColor White
Write-Host "      [6] ⚙️  Advanced Configuration" -ForegroundColor White
Write-Host ""
Write-Host "   🤖 TRADING OPERATIONS:" -ForegroundColor Cyan
Write-Host "      [7] 🚀 Start Automated Trading" -ForegroundColor White
Write-Host "      [8] 📈 View Performance Report" -ForegroundColor White
Write-Host "      [9] 🛑 Stop All Trading" -ForegroundColor White
Write-Host ""
Write-Host "   📚 HELP & INFORMATION:" -ForegroundColor Cyan
Write-Host "      [10] 📖 Quick Start Guide" -ForegroundColor White
Write-Host "      [11] 🧪 Run System Tests" -ForegroundColor White
Write-Host "      [12] 🆘 Help & Support" -ForegroundColor White
Write-Host ""
Write-Host "      [0] Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter your choice (0-12)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🎮 LAUNCHING DEMO MODE..." -ForegroundColor Green
        Write-Host ""
        Write-Host "🇬🇧 UK Crypto Trading Simulator Features:" -ForegroundColor Cyan
        Write-Host "   💷 £5,000 demo balance" -ForegroundColor White
        Write-Host "   📊 Realistic UK market prices" -ForegroundColor White
        Write-Host "   🏦 GBP pairs focus (BTC/GBP, ETH/GBP)" -ForegroundColor White
        Write-Host "   📈 Bull/bear market simulations" -ForegroundColor White
        Write-Host "   🎯 Zero risk, maximum learning" -ForegroundColor White
        Write-Host ""
        
        python -c "
import sys
sys.path.append('src')
from demo.demo_kraken import run_demo_kraken
import asyncio

print('🎮 STARTING DEMO KRAKEN MODE...')
print('')
asyncio.run(run_demo_kraken())

print('')
print('🎓 Demo completed! Ready for real trading?')
print('   💡 Tip: Run this app again and choose option 3 for Express Setup')
"
    }
    
    "2" {
        Write-Host ""
        Write-Host "📊 LAUNCHING TRADING DASHBOARD..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🇬🇧 UK-Optimized Dashboard Features:" -ForegroundColor Yellow
        Write-Host "   💷 Real-time profit/loss in GBP" -ForegroundColor Green
        Write-Host "   📈 Performance metrics and win rates" -ForegroundColor Green
        Write-Host "   📋 Complete trade history for HMRC" -ForegroundColor Green
        Write-Host "   🎯 System status monitoring" -ForegroundColor Green
        Write-Host "   🔄 Auto-refresh every 30 seconds" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Dashboard will be available at: http://localhost:8080" -ForegroundColor Yellow
        Write-Host ""
        
        .\launch_dashboard.ps1
    }
    
    "3" {
        Write-Host ""
        Write-Host "⚡ EXPRESS SETUP - GET TRADING IN MINUTES!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🇬🇧 This will setup Kraken (UK's best crypto exchange):" -ForegroundColor Cyan
        Write-Host "   ✅ FCA-regulated and UK-compliant" -ForegroundColor Green
        Write-Host "   ✅ Direct GBP pairs (BTC/GBP, ETH/GBP)" -ForegroundColor Green
        Write-Host "   ✅ UK bank transfers via Faster Payments" -ForegroundColor Green
        Write-Host "   ✅ Lower fees for GBP trading" -ForegroundColor Green
        Write-Host ""
        
        $proceed = Read-Host "Do you have Kraken API credentials ready? (y/n)"
        if ($proceed -eq "y" -or $proceed -eq "Y") {
            Write-Host ""
            Write-Host "🔑 KRAKEN API SETUP:" -ForegroundColor Yellow
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
    print('✅ Kraken API configured securely!')
else:
    print('❌ Failed to store credentials')
"
                
                Write-Host ""
                Write-Host "🧪 Testing connection..." -ForegroundColor Cyan
                
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
            print('✅ Connection successful!')
            print('🇬🇧 Ready for UK crypto trading!')
        else:
            print('⚠️  Using demo mode - check API credentials')
        
        await exchange_mgr.shutdown()
    except Exception as e:
        print(f'⚠️  Connection issue: {e}')
        print('💡 Will use demo mode for now')

asyncio.run(test_connection())
"
                
                Write-Host ""
                Write-Host "🚀 READY TO START!" -ForegroundColor Green
                Write-Host ""
                $startNow = Read-Host "Start trading dashboard now? (y/n)"
                if ($startNow -eq "y" -or $startNow -eq "Y") {
                    .\launch_dashboard.ps1
                }
            }
        } else {
            Write-Host ""
            Write-Host "📖 To get Kraken API credentials:" -ForegroundColor Cyan
            Write-Host "   1. Visit: https://www.kraken.com/u/security/api" -ForegroundColor White
            Write-Host "   2. Click 'Generate New Key'" -ForegroundColor White
            Write-Host "   3. Enable: Query Funds, Query Orders, Create Orders" -ForegroundColor White
            Write-Host "   4. Disable: Withdraw Funds (for security)" -ForegroundColor White
            Write-Host "   5. Run this app again and choose Express Setup" -ForegroundColor White
            Write-Host ""
            Write-Host "💡 Or try Demo Mode (option 1) to practice first!" -ForegroundColor Yellow
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "🇬🇧 KRAKEN API SETUP (UK RECOMMENDED)" -ForegroundColor Green
        Write-Host ""
        .\setup_api.ps1
    }
    
    "5" {
        Write-Host ""
        Write-Host "🔵 COINBASE PRO API SETUP (UK ALTERNATIVE)" -ForegroundColor Blue
        Write-Host ""
        Write-Host "📖 Coinbase Pro Setup:" -ForegroundColor Cyan
        Write-Host "   1. Visit: https://pro.coinbase.com/profile/api" -ForegroundColor White
        Write-Host "   2. Click '+ New API Key'" -ForegroundColor White
        Write-Host "   3. Enable: View, Trade" -ForegroundColor White
        Write-Host "   4. Disable: Transfer" -ForegroundColor White
        Write-Host ""
        
        $apiKey = Read-Host "Enter your Coinbase Pro API Key"
        $apiSecret = Read-Host "Enter your Coinbase Pro Secret" -MaskInput
        
        if ($apiKey -and $apiSecret) {
            python -c "
import sys
sys.path.append('src')
from security.crypto_manager import SecurityManager
sm = SecurityManager()
result = sm.encrypt_api_credentials('coinbase', '$apiKey', '$apiSecret')
if result:
    print('✅ Coinbase Pro API configured!')
else:
    print('❌ Failed to store credentials')
"
        }
    }
    
    "6" {
        Write-Host ""
        Write-Host "⚙️ ADVANCED CONFIGURATION" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Configuration Options:" -ForegroundColor Cyan
        Write-Host "   [1] Edit trading parameters" -ForegroundColor White
        Write-Host "   [2] Risk management settings" -ForegroundColor White
        Write-Host "   [3] Notification setup" -ForegroundColor White
        Write-Host "   [4] View current config" -ForegroundColor White
        Write-Host ""
        
        $configChoice = Read-Host "Choose option (1-4)"
        
        switch ($configChoice) {
            "4" {
                Write-Host ""
                Write-Host "📋 CURRENT CONFIGURATION:" -ForegroundColor Cyan
                python -c "
import json
with open('config.json', 'r') as f:
    config = json.load(f)

print('💷 Trading Settings:')
trading = config.get('trading', {})
for key, value in trading.items():
    print(f'   {key}: {value}')

print('')
print('🏦 Exchanges:')
exchanges = config.get('exchanges', {})
for name, settings in exchanges.items():
    enabled = settings.get('enabled', False)
    uk_reg = settings.get('uk_regulated', False)
    status = '✅' if enabled else '❌'
    uk_status = '🇬🇧' if uk_reg else ''
    print(f'   {status} {name} {uk_status}')
"
            }
            default {
                Write-Host "Feature coming soon!" -ForegroundColor Yellow
            }
        }
    }
    
    "7" {
        Write-Host ""
        Write-Host "🚀 STARTING AUTOMATED TRADING..." -ForegroundColor Green
        Write-Host ""
        Write-Host "🇬🇧 UK Trading Configuration Active:" -ForegroundColor Cyan
        Write-Host "   🕐 London timezone (GMT/BST)" -ForegroundColor Green
        Write-Host "   💷 GBP base currency priority" -ForegroundColor Green
        Write-Host "   🏦 FCA-regulated exchanges first" -ForegroundColor Green
        Write-Host "   📊 Real-time monitoring enabled" -ForegroundColor Green
        Write-Host ""
        
        .\start_trader_windows.ps1
    }
    
    "8" {
        Write-Host ""
        Write-Host "📈 PERFORMANCE REPORT" -ForegroundColor Cyan
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
    
    print('💷 UK TRADING PERFORMANCE:')
    print('=' * 30)
    print(f'📊 Total Trades: {total_trades}')
    print(f'💰 Total P&L: £{total_pnl:.2f}')
    print(f'🎯 Win Rate: {win_rate:.1f}%')
    print(f'✅ Winning Trades: {winning_trades}')
    print(f'❌ Losing Trades: {total_trades - winning_trades}')
    
    if total_trades > 0:
        avg_trade = total_pnl / total_trades
        print(f'📈 Average per Trade: £{avg_trade:.2f}')
    
    # Recent trades
    print('')
    print('📋 Recent Trades:')
    cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5')
    recent = cursor.fetchall()
    
    if recent:
        for trade in recent:
            print(f'   {trade[1]} {trade[2]} - £{trade[5]:.2f}' if len(trade) > 5 else f'   {trade[1]} {trade[2]}')
    else:
        print('   No trades yet')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error reading trading data: {e}')
    print('💡 Start trading to see performance metrics')
"
        } else {
            Write-Host "📊 No trading data yet" -ForegroundColor Yellow
            Write-Host "💡 Start trading to see performance metrics" -ForegroundColor Cyan
        }
    }
    
    "9" {
        Write-Host ""
        Write-Host "🛑 STOPPING ALL TRADING OPERATIONS..." -ForegroundColor Red
        Write-Host ""
        
        try {
            Stop-Process -Name "python" -Force 2>$null
            Write-Host "✅ All trading processes stopped" -ForegroundColor Green
        } catch {
            Write-Host "ℹ️  No trading processes were running" -ForegroundColor Yellow
        }
        
        if (Test-Path "trader.pid") {
            Remove-Item "trader.pid"
            Write-Host "✅ Trading PID file removed" -ForegroundColor Green
        }
        
        Write-Host "🇬🇧 All UK trading operations halted safely" -ForegroundColor Green
    }
    
    "10" {
        Write-Host ""
        Write-Host "📖 QUICK START GUIDE" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🇬🇧 UK CRYPTO TRADING IN 3 STEPS:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "STEP 1: Practice (5 minutes)" -ForegroundColor Green
        Write-Host "   🎮 Choose option 1 (Demo Mode)" -ForegroundColor White
        Write-Host "   💷 Practice with £5,000 demo money" -ForegroundColor White
        Write-Host "   📊 Learn GBP pairs (BTC/GBP, ETH/GBP)" -ForegroundColor White
        Write-Host ""
        Write-Host "STEP 2: Setup (5 minutes)" -ForegroundColor Green  
        Write-Host "   🇬🇧 Get Kraken API from kraken.com/u/security/api" -ForegroundColor White
        Write-Host "   🔑 Choose option 3 (Express Setup)" -ForegroundColor White
        Write-Host "   ✅ Enter your API credentials" -ForegroundColor White
        Write-Host ""
        Write-Host "STEP 3: Trade (Ongoing)" -ForegroundColor Green
        Write-Host "   📊 Choose option 2 (Launch Dashboard)" -ForegroundColor White
        Write-Host "   🤖 Choose option 7 (Start Trading)" -ForegroundColor White
        Write-Host "   💰 Watch your £ profits grow!" -ForegroundColor White
        Write-Host ""
        Write-Host "🎯 BONUS TIPS:" -ForegroundColor Yellow
        Write-Host "   💡 Start with small amounts (£50-100)" -ForegroundColor Cyan
        Write-Host "   💡 Use testnet mode first (enabled by default)" -ForegroundColor Cyan
        Write-Host "   💡 Monitor via dashboard regularly" -ForegroundColor Cyan
        Write-Host "   💡 Enable notifications for trade alerts" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
    "11" {
        Write-Host ""
        Write-Host "🧪 RUNNING SYSTEM TESTS..." -ForegroundColor Cyan
        Write-Host ""
        
        # Test 1: Python environment
        Write-Host "Test 1: Python Environment" -ForegroundColor Yellow
        try {
            python -c "import sys; print(f'✅ Python {sys.version.split()[0]}')"
        } catch {
            Write-Host "❌ Python test failed" -ForegroundColor Red
        }
        
        # Test 2: Dependencies
        Write-Host "Test 2: Dependencies" -ForegroundColor Yellow
        try {
            python -c "
import aiohttp, ccxt, cryptography, asyncio
print('✅ All dependencies available')
"
        } catch {
            Write-Host "❌ Dependencies missing" -ForegroundColor Red
        }
        
        # Test 3: Demo mode
        Write-Host "Test 3: Demo Mode" -ForegroundColor Yellow
        try {
            python -c "
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenExchange
demo = DemoKrakenExchange()
print('✅ Demo Kraken working')
"
        } catch {
            Write-Host "❌ Demo mode failed" -ForegroundColor Red
        }
        
        # Test 4: Security
        Write-Host "Test 4: Security System" -ForegroundColor Yellow
        try {
            python -c "
import sys
sys.path.append('src')
from security.crypto_manager import SecurityManager
sm = SecurityManager()
print('✅ Security system working')
"
        } catch {
            Write-Host "❌ Security test failed" -ForegroundColor Red
        }
        
        # Test 5: Configuration
        Write-Host "Test 5: Configuration" -ForegroundColor Yellow
        if (Test-Path "config.json") {
            try {
                python -c "
import json
with open('config.json', 'r') as f:
    config = json.load(f)
print('✅ Configuration valid')
"
            } catch {
                Write-Host "❌ Configuration invalid" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Configuration file missing" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "🎯 System test completed!" -ForegroundColor Green
    }
    
    "12" {
        Write-Host ""
        Write-Host "🆘 HELP & SUPPORT" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📚 AVAILABLE RESOURCES:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📖 Documentation:" -ForegroundColor Green
        Write-Host "   • API_SETUP_GUIDE.md - Exchange API setup" -ForegroundColor White
        Write-Host "   • UK_TRADING_GUIDE.md - UK-specific trading guide" -ForegroundColor White
        Write-Host "   • DEMO_KRAKEN_GUIDE.md - Demo mode tutorial" -ForegroundColor White
        Write-Host "   • COMPLETE_SETUP_GUIDE.md - Full setup guide" -ForegroundColor White
        Write-Host ""
        Write-Host "🛠️ Tools:" -ForegroundColor Green
        Write-Host "   • setup_api.ps1 - API configuration wizard" -ForegroundColor White
        Write-Host "   • demo_kraken.ps1 - Demo trading mode" -ForegroundColor White
        Write-Host "   • launch_dashboard.ps1 - Trading dashboard" -ForegroundColor White
        Write-Host ""
        Write-Host "🇬🇧 UK-Specific Help:" -ForegroundColor Green
        Write-Host "   • Kraken: FCA-regulated, best for UK" -ForegroundColor White
        Write-Host "   • GBP pairs: BTC/GBP, ETH/GBP priority" -ForegroundColor White
        Write-Host "   • HMRC compliance: Built-in reporting" -ForegroundColor White
        Write-Host "   • Faster Payments: Direct UK banking" -ForegroundColor White
        Write-Host ""
        Write-Host "🚨 Common Issues:" -ForegroundColor Yellow
        Write-Host "   • Binance unavailable in UK? ✅ Use Kraken instead" -ForegroundColor White
        Write-Host "   • Connection errors? ✅ Check API credentials" -ForegroundColor White
        Write-Host "   • No trades showing? ✅ Enable live trading in config" -ForegroundColor White
        Write-Host "   • Dashboard not loading? ✅ Check port 8080" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Quick Fixes:" -ForegroundColor Cyan
        Write-Host "   1. Try demo mode first (option 1)" -ForegroundColor White
        Write-Host "   2. Run system tests (option 11)" -ForegroundColor White
        Write-Host "   3. Check configuration (option 6 → 4)" -ForegroundColor White
        Write-Host "   4. Restart the application" -ForegroundColor White
    }
    
    "0" {
        Write-Host ""
        Write-Host "👋 Thank you for using Auto Profit Trader!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🇬🇧 Happy UK crypto trading!" -ForegroundColor Blue
        Write-Host "💷 May your profits be ever in your favour!" -ForegroundColor Yellow
        Write-Host ""
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice. Please select 0-12." -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Tip: Choose 1 for Demo Mode to get started!" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "🔄 Run this application again anytime for full access!" -ForegroundColor Cyan
Write-Host "💷 Auto Profit Trader - Your UK Crypto Trading Partner" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
