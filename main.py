#!/usr/bin/env python3
"""
NEURAFORGEA BOT - SISTEMA DE VENTAS INTELIGENTE
Versión estable para Render.com
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
import telebot
import json

# ================= CONFIGURACIÓN =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Cargar configuración
try:
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
except:
    CONFIG = {}
    logger.warning("⚠️ No se encontró config.json, usando valores por defecto")

# Token de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or CONFIG.get('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error("❌ ERROR: No se encontró TELEGRAM_TOKEN")
    logger.error("   Configura en Render: Environment -> TELEGRAM_TOKEN")
    # NO salimos - dejamos que el servidor corra pero sin bot
    bot = None
else:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    logger.info("✅ Bot de Telegram inicializado")

# ================= RUTAS WEB =================
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 NEURAFORGEA BOT</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; }
            h1 { color: #2c3e50; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🚀 NEURAFORGEA BOT</h1>
        <h2>SISTEMA DE VENTAS INTELIGENTE</h2>
        <hr>
        <p><strong>Producto:</strong> Curso de Resina Epóxica</p>
        <p><strong>Comisión:</strong> $48.5 por venta</p>
        <p><strong>Link:</strong> <a href="http://bit.ly/3LsKPAo">http://bit.ly/3LsKPAo</a></p>
        <p><strong>Estado:</strong> <span class="status">✅ EN LÍNEA</span></p>
        <hr>
        <p>Bot de Telegram para afiliados Hotmart</p>
        <p>Admin ID: 8362361029</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Endpoint para verificar salud del servicio (Render lo usa)"""
    return jsonify({
        "status": "healthy",
        "service": "NeuraForgea Affiliate Bot",
        "timestamp": os.datetime.now().isoformat()
    })

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Webhook para Telegram"""
    if bot is None:
        return "Bot no configurado", 500
    
    try:
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook de Telegram: {e}")
        return 'error', 500

@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    """Webhook para Hotmart"""
    try:
        data = request.get_json()
        logger.info(f"📦 Webhook de Hotmart recibido: {data}")
        
        # Aquí procesas la venta
        # Por ahora solo logueamos
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook de Hotmart: {e}")
        return 'error', 500

# ================= HANDLERS DEL BOT =================
if bot:
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        try:
            welcome_text = """
            ¡BIENVENIDO A NEURAFORGEA! 🎉
            
            Especialistas en el CURSO DE RESINA EPÓXICA
            
            GANA $48.5 POR CADA VENTA
            
            🔗 Enlace de afiliado: http://bit.ly/3LsKPAo
            
            Comandos disponibles:
            /start - Este mensaje
            /link - Obtener link de afiliado
            /info - Ver información del producto
            
            ¡Comparte el enlace y gana comisiones!
            """
            bot.reply_to(message, welcome_text)
            logger.info(f"✅ /start respondido a {message.chat.id}")
        except Exception as e:
            logger.error(f"Error en /start: {e}")

    @bot.message_handler(commands=['link'])
    def send_link(message):
        try:
            bot.reply_to(message, "🔗 Enlace de afiliado: https://bit.ly/4a8qXf8")
        except Exception as e:
            logger.error(f"Error en /link: {e}")

# ================= INICIO SEGURO =================
def configure_webhook():
    """Configurar webhook solo si estamos en producción"""
    if not bot:
        return
    
    try:
        # En Render, esta variable existe
        render_external_url = os.getenv('RENDER_EXTERNAL_URL')
        
        if render_external_url:
            webhook_url = f"{render_external_url}/telegram-webhook"
            bot.remove_webhook()
            bot.set_webhook(url=webhook_url)
            logger.info(f"✅ Webhook configurado: {webhook_url}")
            return True
        else:
            logger.warning("⚠️ No se encontró RENDER_EXTERNAL_URL")
            logger.warning("   Ejecutando en modo desarrollo sin webhook")
            bot.remove_webhook()
            return False
    except Exception as e:
        logger.error(f"❌ Error configurando webhook: {e}")
        return False

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🚀 INICIANDO NEURAFORGEA BOT")
    logger.info("=" * 50)
    
    # Configurar webhook si hay bot
    webhook_configured = False
    if bot:
        webhook_configured = configure_webhook()
    
    # Obtener puerto (Render asigna uno automático)
    port = int(os.getenv('PORT', 10000))
    
    # Información del sistema
    logger.info(f"🔧 Puerto: {port}")
    logger.info(f"🔧 Webhook: {'✅ Configurado' if webhook_configured else '❌ No configurado'}")
    logger.info(f"🔧 Bot: {'✅ Activo' if bot else '❌ Inactivo'}")
    logger.info(f"🔧 Debug: {'✅ ON' if os.getenv('FLASK_DEBUG') else '❌ OFF'}")
    
    # INICIAR SERVIDOR FLASK (ESTA ES LA ÚLTIMA LÍNEA)
    # No poner NADA después de app.run()
    logger.info(f"🌐 Servidor iniciando en http://0.0.0.0:{port}")
    logger.info("=" * 50)
    
    # 🚨 IMPORTANTE: debug=False en producción
    app.run(host='0.0.0.0', port=port, debug=False)
