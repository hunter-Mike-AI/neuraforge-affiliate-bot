import os
import threading
import time
import schedule
from telebot import TeleBot
from flask import Flask, request, jsonify
from config import TELEGRAM_TOKEN, COOLDOWN_SECONDS, ADMIN_CHAT_ID
from database import init_db, get_connection
from security import can_proceed
from affiliates.hotmart import generate_link

# Inicialización
bot = TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)
init_db()

# --- LÓGICA DEL BOT DE TELEGRAM ---

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(
        msg,
        "🐝 Bienvenido a NeuraForgeAI\n\n"
        "/hotmart - Generar enlace manual\n"
        "/status - Verificar sistema"
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
        "INSERT INTO links (telegram_id, platform, url) VALUES (%s, %s, %s)",
        (user_id, "hotmart", link)
    )
    conn.commit()
    conn.close()
    bot.reply_to(msg, f"🔗 Tu enlace Hotmart:\n{link}")

# --- LÓGICA DE BÚSQUEDA AUTOMÁTICA ---

def buscar_oferta_del_dia():
    link = generate_link("AUTO_SYSTEM")
    mensaje = (
        "🚀 **OFERTA AUTOMÁTICA NEURAFORGE** 🚀\n\n"
        "Sistema de búsqueda activa: Producto detectado.\n"
        f"🔗 Enlace: {link}"
    )
    bot.send_message(ADMIN_CHAT_ID, mensaje, parse_mode="Markdown")

schedule.every().day.at("09:00").do(buscar_oferta_del_dia)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- LÓGICA DE WEBHOOK (RECEPCIÓN DE VENTAS) ---

@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    data = request.json
    event = data.get("event")
    
    product_name = data.get("data", {}).get("product", {}).get("name", "Producto Desconocido")
    price = data.get("data", {}).get("purchase", {}).get("commission", {}).get("value", 0)

    if event == "PURCHASE_APPROVED":
        mensaje = (
            "💰 **¡VENTA CONFIRMADA!** 💰\n\n"
            f"Felicidades Miguel, has vendido: *{product_name}*\n"
            f"Comisión estimada: *${price}*\n\n"
            "¡El sistema NeuraForge está funcionando!"
        )
        bot.send_message(ADMIN_CHAT_ID, mensaje, parse_mode="Markdown")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=bot.polling, kwargs={'non_stop': True}, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
