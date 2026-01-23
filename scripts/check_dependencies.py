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
