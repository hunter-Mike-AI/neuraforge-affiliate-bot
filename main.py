#!/usr/bin/env python3
"""
NEURAFORGEA BOT - SISTEMA DE VENTAS INTELIGENTE
Versión definitiva para Termux y Render
"""

import os
import sys
import json
import logging
from flask import Flask, request
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
    logger.error("❌ ERROR: No se encontró config.json")
    logger.error("   Ejecuta: nano config.json")
    sys.exit(1)

# Token de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or CONFIG.get('TELEGRAM_TOKEN', '')

if not TELEGRAM_TOKEN:
    logger.error("❌ ERROR: No se encontró TELEGRAM_TOKEN en config.json")
    logger.error("   Agrega: \"TELEGRAM_TOKEN\": \"tu_token_aqui\"")
    sys.exit(1)

# Inicializar bot
try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot_info = bot.get_me()
    logger.info(f"✅ Bot inicializado: @{bot_info.username}")
except Exception as e:
    logger.error(f"❌ Error inicializando bot: {e}")
    sys.exit(1)

# Inicializar Flask
app = Flask(__name__)

# ================= HANDLERS DEL BOT =================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Manejador del comando /start"""
    try:
        chat_id = message.chat.id
        logger.info(f"📨 /start recibido de {chat_id}")
        
        welcome_text = """
<b>¡BIENVENIDO A NEURAFORGEA!</b> 🎉
<i>Especialistas en el CURSO DE RESINA EPÓXICA</i>

<b>GANA $48.5 POR CADA VENTA</b>

🔗 <b>Enlace de afiliado:</b> <a href="https://bit.ly/4a8qXf8">https://bit.ly/4a8qXf8</a>

<b>Comandos disponibles:</b>
/start - Este mensaje
/link - Obtener link de afiliado  
/info - Ver información del producto
/curso - Detalles del curso
/comision - Sistema de ganancias

<em>¡Comparte el enlace y gana comisiones!</em>
"""
        bot.reply_to(message, welcome_text, parse_mode='HTML')
        logger.info(f"✅ /start enviado a {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en /start: {e}")

@bot.message_handler(commands=['link'])
def send_link(message):
    """Manejador del comando /link"""
    try:
        link_text = """
🔗 <b>TU LINK DE AFILIADO:</b>

<code>https://bit.ly/4a8qXf8</code>

<b>📤 Cómo compartir:</b>
1. Copia el link de arriba
2. Compártelo en redes sociales  
3. Gana $48.5 por cada venta

<b>💰 Ejemplo de ganancias:</b>
• 10 ventas = $485
• 20 ventas = $970  
• 50 ventas = $2,425

<em>¡El link ya tiene tu código de afiliado incluido!</em>
"""
        bot.reply_to(message, link_text, parse_mode='HTML')
        logger.info(f"✅ /link enviado a {message.chat.id}")
    except Exception as e:
        logger.error(f"Error en /link: {e}")

@bot.message_handler(commands=['info', 'curso'])
def send_course_info(message):
    """Manejador del comando /info y /curso"""
    try:
        course_text = """
🎨 <b>CURSO DE RESINA EPÓXICA COMPLETO</b>

<b>✅ LO QUE INCLUYE:</b>
• 15 módulos en video HD
• Técnicas profesionales
• Certificado digital  
• Acceso de por vida
• Soporte 24/7

<b>🎁 BONOS GRATIS:</b>
• Plantillas para Instagram
• Guía de precios de venta
• Comunidad privada
• Actualizaciones gratis

<b>💰 INVERSIÓN:</b>
• Precio normal: $97 USD
• Tu comisión: $48.5 por venta
• Pago único, sin mensualidades

<b>🔗 VER CURSO:</b>
<a href="https://bit.ly/4a8qXf8">https://bit.ly/4a8qXf8</a>

<em>Promociona este link y gana $48.5 por cada compra</em>
"""
        bot.reply_to(message, course_text, parse_mode='HTML')
        logger.info(f"✅ /info enviado a {message.chat.id}")
    except Exception as e:
        logger.error(f"Error en /info: {e}")

@bot.message_handler(commands=['comision', 'ganancias'])
def send_commission_info(message):
    """Manejador del comando /comision"""
    try:
        commission_text = """
💰 <b>SISTEMA DE COMISIONES</b>

<b>💵 Ganas por cada venta:</b>
• $48.5 USD (50% de comisión)

<b>📊 Ejemplos de ganancias mensuales:</b>
• 1 venta/día = $1,455/mes
• 2 ventas/día = $2,910/mes  
• 5 ventas/día = $7,275/mes

<b>🔄 Cómo recibes el pago:</b>
• Hotmart paga cada 30 días
• Paypal, transferencia, etc.
• Sin límite de ganancias

<b>📈 Recomendaciones:</b>
1. Comparte en grupos de manualidades
2. Usa historias de Instagram
3. Contacta amigos/familiares  
4. Publica en Facebook Marketplace

🔗 <b>Tu link:</b> <a href="https://bit.ly/4a8qXf8">https://bit.ly/4a8qXf8</a>
"""
        bot.reply_to(message, commission_text, parse_mode='HTML')
        logger.info(f"✅ /comision enviado a {message.chat.id}")
    except Exception as e:
        logger.error(f"Error en /comision: {e}")

@bot.message_handler(commands=['testimonios'])
def send_testimonials(message):
    """Manejador del comando /testimonios"""
    try:
        testimonials_text = """
📢 <b>TESTIMONIOS REALES</b>

👩 <b>María G. - México:</b>
<em>"Aprendí resina con este curso y ahora vendo mis creaciones en ferias locales. ¡En mi primer mes gané $800!"</em>

👨 <b>Carlos R. - Colombia:</b>
<em>"Dejé mi trabajo y ahora vivo de las manualidades con resina. El curso me dio todas las herramientas."</em>

👩 <b>Ana L. - Argentina:</b>
<em>"Como afiliada, gano comisiones recomendando el curso. Es mi ingreso extra perfecto."</em>

👨 <b>José M. - Perú:</b>
<em>"Invertí en el curso y en 2 semanas recuperé mi inversión con las primeras ventas."</em>

🎯 <b>¿Listo para tu historia de éxito?</b>

🔗 <a href="https://bit.ly/4a8qXf8">EMPEZAR AHORA</a>
"""
        bot.reply_to(message, testimonials_text, parse_mode='HTML')
        logger.info(f"✅ /testimonios enviado a {message.chat.id}")
    except Exception as e:
        logger.error(f"Error en /testimonios: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Responde a cualquier mensaje no reconocido"""
    try:
        response = """
🤖 <b>Comandos disponibles:</b>

/start - Mensaje de bienvenida
/link - Obtener link de afiliado
/info - Ver información del curso
/comision - Sistema de ganancias
/testimonios - Casos de éxito

<em>Usa uno de los comandos de arriba</em>
"""
        bot.reply_to(message, response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error en echo_all: {e}")

# ================= WEBHOOK PARA RENDER =================
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 NEURAFORGEA BOT</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #2c3e50; }
            .status { color: #27ae60; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🚀 NEURAFORGEA BOT</h1>
        <h2>Sistema de Ventas Inteligente</h2>
        <hr>
        <p><strong>Producto:</strong> Curso de Resina Epóxica</p>
        <p><strong>Comisión:</strong> $48.5 por venta</p>
        <p><strong>Link:</strong> <a href="https://bit.ly/4a8qXf8">https://bit.ly/4a8qXf8</a></p>
        <p><strong>Estado:</strong> <span class="status">✅ EN LÍNEA</span></p>
        <hr>
        <p>Bot de Telegram para afiliados Hotmart</p>
        <p>Admin ID: 8362361029</p>
    </body>
    </html>
    """

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Webhook para Telegram (solo Render)"""
    try:
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return 'error', 500

@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    """Webhook para Hotmart"""
    try:
        data = request.get_json()
        logger.info(f"📦 Webhook de Hotmart recibido")
        
        # Aquí procesarías la venta
        # Por ahora solo logueamos
        if data:
            logger.info(f"📊 Datos: {json.dumps(data, indent=2)}")
        
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook de Hotmart: {e}")
        return 'error', 500

# ================= INICIO SEGÚN ENTORNO =================
def setup_webhook():
    """Configurar webhook solo si estamos en producción (Render)"""
    try:
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_url:
            webhook_url = f"{render_url}/telegram-webhook"
            bot.remove_webhook()
            bot.set_webhook(url=webhook_url)
            logger.info(f"✅ Webhook configurado: {webhook_url}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error configurando webhook: {e}")
        return False

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🚀 INICIANDO NEURAFORGEA BOT")
    logger.info("=" * 50)
    
    logger.info(f"🤖 Bot: @{bot_info.username}")
    logger.info(f"🔗 Link: {CONFIG.get('AFFILIATE_LINK', 'https://bit.ly/4a8qXf8')}")
    logger.info(f"💰 Comisión: ${CONFIG.get('COMMISSION', 48.5)}")
    
    # Detectar entorno
    is_render = 'RENDER' in os.environ or os.getenv('RENDER_EXTERNAL_URL')
    
    if is_render:
        # MODO PRODUCCIÓN (Render) - Webhook + Flask
        logger.info("🌐 Modo: Producción (Webhook)")
        
        if setup_webhook():
            port = int(os.getenv('PORT', 10000))
            logger.info(f"🔧 Puerto: {port}")
            logger.info("🔄 Iniciando servidor Flask...")
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            logger.error("❌ No se pudo configurar webhook")
            sys.exit(1)
    else:
        # MODO DESARROLLO (Termux) - Polling
        logger.info("📱 Modo: Termux (Polling)")
        
        # Detener webhook si existe
        try:
            bot.remove_webhook()
            logger.info("✅ Webhook detenido")
        except:
            pass
        
        logger.info("🔄 Iniciando polling...")
        logger.info("📨 Envía /start a tu bot en Telegram")
        logger.info("=" * 50)
        
        # Iniciar polling
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"❌ Error en polling: {e}")
            logger.error("🔄 Reiniciando en 5 segundos...")
            import time
            time.sleep(5)
            # Reintentar
            bot.polling(none_stop=True, interval=1, timeout=30)
