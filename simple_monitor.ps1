# Auto Profit Trader - Simple Monitoring Solution
Write-Host ""
Write-Host "🚀 AUTO PROFIT TRADER MONITOR 🚀" -ForegroundColor Green
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set environment
$env:PYTHONPATH = Join-Path $scriptPath "src"

Write-Host "Choose your monitoring option:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 🌐 Web Dashboard (Best Option)" -ForegroundColor Yellow
Write-Host "2. 📊 Quick Performance Check" -ForegroundColor Yellow  
Write-Host "3. 📋 View Recent Logs" -ForegroundColor Yellow
Write-Host "4. 🚀 Start Trader" -ForegroundColor Yellow
Write-Host "0. Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter choice (0-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🌐 Starting Web Dashboard..." -ForegroundColor Green
        Write-Host "📊 Dashboard will be available at: http://localhost:8080" -ForegroundColor Yellow
        Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        
        try {
            python dashboard.py
        } catch {
            Write-Host "❌ Error: $_" -ForegroundColor Red
            Write-Host "💡 Make sure you've run the trader at least once" -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "📊 PERFORMANCE SUMMARY" -ForegroundColor Green
        Write-Host "=" * 30 -ForegroundColor Green
        
        # Check trader status
        if (Test-Path "trader.pid") {
            Write-Host "🟢 Status: RUNNING" -ForegroundColor Green
        } else {
            Write-Host "🔴 Status: STOPPED" -ForegroundColor Red
        }
        
        # Show performance log
        if (Test-Path "logs\performance.log") {
            Write-Host ""
            Write-Host "💰 Recent Performance:" -ForegroundColor Yellow
            Get-Content "logs\performance.log" | Select-Object -Last 5
        }
        
        # Show recent trades
        if (Test-Path "logs\trades.log") {
            Write-Host ""
            Write-Host "📈 Recent Trades:" -ForegroundColor Yellow
            Get-Content "logs\trades.log" | Select-Object -Last 5
        }
        
        Write-Host ""
        Read-Host "Press Enter to continue"
    }
    
    "3" {
        Write-Host ""
        Write-Host "📋 RECENT LOGS" -ForegroundColor Green
        Write-Host "=" * 20 -ForegroundColor Green
        
        $logFiles = @("daemon.log", "trading_engine.log", "trades.log", "performance.log")
        
        foreach ($logFile in $logFiles) {
            $fullPath = "logs\$logFile"
            if (Test-Path $fullPath) {
                Write-Host ""
                Write-Host "📄 $logFile" -ForegroundColor Yellow
                Get-Content $fullPath | Select-Object -Last 3
            }
        }
        
        Write-Host ""
        Read-Host "Press Enter to continue"
    }
    
    "4" {
        Write-Host ""
        Write-Host "🚀 Starting Trader..." -ForegroundColor Green
        Write-Host ""
        
        if (Test-Path "trader.pid") {
            Write-Host "⚠️ Trader may already be running" -ForegroundColor Yellow
        } else {
            Write-Host "Starting with PowerShell script..." -ForegroundColor Green
            Start-Process powershell -ArgumentList "-File", "start_trader_windows.ps1"
            Write-Host "✅ Trader started in new window" -ForegroundColor Green
        }
        
        Write-Host ""
        Read-Host "Press Enter to continue"
    }
    
    "0" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Green
    }
    
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
    }
}
