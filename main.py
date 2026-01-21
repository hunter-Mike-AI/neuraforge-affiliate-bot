import os
import telebot
import google.generativeai as genai
from flask import Flask, request
import threading

# 1. CONFIGURACIÓN (Las piezas del búnker)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 2. TU CATÁLOGO (Links reales detectados en tus capturas)
# He completado los links basados en tu captura de HotLinks
PRODUCTOS = {
    "resina": {
        "nombre": "Accesorios en resina para emprender", 
        "link": "https://go.hotmart.com/X104000770T"
    },
    "velas": {
        "nombre": "Velas Artesanales como Negocio Creativo", 
        "link": "https://go.hotmart.com/X104000770T?dp=1"
    }
}

# 3. LÓGICA DE VENTAS CON RADAR (Tracking)
@bot.message_handler(func=lambda message: True)
def agente_ventas(message):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Usamos flash para mayor velocidad
        contexto = (
            f"Eres el Agente Elite de NeuraForgeAI. Tu misión es vender. "
            f"Aquí tienes tus productos y links: {PRODUCTOS}. "
            "Responde de forma breve, persuasiva y motivadora. "
            "Si el usuario está interesado, entrega el link exacto del producto."
        )
        
        response = model.generate_content(f"{contexto}\nUsuario: {message.text}")
        respuesta_ia = response.text

        # --- EL RADAR DE TRACKING ---
        # Si la IA puso un link en la respuesta, te avisa a ti de inmediato
        for clave, info in PRODUCTOS.items():
            if info['link'] in respuesta_ia:
                bot.send_message(ADMIN_CHAT_ID, f"🎯 ¡RADAR! Un prospecto recibió el link de: {info['nombre']}. ¡Casi cae la venta!")

        bot.reply_to(message, respuesta_ia)
    except Exception as e:
        print(f"Error en IA: {e}")

# 4. RECEPTOR DE DINERO (Hotmart Webhook)
@app.route('/hotmart-webhook', methods=['POST'])
def webhook():
    data = request.json
    # Registro de logs para que veas el movimiento en Render
    print(f"Evento recibido: {data.get('event')}") 
    
    if data.get("event") == "PURCHASE_APPROVED":
        nombre_prod = data['data']['product']['name']
        comision = data['data']['commission']['value']
        msg = f"💰 ¡VENTA CONFIRMADA! 💰\nProducto: {nombre_prod}\nComisión: ${comision}\n\n¡NeuraForgeAI está facturando!"
        bot.send_message(ADMIN_CHAT_ID, msg)
    
    return "OK", 200

# 5. LANZAMIENTO DUAL (Bot + Webhook)
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Arrancamos el bot en un hilo separado para que no bloquee a Flask
    threading.Thread(target=run_bot).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
