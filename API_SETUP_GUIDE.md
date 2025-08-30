# 🔑 API SETUP GUIDE - Auto Profit Trader

Your trading bot needs API access to cryptocurrency exchanges to execute trades. Here's everything you need to set up:

## 🎯 **QUICK ANSWER: What APIs Do You Need?**

### **Required APIs:**
1. **Cryptocurrency Exchange APIs** (at least one):
   - 🟡 **Binance API** (recommended - most popular)
   - 🔵 **Coinbase Pro API** (US-friendly)
   - 🟠 **Kraken API** (European-friendly)

### **Optional APIs:**
2. **Notification APIs** (for alerts):
   - 📱 **Telegram Bot API** (trade notifications)
   - 💬 **Discord Webhook** (community alerts)
   - 📧 **Email SMTP** (profit/loss reports)

---

## 🚀 **STEP-BY-STEP SETUP**

### **STEP 1: Choose Your Exchange(s) - UK OPTIMIZED**

#### 🇬🇧 **Kraken (BEST FOR UK)**
- **Why:** FCA-regulated, GBP support, UK-friendly
- **Supports:** Full UK regulation & compliance
- **Fees:** 0.16-0.26% trading fee
- **GBP Pairs:** BTC/GBP, ETH/GBP, ADA/GBP
- **Setup Link:** https://www.kraken.com/
- **UK Benefits:** Direct GBP deposits, UK bank transfers

#### 🟡 **Binance (Currently Unavailable in UK)**
- **Status:** Service suspended in UK (August 2025)
- **Why:** Regulatory reorganization with FCA
- **Alternative:** Use Kraken or Coinbase Pro instead
- **Note:** May return in future with FCA authorization
- **Current Message:** "Our service is not available at this time"

#### 🔵 **Coinbase Pro (UK Regulated)** 
- **Why:** UK-regulated, beginner-friendly
- **Supports:** Full UK operations, GBP support
- **Fees:** 0.5% trading fee
- **GBP Pairs:** BTC/GBP, ETH/GBP
- **Setup Link:** https://pro.coinbase.com/

#### ⭐ **UK RECOMMENDATION: Kraken + Coinbase Pro**
- **Kraken** for primary trading (FCA-regulated, GBP pairs)
- **Coinbase Pro** for backup/additional liquidity
- **Binance** = Currently unavailable in UK
- **Result:** Better regulatory compliance and consumer protection!

---

### **STEP 2: Get Your API Keys**

#### 🟡 **For Binance:**
1. Log into your Binance account
2. Go to **Account** → **API Management**
3. Click **Create API**
4. Name it: "Auto Profit Trader"
5. **IMPORTANT PERMISSIONS:**
   - ✅ **Spot & Margin Trading** (required)
   - ✅ **Read Info** (required)
   - ❌ **Futures** (disable for safety)
   - ❌ **Withdrawals** (disable for safety)
6. **Restrict IP:** Add your home IP for extra security
7. Save your **API Key** and **Secret Key**

#### 🔵 **For Coinbase Pro:**
1. Log into Coinbase Pro
2. Go to **Settings** → **API**
3. Click **+ New API Key**
4. **Permissions:**
   - ✅ **View** (required)
   - ✅ **Trade** (required)
   - ❌ **Transfer** (disable for safety)
5. Save your **API Key**, **Secret**, and **Passphrase**

#### 🇬🇧 **For Kraken (UK PRIORITY):**
1. Log into Kraken (UK-regulated exchange)
2. Go to **Settings** → **API**
3. Click **Generate New Key**
4. **Name it:** "Auto Profit Trader UK"
5. **Permissions:**
   - ✅ **Query Funds** (required)
   - ✅ **Query Open Orders** (required)
   - ✅ **Query Closed Orders** (required)
   - ✅ **Query Trades History** (required)
   - ✅ **Create & Modify Orders** (required)
   - ❌ **Withdraw Funds** (disable for security)
   - ❌ **Export Data** (disable)
6. **IP Restriction:** Add your UK IP for extra security
7. Save your **API Key** and **Private Key**
8. **UK Bonus:** Enable GBP pairs: BTC/GBP, ETH/GBP, ADA/GBP

---

### **STEP 3: Add APIs to Your Bot**

#### 🔐 **Secure Method (Recommended):**
Run this command to securely store your API keys:

```powershell
python -c "
from src.security.crypto_manager import SecurityManager
sm = SecurityManager()

# For Binance:
sm.encrypt_api_credentials('binance', 'YOUR_API_KEY', 'YOUR_SECRET_KEY')

# For Coinbase:
sm.encrypt_api_credentials('coinbase', 'YOUR_API_KEY', 'YOUR_SECRET_KEY')

# For Kraken:
sm.encrypt_api_credentials('kraken', 'YOUR_API_KEY', 'YOUR_SECRET_KEY')

print('✅ API keys encrypted and stored securely!')
"
```

#### 📝 **Manual Method:**
Edit `config.json` and add your keys:

```json
{
  "exchanges": {
    "binance": {
      "enabled": true,
      "api_key": "YOUR_BINANCE_API_KEY",
      "api_secret": "YOUR_BINANCE_SECRET",
      "testnet": true
    },
    "coinbase": {
      "enabled": false,
      "api_key": "",
      "api_secret": "",
      "testnet": true
    }
  }
}
```

---

### **STEP 4: Test Your Setup**

Run this to verify your API connections:

```powershell
python -c "
import asyncio
from src.exchanges.exchange_manager import ExchangeManager
from src.utils.config_manager import ConfigManager
from src.security.crypto_manager import SecurityManager

async def test_apis():
    config = ConfigManager()
    security = SecurityManager()
    exchange_mgr = ExchangeManager(config, security)
    
    await exchange_mgr.initialize_exchanges()
    
    for name, exchange in exchange_mgr.exchanges.items():
        balance = await exchange_mgr.get_balance(name)
        print(f'✅ {name}: Connected successfully')
        print(f'   USDT Balance: {balance.get(\"USDT\", {}).get(\"total\", 0)}')
    
    await exchange_mgr.shutdown()

asyncio.run(test_apis())
"
```

---

## 🛡️ **SECURITY BEST PRACTICES**

### **🔒 API Key Security:**
- ✅ **Never share** your API keys
- ✅ **Disable withdrawals** on all API keys
- ✅ **Use IP restrictions** when possible
- ✅ **Start with testnet/sandbox** mode
- ✅ **Store keys encrypted** (our bot does this automatically)

### **💰 Risk Management:**
- ✅ **Start small** - test with $50-100
- ✅ **Enable testnet** first (paper trading)
- ✅ **Set daily loss limits** in config.json
- ✅ **Monitor regularly** via dashboard

---

## 📱 **OPTIONAL: Notification Setup**

### **Telegram Notifications:**
1. Create a Telegram bot: https://t.me/BotFather
2. Get your bot token
3. Get your chat ID: https://t.me/userinfobot
4. Add to config:
```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID"
    }
  }
}
```

### **Email Notifications:**
```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your.email@gmail.com",
      "password": "your_app_password",
      "to_email": "your.email@gmail.com"
    }
  }
}
```

---

## 🎯 **NEXT STEPS**

1. **Choose your exchange** (Binance recommended)
2. **Create account** and enable 2FA
3. **Generate API keys** with trading permissions
4. **Add keys to bot** using secure method
5. **Test connection** with our verification script
6. **Start with testnet** mode enabled
7. **Launch dashboard** to monitor: `.\launch_dashboard.ps1`
8. **Start trading bot**: `.\start_trader_windows.ps1`

---

## ❓ **FREQUENTLY ASKED QUESTIONS**

**Q: Which exchange should I choose?**
A: Binance for most users, Coinbase Pro for US users wanting regulation

**Q: Is it safe to give API access?**
A: Yes, when you disable withdrawals and use proper permissions

**Q: Can I use multiple exchanges?**
A: Yes! The bot supports arbitrage between exchanges

**Q: What if I don't want to risk real money?**
A: Keep "testnet": true in config for paper trading

**Q: How much money do I need?**
A: Start with $50-100 for testing, scale up as you gain confidence

---

🚀 **Ready to start trading?** Follow the steps above and you'll be monitoring profits on your dashboard in minutes!
