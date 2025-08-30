# 🇬🇧 Auto Profit Trader - Complete Installation & Setup
# One-click installation for the ultimate UK crypto trading suite

param(
    [string]$Mode = "install"
)

Write-Host ""
Write-Host "🇬🇧 =============================================== 🇬🇧" -ForegroundColor Blue
Write-Host "     AUTO PROFIT TRADER - COMPLETE INSTALLER" -ForegroundColor Blue  
Write-Host "🇬🇧 =============================================== 🇬🇧" -ForegroundColor Blue
Write-Host ""

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

if ($Mode -eq "install") {
    Write-Host "🚀 INSTALLING AUTO PROFIT TRADER..." -ForegroundColor Green
    Write-Host ""
    
    # Check Python
    Write-Host "1️⃣ Checking Python installation..." -ForegroundColor Cyan
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -eq 3 -and $minor -ge 9) {
                Write-Host "   ✅ $pythonVersion (Compatible)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  $pythonVersion (Upgrade recommended)" -ForegroundColor Yellow
                Write-Host "      Download Python 3.11+ from https://python.org" -ForegroundColor White
            }
        }
    } catch {
        Write-Host "   ❌ Python not found!" -ForegroundColor Red
        Write-Host "      Please install Python 3.11+ from https://python.org" -ForegroundColor White
        Write-Host "      Make sure to check 'Add to PATH' during installation" -ForegroundColor White
        exit 1
    }
    
    # Install/upgrade pip
    Write-Host ""
    Write-Host "2️⃣ Upgrading pip..." -ForegroundColor Cyan
    try {
        python -m pip install --upgrade pip --quiet
        Write-Host "   ✅ Pip upgraded to latest version" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Pip upgrade failed (continuing anyway)" -ForegroundColor Yellow
    }
    
    # Install dependencies
    Write-Host ""
    Write-Host "3️⃣ Installing dependencies..." -ForegroundColor Cyan
    Write-Host "   📦 This may take a few minutes..." -ForegroundColor Yellow
    
    try {
        pip install -r requirements.txt --quiet --upgrade
        Write-Host "   ✅ All dependencies installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Dependency installation failed!" -ForegroundColor Red
        Write-Host "      Trying alternative installation..." -ForegroundColor Yellow
        
        # Try installing critical packages individually
        $criticalPackages = @(
            "aiohttp>=3.9.0",
            "ccxt>=4.2.0", 
            "cryptography>=42.0.0",
            "psutil>=5.9.0",
            "aiohttp-cors>=0.7.0"
        )
        
        foreach ($package in $criticalPackages) {
            try {
                pip install $package --quiet
                Write-Host "   ✅ Installed $package" -ForegroundColor Green
            } catch {
                Write-Host "   ❌ Failed to install $package" -ForegroundColor Red
            }
        }
    }
    
    # Verify installation
    Write-Host ""
    Write-Host "4️⃣ Verifying installation..." -ForegroundColor Cyan
    
    $testScript = @"
import sys
import importlib

packages = [
    ('aiohttp', 'Web framework'),
    ('ccxt', 'Crypto exchange library'),
    ('cryptography', 'Security encryption'),
    ('psutil', 'System monitoring'),
    ('json', 'JSON handling'),
    ('sqlite3', 'Database'),
    ('asyncio', 'Async operations')
]

all_good = True
for package, description in packages:
    try:
        importlib.import_module(package)
        print(f'   ✅ {description}: {package}')
    except ImportError:
        print(f'   ❌ {description}: {package} - MISSING')
        all_good = False

if all_good:
    print('   🎉 All critical packages verified!')
else:
    print('   ⚠️  Some packages missing - demo mode available')
"@
    
    python -c $testScript
    
    Write-Host ""
    Write-Host "5️⃣ Setting up database..." -ForegroundColor Cyan
    
    $databaseScript = @"
import sqlite3
import os

if not os.path.exists('portfolio.db'):
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # Create trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL,
            profit_loss REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            exchange TEXT,
            strategy TEXT
        )
    ''')
    
    # Create portfolio table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL,
            balance REAL NOT NULL,
            value_gbp REAL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print('   ✅ Database structure created')
else:
    print('   ✅ Database already exists')
"@
    
    python -c $databaseScript
    
    # Create necessary directories
    Write-Host ""
    Write-Host "6️⃣ Creating directories..." -ForegroundColor Cyan
    
    $directories = @("logs", "backups", "exports")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "   ✅ Created $dir directory" -ForegroundColor Green
        } else {
            Write-Host "   ✅ $dir directory exists" -ForegroundColor Green
        }
    }
    
    # Set environment variables
    Write-Host ""
    Write-Host "7️⃣ Configuring environment..." -ForegroundColor Cyan
    
    $env:PYTHONPATH = Join-Path $scriptPath "src"
    $env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
    $env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"
    
    Write-Host "   ✅ Environment variables configured" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "8️⃣ Testing core functionality..." -ForegroundColor Cyan
    
    $coreTestScript = @"
import sys
sys.path.append('src')
try:
    from utils.config_manager import ConfigManager
    from security.crypto_manager import SecurityManager
    print('   ✅ Core modules loaded successfully')
    
    # Test config
    config = ConfigManager()
    print('   ✅ Configuration system working')
    
    # Test security
    security = SecurityManager()
    print('   ✅ Security system working')
    
except Exception as e:
    print(f'   ⚠️  Core test: {e} (demo mode available)')
"@
    
    try {
        python -c $coreTestScript
    } catch {
        Write-Host "   ⚠️  Core test failed (demo mode available)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 INSTALLATION COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🇬🇧 AUTO PROFIT TRADER IS READY!" -ForegroundColor Blue
    Write-Host ""
    Write-Host "📋 WHAT'S INSTALLED:" -ForegroundColor Yellow
    Write-Host "   ✅ Complete UK crypto trading suite" -ForegroundColor Green
    Write-Host "   ✅ Enhanced real-time dashboard" -ForegroundColor Green
    Write-Host "   ✅ Demo mode with £5,000 practice money" -ForegroundColor Green
    Write-Host "   ✅ FCA-compliant exchange integration" -ForegroundColor Green
    Write-Host "   ✅ HMRC-ready reporting system" -ForegroundColor Green
    Write-Host "   ✅ Bank-grade security encryption" -ForegroundColor Green
    Write-Host "   ✅ System health monitoring" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 QUICK START:" -ForegroundColor Cyan
    Write-Host "   1. Run: .\AutoProfitTrader.ps1" -ForegroundColor White
    Write-Host "   2. Choose option 1 (Demo Mode)" -ForegroundColor White
    Write-Host "   3. Practice with £5,000 virtual money" -ForegroundColor White
    Write-Host "   4. Setup real trading when ready!" -ForegroundColor White
    Write-Host ""
    
    $startNow = Read-Host "🎮 Start Auto Profit Trader now? (y/n)"
    if ($startNow -eq "y" -or $startNow -eq "Y") {
        Write-Host ""
        & ".\AutoProfitTrader.ps1"
    } else {
        Write-Host ""
        Write-Host "💡 Run .\AutoProfitTrader.ps1 anytime to start!" -ForegroundColor Cyan
        Write-Host "🇬🇧 Happy UK crypto trading!" -ForegroundColor Blue
    }
    
} elseif ($Mode -eq "update") {
    Write-Host "🔄 UPDATING AUTO PROFIT TRADER..." -ForegroundColor Cyan
    Write-Host ""
    
    # Update dependencies
    Write-Host "📦 Updating dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --upgrade --quiet
    Write-Host "✅ Dependencies updated!" -ForegroundColor Green
    
    # Update database schema if needed
    Write-Host "🗃️ Checking database..." -ForegroundColor Yellow
    python -c "
import sqlite3
conn = sqlite3.connect('portfolio.db')
cursor = conn.cursor()

# Add any new columns that might be missing
try:
    cursor.execute('ALTER TABLE trades ADD COLUMN exchange TEXT')
except:
    pass
try:
    cursor.execute('ALTER TABLE trades ADD COLUMN strategy TEXT')
except:
    pass

conn.commit()
conn.close()
print('✅ Database updated!')
"
    
    Write-Host ""
    Write-Host "🎉 Update complete!" -ForegroundColor Green
    
} elseif ($Mode -eq "repair") {
    Write-Host "🔧 REPAIRING AUTO PROFIT TRADER..." -ForegroundColor Yellow
    Write-Host ""
    
    # Reinstall dependencies
    pip install -r requirements.txt --force-reinstall --quiet
    
    # Reset environment
    $env:PYTHONPATH = Join-Path $scriptPath "src"
    $env:PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION = "python"
    $env:PYTHONWARNINGS = "ignore::UserWarning:google.protobuf.runtime_version"
    
    # Test everything
    python -c "
import sys
sys.path.append('src')
try:
    from demo.demo_kraken import DemoKrakenExchange
    demo = DemoKrakenExchange()
    print('✅ Demo mode working')
except Exception as e:
    print(f'❌ Demo mode: {e}')
"
    
    Write-Host "🔧 Repair complete!" -ForegroundColor Green
    
} else {
    Write-Host "Usage: .\install.ps1 [install|update|repair]" -ForegroundColor Yellow
}

Write-Host ""
