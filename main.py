import os
import telebot
import google.generativeai as genai
from flask import Flask, request, jsonify
from datetime import datetime

# 1. CARGAR LLAVES (Primero las piezas)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 2. INICIALIZAR OBJETOS (Compramos las máquinas)
genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 3. TU CATÁLOGO COMERCIAL
PRODUCTOS = {
    "resina": {"nombre": "Accesorios en Resina", "link": "https://go.hotmart.com/X104000770T"},
    "velas": {"nombre": "Velas Artesanales", "link": "https://go.hotmart.com/F104000855I"},
    "sublimacion": {"nombre": "Negocio de la Sublimación", "link": "https://go.hotmart.com/F104000799H"},
    "cinvest": {"nombre": "CinvestClub", "link": "https://go.hotmart.com/Y104000802F"},
    "aparatologia": {"nombre": "Fórmula Brasileña con Aparatología", "link": "https://go.hotmart.com/N104000786E"}
}

# 4. LÓGICA DE VENTAS CON IA
@bot.message_handler(func=lambda message: True)
def agente_ventas(message):
    model = genai.GenerativeModel('gemini-pro')
    contexto = f"Eres NeuraForgeAI. Tienes estos productos: {PRODUCTOS}. Recomienda el adecuado según el interés del usuario. Sé persuasivo y entrega el link correspondiente."
    response = model.generate_content(f"{contexto}\nUsuario: {message.text}")
    bot.reply_to(message, response.text)

# 5. RECEPTOR DE DINERO (WEBHOOK)
@app.route('/hotmart-webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("event") == "PURCHASE_APPROVED":
        prod_name = data['data']['product']['name']
        msg = f"💰 ¡VENTA CONFIRMADA! 💰\nProducto: {prod_name}\nEl sistema NeuraForge está funcionando!"
        bot.send_message(ADMIN_CHAT_ID, msg)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
