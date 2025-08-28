# Auto Profit Trader 🚀

**Professional Automated Cryptocurrency Trading Bot**

A production-ready trading bot featuring advanced arbitrage and momentum strategies, multi-exchange support, comprehensive risk management, and professional monitoring capabilities.

## 🎯 Features

### 💰 Trading Strategies
- **Arbitrage Trading**: 0.1-2% profit per trade across exchanges
- **Momentum Trading**: Technical analysis with RSI, MACD, Bollinger Bands
- **Multi-Strategy Orchestration**: Run multiple strategies simultaneously
- **Signal Confidence Scoring**: AI-powered trade signal strength assessment

### 🛡️ Safety & Security
- **API Key Encryption**: Military-grade Fernet encryption
- **Daily Loss Limits**: Configurable maximum loss thresholds
- **Stop-Loss Automation**: Automatic exit on adverse moves
- **Emergency Shutdown**: Instant system halt on unusual conditions
- **Risk Management**: Maximum 2% account risk per trade

### 📱 Notification System
- **Telegram Alerts**: Instant trade notifications
- **Discord Integration**: Rich embed notifications with status colors
- **Email Reports**: Professional HTML email reporting
- **Real-time Monitoring**: Live P&L and performance tracking

### 🔧 Technical Architecture
- **Async/Await Design**: High-performance asynchronous operations
- **Signal Handling**: Graceful shutdown (SIGINT/SIGTERM)
- **Modular Components**: Professional software architecture
- **Error Recovery**: Robust error handling and recovery
- **Database Integration**: SQLite/PostgreSQL support

### 🏢 Exchange Support
- **Binance**: Full API integration with testnet support
- **Coinbase Pro**: Professional trading interface
- **Kraken**: Advanced order management
- **Unified Interface**: Single API for all exchanges

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/meltonjoshua/auto-profit-trader.git
cd auto-profit-trader
pip install -r requirements.txt
```

### 2. Configuration
```bash
python main.py
```
On first run, a `config.json` file will be created with default settings.

### 3. Configure API Keys
Edit `config.json` and add your exchange API credentials:
```json
{
  "exchanges": {
    "binance": {
      "enabled": true,
      "api_key": "your_api_key",
      "api_secret": "your_api_secret",
      "testnet": true
    }
  }
}
```

### 4. Set Up Notifications (Optional)
Configure Telegram, Discord, or Email notifications in `config.json`:
```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token",
      "chat_id": "your_chat_id"
    }
  }
}
```

### 5. Start Trading
```bash
python main.py
```

## 📊 Performance Targets

### Expected Returns
- **Conservative Mode**: 10-20% annual returns (low risk)
- **Balanced Mode**: 20-40% annual returns (moderate risk)  
- **Aggressive Mode**: 40%+ annual returns (higher risk)

### Daily Operations
- **24/7 Trading**: Continuous market scanning
- **5-20 Opportunities**: Profitable trades daily
- **Sub-second Execution**: Lightning-fast trade execution
- **Real-time Risk Management**: Continuous portfolio protection

## 🔧 Configuration Options

### Trading Settings
```json
{
  "trading": {
    "daily_loss_limit": 100.0,
    "max_position_size": 0.02,
    "enable_arbitrage": true,
    "enable_momentum": true,
    "target_profit_arbitrage": 0.005,
    "target_profit_momentum": 0.02
  }
}
```

### Risk Management
```json
{
  "risk_management": {
    "stop_loss_percentage": 0.02,
    "take_profit_percentage": 0.05,
    "max_trades_per_day": 50,
    "cooldown_after_loss": 300
  }
}
```

### Technical Analysis
```json
{
  "technical_analysis": {
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9
  }
}
```

## 📱 Monitoring & Alerts

### Real-time Notifications
- **Trade Execution**: Instant alerts on every trade
- **Profit Milestones**: Celebrations for profit targets
- **Risk Warnings**: Immediate alerts on loss limits
- **System Status**: Startup/shutdown/error notifications

### Performance Dashboard
- **Live P&L Tracking**: Real-time profit/loss monitoring
- **Win Rate Statistics**: Success rate calculations
- **Trade History**: Comprehensive trade logs
- **Performance Metrics**: Daily/weekly/monthly summaries

## 🛡️ Security Best Practices

1. **API Permissions**: Use read-only API keys when possible
2. **Testnet First**: Always test with sandbox/testnet environments
3. **Start Small**: Begin with minimal position sizes
4. **Monitor Closely**: Keep an eye on initial performance
5. **Backup Config**: Keep secure backups of configuration

## 📝 Logging

Comprehensive logging system creates detailed logs in the `logs/` directory:
- `main.log`: System operations and startup/shutdown
- `trades.log`: All trade executions and details
- `performance.log`: Performance metrics and statistics

## 🔄 Updates & Maintenance

The bot includes automatic error recovery and graceful shutdown capabilities. For updates:

1. Stop the bot gracefully (Ctrl+C)
2. Pull latest changes
3. Review configuration for new options
4. Restart the bot

## ⚠️ Disclaimer

**Important**: Cryptocurrency trading involves substantial risk of loss. This bot is for educational and research purposes. Always:
- Start with small amounts
- Use testnet/sandbox environments
- Monitor performance closely
- Never invest more than you can afford to lose
- Understand the risks involved

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review the logs for detailed error information
- Check configuration settings
- Ensure API credentials are correct

---

**Happy Trading! 💰🚀**

*Built with ❤️ for the crypto community*