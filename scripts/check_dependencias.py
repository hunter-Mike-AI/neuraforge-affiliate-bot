#!/usr/bin/env python3
"""
VERIFICADOR DE DEPENDENCIAS - Versión simplificada
"""

import subprocess
import sys

def check_and_install():
    print("🔍 Verificando dependencias...")
    
    required = [
        ("Flask", "flask"),
        ("pyTelegramBotAPI", "telebot"),
        ("requests", "requests"),
        ("schedule", "schedule"),
    ]
    
    missing = []
    
    for lib_name, import_name in required:
        try:
            __import__(import_name)
            print(f"✅ {lib_name}")
        except ImportError:
            print(f"❌ {lib_name} - FALTANTE")
            missing.append(lib_name)
    
    if missing:
        print(f"\n📦 Instalando {len(missing)} librerías...")
        for lib in missing:
            if lib == "pyTelegramBotAPI":
                subprocess.run([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
            else:
                subprocess.run([sys.executable, "-m", "pip", "install", lib])
        print("✅ Instalación completada")
    else:
        print("\n🎉 Todas las librerías están instaladas")

if __name__ == "__main__":
    check_and_install()
