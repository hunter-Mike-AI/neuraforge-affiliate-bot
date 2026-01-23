#!/bin/bash
# deploy.sh - Actualización automática segura

echo "🚀 INICIANDO SISTEMA DE ACTUALIZACIÓN"
echo "======================================"

# Colores para mejor visualización
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    error "No estás en el directorio del bot. Cambia a la carpeta correcta."
    exit 1
fi

info "Directorio correcto detectado"

# 2. Verificar conexión a internet
if ! ping -c 1 google.com &> /dev/null; then
    error "Sin conexión a internet"
    exit 1
fi

info "Conexión a internet OK"

# 3. Crear carpeta de backups si no existe
mkdir -p backups
info "Carpeta de backups lista"

# 4. Ejecutar el sistema de actualización Python
info "Ejecutando sistema de actualización segura..."
python3 scripts/updater.py

# 5. Verificar que el bot está corriendo
sleep 5
if pgrep -f "main.py" > /dev/null; then
    info "✅ Bot está funcionando correctamente"
else
    warn "⚠️  Bot no está corriendo. Iniciando..."
    python3 main.py &
    sleep 3
    if pgrep -f "main.py" > /dev/null; then
        info "✅ Bot iniciado exitosamente"
    else
        error "❌ No se pudo iniciar el bot"
        exit 1
    fi
fi

echo ""
echo "======================================"
info "🎉 ACTUALIZACIÓN COMPLETADA"
info "📅 Última actualización: $(date)"
echo "======================================"
