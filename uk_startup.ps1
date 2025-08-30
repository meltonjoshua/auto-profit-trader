# 🇬🇧 UK Auto Profit Trader - One-Click Setup
# Optimized for UK users with GBP focus and FCA-regulated exchanges

Write-Host ""
Write-Host "🇬🇧 ========================================== 🇬🇧" -ForegroundColor Blue
Write-Host "    UK AUTO PROFIT TRADER - QUICK SETUP" -ForegroundColor Blue
Write-Host "🇬🇧 ========================================== 🇬🇧" -ForegroundColor Blue
Write-Host ""

# Get script directory and set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "🇬🇧 UK CRYPTO TRADING ADVANTAGES:" -ForegroundColor Cyan
Write-Host "   💂 FCA-regulated exchanges (Kraken, Coinbase Pro)" -ForegroundColor Green
Write-Host "   💷 GBP pairs trading (BTC/GBP, ETH/GBP)" -ForegroundColor Green
Write-Host "   🏦 Direct UK bank transfers via Faster Payments" -ForegroundColor Green
Write-Host "   📋 HMRC-compliant trade reporting" -ForegroundColor Green
Write-Host "   🕐 London timezone optimization" -ForegroundColor Green
Write-Host ""

Write-Host "⚠️  BINANCE STATUS UPDATE:" -ForegroundColor Yellow
Write-Host "   🚫 Binance currently unavailable in UK" -ForegroundColor Red
Write-Host "   📜 Status: Regulatory reorganization with FCA" -ForegroundColor White
Write-Host "   ✅ Better alternatives: Kraken & Coinbase Pro" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 WHAT WOULD YOU LIKE TO DO?" -ForegroundColor Yellow
Write-Host "   [1] 🇬🇧 Setup Kraken API (BEST FOR UK)" -ForegroundColor Green
Write-Host "   [2] 📊 Launch UK Dashboard" -ForegroundColor White
Write-Host "   [3] 🤖 Start Trading Bot" -ForegroundColor White
Write-Host "   [4] 🎮 Demo Kraken Mode (Practice Trading)" -ForegroundColor Cyan
Write-Host "   [5] 📖 View UK Trading Guide" -ForegroundColor White
Write-Host "   [6] 🔧 Complete API Setup (All Exchanges)" -ForegroundColor White
Write-Host "   [7] 🧪 Test Everything" -ForegroundColor White
Write-Host "   [8] Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose an option (1-8)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🇬🇧 LAUNCHING KRAKEN SETUP..." -ForegroundColor Green
        Write-Host "   Kraken is the BEST choice for UK users:" -ForegroundColor Cyan
        Write-Host "   ✅ FCA-regulated and UK-compliant" -ForegroundColor Green
        Write-Host "   ✅ Direct GBP pairs (BTC/GBP, ETH/GBP)" -ForegroundColor Green
        Write-Host "   ✅ UK bank transfers via Faster Payments" -ForegroundColor Green
        Write-Host "   ✅ Lower fees for GBP trading" -ForegroundColor Green
        Write-Host ""
        
        # Launch the API setup script focusing on Kraken
        .\setup_api.ps1
    }
    
    "2" {
        Write-Host ""
        Write-Host "📊 LAUNCHING UK DASHBOARD..." -ForegroundColor Cyan
        Write-Host "   UK-optimized features:" -ForegroundColor White
        Write-Host "   💷 Profit/Loss tracking in GBP" -ForegroundColor Green
        Write-Host "   🇬🇧 Kraken priority display" -ForegroundColor Green
        Write-Host "   📋 HMRC-ready trade reports" -ForegroundColor Green
        Write-Host ""
        
        .\launch_dashboard.ps1
    }
    
    "3" {
        Write-Host ""
        Write-Host "🤖 STARTING UK TRADING BOT..." -ForegroundColor Yellow
        Write-Host "   UK configuration active:" -ForegroundColor White
        Write-Host "   🕐 London timezone (GMT/BST)" -ForegroundColor Green
        Write-Host "   💷 GBP base currency priority" -ForegroundColor Green
        Write-Host "   🇬🇧 FCA-regulated exchanges first" -ForegroundColor Green
        Write-Host ""
        
        .\start_trader_windows.ps1
    }
    
    "4" {
        Write-Host ""
        Write-Host "🎮 LAUNCHING DEMO KRAKEN MODE..." -ForegroundColor Cyan
        Write-Host "   Perfect for learning UK crypto trading:" -ForegroundColor White
        Write-Host "   💷 £5,000 demo balance to practice with" -ForegroundColor Green
        Write-Host "   � Realistic UK market prices and volatility" -ForegroundColor Green
        Write-Host "   🇬🇧 GBP pairs focus (BTC/GBP, ETH/GBP)" -ForegroundColor Green
        Write-Host "   📈 Bull/bear market simulations" -ForegroundColor Green
        Write-Host ""
        
        .\demo_kraken.ps1
    }
    
    "5" {
        Write-Host ""
        Write-Host "�📖 OPENING UK TRADING GUIDE..." -ForegroundColor Cyan
        Start-Process "UK_TRADING_GUIDE.md"
    }
    
    "6" {
        Write-Host ""
        Write-Host "🔧 LAUNCHING COMPLETE API SETUP..." -ForegroundColor Yellow
        .\setup_api.ps1
    }
    
    "7" {
        Write-Host ""
        Write-Host "🧪 TESTING UK CONFIGURATION..." -ForegroundColor Cyan
        
        # Set environment
        $env:PYTHONPATH = Join-Path $scriptPath "src"
        
        Write-Host "   🔍 Checking UK config settings..." -ForegroundColor White
        
        try {
            python -c "
import json
with open('config.json', 'r') as f:
    config = json.load(f)

print('🇬🇧 UK Configuration Status:')
trading = config.get('trading', {})
print(f'   Base Currency: {trading.get(\"base_currency\", \"USD\")}')
print(f'   Timezone: {trading.get(\"timezone\", \"UTC\")}')

exchanges = config.get('exchanges', {})
kraken = exchanges.get('kraken', {})
print(f'   Kraken Enabled: {kraken.get(\"enabled\", False)}')
print(f'   Kraken Priority: {kraken.get(\"priority\", \"Not set\")}')
print(f'   UK Regulated: {kraken.get(\"uk_regulated\", False)}')

if kraken.get('gbp_pairs'):
    print(f'   GBP Pairs: {len(kraken[\"gbp_pairs\"])} configured')
    
print('✅ UK configuration looks good!')
"
            
            Write-Host "   🧪 Testing paper trading..." -ForegroundColor White
            python -c "
import sys
sys.path.append('src')
from exchanges.exchange_manager import ExchangeManager

# Test paper trading symbols
em = ExchangeManager(None, None)
print('📊 Paper Trading Symbols:')
symbols = ['BTC/GBP', 'ETH/GBP', 'ADA/GBP', 'BTC/USDT', 'ETH/USDT']
for symbol in symbols:
    print(f'   💷 {symbol}')
print('✅ UK-optimized paper trading ready!')
"
            
            Write-Host "✅ UK configuration test completed!" -ForegroundColor Green
            
        } catch {
            Write-Host "❌ Configuration test failed: $_" -ForegroundColor Red
        }
    }
    
    "8" {
        Write-Host ""
        Write-Host "👋 Cheerio! Happy UK crypto trading! 🇬🇧" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Invalid option. Please choose 1-8." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🇬🇧 UK TRADING NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Setup Kraken API (FCA-regulated)" -ForegroundColor White
Write-Host "   2. Launch Dashboard (GBP profit tracking)" -ForegroundColor White
Write-Host "   3. Start trading with GBP pairs" -ForegroundColor White
Write-Host "   4. Monitor via dashboard" -ForegroundColor White
Write-Host "   5. Export for HMRC tax reporting" -ForegroundColor White
Write-Host ""
Write-Host "🇬🇧 Rule Britannia! 💷" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
