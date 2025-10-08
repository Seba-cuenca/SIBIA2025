#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE INICIO AUTOMÁTICO SIBIA CON ML
========================================

Inicializa todo el sistema automáticamente:
- Instala dependencias si faltan
- Verifica modelos ML
- Inicia scheduler de reentrenamiento
- Arranca servidor Flask

Autor: SIBIA - Sistema Inteligente de Biogás Avanzado
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencias():
    """Instala dependencias necesarias para ML"""
    print("🔧 Verificando dependencias...")
    
    dependencias = [
        'flask',
        'pandas',
        'numpy',
        'scikit-learn',
        'joblib',
        'apscheduler',
        'python-dotenv',
        'openpyxl'
    ]
    
    dependencias_faltantes = []
    
    for dep in dependencias:
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - FALTA")
            dependencias_faltantes.append(dep)
    
    if dependencias_faltantes:
        print(f"\n📦 Instalando {len(dependencias_faltantes)} dependencias faltantes...")
        for dep in dependencias_faltantes:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                print(f"   ✅ {dep} instalado")
            except Exception as e:
                print(f"   ❌ Error instalando {dep}: {e}")
                return False
    
    print("✅ Todas las dependencias están instaladas\n")
    return True

def verificar_modelos():
    """Verifica que los modelos ML existan"""
    print("🤖 Verificando modelos ML...")
    
    models_dir = Path('models')
    if not models_dir.exists():
        models_dir.mkdir()
        print("   📁 Directorio 'models' creado")
    
    modelo_fallos = models_dir / 'modelo_prediccion_fallos.pkl'
    
    if not modelo_fallos.exists():
        print("   ⚠️ Modelo de predicción de fallos no encontrado")
        print("   🔧 Entrenando modelo con datos iniciales...")
        try:
            subprocess.check_call([sys.executable, 'entrenar_modelo_prediccion_fallos_reales.py'])
            print("   ✅ Modelo entrenado correctamente")
        except Exception as e:
            print(f"   ⚠️ No se pudo entrenar automáticamente: {e}")
            print("   ℹ️ El sistema funcionará sin este modelo")
    else:
        print("   ✅ Modelo de predicción de fallos encontrado")
    
    print()

def crear_directorios():
    """Crea directorios necesarios para el sistema"""
    print("📁 Creando directorios necesarios...")
    
    directorios = [
        'ml_training_data',
        'models',
        'logs',
        'reportes'
    ]
    
    for directorio in directorios:
        path = Path(directorio)
        if not path.exists():
            path.mkdir(parents=True)
            print(f"   ✅ {directorio} creado")
        else:
            print(f"   ✅ {directorio} existe")
    
    print()

def verificar_archivos_config():
    """Verifica archivos de configuración"""
    print("⚙️ Verificando archivos de configuración...")
    
    archivos = {
        'stock.json': {'materiales': {}},
        'parametros_configuracion.json': {'kw_objetivo': 28800},
        'seguimiento_biodigestores.json': {'fecha': '2025-10-08', 'biodigestores': {}}
    }
    
    import json
    
    for archivo, contenido_default in archivos.items():
        path = Path(archivo)
        if not path.exists():
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(contenido_default, f, indent=2)
            print(f"   ✅ {archivo} creado")
        else:
            print(f"   ✅ {archivo} existe")
    
    print()

def mostrar_info():
    """Muestra información del sistema"""
    print("=" * 70)
    print("   🚀 SIBIA - Sistema Inteligente de Biogás Avanzado")
    print("   📊 Con Aprendizaje Continuo ML")
    print("   © 2025 AutoLinkSolutions SRL")
    print("=" * 70)
    print()

def iniciar_servidor():
    """Inicia el servidor Flask"""
    print("🚀 Iniciando servidor SIBIA...")
    print()
    print("   📍 URL: http://localhost:5000")
    print("   📍 Dashboard: http://localhost:5000/dashboard")
    print()
    print("   🤖 Sistema de aprendizaje continuo: ACTIVO")
    print("   📊 Reentrenamiento automático: PROGRAMADO")
    print()
    print("=" * 70)
    print()
    
    try:
        subprocess.run([sys.executable, 'app_CORREGIDO_OK_FINAL.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    try:
        mostrar_info()
        
        # Paso 1: Instalar dependencias
        if not instalar_dependencias():
            print("❌ Error instalando dependencias. Abortando...")
            return 1
        
        # Paso 2: Crear directorios
        crear_directorios()
        
        # Paso 3: Verificar archivos de configuración
        verificar_archivos_config()
        
        # Paso 4: Verificar modelos
        verificar_modelos()
        
        # Paso 5: Iniciar servidor
        if not iniciar_servidor():
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
