#!/bin/bash
echo "🔧 INSTALANDO SISTEMA COMPLETO"
echo "==============================="

# Actualizar Termux
pkg update -y
pkg upgrade -y

# Instalar Python y herramientas
pkg install -y python git wget curl

# Actualizar pip
pip install --upgrade pip

# Instalar librerías del sistema
echo "📦 Instalando librerías del sistema..."
pip install Flask python-telegram-bot requests schedule gitpython

# Verificar instalación
echo "✅ Verificando instalación..."
python3 -c "
import flask, telegram, requests, schedule, git
print('✅ Flask:', flask.__version__)
print('✅ python-telegram-bot: OK')
print('✅ Requests:', requests.__version__)
print('✅ Schedule: OK')
print('✅ GitPython:', git.__version__)
"

# Crear estructura de carpetas
echo "📁 Creando estructura de carpetas..."
mkdir -p scripts modules backups logs

echo "🎉 INSTALACIÓN COMPLETADA"
echo "=========================="
echo "Para iniciar el bot: python3 main.py"
echo "Para actualizar: python3 scripts/updater.py"
