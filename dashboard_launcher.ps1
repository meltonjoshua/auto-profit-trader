# Auto Profit Trader - Dashboard Launcher
Write-Host ""
Write-Host "🚀 AUTO PROFIT TRADER DASHBOARD" -ForegroundColor Green
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
$env:PYTHONPATH = Join-Path $scriptPath "src"

Write-Host "📊 Starting Web Dashboard..." -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Your dashboard will be available at:" -ForegroundColor Yellow
Write-Host "   🌐 http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "📈 Features:" -ForegroundColor Yellow
Write-Host "   💰 Real-time profit/loss tracking" -ForegroundColor White
Write-Host "   📊 Performance metrics & statistics" -ForegroundColor White
Write-Host "   📋 Recent trades history" -ForegroundColor White
Write-Host "   🎯 Win/loss rate monitoring" -ForegroundColor White
Write-Host "   ⏱️ Live system status" -ForegroundColor White
Write-Host "   🔄 Auto-refresh every 30 seconds" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop the dashboard" -ForegroundColor Red
Write-Host ""

try {
    python dashboard.py
} catch {
    Write-Host "❌ Error starting dashboard: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure you've run the trader at least once" -ForegroundColor White
    Write-Host "   2. Check that Python is installed correctly" -ForegroundColor White
    Write-Host "   3. Try: pip install aiohttp aiohttp-cors" -ForegroundColor White
}
