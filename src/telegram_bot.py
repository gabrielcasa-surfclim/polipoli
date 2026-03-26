import os
import time
from collections import deque
from typing import Optional

import requests


class TelegramBot:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self._last_sent = deque(maxlen=10)

        if not self.token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurado.")

    def send(self, message: str) -> bool:
        now = time.time()
        if self._last_sent and now - self._last_sent[-1] < 1:
            time.sleep(1)

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            self._last_sent.append(time.time())
            return True
        except Exception:
            return False
