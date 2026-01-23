#!/bin/bash
echo "🔧 REPARANDO BOT NEURAFORGEA"
echo "============================="

# Ir al directorio del bot
cd ~/neuraforge-affiliate-bot

# Crear estructura de carpetas
echo "📁 Creando estructura..."
mkdir -p scripts modules backups logs

# Crear requirements.txt si no existe
if [ ! -f "requirements.txt" ]; then
    echo "📦 Creando requirements.txt..."
    cat > requirements.txt << EOL
Flask==2.3.3
pyTelegramBotAPI==4.18.0
requests==2.31.0
schedule==1.2.0
gitpython==3.1.37
Werkzeug==2.3.7
python-dotenv==1.0.0
EOL
fi

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Crear check_dependencies.py
echo "🔍 Creando verificador..."
cat > scripts/check_dependencies.py << 'EOL'
#!/usr/bin/env python3
import sys
import subprocess

libs = [
    ("flask", "Flask"),
    ("telebot", "pyTelegramBotAPI"),
    ("requests", "requests"),
    ("schedule", "schedule"),
    ("git", "gitpython"),
]

print("Verificando librerías:")
for import_name, pip_name in libs:
    try:
        __import__(import_name)
        print(f"✅ {pip_name}")
    except:
        print(f"❌ {pip_name}")
        subprocess.run([sys.executable, "-m", "pip", "install", pip_name])
EOL

# Dar permisos
chmod +x scripts/check_dependencies.py

# Verificar instalación
echo "✅ Verificando..."
python3 scripts/check_dependencies.py

echo ""
echo "🎉 REPARACIÓN COMPLETADA"
echo "Ejecuta: python3 main.py"
