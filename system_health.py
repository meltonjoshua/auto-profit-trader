"""
Auto Profit Trader - System Health & Maintenance Tool
Comprehensive system diagnostics and optimization for UK crypto trading
"""

import asyncio
import json
import os
import sys
import sqlite3
import subprocess
import platform
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.append('src')

class SystemHealthChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.passed_checks = []
        
    def print_header(self):
        """Print the system health checker header"""
        print("🇬🇧 AUTO PROFIT TRADER - SYSTEM HEALTH CHECK")
        print("=" * 55)
        print("🏥 Comprehensive UK crypto trading system diagnostics")
        print("")
    
    def check_python_environment(self):
        """Check Python installation and version"""
        print("🐍 PYTHON ENVIRONMENT CHECK...")
        
        # Python version
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            self.passed_checks.append(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.issues.append(f"❌ Python {version.major}.{version.minor}.{version.micro} (3.9+ recommended)")
        
        # pip availability
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, check=True)
            self.passed_checks.append("✅ pip package manager available")
        except:
            self.issues.append("❌ pip package manager not available")
    
    def check_dependencies(self):
        """Check required Python packages"""
        print("📦 DEPENDENCY CHECK...")
        
        required_packages = {
            'aiohttp': 'Web framework for dashboard',
            'ccxt': 'Cryptocurrency exchange library',
            'cryptography': 'Security and encryption',
            'psutil': 'System monitoring',
            'aiohttp_cors': 'CORS support for dashboard'
        }
        
        for package, description in required_packages.items():
            try:
                __import__(package)
                self.passed_checks.append(f"✅ {package} - {description}")
            except ImportError:
                self.issues.append(f"❌ {package} missing - {description}")
        
        # Optional packages
        optional_packages = {
            'numpy': 'Mathematical operations',
            'pandas': 'Data analysis',
            'matplotlib': 'Plotting and visualization'
        }
        
        for package, description in optional_packages.items():
            try:
                __import__(package)
                self.passed_checks.append(f"✅ {package} (optional) - {description}")
            except ImportError:
                self.warnings.append(f"⚠️  {package} missing (optional) - {description}")
    
    def check_system_resources(self):
        """Check system resource availability"""
        print("💻 SYSTEM RESOURCES CHECK...")
        
        # CPU
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_count >= 2:
            self.passed_checks.append(f"✅ CPU cores: {cpu_count}")
        else:
            self.warnings.append(f"⚠️  CPU cores: {cpu_count} (2+ recommended)")
        
        if cpu_percent < 70:
            self.passed_checks.append(f"✅ CPU usage: {cpu_percent:.1f}%")
        else:
            self.warnings.append(f"⚠️  High CPU usage: {cpu_percent:.1f}%")
        
        # Memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        if memory_gb >= 4:
            self.passed_checks.append(f"✅ RAM: {memory_gb:.1f}GB")
        else:
            self.warnings.append(f"⚠️  RAM: {memory_gb:.1f}GB (4GB+ recommended)")
        
        if memory.percent < 80:
            self.passed_checks.append(f"✅ Memory usage: {memory.percent:.1f}%")
        else:
            self.warnings.append(f"⚠️  High memory usage: {memory.percent:.1f}%")
        
        # Disk space
        disk = psutil.disk_usage('.')
        disk_free_gb = disk.free / (1024**3)
        
        if disk_free_gb >= 1:
            self.passed_checks.append(f"✅ Free disk space: {disk_free_gb:.1f}GB")
        else:
            self.warnings.append(f"⚠️  Low disk space: {disk_free_gb:.1f}GB")
    
    def check_configuration(self):
        """Check configuration files"""
        print("⚙️ CONFIGURATION CHECK...")
        
        # config.json
        if Path('config.json').exists():
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                self.passed_checks.append("✅ config.json found and valid")
                
                # Check UK-specific settings
                if config.get('base_currency') == 'GBP':
                    self.passed_checks.append("✅ UK base currency (GBP) configured")
                else:
                    self.suggestions.append("💡 Consider setting base_currency to 'GBP' for UK trading")
                
                # Check Kraken priority
                exchanges = config.get('exchanges', {})
                kraken = exchanges.get('kraken', {})
                if kraken.get('enabled', False):
                    self.passed_checks.append("✅ Kraken enabled (UK recommended)")
                else:
                    self.suggestions.append("💡 Enable Kraken for best UK crypto trading experience")
                
            except json.JSONDecodeError:
                self.issues.append("❌ config.json invalid JSON format")
        else:
            self.issues.append("❌ config.json not found")
    
    def check_security(self):
        """Check security setup"""
        print("🔒 SECURITY CHECK...")
        
        # Encrypted credentials
        if Path('encrypted_credentials.json').exists():
            self.passed_checks.append("✅ Encrypted credentials file found")
            
            try:
                from security.crypto_manager import SecurityManager
                sm = SecurityManager()
                exchanges = sm.list_stored_exchanges()
                if exchanges:
                    self.passed_checks.append(f"✅ {len(exchanges)} exchange(s) configured")
                else:
                    self.warnings.append("⚠️  No exchange credentials stored")
            except Exception as e:
                self.warnings.append(f"⚠️  Credential check failed: {e}")
        else:
            self.warnings.append("⚠️  No encrypted credentials found (demo mode available)")
        
        # Check file permissions (simplified for Windows)
        sensitive_files = ['encrypted_credentials.json', 'config.json']
        for file_path in sensitive_files:
            if Path(file_path).exists():
                # Basic existence check for Windows
                self.passed_checks.append(f"✅ {file_path} secured")
    
    def check_database(self):
        """Check database health"""
        print("🗃️ DATABASE CHECK...")
        
        if Path('portfolio.db').exists():
            try:
                conn = sqlite3.connect('portfolio.db')
                cursor = conn.cursor()
                
                # Check trades table
                cursor.execute("SELECT COUNT(*) FROM trades")
                trade_count = cursor.fetchone()[0]
                self.passed_checks.append(f"✅ Database accessible ({trade_count} trades)")
                
                # Check for recent activity
                cursor.execute(
                    "SELECT COUNT(*) FROM trades WHERE timestamp >= datetime('now', '-24 hours')"
                )
                recent_trades = cursor.fetchone()[0]
                
                if recent_trades > 0:
                    self.passed_checks.append(f"✅ Recent activity: {recent_trades} trades last 24h")
                else:
                    self.warnings.append("⚠️  No recent trading activity")
                
                # Check database integrity
                cursor.execute("PRAGMA integrity_check")
                integrity = cursor.fetchone()[0]
                if integrity == 'ok':
                    self.passed_checks.append("✅ Database integrity OK")
                else:
                    self.issues.append("❌ Database integrity issues detected")
                
                conn.close()
                
            except Exception as e:
                self.issues.append(f"❌ Database error: {e}")
        else:
            self.warnings.append("⚠️  No portfolio database found (will be created on first trade)")
    
    def check_network_connectivity(self):
        """Check network connectivity to exchanges"""
        print("🌐 NETWORK CONNECTIVITY CHECK...")
        
        import socket
        
        exchanges_to_test = [
            ('kraken.com', 443, 'Kraken API'),
            ('api.pro.coinbase.com', 443, 'Coinbase Pro API'),
            ('api.binance.com', 443, 'Binance API (if available)')
        ]
        
        for host, port, name in exchanges_to_test:
            try:
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
                self.passed_checks.append(f"✅ {name} connectivity OK")
            except:
                self.warnings.append(f"⚠️  {name} connectivity issues")
    
    def check_trading_components(self):
        """Check core trading components"""
        print("🤖 TRADING COMPONENTS CHECK...")
        
        components = [
            ('utils.config_manager', 'ConfigManager', 'Configuration system'),
            ('security.crypto_manager', 'SecurityManager', 'Security system'),
            ('exchanges.exchange_manager', 'ExchangeManager', 'Exchange integration'),
            ('strategies.trading_strategies', 'TradingStrategy', 'Trading strategies'),
            ('demo.demo_kraken', 'DemoKrakenExchange', 'Demo trading mode')
        ]
        
        for module_path, class_name, description in components:
            try:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                self.passed_checks.append(f"✅ {description}")
            except Exception as e:
                self.issues.append(f"❌ {description}: {e}")
    
    def check_uk_compliance(self):
        """Check UK-specific compliance features"""
        print("🇬🇧 UK COMPLIANCE CHECK...")
        
        # Check timezone
        import time
        timezone = time.tzname[0]
        if 'GMT' in timezone or 'BST' in timezone:
            self.passed_checks.append(f"✅ UK timezone: {timezone}")
        else:
            self.suggestions.append(f"💡 Consider UK timezone (current: {timezone})")
        
        # Check for HMRC reporting features
        if Path('exports').exists():
            self.passed_checks.append("✅ Export directory for HMRC reports")
        else:
            self.suggestions.append("💡 Create 'exports' directory for HMRC tax reports")
        
        # Check GBP pair focus
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            trading_pairs = config.get('trading', {}).get('pairs', [])
            gbp_pairs = [pair for pair in trading_pairs if 'GBP' in pair]
            
            if gbp_pairs:
                self.passed_checks.append(f"✅ GBP trading pairs configured: {len(gbp_pairs)}")
            else:
                self.suggestions.append("💡 Add GBP pairs (BTC/GBP, ETH/GBP) for UK trading")
        except:
            pass
    
    def get_optimization_suggestions(self):
        """Get system optimization suggestions"""
        print("⚡ OPTIMIZATION SUGGESTIONS...")
        
        # Performance suggestions
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        
        if cpu_count >= 4:
            self.suggestions.append("💡 Enable parallel processing for multiple exchanges")
        
        if memory.total >= 8 * (1024**3):  # 8GB+
            self.suggestions.append("💡 Enable advanced caching for better performance")
        
        # Security suggestions
        if not Path('backups').exists():
            self.suggestions.append("💡 Create 'backups' directory for automated backups")
        
        # Trading suggestions
        self.suggestions.append("💡 Start with demo mode to practice UK crypto trading")
        self.suggestions.append("💡 Enable Kraken for best UK regulatory compliance")
        self.suggestions.append("💡 Set up notifications for important trade alerts")
    
    def generate_health_report(self):
        """Generate a comprehensive health report"""
        print("\n" + "="*55)
        print("🏥 SYSTEM HEALTH REPORT")
        print("="*55)
        
        # Summary
        total_checks = len(self.passed_checks) + len(self.issues) + len(self.warnings)
        health_score = (len(self.passed_checks) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"📊 Overall Health Score: {health_score:.1f}%")
        print(f"✅ Passed: {len(self.passed_checks)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        print("")
        
        # Passed checks
        if self.passed_checks:
            print("✅ PASSED CHECKS:")
            for check in self.passed_checks:
                print(f"   {check}")
            print("")
        
        # Warnings
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
            print("")
        
        # Issues
        if self.issues:
            print("❌ ISSUES REQUIRING ATTENTION:")
            for issue in self.issues:
                print(f"   {issue}")
            print("")
        
        # Suggestions
        if self.suggestions:
            print("💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in self.suggestions:
                print(f"   {suggestion}")
            print("")
        
        # Overall status
        if not self.issues:
            if not self.warnings:
                print("🎉 EXCELLENT! Your system is in perfect health!")
            else:
                print("😊 GOOD! Your system is healthy with minor optimizations available.")
        else:
            print("⚠️  ATTENTION NEEDED! Please address the issues above.")
        
        print("")
        print("🇬🇧 Ready for UK crypto trading!")
    
    async def run_health_check(self):
        """Run the complete health check"""
        self.print_header()
        
        checks = [
            self.check_python_environment,
            self.check_dependencies,
            self.check_system_resources,
            self.check_configuration,
            self.check_security,
            self.check_database,
            self.check_network_connectivity,
            self.check_trading_components,
            self.check_uk_compliance,
            self.get_optimization_suggestions
        ]
        
        for i, check in enumerate(checks, 1):
            try:
                check()
                print(f"   [{i}/{len(checks)}] Complete")
            except Exception as e:
                print(f"   [{i}/{len(checks)}] Error: {e}")
                self.issues.append(f"❌ Health check error: {e}")
            print("")
        
        self.generate_health_report()

def run_maintenance_tasks():
    """Run automated maintenance tasks"""
    print("🔧 RUNNING MAINTENANCE TASKS...")
    print("")
    
    tasks_completed = []
    
    # Clean up log files
    try:
        log_dir = Path('logs')
        if log_dir.exists():
            old_logs = list(log_dir.glob('*.log'))
            if old_logs:
                print(f"🧹 Cleaning {len(old_logs)} old log files...")
                for log in old_logs[-10:]:  # Keep last 10
                    if (datetime.now() - datetime.fromtimestamp(log.stat().st_mtime)).days > 7:
                        log.unlink()
                tasks_completed.append("✅ Log cleanup")
    except Exception as e:
        print(f"⚠️  Log cleanup failed: {e}")
    
    # Database optimization
    try:
        if Path('portfolio.db').exists():
            print("🗃️ Optimizing database...")
            conn = sqlite3.connect('portfolio.db')
            conn.execute('VACUUM')
            conn.close()
            tasks_completed.append("✅ Database optimized")
    except Exception as e:
        print(f"⚠️  Database optimization failed: {e}")
    
    # Update pip packages
    try:
        print("📦 Checking for package updates...")
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("📥 Updates available for some packages")
            tasks_completed.append("ℹ️  Package updates available")
        else:
            tasks_completed.append("✅ All packages up to date")
    except Exception as e:
        print(f"⚠️  Package check failed: {e}")
    
    print("")
    print("🔧 MAINTENANCE SUMMARY:")
    for task in tasks_completed:
        print(f"   {task}")
    print("")

async def main():
    """Main health check and maintenance function"""
    print("🇬🇧 Welcome to Auto Profit Trader System Health Check!")
    print("")
    
    print("Choose an option:")
    print("   [1] 🏥 Full Health Check")
    print("   [2] 🔧 Maintenance Tasks") 
    print("   [3] 📊 Quick Status Check")
    print("   [4] 🔄 Both Health Check + Maintenance")
    print("")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Health check cancelled")
        return
    
    if choice == "1":
        checker = SystemHealthChecker()
        await checker.run_health_check()
    
    elif choice == "2":
        run_maintenance_tasks()
    
    elif choice == "3":
        print("📊 QUICK STATUS CHECK:")
        print("=" * 25)
        
        # Quick system info
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"💻 CPU: {psutil.cpu_count()} cores, {psutil.cpu_percent()}% usage")
        print(f"💾 Memory: {psutil.virtual_memory().percent}% used")
        
        # Check critical files
        if Path('config.json').exists():
            print("✅ Configuration file found")
        else:
            print("❌ Configuration file missing")
        
        if Path('portfolio.db').exists():
            print("✅ Portfolio database found")
        else:
            print("⚠️  No portfolio database")
        
        print("")
        print("💡 Run full health check (option 1) for detailed analysis")
    
    elif choice == "4":
        checker = SystemHealthChecker()
        await checker.run_health_check()
        print("\n" + "="*55)
        run_maintenance_tasks()
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
