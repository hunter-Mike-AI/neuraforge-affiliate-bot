import os
import random
import threading
import time
from dotenv import load_dotenv
load_dotenv()

import telebot
from flask import Flask, request
import google.generativeai as genai  # ✅ CORREGIDO

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']  # ✅ CORREGIDO
HOTMART_SECRET = os.environ.get('HOTMART_SECRET', '')

# Definir PRODUCTOS (faltaba en tu código)
PRODUCTOS = {
    'ia': {
        'nombre': 'Curso de IA para Afiliados',
        'link': 'https://go.hotmart.com/TU_LINK_IA'
    },
    'resina': {
        'nombre': 'Curso de Resina Epóxica',
        'link': 'https://go.hotmart.com/TU_LINK_RESINA'
    },
    'velas': {
        'nombre': 'Curso de Velas Artesanales',
        'link': 'https://go.hotmart.com/TU_LINK_VELAS'
    }
}

genai.configure(api_key=GEMINI_API_KEY)  # ✅ AHORA SÍ FUNCIONARÁ
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Lista de destinos para difusión (canales/grupos)
DESTINOS_DIFUSION = [
    -1001234567890,  # Reemplaza con tu canal/grupo real
    -1009876543210,
]

# Usuarios interesados pero sin compra (retargeting)
USUARIOS_INTERESADOS = {}

def verificar_links():  # ✅ FUNCIÓN AÑADIDA
    """Verifica que todos los links de productos estén configurados"""
    for key, producto in PRODUCTOS.items():
        if 'TU_LINK' in producto['link']:
            print(f"⚠️ ADVERTENCIA: El link para '{producto['nombre']}' no ha sido configurado")

def generar_mensaje_promocional():
    prompt = (
        "Eres NeuraForgeAI, el agente de ventas más persuasivo. "
        "Promociona un curso digital con urgencia y emoción. "
        "Sé breve, usa emojis, y dirige al link."
    )
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    return response.text[:4000]

def difundir_mensaje():
    try:
        mensaje = generar_mensaje_promocional()
        for chat_id in DESTINOS_DIFUSION:
            bot.send_message(chat_id, mensaje, parse_mode="HTML")
        print("✅ Difusión enviada")
    except Exception as e:
        print(f"⚠️ Error en difusión: {str(e)}")

def iniciar_difusion_automatica():
    intervalo = random.randint(1800, 3600)  # cada 30–60 min
    threading.Timer(intervalo, lambda: [difundir_mensaje(), iniciar_difusion_automatica()]).start()

def enviar_recordatorio(usuario_id):
    try:
        bot.send_message(
            usuario_id,
            "👋 ¡Hola! Ayer preguntaste por nuestros cursos. ¿Ya viste el de IA para afiliados? 💡\n"
            "👉 https://go.hotmart.com/TU_LINK_IA?utm_source=telegram&utm_medium=bot&utm_campaign=retargeting",
            parse_mode="HTML"
        )
        print(f"📣 Recordatorio enviado a {usuario_id}")
    except Exception as e:
        print(f"⚠️ Error en recordatorio: {str(e)}")

def iniciar_retargeting():
    for usuario_id, timestamp in list(USUARIOS_INTERESADOS.items()):
        if time.time() - timestamp > 86400:  # 24 horas
            enviar_recordatorio(usuario_id)
            del USUARIOS_INTERESADOS[usuario_id]
    threading.Timer(3600, iniciar_retargeting).start()  # revisa cada hora

@app.route('/telegram-webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Unsupported Media Type', 415

@bot.message_handler(func=lambda message: True)
def agente_ventas(message):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        contexto = (
            "Eres 'NeuraForgeAI', el AGENTE DE VENTAS MÁS PERSUASIVO de Latinoamérica. "
            "Tu misión: VENDER cursos digitales con urgencia y emoción. "
            f"Productos disponibles: {PRODUCTOS}. "
            "REGLAS: "
            "1. Sé breve (máx 2 oraciones) "
            "2. Usa emojis estratégicos (🔥, 💰, 🚨) "
            "3. Si pregunta precios, DIRIGE AL LINK. "
            "4. Si es escéptico, usa testimonios falsos pero creíbles: 'María ganó $500 en su primera semana'."
        )
        response = model.generate_content(
            f"{contexto}\nUsuario: {message.text}",
            generation_config=genai.GenerationConfig(
                max_output_tokens=150,
                temperature=0.85,
            )
        )
        respuesta_ia = response.text[:4000]

        # 🎯 RADAR DE SEGUIMIENTO + RETARGETING
        interesado = False
        for producto in PRODUCTOS.values():
            if producto['link'] in respuesta_ia:
                interesado = True
                bot.send_message(
                    ADMIN_CHAT_ID,
                    f"🚨 ¡OPORTUNIDAD CALIENTE!\n"
                    f"Usuario: @{message.from_user.username} (ID: {message.from_user.id})\n"
                    f"Producto: {producto['nombre']}\n"
                    f"Mensaje: {message.text[:50]}...",
                    parse_mode="HTML"
                )

        if interesado:
            USUARIOS_INTERESADOS[message.from_user.id] = time.time()

        bot.reply_to(message, respuesta_ia)
    except Exception as e:
        bot.reply_to(message, "🤖 ¡Hola! Soy NeuraForgeAI. ¿En qué curso puedo ayudarte hoy? (Resina, Velas o IA)")
        print(f"🔥 Error crítico en IA: {str(e)}")

# 🔁 INICIO DE DIFUSIÓN Y RETARGETING
if __name__ == "__main__":
    verificar_links()
    iniciar_difusion_automatica()
    iniciar_retargeting()

    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/telegram-webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url, allowed_updates=['message'])

    print(f"✅ Webhook activo en: {webhook_url}")
    print("🚀 NeuraForgeAI listo para vender en producción")

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, threaded=False)
