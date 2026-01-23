#!/bin/bash
# git-sync.sh - Sincronización automática con GitHub

echo "🔄 SINCRONIZANDO CON GITHUB"
echo "==========================="

# Configuración
BRANCH="main"
REPO_URL="https://github.com/tuusuario/tubot.git"

# 1. Verificar cambios locales
git status

read -p "¿Deseas continuar con la sincronización? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operación cancelada"
    exit 1
fi

# 2. Agregar todos los cambios
git add .

# 3. Commit con mensaje
read -p "Mensaje del commit: " commit_msg
git commit -m "$commit_msg"

# 4. Pull antes de push (evitar conflictos)
echo "Descargando últimos cambios..."
git pull origin $BRANCH

# 5. Subir cambios
echo "Subiendo cambios..."
git push origin $BRANCH

echo "✅ Sincronización completada"
