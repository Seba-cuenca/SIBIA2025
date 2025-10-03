#!/usr/bin/env python3
"""
Sistema de sincronización automática con GitHub
Detecta cambios y sincroniza automáticamente con SIBIA_GITHUB
"""

import os
import shutil
import time
import threading
import json
from pathlib import Path
from datetime import datetime
import subprocess

class AutoGitHubSync:
    def __init__(self):
        self.source_dir = Path('.')
        self.github_dir = Path('SIBIA_GITHUB')
        self.last_sync = {}
        self.running = False
        
        # Archivos esenciales que deben sincronizarse
        self.essential_files = [
            'app_CORREGIDO_OK_FINAL.py',
            'config.json',
            'configuracion_ml_dashboard.json',
            'parametros_globales.json',
            'materiales_base_config.json',
            'historico_diario_productivo.json',
            'registros.json',
            'adan_calculator.py',
            'entrenador_modelos_ml.py',
            'mega_agente_ia.py',
            'buscador_web.py',
            'endpoint_analisis_quimico.py',
            'voice_integration.py',
            'web_voice_system.py'
        ]
        
        # Modelos ML
        self.ml_models = [
            'label_encoder_sibia_entrenado.pkl',
            'modelo_random_forest_sibia_entrenado.pkl',
            'modelo_xgboost_sibia_entrenado.pkl',
            'vectorizer_sibia_entrenado.pkl',
            'modelo_ml_inhibicion_biodigestores.py'
        ]
        
        # Carpetas esenciales
        self.essential_dirs = [
            'templates',
            'static',
            'asistente',
            'asistente_avanzado'
        ]
        
        # Archivos de configuración para GitHub
        self.github_config = {
            'requirements.txt': '''Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.1.1
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
openpyxl==3.1.2
plotly==5.17.0
scikit-learn==1.3.0
xgboost==1.7.6
PyMySQL==1.1.0
edge-tts==6.1.9
google-generativeai==0.3.2
psutil==5.9.5
matplotlib==3.7.2
seaborn==0.12.2
joblib==1.3.2
gunicorn==21.2.0''',
            
            'Procfile': 'web: gunicorn -w 4 -b 0.0.0.0:$PORT app_CORREGIDO_OK_FINAL:app',
            
            'runtime.txt': 'python-3.11.0',
            
            'README.md': '''# SIBIA - Sistema Inteligente de Biodigestores Industriales Avanzados

## 🏢 AutoLinkSolutions SRL
**Copyright © 2025 AutoLinkSolutions SRL. Todos los derechos reservados.**

## 🚀 Descripción
SIBIA es un sistema completo de monitoreo y control de biodigestores industriales con inteligencia artificial, análisis predictivo y gestión automatizada.

## ✨ Características Principales
- 🤖 **Asistente IA** con síntesis de voz gratuita
- 📊 **Dashboard** interactivo de biodigestores
- 🧮 **Calculadora Avanzada Adán** con XGBoost
- 📈 **Análisis predictivo** con Machine Learning
- 🔧 **Mantenimiento predictivo**
- 📱 **Interfaz responsive** y PWA
- 🎵 **Sistema de voz gratuito** sin límites
- ⏰ **Seguimiento horario** con dosificación automática

## 🛠️ Tecnologías
- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **IA:** XGBoost, Random Forest, Redes Neuronales
- **Voz:** Edge-TTS (Gratuito)
- **Base de Datos:** MySQL, PyMySQL
- **Despliegue:** Cloud Run, Railway

## 🚀 Despliegue Automático
Este proyecto está configurado para despliegue automático:
- Cada push a `main` activa el despliegue
- CI/CD configurado con GitHub Actions
- Health check en `/health`

## 📋 Instalación Local
```bash
pip install -r requirements.txt
python app_CORREGIDO_OK_FINAL.py
```

## 🔧 Variables de Entorno
- `FLASK_ENV=production`
- `DEBUG=false`
- `SECRET_KEY=sibia-autolinksolutions-2025-secure-key`
- `DATABASE_URL=mysql://user:pass@host:port/db`

## 📞 Soporte
**AutoLinkSolutions SRL**
- Email: info@autolinksolutions.com
- Web: www.autolinksolutions.com

## 📄 Licencia
Copyright © 2025 AutoLinkSolutions SRL. Todos los derechos reservados.
''',
            
            '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
temp/
tmp/
*.tmp

# Backup files
*.backup
*.bak

# Large files
*.pkl
*.joblib
*.model

# But keep essential ML models
!label_encoder_sibia_entrenado.pkl
!modelo_random_forest_sibia_entrenado.pkl
!modelo_xgboost_sibia_entrenado.pkl
!vectorizer_sibia_entrenado.pkl
'''
        }
        
        # Cargar estado de última sincronización
        self.load_sync_state()
    
    def load_sync_state(self):
        """Carga el estado de la última sincronización"""
        state_file = Path('sync_state.json')
        if state_file.exists():
            with open(state_file, 'r') as f:
                self.last_sync = json.load(f)
    
    def save_sync_state(self):
        """Guarda el estado de la sincronización"""
        state_file = Path('sync_state.json')
        with open(state_file, 'w') as f:
            json.dump(self.last_sync, f, indent=2)
    
    def get_file_hash(self, file_path):
        """Obtiene un hash simple del archivo para detectar cambios"""
        try:
            stat = file_path.stat()
            return f"{stat.st_mtime}_{stat.st_size}"
        except:
            return None
    
    def has_changes(self):
        """Detecta si hay cambios en los archivos esenciales"""
        changes = []
        
        # Verificar archivos esenciales
        for file_name in self.essential_files:
            source_file = self.source_dir / file_name
            if source_file.exists():
                current_hash = self.get_file_hash(source_file)
                last_hash = self.last_sync.get(file_name)
                
                if current_hash != last_hash:
                    changes.append(file_name)
                    self.last_sync[file_name] = current_hash
        
        # Verificar modelos ML
        for file_name in self.ml_models:
            source_file = self.source_dir / file_name
            if source_file.exists():
                current_hash = self.get_file_hash(source_file)
                last_hash = self.last_sync.get(file_name)
                
                if current_hash != last_hash:
                    changes.append(file_name)
                    self.last_sync[file_name] = current_hash
        
        # Verificar carpetas
        for dir_name in self.essential_dirs:
            source_dir_path = self.source_dir / dir_name
            if source_dir_path.exists():
                # Verificar archivos dentro de la carpeta
                for file_path in source_dir_path.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.source_dir)
                        current_hash = self.get_file_hash(file_path)
                        last_hash = self.last_sync.get(str(rel_path))
                        
                        if current_hash != last_hash:
                            changes.append(str(rel_path))
                            self.last_sync[str(rel_path)] = current_hash
        
        return changes
    
    def sync_files(self, changed_files):
        """Sincroniza los archivos cambiados"""
        print(f"🔄 Sincronizando {len(changed_files)} archivos...")
        
        # Crear directorio si no existe
        self.github_dir.mkdir(exist_ok=True)
        
        for file_path in changed_files:
            source_file = self.source_dir / file_path
            
            if source_file.exists() and source_file.is_file():
                dest_file = self.github_dir / file_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                print(f"  ✅ {file_path}")
        
        # Actualizar archivos de configuración
        for file_name, content in self.github_config.items():
            file_path = self.github_dir / file_name
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("✅ Sincronización completada")
    
    def git_commit_push(self):
        """Hace commit y push automático a GitHub"""
        try:
            # Cambiar al directorio de GitHub
            os.chdir(self.github_dir)
            
            # Agregar todos los archivos
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            
            # Commit con timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-sync: {timestamp} - Actualización automática desde Cursor"
            
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         check=True, capture_output=True)
            
            # Push a GitHub
            result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("🚀 Push exitoso a GitHub")
            else:
                print(f"⚠️ Error en push: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en git: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        finally:
            # Volver al directorio original
            os.chdir(self.source_dir)
    
    def sync_and_push(self):
        """Sincroniza y hace push si hay cambios"""
        changes = self.has_changes()
        
        if changes:
            print(f"📝 Detectados cambios en: {', '.join(changes[:5])}{'...' if len(changes) > 5 else ''}")
            self.sync_files(changes)
            self.save_sync_state()
            self.git_commit_push()
            return True
        return False
    
    def start_monitoring(self, interval=30):
        """Inicia el monitoreo automático"""
        self.running = True
        print(f"🔄 Iniciando monitoreo automático (cada {interval}s)")
        print("💡 Trabaja tranquilamente en Cursor, la sincronización es automática")
        
        while self.running:
            try:
                self.sync_and_push()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⏹️ Monitoreo detenido por el usuario")
                break
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.running = False

def main():
    """Función principal"""
    sync = AutoGitHubSync()
    
    print("🚀 Sistema de Sincronización Automática con GitHub")
    print("=" * 50)
    
    # Sincronización inicial
    print("🔄 Realizando sincronización inicial...")
    sync.sync_and_push()
    
    # Iniciar monitoreo
    try:
        sync.start_monitoring(interval=30)  # Cada 30 segundos
    except KeyboardInterrupt:
        print("\n👋 Sincronización automática finalizada")

if __name__ == "__main__":
    main()
