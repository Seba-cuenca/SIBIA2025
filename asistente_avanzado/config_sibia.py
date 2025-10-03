#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración para el Asistente SIBIA Avanzado
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ConfigSIBIA:
    """Configuración específica para SIBIA Avanzado"""
    
    # Directorios
    ASISTENTE_DIR = os.path.join(os.path.dirname(__file__), 'asistente_avanzado')
    DATA_DIR = os.path.join(ASISTENTE_DIR, 'data')
    CORE_DIR = os.path.join(ASISTENTE_DIR, 'core')
    
    # Archivos de datos
    USUARIO_SIBIA_FILE = os.path.join(DATA_DIR, 'usuario_sibia.json')
    CONOCIMIENTO_SIBIA_FILE = os.path.join(DATA_DIR, 'conocimiento_sibia.json')
    ESCENARIOS_SIBIA_FILE = os.path.join(DATA_DIR, 'escenarios_sibia.json')
    
    # APIs externas
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    # Sistema de voz
    VOICE_ENABLED = os.getenv('VOICE_ENABLED', 'True') == 'True'
    VOICE_LANGUAGE = os.getenv('VOICE_LANGUAGE', 'es')
    
    # Machine Learning
    ML_CONFIDENCE_THRESHOLD = 0.7
    ML_MAX_ITERATIONS = 100
    
    # Sistema de aprendizaje
    LEARNING_CONFIDENCE_INITIAL = 0.8
    LEARNING_CONFIDENCE_MAX = 0.98
    LEARNING_SIMILARITY_THRESHOLD = 0.8
    
    # Gráficos
    GRAPHICS_ENABLED = True
    GRAPHICS_DPI = 150
    GRAPHICS_FORMAT = 'png'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def crear_directorios(cls):
        """Crea los directorios necesarios si no existen"""
        directorios = [
            cls.ASISTENTE_DIR,
            cls.DATA_DIR,
            cls.CORE_DIR
        ]
        
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"📁 Directorio creado: {directorio}")
    
    @classmethod
    def verificar_configuracion(cls):
        """Verifica que la configuración esté correcta"""
        print("🔍 Verificando configuración SIBIA...")
        
        # Verificar directorios
        cls.crear_directorios()
        
        # Verificar APIs
        if cls.WEATHER_API_KEY:
            print("✅ API de clima configurada")
        else:
            print("⚠️  API de clima no configurada (usará datos simulados)")
        
        # Verificar sistema de voz
        if cls.VOICE_ENABLED:
            print("✅ Sistema de voz habilitado")
        else:
            print("⚠️  Sistema de voz deshabilitado")
        
        # Verificar gráficos
        try:
            import matplotlib
            print("✅ Matplotlib disponible para gráficos")
        except ImportError:
            print("⚠️  Matplotlib no disponible (gráficos deshabilitados)")
            cls.GRAPHICS_ENABLED = False
        
        print("✅ Configuración SIBIA verificada")

# Configuración por defecto
config = ConfigSIBIA()

if __name__ == "__main__":
    config.verificar_configuracion()
