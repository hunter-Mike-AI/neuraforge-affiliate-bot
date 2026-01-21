# config.py
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
COOLDOWN_SECONDS = int(os.environ.get("COOLDOWN_SECONDS", "60"))
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])
