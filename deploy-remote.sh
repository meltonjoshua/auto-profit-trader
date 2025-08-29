#!/bin/bash
# Auto Profit Trader Remote Deployment Script
# This script can be used to deploy the auto-profit-trader on any Docker-enabled server

echo "🚀 Auto Profit Trader - Remote Deployment"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p config logs data

# Download the production docker-compose file if it doesn't exist
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "📥 Downloading production docker-compose.yml..."
    curl -o docker-compose.prod.yml https://raw.githubusercontent.com/meltonjoshua/auto-profit-trader/main/docker-compose.prod.yml
fi

# Download sample config if it doesn't exist
if [ ! -f "config/config.json" ]; then
    echo "⚙️ Downloading sample configuration..."
    curl -o config/config.json https://raw.githubusercontent.com/meltonjoshua/auto-profit-trader/main/config.json
    echo "⚠️ Please edit config/config.json with your exchange API keys before starting!"
fi

# Pull the latest image
echo "📦 Pulling latest auto-profit-trader image..."
docker pull joshm0406/auto-profit-trader:latest

# Start the service
echo "🚀 Starting auto-profit-trader..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Auto Profit Trader has been deployed!"
echo ""
echo "📊 To check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "⏹️ To stop: docker-compose -f docker-compose.prod.yml down"
echo "🔄 To restart: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "⚠️ Don't forget to configure your config/config.json with your exchange API keys!"
