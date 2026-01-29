import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def send_alert(self, title: str, message: str, severity: str = "CRITICAL"):
        logger.error(f"ALERT [{severity}]: {title} - {message}")
        
        self._send_email(title, message)
        self._send_telegram(title, message)
        self._send_webhook(title, message)

    def _send_email(self, title, message):
        # Mock Email Alert
        print(f"[MOCK EMAIL] To: admin@example.com | Subject: {title} | Body: {message}")

    def _send_telegram(self, title, message):
        # Mock Telegram Alert
        print(f"[MOCK TELEGRAM] Sending: {title} - {message}")

    def _send_webhook(self, title, message):
        # Mock Webhook Alert
        print(f"[MOCK WEBHOOK] POST /alerts/webhook data: {{'title': '{title}', 'message': '{message}'}}")

# Global instance for easy access
alerts = AlertSystem()
