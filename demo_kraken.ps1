# 🇬🇧 Demo Kraken Mode Launcher
# Experience realistic UK cryptocurrency trading simulation

Write-Host ""
Write-Host "🇬🇧 ======================================== 🇬🇧" -ForegroundColor Blue
Write-Host "    DEMO KRAKEN MODE - UK CRYPTO TRADING" -ForegroundColor Blue
Write-Host "🇬🇧 ======================================== 🇬🇧" -ForegroundColor Blue
Write-Host ""

# Get script directory and set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set environment
$env:PYTHONPATH = Join-Path $scriptPath "src"

Write-Host "🎮 DEMO KRAKEN FEATURES:" -ForegroundColor Yellow
Write-Host "   💷 Realistic UK crypto prices (BTC/GBP, ETH/GBP)" -ForegroundColor Green
Write-Host "   📊 Live market simulation with volatility" -ForegroundColor Green
Write-Host "   🏦 £5,000 demo balance to practice with" -ForegroundColor Green
Write-Host "   🇬🇧 UK market hours simulation" -ForegroundColor Green
Write-Host "   📈 Bull/bear market conditions" -ForegroundColor Green
Write-Host "   🎯 Real order execution and slippage" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 DEMO OPTIONS:" -ForegroundColor Cyan
Write-Host "   [1] 🎮 Quick Demo (1 minute)" -ForegroundColor White
Write-Host "   [2] 📊 Market Prices Demo" -ForegroundColor White
Write-Host "   [3] 🏦 Account Balance Demo" -ForegroundColor White
Write-Host "   [4] 📈 Trading Simulation (5 minutes)" -ForegroundColor White
Write-Host "   [5] 🎭 Market Conditions Demo" -ForegroundColor White
Write-Host "   [6] 📋 Interactive Demo Menu" -ForegroundColor White
Write-Host "   [7] Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose demo option (1-7)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🎮 LAUNCHING QUICK DEMO..." -ForegroundColor Green
        Write-Host ""
        
        python -c "
import asyncio
import sys
sys.path.append('src')
from demo.demo_kraken import run_demo_kraken

print('🇬🇧 Welcome to Demo Kraken UK!')
print('🎮 This is a realistic simulation of UK crypto trading')
print('')

asyncio.run(run_demo_kraken())
"
    }
    
    "2" {
        Write-Host ""
        Write-Host "📊 UK CRYPTO MARKET PRICES..." -ForegroundColor Cyan
        Write-Host ""
        
        python -c "
import asyncio
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenExchange

async def show_prices():
    demo = DemoKrakenExchange()
    
    print('💷 CURRENT UK CRYPTO PRICES (DEMO):')
    print('=' * 45)
    
    for symbol in demo.get_gbp_pairs():
        ticker = await demo.fetch_ticker(symbol)
        change = ticker['change']
        change_color = '📈' if change > 0 else '📉'
        print(f'{change_color} {symbol:12} £{ticker[\"last\"]:>8,.2f} ({change:+.1f}%)')
    
    print('')
    print('💰 Demo Account Balance:')
    balance = await demo.fetch_balance()
    for currency in ['GBP', 'USDT', 'BTC', 'ETH']:
        if currency in balance:
            total = balance[currency]['total']
            symbol = '£' if currency == 'GBP' else '$' if currency == 'USDT' else ''
            print(f'   {currency}: {symbol}{total:,.4f}')

asyncio.run(show_prices())
"
    }
    
    "3" {
        Write-Host ""
        Write-Host "🏦 DEMO ACCOUNT BALANCE..." -ForegroundColor Yellow
        Write-Host ""
        
        python -c "
import asyncio
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenExchange

async def show_balance():
    demo = DemoKrakenExchange()
    balance = await demo.fetch_balance()
    
    print('🏦 DEMO KRAKEN ACCOUNT BALANCE:')
    print('=' * 40)
    print('')
    
    total_gbp = 0
    for currency, info in balance.items():
        total = info['total']
        free = info['free']
        used = info['used']
        
        if currency == 'GBP':
            print(f'💷 {currency}: £{total:>10,.2f} (£{free:,.2f} available)')
            total_gbp += total
        elif currency == 'USDT':
            print(f'💵 {currency}: ${total:>10,.2f} (${free:,.2f} available)')
            total_gbp += total * 0.79  # Rough GBP conversion
        elif total > 0:
            print(f'₿  {currency}: {total:>12.6f} ({free:.6f} available)')
    
    print('')
    print(f'📊 Estimated Total Value: £{total_gbp:,.2f}')
    print('')
    print('🎯 Ready for UK crypto trading simulation!')

asyncio.run(show_balance())
"
    }
    
    "4" {
        Write-Host ""
        Write-Host "📈 STARTING 5-MINUTE TRADING SIMULATION..." -ForegroundColor Green
        Write-Host ""
        
        python -c "
import asyncio
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenManager

async def trading_simulation():
    demo_manager = DemoKrakenManager()
    demo_exchange = await demo_manager.start_demo_mode()
    
    print('🇬🇧 Starting UK crypto trading simulation...')
    print('⏱️  Duration: 5 minutes')
    print('💷 Focus: GBP pairs (BTC/GBP, ETH/GBP, etc.)')
    print('')
    
    # Run simulation
    stats = await demo_manager.demo_trading_session(5)
    
    print('')
    print('🏁 SIMULATION COMPLETE!')
    print('=' * 30)
    print(f'📊 Total Trades: {stats.get(\"total_trades\", 0)}')
    print(f'💷 Profit/Loss: £{stats.get(\"total_profit_gbp\", 0):.2f}')
    print(f'🎯 Win Rate: {stats.get(\"win_rate\", 0):.1f}%')
    print(f'🏦 Final Balance: £{stats.get(\"current_balance_gbp\", 0):,.2f}')
    print('')
    print('🇬🇧 UK demo trading session completed!')

asyncio.run(trading_simulation())
"
    }
    
    "5" {
        Write-Host ""
        Write-Host "🎭 MARKET CONDITIONS DEMO..." -ForegroundColor Magenta
        Write-Host ""
        
        python -c "
import asyncio
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenExchange

async def market_conditions():
    demo = DemoKrakenExchange()
    
    print('🎭 MARKET CONDITIONS SIMULATION')
    print('=' * 35)
    print('')
    
    # Show normal prices
    print('📊 Normal Market Conditions:')
    ticker = await demo.fetch_ticker('BTC/GBP')
    btc_normal = ticker['last']
    print(f'   BTC/GBP: £{btc_normal:,.2f}')
    
    # Bull run
    await demo.simulate_market_conditions('bull_run')
    ticker = await demo.fetch_ticker('BTC/GBP')
    btc_bull = ticker['last']
    print(f'📈 Bull Run: £{btc_bull:,.2f} (+{((btc_bull/btc_normal-1)*100):+.1f}%)')
    
    # Bear market
    await demo.simulate_market_conditions('bear_market')
    ticker = await demo.fetch_ticker('BTC/GBP')
    btc_bear = ticker['last']
    print(f'📉 Bear Market: £{btc_bear:,.2f} ({((btc_bear/btc_normal-1)*100):+.1f}%)')
    
    # High volatility
    await demo.simulate_market_conditions('high_volatility')
    ticker = await demo.fetch_ticker('BTC/GBP')
    btc_volatile = ticker['last']
    print(f'⚡ High Volatility: £{btc_volatile:,.2f} ({((btc_volatile/btc_normal-1)*100):+.1f}%)')
    
    print('')
    print('🇬🇧 Market conditions demo completed!')

asyncio.run(market_conditions())
"
    }
    
    "6" {
        Write-Host ""
        Write-Host "📋 LAUNCHING INTERACTIVE DEMO..." -ForegroundColor Cyan
        Write-Host ""
        
        python -c "
import asyncio
import sys
sys.path.append('src')
from demo.demo_kraken import DemoKrakenManager, DemoKrakenExchange

async def interactive_demo():
    demo_manager = DemoKrakenManager()
    demo = await demo_manager.start_demo_mode()
    
    print('🇬🇧 INTERACTIVE DEMO KRAKEN MODE')
    print('=' * 35)
    print('')
    
    while True:
        print('💼 Demo Options:')
        print('   1. Show current prices')
        print('   2. Check account balance')  
        print('   3. Execute demo trade')
        print('   4. Change market conditions')
        print('   5. View trade history')
        print('   6. Exit demo')
        print('')
        
        try:
            choice = input('Choose option (1-6): ').strip()
            
            if choice == '1':
                print('')
                for symbol in demo.get_gbp_pairs()[:5]:
                    ticker = await demo.fetch_ticker(symbol)
                    print(f'💷 {symbol}: £{ticker[\"last\"]:,.2f}')
                print('')
                
            elif choice == '2':
                balance = await demo.fetch_balance()
                print('')
                for currency in ['GBP', 'USDT', 'BTC', 'ETH']:
                    if currency in balance:
                        total = balance[currency]['total']
                        if currency == 'GBP':
                            print(f'💷 {currency}: £{total:,.2f}')
                        elif currency == 'USDT':
                            print(f'💵 {currency}: ${total:,.2f}')
                        else:
                            print(f'₿  {currency}: {total:.6f}')
                print('')
                
            elif choice == '3':
                symbol = 'BTC/GBP'
                side = 'buy'
                amount = 0.01
                print(f'🔄 Executing demo {side}: {amount} {symbol}...')
                try:
                    order = await demo.create_market_order(symbol, side, amount)
                    print(f'✅ Order executed: £{order[\"cost\"]:.2f}')
                except Exception as e:
                    print(f'❌ Order failed: {e}')
                print('')
                
            elif choice == '4':
                conditions = ['normal', 'bull_run', 'bear_market', 'high_volatility']
                condition = conditions[len(demo.trade_history) % len(conditions)]
                await demo.simulate_market_conditions(condition)
                print(f'🎭 Market condition changed to: {condition}')
                print('')
                
            elif choice == '5':
                history = demo.get_trade_history(5)
                print('')
                if history:
                    print('📋 Recent Trades:')
                    for trade in history[-5:]:
                        print(f'   {trade[\"side\"].upper()} {trade[\"amount\"]:.4f} {trade[\"symbol\"]} at £{trade[\"price\"]:.2f}')
                else:
                    print('📋 No trades yet')
                print('')
                
            elif choice == '6':
                break
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Error: {e}')
    
    print('👋 Demo session ended!')

asyncio.run(interactive_demo())
"
    }
    
    "7" {
        Write-Host ""
        Write-Host "👋 Thanks for trying Demo Kraken! 🇬🇧" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Invalid option. Please choose 1-7." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🇬🇧 DEMO KRAKEN BENEFITS:" -ForegroundColor Yellow
Write-Host "   ✅ Risk-free learning with £5,000 demo balance" -ForegroundColor Green
Write-Host "   ✅ Realistic UK crypto prices and market conditions" -ForegroundColor Green
Write-Host "   ✅ Practice trading GBP pairs before using real money" -ForegroundColor Green
Write-Host "   ✅ Test strategies in bull/bear markets" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Ready for real trading? Run: .\uk_startup.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
