import os
import time
import threading
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import telebot
from flask import Flask, request
from telebot import types

# =================== CONFIGURACIÓN ===================
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# --- PRODUCTO ÚNICO (Curso de Resina) ---
PRODUCTO = {
    'nombre': 'Curso de Resina Epóxica',
    'precio': 97,  # Precio del curso (ajustar si es diferente)
    'comision': 48.5,  # Tu comisión (50%)
    'link': 'https://bit.ly/3NMYgvz',  # Tu link de afiliado
    'bonus': '🔥 BONUS: Kit de herramientas profesionales + Plantillas de Instagram',
    'testimonios': [
        "María facturó $800 en su primera semana con resina",
        "Juan dejó su trabajo y ahora vive de sus creaciones",
        "Ana triplicó sus ingresos en 2 meses"
    ]
}

# =================== GESTOR INTELIGENTE DE APIs ===================
class APIManager:
    """Sistema inteligente que selecciona la mejor API según el lead y ventas"""
    
    def __init__(self):
        self.apis = {
            'deepseek': {
                'name': 'DeepSeek',
                'url': 'https://api.deepseek.com/v1/chat/completions',
                'key': DEEPSEEK_API_KEY,
                'cost_per_1k': 0.0,
                'monthly_tokens': 5000000,
                'tokens_used': 0,
                'active': True,
                'priority': 1
            },
            'gpt35': {
                'name': 'GPT-3.5 Turbo',
                'url': 'https://api.openai.com/v1/chat/completions',
                'key': OPENAI_API_KEY,
                'cost_per_1k': 0.0015,
                'monthly_budget': 20,
                'spent': 0,
                'active': False,  # Se activa con ventas
                'priority': 2
            },
            'gemini': {
                'name': 'Gemini Pro',
                'url': f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}',
                'key': GEMINI_API_KEY,
                'cost_per_1k': 0.0,
                'rate_limit': 60,
                'active': True,
                'priority': 3
            }
        }
        
        self.monthly_revenue = 0
        self.total_sales = 0
        self.conversion_log = []
        
        print("🤖 Gestor de APIs inicializado")
        print(f"   - DeepSeek: {'✅ Activo' if self.apis['deepseek']['active'] else '❌ Inactivo'}")
        print(f"   - GPT-3.5: {'✅ Activo' if self.apis['gpt35']['active'] else '❌ Inactivo'}")
        print(f"   - Gemini: {'✅ Activo' if self.apis['gemini']['active'] else '❌ Inactivo'}")
    
    def register_sale(self, amount):
        """Registra una venta y actualiza la estrategia de APIs"""
        self.monthly_revenue += amount
        self.total_sales += 1
        
        print(f"💰 Venta registrada: ${amount} | Total mes: ${self.monthly_revenue}")
        
        # Lógica de escalado automático
        if self.monthly_revenue >= 100 and not self.apis['gpt35']['active']:
            self.apis['gpt35']['active'] = True
            print("🚀 Activando GPT-3.5 (ventas > $100)")
        
        # Guardar log
        self.conversion_log.append({
            'date': datetime.now().isoformat(),
            'amount': amount,
            'monthly_revenue': self.monthly_revenue
        })
    
    def detect_lead_value(self, message_text):
        """Detecta el valor potencial del lead basado en el mensaje"""
        text = message_text.lower()
        
        # Palabras clave de ALTO valor
        high_value_keywords = ['comprar', 'quiero', 'compro', 'pagar', 'tarjeta', 'cupo', 'ahora', 'inmediato']
        
        # Palabras clave de MEDIO valor
        medium_value_keywords = ['precio', 'cuesta', 'valor', 'cuánto', 'información', 'detalles', 'cómo funciona']
        
        if any(word in text for word in high_value_keywords):
            return 'high'  # Cliente listo para comprar
        elif any(word in text for word in medium_value_keywords):
            return 'medium'  # Cliente interesado
        else:
            return 'low'  # Cliente curioso
    
    def select_api(self, lead_value):
        """Selecciona la API óptima para el lead"""
        
        # Lead de ALTO valor: usa la mejor API disponible
        if lead_value == 'high':
            if self.apis['gpt35']['active']:
                return 'gpt35'
            elif self.apis['gemini']['active']:
                return 'gemini'
            else:
                return 'deepseek'
        
        # Lead de MEDIO valor: usa API balanceada
        elif lead_value == 'medium':
            if self.apis['gemini']['active']:
                return 'gemini'
            else:
                return 'deepseek'
        
        # Lead de BAJO valor: usa API gratuita
        else:
            return 'deepseek'
    
    def generate_response(self, user_message):
        """Genera una respuesta usando la API seleccionada"""
        
        # Detectar valor del lead
        lead_value = self.detect_lead_value(user_message)
        
        # Seleccionar API
        api_name = self.select_api(lead_value)
        api = self.apis[api_name]
        
        print(f"🎯 Lead: {lead_value.upper()} | API: {api['name']}")
        
        # Preparar prompt optimizado para ventas
        prompt = self._create_sales_prompt(user_message)
        
        # Llamar a la API correspondiente
        if api_name == 'deepseek':
            return self._call_deepseek(prompt, api)
        elif api_name == 'gpt35':
            return self._call_openai(prompt, api)
        elif api_name == 'gemini':
            return self._call_gemini(prompt, api)
        else:
            return self._fallback_response()
    
    def _create_sales_prompt(self, user_message):
        """Crea un prompt optimizado para vender el curso de resina"""
        
        return f"""
        Eres 'NeuraForgeAI', un experto en el curso de RESINA EPÓXICA.
        Tu única misión es vender este curso.
        
        INFORMACIÓN DEL CURSO:
        • Nombre: {PRODUCTO['nombre']}
        • Precio: ${PRODUCTO['precio']} USD
        • Incluye: {PRODUCTO['bonus']}
        • Link de compra: {PRODUCTO['link']}
        • Testimonios reales: {', '.join(PRODUCTO['testimonios'])}
        
        REGLAS DE VENTA:
        1. Responde SIEMPRE sobre el curso de resina
        2. Sé breve (2-3 oraciones máximo)
        3. Usa emojis relevantes (🎨, 💰, 🔥, 🚀)
        4. Incluye UN testimonio en cada respuesta
        5. Termina SIEMPRE con el link de compra
        6. Crea URGENCIA: "Solo 5 cupos disponibles hoy"
        
        Usuario dice: "{user_message}"
        
        Tu respuesta (2-3 oraciones, con emojis y testimonio):
        """
    
    def _call_deepseek(self, prompt, api):
        """Llama a la API de DeepSeek"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api['key']}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.8,
                "stream": False
            }
            
            if not api['key']:
                # Intentar sin API key (puede funcionar para pruebas)
                del headers["Authorization"]
            
            response = requests.post(api['url'], headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ DeepSeek error: {response.status_code}")
                return self._fallback_response()
                
        except Exception as e:
            print(f"🔥 Error DeepSeek: {e}")
            return self._fallback_response()
    
    def _call_openai(self, prompt, api):
        """Llama a la API de OpenAI GPT-3.5"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api['key']}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.8
            }
            
            response = requests.post(api['url'], headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ OpenAI error: {response.status_code}")
                # Fallback a Gemini
                return self._call_gemini(prompt, self.apis['gemini'])
                
        except Exception as e:
            print(f"🔥 Error OpenAI: {e}")
            return self._fallback_response()
    
    def _call_gemini(self, prompt, api):
        """Llama a la API de Google Gemini"""
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 200,
                    "temperature": 0.8
                }
            }
            
            response = requests.post(api['url'], json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"⚠️ Gemini error: {response.status_code}")
                return self._fallback_response()
                
        except Exception as e:
            print(f"🔥 Error Gemini: {e}")
            return self._fallback_response()
    
    def _fallback_response(self):
        """Respuesta de respaldo si fallan todas las APIs"""
        responses = [
            f"🎨 ¡El curso de Resina Epóxica está cambiando vidas! {PRODUCTO['testimonios'][0]} 💰\n\n👉 {PRODUCTO['link']}",
            f"🔥 Oferta especial hoy: {PRODUCTO['nombre']} + {PRODUCTO['bonus']} 🚀\n\n👉 {PRODUCTO['link']}",
            f"🚀 {PRODUCTO['testimonios'][1]} ¿Listo para empezar? 🎨\n\n👉 {PRODUCTO['link']}"
        ]
        import random
        return random.choice(responses)
    
    def get_stats(self):
        """Obtiene estadísticas del sistema"""
        return {
            'monthly_revenue': self.monthly_revenue,
            'total_sales': self.total_sales,
            'active_apis': [name for name, api in self.apis.items() if api['active']],
            'conversions_today': len([log for log in self.conversion_log if log['date'].startswith(datetime.now().strftime('%Y-%m-%d'))])
        }

# =================== INICIALIZACIÓN ===================
api_manager = APIManager()
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# =================== MANEJO DE TELEGRAM ===================
@bot.message_handler(commands=['start', 'inicio'])
def send_welcome(message):
    """Envía mensaje de bienvenida con teclado"""
    
    welcome_text = f"""
🎨 *¡BIENVENIDO A NEURAFORGEA!* 🔥

*Especialistas en el CURSO DE RESINA EPÓXICA*

💰 *GANA ${PRODUCTO['comision']} POR CADA VENTA*

✅ *INCLUYE:*
• {PRODUCTO['bonus']}
• Soporte 24/7
• Comunidad privada
• Actualizaciones gratuitas

🚀 *TESTIMONIOS:*
• {PRODUCTO['testimonios'][0]}
• {PRODUCTO['testimonios'][1]}

💎 *¿Listo para empezar a ganar?*

_Escribe tu pregunta o elige una opción:_"""
    
    # Crear teclado interactivo
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🎨 Ver curso")
    btn2 = types.KeyboardButton("💰 Precio y comisiones")
    btn3 = types.KeyboardButton("🚀 Testimonios reales")
    btn4 = types.KeyboardButton("💎 Bonus incluidos")
    btn5 = types.KeyboardButton("❓ Cómo funciona")
    btn6 = types.KeyboardButton("👑 Comprar ahora")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    # Registrar en logs
    print(f"✅ /start de {message.from_user.id} (@{message.from_user.username})")

@bot.message_handler(commands=['stats', 'estadisticas'])
def send_stats(message):
    """Envía estadísticas al admin"""
    if str(message.chat.id) == ADMIN_CHAT_ID:
        stats = api_manager.get_stats()
        stats_text = f"""
📊 *ESTADÍSTICAS DEL BOT*

💰 Ingresos este mes: ${stats['monthly_revenue']}
🛒 Ventas totales: {stats['total_sales']}
🚀 APIs activas: {', '.join(stats['active_apis'])}
📈 Conversiones hoy: {stats['conversions_today']}

🔗 Link de afiliado: {PRODUCTO['link']}
        """
        bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Solo el administrador puede ver estadísticas")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Maneja todos los mensajes de texto"""
    try:
        print(f"📥 Mensaje: {message.text[:50]}... de {message.from_user.id}")
        
        # Respuestas rápidas para optimizar
        text = message.text.lower()
        
        # Botones predefinidos
        if "ver curso" in text:
            response = f"🎨 *CURSO DE RESINA EPÓXICA*\n\nAprende a crear:\n• Joyería exclusiva\n• Cuadros artísticos\n• Muebles únicos\n• Decoración premium\n\n💰 Vende cada pieza desde $50-$500\n\n👉 {PRODUCTO['link']}"
            bot.reply_to(message, response, parse_mode="Markdown")
            return
            
        elif "precio" in text or "comisiones" in text:
            response = f"💰 *INVERSIÓN Y GANANCIAS*\n\n• Precio del curso: ${PRODUCTO['precio']}\n• Tu comisión por venta: ${PRODUCTO['comision']}\n\n🚀 *¡Gana ${PRODUCTO['comision']} por cada persona que refieras!*\n\n👉 {PRODUCTO['link']}"
            bot.reply_to(message, response, parse_mode="Markdown")
            return
            
        elif "testimonios" in text:
            testimonios_text = "\n\n".join([f"• {t}" for t in PRODUCTO['testimonios']])
            response = f"🚀 *HISTORIAS REALES*\n\n{testimonios_text}\n\n🎨 ¿Listo para crear tu propia historia?\n\n👉 {PRODUCTO['link']}"
            bot.reply_to(message, response, parse_mode="Markdown")
            return
            
        elif "bonus" in text:
            response = f"💎 *BONUS INCLUIDOS*\n\n{PRODUCTO['bonus']}\n\n➕ Acceso a comunidad privada\n➕ Soporte 24/7\n➕ Actualizaciones gratuitas\n\n👉 {PRODUCTO['link']}"
            bot.reply_to(message, response, parse_mode="Markdown")
            return
            
        elif "cómo funciona" in text or "funciona" in text:
            response = f"❓ *¿CÓMO FUNCIONA?*\n\n1. Te afilias GRATIS\n2. Compartes el link: {PRODUCTO['link']}\n3. Cada venta te da ${PRODUCTO['comision']}\n4. Ganas dinero 24/7\n\n🚀 ¡Así de simple!"
            bot.reply_to(message, response, parse_mode="Markdown")
            return
            
        elif "comprar" in text or "quiero" in text:
            # Lead CALIENTE - respuesta especial
            response = f"🔥 *¡DECISIÓN INTELIGENTE!*\n\n🎨 {PRODUCTO['nombre']}\n💰 ${PRODUCTO['precio']} (Tú ganas ${PRODUCTO['comision']})\n💎 {PRODUCTO['bonus']}\n\n🚨 *OFERTA: Solo 3 cupos disponibles hoy*\n\n👉 {PRODUCTO['link']}?utm_source=bot&utm_medium=hotlead"
            bot.reply_to(message, response, parse_mode="Markdown")
            
            # Notificar al admin
            bot.send_message(
                ADMIN_CHAT_ID,
                f"🔥 LEAD CALIENTE!\nUser: @{message.from_user.username}\nID: {message.from_user.id}\nMensaje: {message.text[:100]}..."
            )
            return
        
        # Si no es una respuesta rápida, usar el sistema de IA inteligente
        response = api_manager.generate_response(message.text)
        bot.reply_to(message, response)
        
    except Exception as e:
        print(f"🔥 Error en handle_message: {e}")
        bot.reply_to(message, "🎨 ¡Hola! ¿Te interesa el curso de Resina Epóxica? Escribe 'info' para más detalles")

# =================== WEBHOOKS ===================
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Webhook para recibir mensajes de Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Error', 400

@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    """Webhook para recibir ventas de Hotmart"""
    try:
        data = request.json
        print(f"🔥 VENTA RECIBIDA: {json.dumps(data, indent=2)}")
        
        # Extraer datos importantes
        product_name = data.get('prod_name', 'Producto desconocido')
        price = float(data.get('price', 0))
        commission = float(data.get('affiliate_commission', 0))
        
        # Registrar la venta en el sistema
        api_manager.register_sale(commission)
        
        # Notificar al admin
        sale_text = f"""
✅ *¡VENTA CONFIRMADA!* 🎉

📦 Producto: {product_name}
💰 Precio: ${price}
💸 Tu comisión: ${commission}
👤 Total ventas: {api_manager.total_sales}
📈 Ingresos mes: ${api_manager.monthly_revenue}

🚀 *¡NEURAFORGEA SIGUE FACTURANDO!*"""
        
        bot.send_message(ADMIN_CHAT_ID, sale_text, parse_mode="Markdown")
        
        # Guardar log de venta
        with open('sales_log.json', 'a') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'product': product_name,
                'price': price,
                'commission': commission,
                'data': data
            }
            f.write(json.dumps(log_entry) + '\n')
        
        return 'OK', 200
        
    except Exception as e:
        print(f"❌ Error en webhook Hotmart: {e}")
        return 'ERROR', 400

@app.route('/health')
def health_check():
    """Endpoint para verificar que el bot está vivo"""
    return {
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'product': PRODUCTO['nombre'],
        'monthly_revenue': api_manager.monthly_revenue,
        'total_sales': api_manager.total_sales
    }

@app.route('/')
def home():
    """Página principal"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuraForgeAI Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .status {{ color: green; font-weight: bold; }}
            .product {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 NeuraForgeAI Bot</h1>
            <p class="status">✅ Bot activo y listo para vender</p>
            
            <div class="product">
                <h2>🎨 {PRODUCTO['nombre']}</h2>
                <p><strong>Precio:</strong> ${PRODUCTO['precio']} USD</p>
                <p><strong>Tu comisión:</strong> ${PRODUCTO['comision']} por venta</p>
                <p><strong>Link de afiliado:</strong> <a href="{PRODUCTO['link']}">{PRODUCTO['link']}</a></p>
            </div>
            
            <p><a href="/health">Ver estado del sistema</a></p>
            <p>📊 Ventas este mes: ${api_manager.monthly_revenue}</p>
            <p>🛒 Total de ventas: {api_manager.total_sales}</p>
        </div>
    </body>
    </html>
    """

# =================== FUNCIONES DE SEGUIMIENTO ===================
def follow_up_hot_leads():
    """Envía seguimiento automático a leads calientes"""
    # Esta función se puede expandir para guardar leads y seguirlos
    pass

# =================== INICIALIZACIÓN ===================
if __name__ == "__main__":
    print("""
    🚀 NEURAFORGEA BOT - SISTEMA DE VENTAS INTELIGENTE
    -------------------------------------------------
    Producto: Curso de Resina Epóxica
    Comisión: $48.5 por venta
    Link: http://bit.ly/3LsKPAo
    -------------------------------------------------
    """)
    
    # Configurar webhook
    try:
        render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        
        if render_hostname:
            webhook_url = f"https://{render_hostname}/telegram-webhook"
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_url)
            print(f"✅ Webhook configurado: {webhook_url}")
            
            # Mostrar información importante
            print(f"🔗 Link de afiliado: {PRODUCTO['link']}")
            print(f"👑 Comisión por venta: ${PRODUCTO['comision']}")
            print(f"📞 Admin ID: {ADMIN_CHAT_ID}")
            
            # Hotmart webhook URL
            hotmart_url = f"https://{render_hostname}/hotmart-webhook"
            print(f"🔥 Hotmart Webhook URL: {hotmart_url}")
            print("   Configura esta URL en Hotmart -> Afiliados -> Webhook")
        else:
            print("⚠️ No se encontró RENDER_EXTERNAL_HOSTNAME")
            print("⚠️ Ejecutando sin webhook (solo para desarrollo)")
            bot.remove_webhook()
            
    except Exception as e:
        print(f"❌ Error configurando webhook: {e}")
    
    print("\n🤖 Bot iniciado correctamente")
    print("💬 Envía /start a tu bot en Telegram para probarlo")
    
    # Iniciar servidor Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
