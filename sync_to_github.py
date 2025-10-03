#!/usr/bin/env python3
"""
Script para sincronizar el proyecto SIBIA actual con la carpeta SIBIA_GITHUB
y prepararlo para subir a GitHub
"""

import os
import shutil
import json
from pathlib import Path

def sync_project_to_github():
    """Sincroniza los archivos esenciales del proyecto actual a SIBIA_GITHUB"""
    
    # Archivos esenciales que deben copiarse
    essential_files = [
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
    
    # Modelos ML que deben copiarse
    ml_models = [
        'label_encoder_sibia_entrenado.pkl',
        'modelo_random_forest_sibia_entrenado.pkl',
        'modelo_xgboost_sibia_entrenado.pkl',
        'vectorizer_sibia_entrenado.pkl',
        'modelo_ml_inhibicion_biodigestores.py'
    ]
    
    # Carpetas que deben copiarse
    essential_dirs = [
        'templates',
        'static',
        'asistente',
        'asistente_avanzado'
    ]
    
    # Archivos de configuración para GitHub
    github_files = {
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
    
    # Directorios
    source_dir = Path('.')
    github_dir = Path('SIBIA_GITHUB')
    
    print("🔄 Sincronizando proyecto con SIBIA_GITHUB...")
    
    # Crear directorio si no existe
    github_dir.mkdir(exist_ok=True)
    
    # Copiar archivos esenciales
    print("📁 Copiando archivos esenciales...")
    for file_name in essential_files:
        source_file = source_dir / file_name
        if source_file.exists():
            dest_file = github_dir / file_name
            shutil.copy2(source_file, dest_file)
            print(f"  ✅ {file_name}")
        else:
            print(f"  ⚠️  {file_name} no encontrado")
    
    # Copiar modelos ML
    print("🤖 Copiando modelos ML...")
    for file_name in ml_models:
        source_file = source_dir / file_name
        if source_file.exists():
            dest_file = github_dir / file_name
            shutil.copy2(source_file, dest_file)
            print(f"  ✅ {file_name}")
        else:
            print(f"  ⚠️  {file_name} no encontrado")
    
    # Copiar carpetas
    print("📂 Copiando carpetas...")
    for dir_name in essential_dirs:
        source_dir_path = source_dir / dir_name
        if source_dir_path.exists() and source_dir_path.is_dir():
            dest_dir_path = github_dir / dir_name
            if dest_dir_path.exists():
                shutil.rmtree(dest_dir_path)
            shutil.copytree(source_dir_path, dest_dir_path)
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ⚠️  {dir_name}/ no encontrado")
    
    # Crear archivos de configuración para GitHub
    print("⚙️  Creando archivos de configuración...")
    for file_name, content in github_files.items():
        file_path = github_dir / file_name
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {file_name}")
    
    print("\n🎉 Sincronización completada!")
    print(f"📁 Archivos listos en: {github_dir.absolute()}")
    print("\n📋 Próximos pasos:")
    print("1. cd SIBIA_GITHUB")
    print("2. git add .")
    print("3. git commit -m 'Update SIBIA app with latest changes'")
    print("4. git push origin main")

if __name__ == "__main__":
    sync_project_to_github()
