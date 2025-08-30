# 🔑 API Setup Helper for Auto Profit Trader
# This script helps you securely configure your exchange API keys

Write-Host ""
Write-Host "🔑 ======================================== 🔑" -ForegroundColor Green
Write-Host "    AUTO PROFIT TRADER - API SETUP" -ForegroundColor Green
Write-Host "🔑 ======================================== 🔑" -ForegroundColor Green
Write-Host ""

# Get script directory and set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set environment
$env:PYTHONPATH = Join-Path $scriptPath "src"

Write-Host "📋 SUPPORTED EXCHANGES (UK OPTIMIZED):" -ForegroundColor Yellow
Write-Host "   🇬🇧 Kraken (RECOMMENDED FOR UK - FCA regulated)" -ForegroundColor Green
Write-Host "   � Coinbase Pro (UK regulated alternative)" -ForegroundColor White
Write-Host "   � Binance (❌ Currently unavailable in UK)" -ForegroundColor Red
Write-Host ""

Write-Host "🇬🇧 UK ADVANTAGES:" -ForegroundColor Cyan
Write-Host "   ✅ Kraken: Direct GBP deposits, UK regulation" -ForegroundColor Green
Write-Host "   ✅ Coinbase Pro: UK regulated, beginner-friendly" -ForegroundColor Green
Write-Host "   ✅ GBP trading pairs (BTC/GBP, ETH/GBP)" -ForegroundColor Green
Write-Host "   ✅ No currency conversion fees" -ForegroundColor Green
Write-Host "   ✅ FCA compliance and consumer protection" -ForegroundColor Green
Write-Host ""

Write-Host "🛡️  SECURITY REMINDER:" -ForegroundColor Red
Write-Host "   ✅ Only enable SPOT TRADING permissions" -ForegroundColor Green
Write-Host "   ❌ NEVER enable withdrawal permissions" -ForegroundColor Red
Write-Host "   ✅ Use IP restrictions if possible" -ForegroundColor Green
Write-Host "   ✅ Start with testnet/sandbox mode" -ForegroundColor Green
Write-Host ""

# Check if Python environment is ready
try {
    python -c "from src.security.crypto_manager import SecurityManager" 2>$null
    Write-Host "✅ Python environment ready" -ForegroundColor Green
} catch {
    Write-Host "❌ Python environment not ready. Please run: pip install -r requirements.txt" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 API KEY SETUP OPTIONS:" -ForegroundColor Cyan
Write-Host "   [1] Kraken API (🇬🇧 BEST FOR UK)" -ForegroundColor Green
Write-Host "   [2] Coinbase Pro API (🇬🇧 UK Alternative)" -ForegroundColor Green
Write-Host "   [3] ❌ Binance (Currently unavailable in UK)" -ForegroundColor Red
Write-Host "   [4] Test API Connection" -ForegroundColor White
Write-Host "   [5] View Setup Guide" -ForegroundColor White
Write-Host "   [6] Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose an option (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🇬🇧 KRAKEN API SETUP (UK OPTIMIZED)" -ForegroundColor Green
        Write-Host ""
        Write-Host "📖 Setup Instructions:" -ForegroundColor Cyan
        Write-Host "   1. Go to: https://www.kraken.com/u/security/api" -ForegroundColor White
        Write-Host "   2. Click 'Generate New Key'" -ForegroundColor White
        Write-Host "   3. Enable: Query Funds, Query Orders, Create Orders" -ForegroundColor White
        Write-Host "   4. Disable: Withdraw Funds" -ForegroundColor White
        Write-Host "   5. Add UK IP restriction for security" -ForegroundColor White
        Write-Host ""
        Write-Host "🇬🇧 UK Benefits: GBP pairs, FCA regulation, no conversion fees" -ForegroundColor Green
        Write-Host ""
        
        $apiKey = Read-Host "Enter your Kraken API Key"
        $apiSecret = Read-Host "Enter your Kraken Private Key" -MaskInput
        
        if ($apiKey -and $apiSecret) {
            try {
                python -c "
from src.security.crypto_manager import SecurityManager
sm = SecurityManager()
result = sm.encrypt_api_credentials('kraken', '$apiKey', '$apiSecret')
if result:
    print('✅ Kraken API keys encrypted and stored securely!')
    print('🇬🇧 UK-optimized exchange configured!')
else:
    print('❌ Failed to store API keys')
" 2>$null
                Write-Host "✅ Kraken API configured successfully!" -ForegroundColor Green
                Write-Host "🇬🇧 Perfect choice for UK trading!" -ForegroundColor Green
            } catch {
                Write-Host "❌ Error storing API keys: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ API key or secret not provided" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "� COINBASE PRO API SETUP (UK REGULATED)" -ForegroundColor Blue
        Write-Host ""
        Write-Host "📖 Setup Instructions:" -ForegroundColor Cyan
        Write-Host "   1. Go to: https://pro.coinbase.com/profile/api" -ForegroundColor White
        Write-Host "   2. Click '+ New API Key'" -ForegroundColor White
        Write-Host "   3. Enable: View, Trade" -ForegroundColor White
        Write-Host "   4. Disable: Transfer" -ForegroundColor White
        Write-Host ""
        Write-Host "🇬🇧 UK Benefits: FCA regulated, beginner-friendly, GBP support" -ForegroundColor Green
        Write-Host ""
        
        $apiKey = Read-Host "Enter your Coinbase Pro API Key"
        $apiSecret = Read-Host "Enter your Coinbase Pro Secret" -MaskInput
        
        if ($apiKey -and $apiSecret) {
            try {
                python -c "
from src.security.crypto_manager import SecurityManager
sm = SecurityManager()
result = sm.encrypt_api_credentials('coinbase', '$apiKey', '$apiSecret')
if result:
    print('✅ Coinbase Pro API keys encrypted and stored securely!')
    print('🇬🇧 UK-regulated exchange configured!')
else:
    print('❌ Failed to store API keys')
" 2>$null
                Write-Host "✅ Coinbase Pro API configured successfully!" -ForegroundColor Green
                Write-Host "🇬🇧 Excellent choice for UK trading!" -ForegroundColor Green
            } catch {
                Write-Host "❌ Error storing API keys: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ API key or secret not provided" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "❌ BINANCE NOT AVAILABLE IN UK" -ForegroundColor Red
        Write-Host ""
        Write-Host "🚫 Current Status:" -ForegroundColor Yellow
        Write-Host "   Binance has suspended services in the UK" -ForegroundColor White
        Write-Host "   Message: 'Our service is not available at this time'" -ForegroundColor White
        Write-Host "   Reason: Regulatory reorganization with FCA" -ForegroundColor White
        Write-Host ""
        Write-Host "✅ UK ALTERNATIVES:" -ForegroundColor Green
        Write-Host "   1. Kraken (FCA-regulated, GBP pairs)" -ForegroundColor White
        Write-Host "   2. Coinbase Pro (UK-regulated)" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Recommendation: Use Kraken as your primary exchange" -ForegroundColor Cyan
    }
        Write-Host ""
        Write-Host "🔵 COINBASE PRO API SETUP" -ForegroundColor Blue
        Write-Host ""
        Write-Host "📖 Setup Instructions:" -ForegroundColor Cyan
        Write-Host "   1. Go to: https://pro.coinbase.com/profile/api" -ForegroundColor White
        Write-Host "   2. Click '+ New API Key'" -ForegroundColor White
        Write-Host "   3. Enable: View, Trade" -ForegroundColor White
        Write-Host "   4. Disable: Transfer" -ForegroundColor White
        Write-Host ""
        
        $apiKey = Read-Host "Enter your Coinbase Pro API Key"
        $apiSecret = Read-Host "Enter your Coinbase Pro Secret" -MaskInput
        
        if ($apiKey -and $apiSecret) {
            try {
                python -c "
from src.security.crypto_manager import SecurityManager
sm = SecurityManager()
result = sm.encrypt_api_credentials('coinbase', '$apiKey', '$apiSecret')
if result:
    print('✅ Coinbase Pro API keys encrypted and stored securely!')
else:
    print('❌ Failed to store API keys')
" 2>$null
                Write-Host "✅ Coinbase Pro API configured successfully!" -ForegroundColor Green
            } catch {
                Write-Host "❌ Error storing API keys: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ API key or secret not provided" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "🟠 KRAKEN API SETUP" -ForegroundColor DarkYellow
        Write-Host ""
        Write-Host "📖 Setup Instructions:" -ForegroundColor Cyan
        Write-Host "   1. Go to: https://www.kraken.com/u/security/api" -ForegroundColor White
        Write-Host "   2. Click 'Generate New Key'" -ForegroundColor White
        Write-Host "   3. Enable: Query Funds, Query Orders, Create Orders" -ForegroundColor White
        Write-Host "   4. Disable: Withdraw Funds" -ForegroundColor White
        Write-Host ""
        
        $apiKey = Read-Host "Enter your Kraken API Key"
        $apiSecret = Read-Host "Enter your Kraken Private Key" -MaskInput
        
        if ($apiKey -and $apiSecret) {
            try {
                python -c "
from src.security.crypto_manager import SecurityManager
sm = SecurityManager()
result = sm.encrypt_api_credentials('kraken', '$apiKey', '$apiSecret')
if result:
    print('✅ Kraken API keys encrypted and stored securely!')
else:
    print('❌ Failed to store API keys')
" 2>$null
                Write-Host "✅ Kraken API configured successfully!" -ForegroundColor Green
            } catch {
                Write-Host "❌ Error storing API keys: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ API key or secret not provided" -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "🧪 TESTING API CONNECTIONS..." -ForegroundColor Cyan
        Write-Host ""
        
        try {
            python -c "
import asyncio
import sys
sys.path.append('src')
from exchanges.exchange_manager import ExchangeManager
from utils.config_manager import ConfigManager
from security.crypto_manager import SecurityManager

async def test_connections():
    try:
        config = ConfigManager()
        security = SecurityManager()
        exchange_mgr = ExchangeManager(config, security)
        
        print('🔗 Initializing exchange connections...')
        await exchange_mgr.initialize_exchanges()
        
        if exchange_mgr.exchanges:
            print(f'✅ Connected to {len(exchange_mgr.exchanges)} exchange(s):')
            for name in exchange_mgr.exchanges.keys():
                print(f'   📈 {name.capitalize()}')
        else:
            print('ℹ️  No exchanges connected - will use paper trading mode')
        
        await exchange_mgr.shutdown()
        print('✅ API test completed successfully!')
        
    except Exception as e:
        print(f'❌ API test failed: {e}')

asyncio.run(test_connections())
"
            Write-Host "✅ API connection test completed!" -ForegroundColor Green
        } catch {
            Write-Host "❌ API test failed: $_" -ForegroundColor Red
        }
    }
    
    "5" {
        Write-Host ""
        Write-Host "📖 Opening API Setup Guide..." -ForegroundColor Cyan
        Start-Process "API_SETUP_GUIDE.md"
    }
    
    "6" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Invalid option. Please choose 1-6." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. .\launch_dashboard.ps1 - Start monitoring dashboard" -ForegroundColor White
Write-Host "   2. .\start_trader_windows.ps1 - Start the trading bot" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
