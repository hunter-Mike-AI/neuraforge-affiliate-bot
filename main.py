#!/usr/bin/env python3
import os
import sys
import json
import logging
from flask import Flask, request, jsonify
import telebot

# 1. CONFIGURACIÓN DE LOGS PARA RENDER
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. CONFIGURACIÓN DE IDENTIDAD
# Tu ID de administrador confirmado por los logs anteriores
ADMIN_ID = "8362361029" 
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    logger.error("❌ ERROR: TELEGRAM_TOKEN no configurado en Environment de Render")
    sys.exit(1)

# Inicializar bot y servidor
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 3. HANDLERS DE COMANDOS (Atención al Cliente)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "<b>¡BIENVENIDO A NEURAFORGEA!</b> 🎉\n"
        "<i>Especialistas en el CURSO DE RESINA EPÓXICA</i>\n\n"
        "<b>Beneficios del Curso:</b>\n"
        "• Aprende desde cero técnicas profesionales.\n"
        "• Certificación al finalizar.\n"
        "• Acceso de por vida.\n\n"
        "🔗 <b>Enlace de Acceso:</b> <a href='https://bit.ly/4a8qXf8'>Haz clic aquí para ver el curso</a>\n\n"
        "Usa /info para ver detalles o /link para tu enlace de afiliado."
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')
    logger.info(f"✅ /start enviado a {message.chat.id}")

@bot.message_handler(commands=['link'])
def send_link(message):
    link_text = (
        "🔗 <b>TU LINK DE AFILIADO LISTO:</b>\n\n"
        "<code>https://bit.ly/4a8qXf8</code>\n\n"
        "Recuerda que ganas <b>$48.5 USD</b> por cada venta realizada a través de este enlace."
    )
    bot.reply_to(message, link_text, parse_mode='HTML')

@bot.message_handler(commands=['info', 'curso'])
def send_info(message):
    info_text = (
        "⚠️ ¡ATENCIÓN: PROMOCIÓN POR TIEMPO LIMITADO! ⚠️\n\n"
        "El productor ha activado un contador regresivo. Una vez que llegue a cero, "
        "el bono de descuento y los regalos desaparecerán para siempre. ⏳\n\n"
        "🎨 CURSO DE RESINA EPÓXICA\n"
        "• Acceso inmediato a los 15 módulos.\n"
        "• Certificado oficial incluido.\n\n"
        "💰 PRECIO ESPECIAL: Solo por las próximas horas.\n"
        "🔗 VER CUENTA REGRESIVA AQUÍ:\n"
        "https://bit.ly/4a8qXf8"
    )
    bot.reply_to(message, info_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Respuesta por defecto para guiar al usuario
    bot.reply_to(message, "🤖 Usa los comandos del menú o escribe /start para ver las opciones.")

# 4. RUTAS PARA WEBHOOKS (Integración con Hotmart y Telegram)
@app.route('/')
def home():
    return "<h1>🚀 NEURAFORGEA BOT OPERATIVO</h1>", 200

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'forbidden', 403

@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    """Recibe notificaciones de ventas de Hotmart y te avisa al Telegram"""
    try:
        data = request.get_json()
        # Verificamos si es una compra aprobada
        if data.get("event") == "PURCHASE_APPROVED":
            comprador = data['data']['buyer']['name']
            producto = data['data']['product']['name']
            comision = data['data']['commission']['value']
            
            notificacion = (
                f"💰 <b>¡NUEVA VENTA CONFIRMADA!</b> 💰\n\n"
                f"👤 <b>Cliente:</b> {comprador}\n"
                f"📦 <b>Producto:</b> {producto}\n"
                f"💵 <b>Tu Comisión:</b> ${comision} USD\n\n"
                f"✅ <i>El sistema ha registrado el pago correctamente.</i>"
            )
            bot.send_message(ADMIN_ID, notificacion, parse_mode='HTML')
            logger.info("💸 Notificación de venta enviada al administrador.")
            
        return jsonify({"status": "received"}), 200
    except Exception as e:
        logger.error(f"❌ Error en Hotmart Webhook: {e}")
        return jsonify({"error": str(e)}), 500

# 5. ARRANQUE DEL SISTEMA
if __name__ == '__main__':
    # Configuración automática del Webhook en Render
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    if render_url:
        webhook_path = f"{render_url}/telegram-webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_path)
        logger.info(f"🌐 Webhook configurado en: {webhook_path}")
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
