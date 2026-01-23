#!/usr/bin/env python3
"""
VERIFICADOR DE DEPENDENCIAS
Verifica que todas las librerías estén instaladas correctamente
"""

import subprocess
import sys

REQUIRED_PACKAGES = [
    ("Flask", "flask"),
    ("python-telegram-bot", "telegram"),
    ("requests", "requests"),
    ("schedule", "schedule"),
    ("gitpython", "git"),
    ("Werkzeug", "werkzeug"),
    ("python-dotenv", "dotenv"),
]

def check_package(package_name, import_name):
    """Verifica si un paquete está instalado"""
    try:
        __import__(import_name)
        print(f"✅ {package_name}: INSTALADO")
        return True
    except ImportError:
        print(f"❌ {package_name}: NO INSTALADO")
        return False

def install_missing_packages():
    """Instala paquetes faltantes"""
    print("\n🔄 Instalando paquetes faltantes...")
    
    # Leer requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print("⚠️ No se encontró requirements.txt")
        packages = [
            "Flask==2.3.3",
            "python-telegram-bot==20.6",
            "requests==2.31.0",
            "schedule==1.2.0",
            "gitpython==3.1.37",
            "Werkzeug==2.3.7",
            "python-dotenv==1.0.0"
        ]
    
    # Instalar cada paquete
    for package in packages:
        print(f"📦 Instalando {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} instalado")
        except:
            print(f"   ⚠️ Error instalando {package}")

def main():
    print("🔍 VERIFICANDO DEPENDENCIAS")
    print("=" * 50)
    
    all_installed = True
    for package_name, import_name in REQUIRED_PACKAGES:
        if not check_package(package_name, import_name):
            all_installed = False
    
    print("\n" + "=" * 50)
    
    if all_installed:
        print("🎉 TODAS LAS DEPENDENCIAS ESTÁN INSTALADAS")
    else:
        print("⚠️ FALTAN ALGUNAS DEPENDENCIAS")
        response = input("¿Instalar automáticamente? (s/n): ")
        if response.lower() == 's':
            install_missing_packages()
        else:
            print("Instala manualmente con: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
