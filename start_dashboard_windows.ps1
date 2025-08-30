# Auto Profit Trader Dashboard - Windows PowerShell Startup Script
Write-Host "🌟 Starting Auto Profit Trader Dashboard..." -ForegroundColor Green
Write-Host ""

# Set environment variables
$env:PYTHONPATH = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "src"
$env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
$env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"

# Change to script directory
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host "📦 Installing dashboard dependencies..." -ForegroundColor Cyan
try {
    pip install aiohttp-cors --quiet
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Some dependencies may already be installed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting dashboard server..." -ForegroundColor Cyan
Write-Host "📊 Your dashboard will be available at: http://localhost:8080" -ForegroundColor Yellow
Write-Host "🛑 Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow
Write-Host ""

try {
    python dashboard.py
}
catch {
    Write-Host "❌ Error starting dashboard: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure Python is installed and in PATH" -ForegroundColor White
    Write-Host "   2. Run: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "   3. Ensure the trader has been run at least once to create database" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
