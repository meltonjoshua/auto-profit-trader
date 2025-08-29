"""
Notification system for Auto Profit Trader
Supports Telegram, Discord, and Email notifications
"""

import asyncio
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiohttp


class Notifier:
    """Handles all notification systems"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.notification_config = config_manager.get_section("notifications")

    async def send_notification(self, title: str, message: str, level: str = "info"):
        """Send notification via all enabled channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {title}\n\n{message}"

        # Send to all enabled notification channels
        tasks = []

        if self.notification_config.get("telegram", {}).get("enabled", False):
            tasks.append(self._send_telegram(title, formatted_message))

        if self.notification_config.get("discord", {}).get("enabled", False):
            tasks.append(self._send_discord(title, formatted_message, level))

        if self.notification_config.get("email", {}).get("enabled", False):
            tasks.append(self._send_email(title, formatted_message))

        # If no notifications are enabled, print to console
        if not tasks:
            print(f"📢 NOTIFICATION: {formatted_message}")
            return

        # Execute all notification tasks
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"⚠️ Notification error: {e}")

    async def _send_telegram(self, title: str, message: str):
        """Send notification via Telegram"""
        try:
            telegram_config = self.notification_config["telegram"]
            bot_token = telegram_config.get("bot_token")
            chat_id = telegram_config.get("chat_id")

            if not bot_token or not chat_id:
                print("⚠️ Telegram credentials not configured")
                return

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

            # Format message for Telegram
            formatted_message = f"🤖 *{title}*\n\n{message}"

            payload = {
                "chat_id": chat_id,
                "text": formatted_message,
                "parse_mode": "Markdown",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        print("✅ Telegram notification sent")
                    else:
                        print(f"❌ Telegram error: {response.status}")

        except Exception as e:
            print(f"❌ Telegram notification failed: {e}")

    async def _send_discord(self, title: str, message: str, level: str = "info"):
        """Send notification via Discord webhook"""
        try:
            discord_config = self.notification_config["discord"]
            webhook_url = discord_config.get("webhook_url")

            if not webhook_url:
                print("⚠️ Discord webhook not configured")
                return

            # Set color based on level
            colors = {
                "info": 0x3498DB,  # Blue
                "success": 0x2ECC71,  # Green
                "warning": 0xF39C12,  # Orange
                "error": 0xE74C3C,  # Red
            }

            embed = {
                "title": title,
                "description": message,
                "color": colors.get(level, colors["info"]),
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Auto Profit Trader"},
            }

            payload = {"embeds": [embed]}

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        print("✅ Discord notification sent")
                    else:
                        print(f"❌ Discord error: {response.status}")

        except Exception as e:
            print(f"❌ Discord notification failed: {e}")

    async def _send_email(self, title: str, message: str):
        """Send notification via email"""
        try:
            email_config = self.notification_config["email"]

            smtp_server = email_config.get("smtp_server")
            smtp_port = email_config.get("smtp_port", 587)
            username = email_config.get("username")
            password = email_config.get("password")
            to_email = email_config.get("to_email")

            if not all([smtp_server, username, password, to_email]):
                print("⚠️ Email credentials not fully configured")
                return

            # Create message
            msg = MIMEMultipart()
            msg["From"] = username
            msg["To"] = to_email
            msg["Subject"] = f"Auto Profit Trader: {title}"

            # Add HTML formatting
            html_message = f"""
            <html>
                <body>
                    <h2 style="color: #2c3e50;">{title}</h2>
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db;">
                        <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{message}</pre>
                    </div>
                    <hr>
                    <p style="color: #7f8c8d; font-size: 12px;">
                        Sent by Auto Profit Trader at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </p>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_message, "html"))

            # Send email in a separate thread to avoid blocking
            def send_email_sync():
                try:
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(username, password)
                        server.send_message(msg)
                    print("✅ Email notification sent")
                except Exception as e:
                    print(f"❌ Email send failed: {e}")

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, send_email_sync)

        except Exception as e:
            print(f"❌ Email notification failed: {e}")

    async def send_trade_alert(
        self, symbol: str, side: str, amount: float, price: float, profit: float
    ):
        """Send trade execution alert"""
        emoji = "📈" if side.upper() == "BUY" else "📉"
        profit_emoji = "💰" if profit > 0 else "📉" if profit < 0 else "➖"

        title = f"{emoji} Trade Executed: {symbol}"
        message = f"""
Side: {side.upper()}
Amount: {amount:.6f}
Price: ${price:.4f}
Profit: ${profit:.4f} {profit_emoji}
        """.strip()

        level = "success" if profit > 0 else "warning" if profit < 0 else "info"
        await self.send_notification(title, message, level)

    async def send_profit_milestone(self, daily_profit: float, total_profit: float):
        """Send profit milestone notification"""
        title = "💰 Profit Milestone Reached!"
        message = f"""
Daily Profit: ${daily_profit:.2f}
Total Profit: ${total_profit:.2f}

Keep up the great work! 🚀
        """.strip()

        await self.send_notification(title, message, "success")

    async def send_risk_alert(self, alert_type: str, details: str):
        """Send risk management alert"""
        title = f"⚠️ Risk Alert: {alert_type}"
        await self.send_notification(title, details, "warning")

    async def send_system_alert(
        self, alert_type: str, details: str, level: str = "info"
    ):
        """Send system status alert"""
        emoji_map = {
            "startup": "🚀",
            "shutdown": "🛑",
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
        }

        emoji = emoji_map.get(alert_type, "ℹ️")
        title = f"{emoji} System Alert: {alert_type.title()}"
        await self.send_notification(title, details, level)
