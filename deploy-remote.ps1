# Auto Profit Trader Remote Deployment Script (PowerShell)
# This script can be used to deploy the auto-profit-trader on any Docker-enabled Windows server

Write-Host "🚀 Auto Profit Trader - Remote Deployment" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "config", "logs", "data" | Out-Null

# Download the production docker-compose file if it doesn't exist
if (!(Test-Path "docker-compose.prod.yml")) {
    Write-Host "📥 Downloading production docker-compose.yml..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/meltonjoshua/auto-profit-trader/main/docker-compose.prod.yml" -OutFile "docker-compose.prod.yml"
}

# Download sample config if it doesn't exist
if (!(Test-Path "config/config.json")) {
    Write-Host "⚙️ Downloading sample configuration..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/meltonjoshua/auto-profit-trader/main/config.json" -OutFile "config/config.json"
    Write-Host "⚠️ Please edit config/config.json with your exchange API keys before starting!" -ForegroundColor Yellow
}

# Pull the latest image
Write-Host "📦 Pulling latest auto-profit-trader image..." -ForegroundColor Yellow
docker pull joshm0406/auto-profit-trader:latest

# Start the service
Write-Host "🚀 Starting auto-profit-trader..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml up -d

Write-Host "✅ Auto Profit Trader has been deployed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 To check logs: docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Cyan
Write-Host "⏹️ To stop: docker-compose -f docker-compose.prod.yml down" -ForegroundColor Cyan
Write-Host "🔄 To restart: docker-compose -f docker-compose.prod.yml restart" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️ Don't forget to configure your config/config.json with your exchange API keys!" -ForegroundColor Yellow
