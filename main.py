#!/usr/bin/env python3
"""
NEURAFORGEA BOT - SISTEMA DE VENTAS INTELIGENTE
Versión corregida para Termux y Render
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify
import telebot
from telebot import types

# ================= CONFIGURACIÓN =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar configuración
CONFIG = {}
try:
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    logger.warning("⚠️ Creando config.json básico...")
    CONFIG = {
        "TELEGRAM_TOKEN": "",
        "ADMIN_ID": 8362361029,
        "AFFILIATE_LINK": "https://bit.ly/4a8qXf8"
    }
    with open('config.json', 'w') as f:
        json.dump(CONFIG, f, indent=2)

# Token de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or CONFIG.get('TELEGRAM_TOKEN', '')

if not TELEGRAM_TOKEN:
    logger.error("❌ ERROR: No se encontró TELEGRAM_TOKEN")
    logger.error("📋 Solución:")
    logger.error("   1. Edita config.json: nano config.json")
    logger.error("   2. Agrega tu token de @BotFather")
    logger.error("   3. Guarda y reinicia el bot")
    sys.exit(1)

# Inicializar bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)
logger.info(f"✅ Bot inicializado: @{bot.get_me().username}")

# Inicializar Flask
app = Flask(__name__)

# ================= RUTAS WEB =================
@app.route('/')
def home():
    return "🚀 NEURAFORGEA BOT - Sistema de Afiliados"

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    try:
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return 'error', 500

# ================= HANDLERS DEL BOT =================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
*¡BIENVENIDO A NEURAFORGEA\!* 🎉
*Especialistas en el CURSO DE RESINA EPÓXICA*

*GANA \\$48.5 POR CADA VENTA*

🔗 *Enlace de afiliado:* [https://bit.ly/4a8qXf8](https://bit.ly/4a8qXf8)

*Comandos disponibles:*
/start - Este mensaje
/link - Obtener link de afiliado
/info - Ver información del producto

_¡Comparte el enlace y gana comisiones\!_
"""
    bot.reply_to(message, welcome_text, parse_mode='MarkdownV2')

@bot.message_handler(commands=['link'])
def send_link(message):
    bot.reply_to(message, "🔗 *Enlace de afiliado:* [https://bit.ly/4a8qXf8](https://bit.ly/4a8qXf8)", 
                parse_mode='MarkdownV2')

@bot.message_handler(commands=['info'])
def send_info(message):
    info_text = """
*📦 CURSO DE RESINA EPÓXICA*

*💰 Precio:* \\$97 USD
*💵 Tu comisión:* \\$48.5 por venta
*📚 Módulos:* 15
*🎓 Certificado:* Sí
*🕒 Acceso:* De por vida

*🎁 BONOS INCLUIDOS:*
• Plantillas para Instagram
• Guía de ventas
• Comunidad privada
• Soporte 24/7

🔗 [Ver curso completo](https://bit.ly/4a8qXf8)
"""
    bot.reply_to(message, info_text, parse_mode='MarkdownV2')

# ================= INICIO =================
if __name__ == '__main__':
    logger.info("🚀 Iniciando NEURAFORGEA BOT")
    logger.info(f"🤖 Bot: @{bot.get_me().username}")
    
    # Configurar webhook solo si está en Render
    if 'RENDER' in os.environ:
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_url:
            webhook_url = f"{render_url}/telegram-webhook"
            bot.remove_webhook()
            bot.set_webhook(url=webhook_url)
            logger.info(f"✅ Webhook configurado: {webhook_url}")
    
    # Iniciar Flask
    port = int(os.getenv('PORT', 10000))
    logger.info(f"🌐 Servidor en puerto: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
