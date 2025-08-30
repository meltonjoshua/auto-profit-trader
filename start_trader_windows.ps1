# Auto Profit Trader - Windows PowerShell Startup Script
Write-Host "🚀 Starting Auto Profit Trader..." -ForegroundColor Green
Write-Host ""

# Set environment variables to suppress warnings
$env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
$env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"

# Set Python path to include src directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $scriptPath "src"

# Change to script directory
Set-Location $scriptPath

# Set console encoding to UTF-8 for emoji support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host "📊 Environment configured for optimal performance" -ForegroundColor Cyan
Write-Host "🔇 Protobuf warnings suppressed for cleaner output" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the trader" -ForegroundColor Yellow
Write-Host ""

try {
    # Start the trader
    python trader_daemon.py
}
catch {
    Write-Host "❌ Error starting trader: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
