# Auto Profit Trader - Complete Monitoring Solution
# This script provides multiple options for monitoring your trading performance

Write-Host ""
Write-Host "🚀 ================================== 🚀" -ForegroundColor Green
Write-Host "   AUTO PROFIT TRADER MONITOR" -ForegroundColor Green  
Write-Host "🚀 ================================== 🚀" -ForegroundColor Green
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set environment
$env:PYTHONPATH = Join-Path $scriptPath "src"
$env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
$env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"

function Show-Menu {
    Write-Host "Choose your monitoring option:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 🌐 Web Dashboard (Recommended)" -ForegroundColor Yellow
    Write-Host "   - Real-time web interface at http://localhost:8080" -ForegroundColor White
    Write-Host "   - Beautiful charts and live updates" -ForegroundColor White
    Write-Host "   - Access from any browser" -ForegroundColor White
    Write-Host ""
    Write-Host "2. 📊 Quick Performance Summary" -ForegroundColor Yellow
    Write-Host "   - Instant P and L snapshot in console" -ForegroundColor White
    Write-Host "   - Current statistics and status" -ForegroundColor White
    Write-Host ""
    Write-Host "3. 📋 Live Log Monitoring" -ForegroundColor Yellow
    Write-Host "   - Real-time log file monitoring" -ForegroundColor White
    Write-Host "   - See trades as they happen" -ForegroundColor White
    Write-Host ""
    Write-Host "4. 📁 View Log Files" -ForegroundColor Yellow
    Write-Host "   - Browse historical performance data" -ForegroundColor White
    Write-Host "   - Check specific log files" -ForegroundColor White
    Write-Host ""
    Write-Host "5. 💾 Database Query Tool" -ForegroundColor Yellow
    Write-Host "   - Direct database queries" -ForegroundColor White
    Write-Host "   - Custom profit/loss reports" -ForegroundColor White
    Write-Host ""
    Write-Host "6. 🔄 Start Trader (if not running)" -ForegroundColor Yellow
    Write-Host "   - Launch the trading bot" -ForegroundColor White
    Write-Host ""
    Write-Host "0. ❌ Exit" -ForegroundColor Red
    Write-Host ""
}

function Start-WebDashboard {
    Write-Host "🌐 Starting Web Dashboard..." -ForegroundColor Green
    Write-Host ""
    
    # Install dashboard dependencies
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    try {
        pip install aiohttp-cors --quiet
        Write-Host "✅ Dependencies ready" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Dependencies may already be installed" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🚀 Dashboard will open at: http://localhost:8080" -ForegroundColor Yellow
    Write-Host "🛑 Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow
    Write-Host ""
    
    # Start dashboard
    try {
        python dashboard.py
    } catch {
        Write-Host "❌ Error starting dashboard: $_" -ForegroundColor Red
        Write-Host "💡 Make sure the trader has been run at least once" -ForegroundColor Yellow
        Start-Sleep 3
    }
}

function Show-QuickSummary {
    Write-Host "📊 Quick Performance Summary" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    Write-Host ""
    
    # Check if trader is running
    $traderRunning = Test-Path "trader.pid"
    if ($traderRunning) {
        Write-Host "🟢 Status: RUNNING" -ForegroundColor Green
    } else {
        Write-Host "🔴 Status: STOPPED" -ForegroundColor Red
    }
    
    # Show recent performance log
    $perfLog = "logs\performance.log"
    if (Test-Path $perfLog) {
        Write-Host ""
        Write-Host "💰 Recent Performance:" -ForegroundColor Yellow
        Get-Content $perfLog | Select-Object -Last 5 | ForEach-Object {
            Write-Host "   $_" -ForegroundColor White
        }
    }
    
    # Show recent trades
    $tradesLog = "logs\trades.log"
    if (Test-Path $tradesLog) {
        Write-Host ""
        Write-Host "📈 Recent Trades:" -ForegroundColor Yellow
        Get-Content $tradesLog | Select-Object -Last 5 | ForEach-Object {
            Write-Host "   $_" -ForegroundColor White
        }
    }
    
    # Database stats
    if (Test-Path "portfolio.db") {
        Write-Host ""
        Write-Host "💾 Database:" -ForegroundColor Yellow
        $dbSize = (Get-Item "portfolio.db").Length
        Write-Host "   Size: $([math]::Round($dbSize/1KB, 2)) KB" -ForegroundColor White
        Write-Host "   File: portfolio.db" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Press any key to return to menu..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Start-LiveMonitoring {
    Write-Host "📋 Live Log Monitoring (Press Ctrl+C to stop)" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    Write-Host ""
    
    $logFiles = @("logs\daemon.log", "logs\trading_engine.log", "logs\trades.log")
    
    try {
        while ($true) {
            Clear-Host
            Write-Host "📋 LIVE MONITORING - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
            Write-Host "=" * 60 -ForegroundColor Green
            
            foreach ($logFile in $logFiles) {
                if (Test-Path $logFile) {
                    Write-Host ""
                    Write-Host "📄 $logFile" -ForegroundColor Yellow
                    Get-Content $logFile | Select-Object -Last 3 | ForEach-Object {
                        Write-Host "   $_" -ForegroundColor White
                    }
                }
            }
            
            Start-Sleep 5
        }
    } catch {
        Write-Host ""
        Write-Host "Monitoring stopped." -ForegroundColor Yellow
    }
}

function Show-LogFiles {
    Write-Host "📁 Available Log Files" -ForegroundColor Green
    Write-Host "=" * 30 -ForegroundColor Green
    Write-Host ""
    
    if (Test-Path "logs") {
        $logs = Get-ChildItem "logs\*.log" | Sort-Object LastWriteTime -Descending
        
        $i = 1
        foreach ($log in $logs) {
            $size = [math]::Round($log.Length/1KB, 2)
            $modified = $log.LastWriteTime.ToString("MM-dd HH:mm")
            Write-Host "$i. $($log.Name)" -ForegroundColor Yellow
            Write-Host "   Size: $size KB | Modified: $modified" -ForegroundColor White
            $i++
        }
        
        Write-Host ""
        Write-Host "Enter number to view file (0 to return): " -NoNewline -ForegroundColor Cyan
        $choice = Read-Host
        
        if ($choice -match '^\d+$' -and [int]$choice -gt 0 -and [int]$choice -le $logs.Count) {
            $selectedLog = $logs[[int]$choice - 1]
            Write-Host ""
            Write-Host "📄 Viewing: $($selectedLog.Name)" -ForegroundColor Green
            Write-Host "=" * 50 -ForegroundColor Green
            
            Get-Content $selectedLog.FullName | Select-Object -Last 20 | ForEach-Object {
                Write-Host $_
            }
            
            Write-Host ""
            Write-Host "Press any key to continue..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
    } else {
        Write-Host "No logs directory found. Run the trader first." -ForegroundColor Red
        Start-Sleep 2
    }
}

function Show-DatabaseQuery {
    Write-Host "💾 Database Query Tool" -ForegroundColor Green
    Write-Host "=" * 25 -ForegroundColor Green
    Write-Host ""
    
    if (-not (Test-Path "portfolio.db")) {
        Write-Host "❌ Database not found. Run the trader first." -ForegroundColor Red
        Start-Sleep 2
        return
    }
    
    Write-Host "Quick Queries:" -ForegroundColor Yellow
    Write-Host "1. Total Profit/Loss" -ForegroundColor White
    Write-Host "2. Trade Count by Symbol" -ForegroundColor White
    Write-Host "3. Daily Performance" -ForegroundColor White
    Write-Host "4. Recent Trades" -ForegroundColor White
    Write-Host "0. Return to menu" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter choice"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "💰 Total Profit/Loss:" -ForegroundColor Green
            sqlite3 portfolio.db "SELECT SUM(profit) as total_profit, COUNT(*) as total_trades FROM trades;"
        }
        "2" {
            Write-Host ""
            Write-Host "📊 Trades by Symbol:" -ForegroundColor Green  
            sqlite3 portfolio.db "SELECT symbol, COUNT(*) as trade_count, SUM(profit) as total_profit FROM trades GROUP BY symbol ORDER BY trade_count DESC;"
        }
        "3" {
            Write-Host ""
            Write-Host "📈 Daily Performance:" -ForegroundColor Green
            sqlite3 portfolio.db "SELECT DATE(timestamp) as date, SUM(profit) as daily_profit, COUNT(*) as trades FROM trades GROUP BY DATE(timestamp) ORDER BY date DESC LIMIT 7;"
        }
        "4" {
            Write-Host ""
            Write-Host "🔄 Recent Trades:" -ForegroundColor Green
            sqlite3 portfolio.db "SELECT timestamp, symbol, action, amount, price, profit FROM trades ORDER BY timestamp DESC LIMIT 10;"
        }
    }
    
    if ($choice -ne "0") {
        Write-Host ""
        Write-Host "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

function Start-Trader {
    Write-Host "🚀 Starting Auto Profit Trader..." -ForegroundColor Green
    Write-Host ""
    
    # Check if already running
    if (Test-Path "trader.pid") {
        Write-Host "⚠️ Trader appears to be already running" -ForegroundColor Yellow
        Write-Host "Check the trader console or stop it first" -ForegroundColor White
        Start-Sleep 2
        return
    }
    
    Write-Host "Choose startup method:" -ForegroundColor Cyan
    Write-Host "1. PowerShell Script (Recommended)" -ForegroundColor White
    Write-Host "2. Direct Python" -ForegroundColor White
    Write-Host "3. Docker" -ForegroundColor White
    Write-Host ""
    
    $method = Read-Host "Enter choice (1-3)"
    
    switch ($method) {
        "1" {
            Write-Host "Starting with PowerShell script..." -ForegroundColor Green
            Start-Process powershell -ArgumentList "-File", "start_trader_windows.ps1"
        }
        "2" {
            Write-Host "Starting with Python..." -ForegroundColor Green
            Start-Process python -ArgumentList "trader_daemon.py"
        }
        "3" {
            Write-Host "Starting with Docker..." -ForegroundColor Green
            docker-compose -f docker-compose.prod.yml up -d
        }
        default {
            Write-Host "Invalid choice" -ForegroundColor Red
            Start-Sleep 1
        }
    }
}

# Main menu loop
do {
    Clear-Host
    Show-Menu
    
    Write-Host "Enter your choice (0-6): " -NoNewline -ForegroundColor Cyan
    $choice = Read-Host
    
    switch ($choice) {
        "1" { Start-WebDashboard }
        "2" { Show-QuickSummary }
        "3" { Start-LiveMonitoring }
        "4" { Show-LogFiles }
        "5" { Show-DatabaseQuery }
        "6" { Start-Trader }
        "0" { 
            Write-Host ""
            Write-Host "👋 Goodbye!" -ForegroundColor Green
            exit 
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Start-Sleep 1
        }
    }
} while ($true)
