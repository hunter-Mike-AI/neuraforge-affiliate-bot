#!/usr/bin/env python3
import os
import sys
import json
import logging
from flask import Flask, request, jsonify
import telebot

# 1. CONFIGURACIÓN DE LOGS
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. VARIABLES DE ENTORNO (Configuradas en Render)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = "8362361029"  # Tu ID de administrador según tus capturas

if not TELEGRAM_TOKEN:
    logger.error("❌ ERROR: No se encontró TELEGRAM_TOKEN en las variables de entorno.")
    sys.exit(1)

# 3. INICIALIZACIÓN DEL BOT Y FLASK
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 4. HANDLERS DE COMANDOS (Estrategia de Ventas)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "<b>¡BIENVENIDO A NEURAFORGEA!</b> 🎉\n"
        "<i>Especialista en el CURSO DE RESINA EPÓXICA</i>\n\n"
        "GANA $48.5 POR CADA VENTA\n"
        "🔗 <b>Enlace:</b> https://bit.ly/4a8qXf8\n\n"
        "Comandos: /start, /link, /info, /testimonios"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

@bot.message_handler(commands=['link'])
def send_link(message):
    link_text = "🔗 <b>TU LINK DE AFILIADO:</b>\n\n<code>https://bit.ly/4a8qXf8</code>"
    bot.reply_to(message, link_text, parse_mode='HTML')

@bot.message_handler(commands=['info', 'curso'])
def send_info(message):
    info_text = (
        "🎨 <b>CURSO DE RESINA EPÓXICA COMPLETO</b>\n"
        "✅ 15 módulos HD + Certificado + Bonos Gratis\n"
        "💰 <b>Tu comisión:</b> $48.5 USD\n"
        "🔗 https://bit.ly/4a8qXf8"
    )
    bot.reply_to(message, info_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.reply_to(message, "🤖 Usa los comandos del menú o escribe /start para ver las opciones.")

# 5. RUTAS WEBHOOK (Comunicación con Telegram y Hotmart)
@app.route('/')
def home():
    return "<h1>🚀 NEURAFORGEA BOT ACTIVO</h1>", 200

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    """Lógica real para avisarte de ventas"""
    try:
        data = request.get_json()
        logger.info(f"📦 Recibido de Hotmart: {data}")

        if data.get("event") == "PURCHASE_APPROVED":
            nombre = data['data']['buyer']['name']
            producto = data['data']['product']['name']
            comision = data['data']['commission']['value']
            
            notificacion = (
                f"💰 <b>¡VENTA CONFIRMADA!</b> 💰\n\n"
                f"👤 <b>Cliente:</b> {nombre}\n"
                f"📦 <b>Producto:</b> {producto}\n"
                f"💵 <b>Comisión:</b> ${comision} USD\n\n"
                f"🚀 <i>NeuraForgeA sigue creciendo.</i>"
            )
            bot.send_message(ADMIN_ID, notificacion, parse_mode='HTML')
            
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"❌ Error en Hotmart Webhook: {e}")
        return jsonify({"error": str(e)}), 500

# 6. ARRANQUE DEL SERVIDOR
if __name__ == '__main__':
    # Configuración de Webhook en producción
    RENDER_URL = os.getenv('RENDER_EXTERNAL_URL')
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/telegram-webhook")
        logger.info(f"✅ Webhook configurado en: {RENDER_URL}/telegram-webhook")
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

