from telebot import TeleBot
from config import TELEGRAM_TOKEN, COOLDOWN_SECONDS
from database import init_db, get_connection
from security import can_proceed
from affiliates.hotmart import generate_link

bot = TeleBot(TELEGRAM_TOKEN)
init_db()

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(
        msg,
        "🐝 Bienvenido a NeuraForgeAI\n\n"
        "/hotmart - Generar enlace\n"
        "/ayuda - Info"
    )

@bot.message_handler(commands=['hotmart'])
def hotmart(msg):
    user_id = msg.from_user.id

    if not can_proceed(user_id, COOLDOWN_SECONDS):
        bot.reply_to(msg, "⏳ Espera un momento antes de generar otro enlace.")
        return

    link = generate_link(user_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO links (telegram_id, platform, url) VALUES (?, ?, ?)",
        (user_id, "hotmart", link)
    )
    conn.commit()
    conn.close()

    bot.reply_to(msg, f"🔗 Tu enlace Hotmart:\n{link}")

bot.polling(none_stop=True)	
