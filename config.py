import os

BOT_NAME = "NeuraForge Affiliate Bot"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))

# Seguridad
MAX_LINKS_PER_DAY = 10
COOLDOWN_SECONDS = 30	

