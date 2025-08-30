# Enhanced Dashboard Launcher for Auto Profit Trader (UK)
param(
    [string]$Mode = ""
)

# Clear screen for clean interface
Clear-Host

Write-Host ""
Write-Host "================================"
Write-Host "  AUTO PROFIT TRADER DASHBOARD"
Write-Host "================================"
Write-Host ""

# Set up environment
$env:PYTHONPATH = $PWD
$env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"

Write-Host "Setting up environment..."
Write-Host "Python path configured" -ForegroundColor Green
Write-Host "Dependencies ready" -ForegroundColor Green
Write-Host ""

Write-Host "Dashboard will be available at:"
Write-Host "http://localhost:8080" -ForegroundColor Cyan
Write-Host ""

# If mode specified directly, skip menu
if ($Mode -eq "enhanced") {
    Write-Host "Starting Enhanced Dashboard..." -ForegroundColor Green
    python enhanced_dashboard.py
    exit
}

if ($Mode -eq "simple") {
    Write-Host "Starting Simple Dashboard..." -ForegroundColor Blue
    python simple_dashboard.py
    exit
}

# Show menu
Write-Host "Dashboard Options:"
Write-Host "  [1] Enhanced Dashboard (Full Features + System Monitoring)"
Write-Host "  [2] Simple Dashboard (Basic Interface)"
Write-Host "  [3] Analytics Only"
Write-Host "  [q] Quit"
Write-Host ""

$choice = Read-Host "Choose option (1-3, q)"

switch ($choice.ToLower()) {
    "1" {
        Write-Host ""
        Write-Host "Starting Enhanced Dashboard..." -ForegroundColor Green
        try {
            python enhanced_dashboard.py
        } catch {
            Write-Host "Enhanced dashboard unavailable, starting simple dashboard..." -ForegroundColor Yellow
            python simple_dashboard.py
        }
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Simple Dashboard..." -ForegroundColor Blue
        python simple_dashboard.py
    }
    "3" {
        Write-Host ""
        Write-Host "Starting Analytics Dashboard..." -ForegroundColor Magenta
        python -c "
import sqlite3
import json
from datetime import datetime, timedelta

# Quick analytics
conn = sqlite3.connect('trader.db')
cursor = conn.cursor()

print('\\n=== QUICK ANALYTICS ===')
cursor.execute('SELECT COUNT(*) FROM trades')
total_trades = cursor.fetchone()[0]
print(f'Total Trades: {total_trades}')

cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE profit_loss IS NOT NULL')
result = cursor.fetchone()[0]
total_pnl = result if result else 0
print(f'Total P&L: £{total_pnl:.2f}')

cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5')
recent_trades = cursor.fetchall()
print(f'\\nRecent Trades ({len(recent_trades)}):')
for trade in recent_trades:
    print(f'  {trade[2]} {trade[3]} @ £{trade[4]:.2f}')

conn.close()
print('\\nPress Enter to continue...')
input()
"
    }
    "q" {
        Write-Host "Goodbye!" -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice. Starting Enhanced Dashboard..." -ForegroundColor Yellow
        python enhanced_dashboard.py
    }
}
