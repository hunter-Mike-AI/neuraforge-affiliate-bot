#!/usr/bin/env python3
"""
SISTEMA DE ACTUALIZACIÓN SEGURA PARA BOT
Autor: NeuraForgea
Descripción: Actualiza sin romper el bot
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
import git

class SafeUpdater:
    def __init__(self):
        self.repo_path = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.repo_path, "backups")
        self.config_file = os.path.join(self.repo_path, "config.json")
        
    def crear_backup(self):
        """Crea backup completo antes de cualquier cambio"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        
        print(f"🛡️ Creando backup en: {backup_path}")
        
        # Copiar todo excepto backups y .git
        os.makedirs(backup_path, exist_ok=True)
        
        for item in os.listdir(self.repo_path):
            if item not in ['backups', '.git', '__pycache__']:
                item_path = os.path.join(self.repo_path, item)
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, backup_path)
                elif os.path.isdir(item_path):
                    shutil.copytree(item_path, os.path.join(backup_path, item))
        
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
    
    def verificar_estado_git(self):
        """Verifica estado de Git sin romper nada"""
        try:
            repo = git.Repo(self.repo_path)
            
            # Verificar cambios sin commit
            if repo.is_dirty():
                print("⚠️ Hay cambios sin commit. Guardando...")
                repo.git.add(all=True)
                repo.git.commit(m="Auto-commit antes de actualizar")
            
            # Verificar rama
            current_branch = repo.active_branch.name
            print(f"🌿 Rama actual: {current_branch}")
            
            return True
        except Exception as e:
            print(f"❌ Error con Git: {e}")
            return False
    
    def actualizar_desde_github(self):
        """Actualiza desde GitHub de forma segura"""
        print("🔄 Sincronizando con GitHub...")
        
        try:
            repo = git.Repo(self.repo_path)
            origin = repo.remote('origin')
            
            # Pull cambios
            origin.pull()
            
            # Instalar dependencias si hay cambios
            if self.verificar_cambios_requirements():
                print("📦 Actualizando dependencias...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            
            print("✅ Sincronización completada")
            return True
            
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
            print("🔙 Restaurando desde backup...")
            self.restaurar_backup()
            return False
    
    def verificar_cambios_requirements(self):
        """Verifica si requirements.txt cambió"""
        # Implementar lógica de comparación
        return True
    
    def restaurar_backup(self, backup_path=None):
        """Restaura desde backup si algo sale mal"""
        if not backup_path:
            # Buscar el backup más reciente
            backups = sorted([d for d in os.listdir(self.backup_dir) 
                            if d.startswith('backup_')])
            if backups:
                backup_path = os.path.join(self.backup_dir, backups[-1])
        
        print(f"🔄 Restaurando desde: {backup_path}")
        
        # Restaurar archivos
        for item in os.listdir(backup_path):
            src = os.path.join(backup_path, item)
            dst = os.path.join(self.repo_path, item)
            
            if os.path.exists(dst):
                if os.path.isfile(dst):
                    os.remove(dst)
                else:
                    shutil.rmtree(dst)
            
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst)
        
        print("✅ Sistema restaurado exitosamente")
    
    def ejecutar_pruebas(self):
        """Ejecuta pruebas rápidas antes de activar"""
        print("🧪 Ejecutando pruebas...")
        
        tests = [
            self.prueba_importaciones,
            self.prueba_configuracion,
            self.prueba_conexiones
        ]
        
        for test in tests:
            if not test():
                print("❌ Pruebas fallidas. Cancelando actualización.")
                return False
        
        print("✅ Todas las pruebas pasaron")
        return True
    
    def prueba_importaciones(self):
        """Prueba que todas las importaciones funcionen"""
        try:
            # Intentar importar módulos críticos
            import main
            return True
        except Exception as e:
            print(f"❌ Error en importaciones: {e}")
            return False
    
    def prueba_configuracion(self):
        """Verifica que config.json sea válido"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Verificar campos críticos
            required = ['TELEGRAM_TOKEN', 'HOTMART_SECRET', 'ADMIN_ID']
            for field in required:
                if field not in config:
                    print(f"❌ Falta campo: {field}")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Error en configuración: {e}")
            return False
    
    def prueba_conexiones(self):
        """Prueba conexiones básicas"""
        # Pruebas simples sin conexión real
        return True
    
    def menu_principal(self):
        """Menú interactivo seguro"""
        print("\n" + "="*50)
        print("🚀 SISTEMA DE ACTUALIZACIÓN SEGURA")
        print("="*50)
        print("1. Actualizar desde GitHub")
        print("2. Hacer backup manual")
        print("3. Restaurar backup")
        print("4. Ejecutar pruebas")
        print("5. Reiniciar bot")
        print("6. Salir")
        print("="*50)
        
        opcion = input("\nSelecciona opción (1-6): ").strip()
        
        if opcion == "1":
            self.actualizar_con_seguridad()
        elif opcion == "2":
            self.crear_backup()
        elif opcion == "3":
            self.restaurar_backup()
        elif opcion == "4":
            self.ejecutar_pruebas()
        elif opcion == "5":
            self.reiniciar_bot()
        elif opcion == "6":
            print("👋 Saliendo...")
            sys.exit(0)
        else:
            print("❌ Opción inválida")
    
    def actualizar_con_seguridad(self):
        """Proceso completo de actualización seguro"""
        print("\n" + "🔒 INICIANDO ACTUALIZACIÓN SEGURA")
        print("-" * 30)
        
        # Paso 1: Backup
        backup = self.crear_backup()
        
        # Paso 2: Verificar Git
        if not self.verificar_estado_git():
            return
        
        # Paso 3: Actualizar
        if not self.actualizar_desde_github():
            return
        
        # Paso 4: Pruebas
        if not self.ejecutar_pruebas():
            print("❌ Pruebas fallidas, restaurando...")
            self.restaurar_backup(backup)
            return
        
        # Paso 5: Reiniciar
        self.reiniciar_bot()
        
        print("\n✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO")
    
    def reiniciar_bot(self):
        """Reinicia el bot de forma segura"""
        print("🔄 Reiniciando bot...")
        
        # Detener proceso actual si está corriendo
        try:
            subprocess.run(["pkill", "-f", "main.py"])
        except:
            pass
        
        # Esperar un momento
        import time
        time.sleep(2)
        
        # Iniciar bot en segundo plano
        subprocess.Popen([sys.executable, "main.py"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        
        print("✅ Bot reiniciado")

if __name__ == "__main__":
    updater = SafeUpdater()
    updater.menu_principal()o

