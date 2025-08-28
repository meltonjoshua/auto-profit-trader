#!/bin/bash
# Auto Profit Trader - Production Deployment Script
# Sets up the bot for autonomous 24/7 operation

set -e

echo "🚀 Auto Profit Trader - Production Deployment"
echo "============================================="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Do not run this script as root. Create a dedicated user instead."
   exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$(echo "$python_version < 3.8" | bc)" -eq 1 ]]; then
    echo "❌ Python 3.8 or higher required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-pip python3-venv

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p backups

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/autotrader > /dev/null <<EOF
$(pwd)/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
    postrotate
        systemctl reload autotrader || true
    endscript
}
EOF

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp autotrader.service /etc/systemd/system/
sudo sed -i "s|/opt/auto-profit-trader|$(pwd)|g" /etc/systemd/system/autotrader.service
sudo sed -i "s|User=trader|User=$(whoami)|g" /etc/systemd/system/autotrader.service
sudo sed -i "s|Group=trader|Group=$(whoami)|g" /etc/systemd/system/autotrader.service
sudo sed -i "s|/usr/bin/python3|$(pwd)/venv/bin/python|g" /etc/systemd/system/autotrader.service

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "✅ Production deployment complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Run configuration: python production_setup.py"
echo "2. Test manually: python trader_daemon.py"
echo "3. Enable service: sudo systemctl enable autotrader"
echo "4. Start service: sudo systemctl start autotrader"
echo "5. Check status: sudo systemctl status autotrader"
echo "6. View logs: journalctl -u autotrader -f"
echo ""
echo "📊 Monitoring:"
echo "- Logs: $(pwd)/logs/"
echo "- Database: $(pwd)/portfolio.db"
echo "- Performance: $(pwd)/performance.json"
echo ""
echo "🛑 Management:"
echo "- Stop: sudo systemctl stop autotrader"
echo "- Restart: sudo systemctl restart autotrader"
echo "- Disable: sudo systemctl disable autotrader"
echo ""
echo "💰 Your autonomous trading bot is ready!"