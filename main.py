import os
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import telebot
from flask import Flask, request

# ========== CONFIGURACIÓN DE APIs ==========
class APIManager:
    """Gestor inteligente de APIs que escala según demanda y presupuesto"""
    
    def __init__(self):
        self.apis = {
            # NIVEL 1: GRATIS (para empezar)
            'deepseek_free': {
                'url': 'https://api.deepseek.com/v1/chat/completions',
                'key': os.environ.get('DEEPSEEK_API_KEY', ''),
                'model': 'deepseek-chat',
                'cost_per_1k_tokens': 0.0,  # GRATIS
                'max_monthly_tokens': 5_000_000,  # Límite mensual
                'tokens_used_this_month': 0,
                'priority': 1,  # Primera opción
                'status': 'active'
            },
            
            # NIVEL 2: ECONÓMICO (cuando empiece a vender)
            'openai_gpt35': {
                'url': 'https://api.openai.com/v1/chat/completions',
                'key': os.environ.get('OPENAI_API_KEY', ''),
                'model': 'gpt-3.5-turbo',
                'cost_per_1k_tokens': 0.0015,  # $1.5 por 1M tokens
                'max_monthly_budget': 50,  # $50 máximo al mes
                'spent_this_month': 0,
                'priority': 2,
                'status': 'inactive'  # Se activa cuando haya ventas
            },
            
            # NIVEL 3: CALIDAD (para clientes premium)
            'openai_gpt4': {
                'url': 'https://api.openai.com/v1/chat/completions',
                'key': os.environ.get('OPENAI_GPT4_KEY', ''),
                'model': 'gpt-4-turbo',
                'cost_per_1k_tokens': 0.03,  # $30 por 1M tokens
                'max_monthly_budget': 100,
                'spent_this_month': 0,
                'priority': 3,
                'status': 'inactive'
            },
            
            # NIVEL 4: BACKUP (si fallan las otras)
            'gemini_free': {
                'url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
                'key': os.environ.get('GEMINI_API_KEY', ''),
                'model': 'gemini-pro',
                'cost_per_1k_tokens': 0.0,
                'rate_limit': 60,  # solicitudes por minuto
                'priority': 4,
                'status': 'active'
            }
        }
        
        self.current_api = 'deepseek_free'
        self.monthly_revenue = 0  # Ingresos del mes
        self.api_usage_log = []  # Registro de uso
        
    def update_revenue(self, sale_amount):
        """Actualiza los ingresos cuando hay una venta"""
        self.monthly_revenue += sale_amount
        print(f"💰 Ingreso registrado: ${sale_amount}. Total mes: ${self.monthly_revenue}")
        
        # Si hay ingresos > $100, activar APIs de pago
        if self.monthly_revenue > 100 and self.apis['openai_gpt35']['status'] == 'inactive':
            print("🚀 Activando API de pago (GPT-3.5) por ingresos > $100")
            self.apis['openai_gpt35']['status'] = 'active'
            
        if self.monthly_revenue > 500 and self.apis['openai_gpt4']['status'] == 'inactive':
            print("🎯 Activando API premium (GPT-4) por ingresos > $500")
            self.apis['openai_gpt4']['status'] = 'active'
    
    def select_best_api(self, message_length=100):
        """Selecciona la mejor API según costo y disponibilidad"""
        available_apis = []
        
        for api_name, api_config in self.apis.items():
            if api_config['status'] == 'active':
                # Verificar límites
                if api_name == 'deepseek_free':
                    if api_config['tokens_used_this_month'] >= api_config['max_monthly_tokens']:
                        print(f"⚠️ {api_name} alcanzó límite mensual")
                        continue
                
                if 'max_monthly_budget' in api_config:
                    estimated_cost = (message_length / 1000) * api_config['cost_per_1k_tokens']
                    if api_config['spent_this_month'] + estimated_cost > api_config['max_monthly_budget']:
                        print(f"⚠️ {api_name} superaría presupuesto mensual")
                        continue
                
                available_apis.append((api_name, api_config['priority']))
        
        if not available_apis:
            # Todas las APIs están en límite, usar la más barata
            print("⚠️ Todas las APIs en límite, usando deepseek_free como fallback")
            return 'deepseek_free'
        
        # Ordenar por prioridad (menor número = mayor prioridad)
        available_apis.sort(key=lambda x: x[1])
        return available_apis[0][0]
    
    def call_api(self, prompt, api_name=None):
        """Llama a la API seleccionada"""
        if not api_name:
            api_name = self.select_best_api(len(prompt))
        
        api_config = self.apis[api_name]
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['key']}"
            }
            
            # Preparar payload según API
            if 'openai' in api_name:
                payload = {
                    "model": api_config['model'],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.8
                }
            elif 'deepseek' in api_name:
                payload = {
                    "model": api_config['model'],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.8,
                    "stream": False
                }
            elif 'gemini' in api_name:
                # Formato diferente para Gemini
                headers = {"Content-Type": "application/json"}
                url = f"{api_config['url']}?key={api_config['key']}"
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": 300,
                        "temperature": 0.8
                    }
                }
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                data = response.json()
                
                # Registrar uso
                self._log_usage(api_name, 100)  # Estimado
                
                if response.status_code == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                return None
            
            # Para OpenAI y DeepSeek
            response = requests.post(
                api_config['url'], 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Calcular tokens usados (estimado)
                tokens_used = len(prompt.split()) * 1.3  # Estimación simple
                
                # Registrar uso y costo
                self._log_usage(api_name, tokens_used)
                
                if 'openai' in api_name:
                    return data['choices'][0]['message']['content']
                elif 'deepseek' in api_name:
                    return data['choices'][0]['message']['content']
            
            print(f"❌ Error en {api_name}: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"🔥 Error llamando {api_name}: {e}")
            return None
    
    def _log_usage(self, api_name, tokens_used):
        """Registra el uso de tokens y actualiza contadores"""
        api_config = self.apis[api_name]
        
        if 'tokens_used_this_month' in api_config:
            api_config['tokens_used_this_month'] += tokens_used
        
        if 'cost_per_1k_tokens' in api_config and api_config['cost_per_1k_tokens'] > 0:
            cost = (tokens_used / 1000) * api_config['cost_per_1k_tokens']
            api_config['spent_this_month'] += cost
            
        # Guardar en log
        self.api_usage_log.append({
            'timestamp': datetime.now().isoformat(),
            'api': api_name,
            'tokens': tokens_used,
            'estimated_cost': cost if 'cost' in locals() else 0
        })
        
        # Guardar en archivo para análisis
        with open('api_usage.json', 'w') as f:
            json.dump(self.api_usage_log, f, indent=2)
    
    def get_usage_report(self):
        """Genera reporte de uso de APIs"""
        report = {
            'monthly_revenue': self.monthly_revenue,
            'apis': {}
        }
        
        for api_name, config in self.apis.items():
            report['apis'][api_name] = {
                'status': config['status'],
                'tokens_used': config.get('tokens_used_this_month', 0),
                'spent': config.get('spent_this_month', 0),
                'max_tokens': config.get('max_monthly_tokens', 'N/A'),
                'max_budget': config.get('max_monthly_budget', 'N/A')
            }
        
        return report

# ========== INICIALIZACIÓN ==========
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']
api_manager = APIManager()
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Productos con comisiones
PRODUCTOS = {
    'ia': {
        'nombre': 'Curso de IA para Afiliados',
        'link': 'https://go.hotmart.com/TU_LINK_IA',
        'price': 97,
        'commission_rate': 0.50  # 50% comisión
    },
    'resina': {
        'nombre': 'Curso de Resina Epóxica',
        'link': 'https://go.hotmart.com/TU_LINK_RESINA',
        'price': 67,
        'commission_rate': 0.50
    },
    'velas': {
        'nombre': 'Curso de Velas Artesanales',
        'link': 'https://go.hotmart.com/TU_LINK_VELAS',
        'price': 57,
        'commission_rate': 0.50
    }
}

# ========== HANDLERS DE TELEGRAM ==========
@bot.message_handler(commands=['start'])
def comando_start(message):
    """Maneja /start con teclado interactivo"""
    welcome_text = """
🤖 *¡HOLA! SOY NEURAFORGEA* 🚀

*🔥 EL AGENTE DE VENTAS INTELIGENTE*

📦 *PRODUCTOS DISPONIBLES:*
• 🧠 IA PARA AFILIADOS - $97 (50% comisión)
• 🎨 RESINA EPÓXICA - $67 (50% comisión)
• 🕯️ VELAS ARTESANALES - $57 (50% comisión)

💰 *GANA HASTA $48.5 POR VENTA*

_Escribe lo que quieras saber..._"""
    
    from telebot import types
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🧠 Curso IA ($97)"),
        types.KeyboardButton("🎨 Curso Resina ($67)"),
        types.KeyboardButton("🕯️ Curso Velas ($57)"),
        types.KeyboardButton("💰 Comisiones"),
        types.KeyboardButton("📊 Estadísticas"),
        types.KeyboardButton("❓ Ayuda")
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ========== WEBHOOK HOTMART (VENTAS REALES) ==========
@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    """Recibe ventas reales de Hotmart"""
    try:
        data = request.json
        print(f"🔥 VENTA RECIBIDA: {json.dumps(data, indent=2)}")
        
        # Extraer datos de la venta
        product_name = data.get('prod_name', '')
        price = data.get('price', 0)
        affiliate_commission = data.get('affiliate_commission', 0)
        
        # Notificar al admin
        venta_text = f"""
✅ *¡VENTA CONFIRMADA!* 🎉

📦 Producto: {product_name}
💰 Precio: ${price}
💸 Comisión: ${affiliate_commission}
⏰ Hora: {datetime.now().strftime('%H:%M')}

🚀 *¡NEURAFORGEA SIGUE FACTURANDO!*"""
        
        bot.send_message(ADMIN_CHAT_ID, venta_text, parse_mode="Markdown")
        
        # Actualizar ingresos en el API Manager
        api_manager.update_revenue(affiliate_commission)
        
        return 'OK', 200
        
    except Exception as e:
        print(f"❌ Error en webhook Hotmart: {e}")
        return 'ERROR', 400

# ========== MANEJO DE MENSAJES ==========
@bot.message_handler(func=lambda message: True)
def manejar_mensajes(message):
    """Maneja todos los mensajes con IA escalable"""
    try:
        texto = message.text.lower()
        
        # Respuestas rápidas para optimizar costo
        quick_responses = {
            'comisiones': "💰 *COMISIONES* 💰\n\n• IA para Afiliados: $48.5 (50%)\n• Resina Epóxica: $33.5 (50%)\n• Velas Artesanales: $28.5 (50%)\n\n🚀 ¡Gana dinero recomendando!",
            'estadísticas': f"📊 *ESTADÍSTICAS DEL BOT* 📊\n\n• Ingresos este mes: ${api_manager.monthly_revenue}\n• API actual: {api_manager.current_api}\n• Uso mensual: {api_manager.apis[api_manager.current_api].get('tokens_used_this_month', 0):,.0f} tokens",
            'ayuda': "❓ *AYUDA* ❓\n\n• Pregunta sobre cualquier curso\n• Te daré info detallada\n• Te envío el link de afiliado\n• ¡Gana comisiones automáticas!",
        }
        
        for keyword, response in quick_responses.items():
            if keyword in texto:
                bot.reply_to(message, response, parse_mode="Markdown")
                return
        
        # Usar IA para respuestas complejas
        prompt = f"""
        Eres 'NeuraForgeAI', el mejor vendedor de cursos digitales.
        
        PRODUCTOS Y COMISIONES:
        1. IA para Afiliados - ${PRODUCTOS['ia']['price']} USD (Ganas ${PRODUCTOS['ia']['price'] * PRODUCTOS['ia']['commission_rate']})
        2. Resina Epóxica - ${PRODUCTOS['resina']['price']} USD (Ganas ${PRODUCTOS['resina']['price'] * PRODUCTOS['resina']['commission_rate']})
        3. Velas Artesanales - ${PRODUCTOS['velas']['price']} USD (Ganas ${PRODUCTOS['velas']['price'] * PRODUCTOS['velas']['commission_rate']})
        
        Usuario pregunta: {message.text}
        
        Responde:
        1. Breve y persuasivo (2-3 oraciones)
        2. Incluye emojis relevantes
        3. Menciona la comisión que ganará
        4. Termina con link correspondiente
        """
        
        respuesta = api_manager.call_api(prompt)
        
        if respuesta:
            bot.reply_to(message, respuesta)
            
            # Log para análisis
            print(f"📝 IA usada: {api_manager.current_api} | Usuario: {message.from_user.id}")
        else:
            # Fallback si falla la IA
            bot.reply_to(message, "🤖 ¡Hola! ¿Sobre qué curso quieres información?\n\n• 🧠 IA para Afiliados\n• 🎨 Resina Epóxica\n• 🕯️ Velas Artesanales")
            
    except Exception as e:
        print(f"🔥 Error en mensaje: {e}")
        bot.reply_to(message, "🤖 ¡Hola! ¿En qué curso te puedo ayudar hoy?")

# ========== ENDPOINTS DE CONTROL ==========
@app.route('/api/status')
def api_status():
    """Dashboard para ver estado de APIs y ventas"""
    report = api_manager.get_usage_report()
    return {
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'monthly_revenue': report['monthly_revenue'],
        'apis': report['apis'],
        'current_api': api_manager.current_api
    }

@app.route('/api/switch/<api_name>')
def switch_api(api_name):
    """Cambiar API manualmente (protegido)"""
    # Aquí deberías agregar autenticación
    if api_name in api_manager.apis:
        api_manager.current_api = api_name
        return {'status': 'switched', 'new_api': api_name}
    return {'status': 'error', 'message': 'API no encontrada'}

# ========== WEBHOOK TELEGRAM ==========
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Error', 400

@app.route('/')
def index():
    return '🚀 NeuraForgeAI Bot - Sistema de APIs Escalable'

# ========== MAIN ==========
if __name__ == "__main__":
    print("🚀 Iniciando NeuraForgeAI Bot con Sistema de APIs Escalable...")
    print(f"💰 API inicial: {api_manager.current_api}")
    print(f"📊 Ingresos mes: ${api_manager.monthly_revenue}")
    
    # Configurar webhooks
    try:
        render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        
        if render_hostname:
            # Webhook Telegram
            webhook_url = f"https://{render_hostname}/telegram-webhook"
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_url)
            print(f"✅ Telegram Webhook: {webhook_url}")
            
            # Webhook Hotmart
            hotmart_url = f"https://{render_hostname}/hotmart-webhook"
            print(f"✅ Hotmart Webhook: {hotmart_url}")
            print("🔗 Configura este URL en Hotmart -> Configuración -> Webhook")
        else:
            print("⚠️ Sin RENDER_EXTERNAL_HOSTNAME")
            
    except Exception as e:
        print(f"❌ Error configurando webhooks: {e}")
    
    print("🤖 Bot listo para generar dinero real 💰")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
