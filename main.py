import os
import telebot
import google.generativeai as genai
from flask import Flask, request, jsonify
from datetime import datetime

# LEER VARIABLES DIRECTO DE RENDER
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# DICCIONARIO DE PRODUCTOS (Tu nueva base de datos comercial)
PRODUCTOS = {
    "resina": {
        "nombre": "Accesorios en Resina",
        "link": "https://go.hotmart.com/X104000770T",
        "ventas_actuales": 0,
        "fecha_inicio": datetime.now()
    },
    "velas": {
        "nombre": "Velas Artesanales",
        "link": "https://go.hotmart.com/F104000855I",
        "ventas_actuales": 0,
        "fecha_inicio": datetime.now()
    },
    "sublimacion": {
        "nombre": "Negocio de la Sublimación",
        "link": "https://go.hotmart.com/F104000799H",
        "ventas_actuales": 0,
        "fecha_inicio": datetime.now()
    },
    "cinvest": {
        "nombre": "CinvestClub",
        "link": "https://go.hotmart.com/Y104000802F",
        "ventas_actuales": 0,
        "fecha_inicio": datetime.now()
    },
    "aparatologia": {
        "nombre": "Fórmula Brasileña con Aparatología",
        "link": "https://go.hotmart.com/N104000786E",
        "ventas_actuales": 0,
        "fecha_inicio": datetime.now()
    }
}

@bot.message_handler(func=lambda message: True)
def agente_ventas(message):
    model = genai.GenerativeModel('gemini-pro')
    # Contexto para que Gemini sepa qué vender
    contexto = f"Eres NeuraForgeAI. Tienes estos productos: {PRODUCTOS}. Recomienda el más adecuado según el interés del usuario. Sé persuasivo."
    response = model.generate_content(f"{contexto}\nUsuario: {message.text}")
    bot.reply_to(message, response.text)

@app.route('/hotmart-webhook', methods=['POST'])
def webhook():
    data = request.json
    # Aquí es donde el bot "aprende" qué se vende para la rotación futura
    if data.get("event") == "PURCHASE_APPROVED":
        prod_name = data['data']['product']['name']
        bot.send_message(ADMIN_CHAT_ID, f"💰 ¡Venta de {prod_name} confirmada!")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
