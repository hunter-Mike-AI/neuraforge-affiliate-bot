import os
import telebot
import google.generativeai as genai
from flask import Flask, request, jsonify
import hmac
import hashlib
from dotenv import load_dotenv
import requests  # ¡Importante para el dashboard!

# 🔐 Carga variables de entorno (seguro en Render)
load_dotenv()

# 1. CONFIGURACIÓN SEGURA (¡NUNCA expuestas en código!)
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
HOTMART_SECRET = os.environ.get('HOTMART_SECRET', '')  # Opcional

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 2. CATÁLOGO PROFESIONAL (con tracking UTM)
PRODUCTOS = {
    "resina": {
        "nombre": "Accesorios en Resina para Emprender",
        "link": "https://go.hotmart.com/X104000770T?utm_source=telegram&utm_medium=bot&utm_campaign=resina"
    },
    "velas": {
        "nombre": "Velas Artesanales como Negocio",
        "link": "https://go.hotmart.com/X104000770T?dp=1&utm_source=telegram&utm_medium=bot&utm_campaign=velas"
    },
    "ia": {
        "nombre": "Curso de IA para Afiliados",
        "link": "https://go.hotmart.com/TU_LINK_IA?utm_source=telegram&utm_medium=bot&utm_campaign=ia"
    }
}

# 3. EL AGENTE DE VENTAS (con IA de élite)
@bot.message_handler(func=lambda message: True)
def agente_ventas(message):
    try:
        # ✅ MEJOR MODELO PARA VENTAS: GEMINI 1.5 PRO
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        contexto = (
            "Eres 'NeuraForgeAI', el AGENTE DE VENTAS MÁS PERSUASIVO de Latinoamérica. "
            "Tu misión: VENDER cursos digitales con urgencia y emoción. "
            f"Productos disponibles: {PRODUCTOS}. "
            "REGLAS: "            "1. Sé breve (máx 2 oraciones) "
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
        respuesta_ia = response.text[:4000]  # Límite seguro de Telegram

        # 🎯 RADAR DE SEGUIMIENTO (mejorado)
        for producto in PRODUCTOS.values():
            if producto['link'] in respuesta_ia:
                bot.send_message(
                    ADMIN_CHAT_ID,
                    f"🚨 ¡OPORTUNIDAD CALIENTE!\n"
                    f"Usuario: @{message.from_user.username} (ID: {message.from_user.id})\n"
                    f"Producto: {producto['nombre']}\n"
                    f"Mensaje: {message.text[:50]}...",
                    parse_mode="HTML"
                )

        bot.reply_to(message, respuesta_ia)
    except Exception as e:
        # ❌ SIEMPRE responde aunque falle la IA
        bot.reply_to(message, "🤖 ¡Hola! Soy NeuraForgeAI. ¿En qué curso puedo ayudarte hoy? (Resina, Velas o IA)")
        print(f"🔥 Error crítico en IA: {str(e)}")

# 4. WEBHOOK DE HOTMART (con verificación de firma)
@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    # ✅ VERIFICACIÓN DE FIRMA (evita fraudes)
    if HOTMART_SECRET:
        signature = request.headers.get('x-hotmart-signature')
        body = request.data
        computed = hmac.new(HOTMART_SECRET.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, computed):
            print("⚠️ ¡Firma inválida en webhook!")
            return "Forbidden", 403

    data = request.json
    print(f"💰 [VENTA] Recibido: {data.get('event')}")

    if data.get("event") == "PURCHASE_APPROVED":
        try:            product = data['data']['product']['name']
            commission = data['data'].get('commission', {}).get('value', '0.00')
            buyer = data['data']['buyer']['name']
            
            # 📊 MENSAJE DE VENTA CON ESTADÍSTICAS
            msg = (
                f"💸 ¡VENTA CONFIRMADA! 💸\n"
                f"✅ Comprador: {buyer}\n"
                f"📦 Producto: <b>{product}</b>\n"
                f"💰 Comisión: <b>${commission}</b>\n"
                f"🔗 Enlace: https://hotmart.com/es/mi-cuenta/affiliates/sales\n\n"
                "📈 ¡NEURAFORGEAI sigue facturando!"
            )
            bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="HTML")
            
            # ✅ REGISTRA VENTA EN EL DASHBOARD (¡IMPORTANTE!)
            try:
                dashboard_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/registrar-venta"
                requests.post(dashboard_url, json={
                    "producto": product,
                    "comision": float(commission)
                }, timeout=3)
            except Exception as e:
                print(f"⚠️ Error registrando venta en dashboard: {str(e)}")
        except Exception as e:
            print(f"❌ Error procesando venta: {str(e)}")
            print(f"🔍 Data recibida: {data}")

    return jsonify({"status": "success"}), 200

# 5. WEBHOOK DE TELEGRAM (estable y seguro)
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid content-type', 400

# 6. HEALTH CHECK PARA RENDER
@app.route('/health')
def health_check():
    return jsonify({
        "status": "activo",
        "webhook": bot.get_webhook_info().url,
        "instancias": 1  # ¡Siempre 1!
    }), 200

# 7. ARRANQUE EN PRODUCCIÓN (¡SOLO WEBHOOKS!)if __name__ == "__main__":
    # 🌐 CONFIGURACIÓN DE WEBHOOK (¡clave para evitar 409!)
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/telegram-webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url, allowed_updates=['message'])

    print(f"✅ Webhook activo en: {webhook_url}")
    print("🚀 NeuraForgeAI listo para vender en producción")

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, threaded=False)  # ¡threaded=False es crucial!
