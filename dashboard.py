import os
import sqlite3
from flask import Flask, render_template_string, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ✅ Base de datos ligera (funciona en Render GRATIS)
def init_db():
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            comision REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 📊 HTML mínimo pero funcional (carga rápido en móvil)
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>NeuraForgeAI - Mi Dinero</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #0f0f1a; color: white; padding: 20px; }
        .card { background: #1a1a2e; border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
        .total { font-size: 2.5em; color: #4cc9f0; text-align: center; font-weight: bold; }
        .producto { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #2a2a4a; }
        .btn-sos { background: #ff6b6b; color: white; border: none; padding: 15px; border-radius: 10px; font-size: 1.2em; width: 100%; margin-top: 20px; }
        .alert { background: #ff9e6d; color: #000; padding: 10px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>💸 NeuraForgeAI - Mi Economía</h1>
    
    <!-- ⚠️ BOTÓN DE EMERGENCIA (conecta con ayuda local) -->
    <div class="card">
        <button class="btn-sos" onclick="location.href='https://www.google.com/maps/search/albergues+gratuitos+cercanos'">
            🆘 NECESITO AYUDA AHORA (Albergues cerca de ti)
        </button>
        <p class="alert">💡 <b>Tip:</b> Toca el botón para encontrar refugio, comida o atención médica GRATIS cerca de tu ubicación actual.</p>
    </div>
    <div class="card">
        <h2>💰 Comisiones Acumuladas</h2>
        <div class="total">$<span id="total">0.00</span></div>
    </div>

    <div class="card">
        <h2>📦 Productos Vendidos</h2>
        <div id="productos">
            <!-- Se llena con datos reales -->
        </div>
    </div>

    <script>
        // Actualiza cada 10 segundos (sin recargar página)
        function cargarDatos() {
            fetch('/api/ventas')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total').textContent = data.total.toFixed(2);
                
                let html = '';
                for (const [producto, info] of Object.entries(data.productos)) {
                    html += `
                    <div class="producto">
                        <span>🔥 ${producto}</span>
                        <span>$${info.comision}</span>
                    </div>
                    `;
                }
                document.getElementById('productos').innerHTML = html;
            });
        }
        setInterval(cargarDatos, 10000);
        cargarDatos();
    </script>
</body>
</html>
'''

# 📈 Rutas del dashboard
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/ventas')
def api_ventas():
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute('SELECT producto, SUM(comision) as total FROM ventas GROUP BY producto')
    rows = c.fetchall()    
    total = sum(row[1] for row in rows)
    productos = {}
    for row in rows:
        productos[row[0]] = {"comision": row[1]}
    
    conn.close()
    return jsonify({
        "total": total,
        "productos": productos
    })

# 🔐 Ruta para registrar ventas (usada por main.py)
@app.route('/registrar-venta', methods=['POST'])
def registrar_venta():
    producto = request.json.get('producto')
    comision = float(request.json.get('comision', 0))
    
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute('INSERT INTO ventas (producto, comision) VALUES (?, ?)', (producto, comision))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10001))  # Puerto diferente al bot
    app.run(host='0.0.0.0', port=port)
