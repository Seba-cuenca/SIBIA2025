#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración Simplificada del Asistente SIBIA Avanzado
Para usar en app_CORREGIDO_OK_FINAL.py
"""

import sys
import os
from flask import Blueprint, request, jsonify

# Agregar el directorio del asistente avanzado al path
asistente_path = os.path.join(os.path.dirname(__file__), 'asistente_avanzado')
sys.path.append(asistente_path)

def registrar_asistente_sibia_simple(app):
    """Registra el asistente SIBIA de forma simplificada"""
    
    # Importar el asistente
    try:
        from asistente_avanzado.core.asistente_sibia_definitivo import asistente_sibia_definitivo
        print("SUCCESS: Asistente SIBIA importado exitosamente")
    except Exception as e:
        print(f"ERROR: Error importando asistente SIBIA: {e}")
        return False
    
    # Crear blueprint para el chat SIBIA
    sibia_bp = Blueprint('sibia', __name__)
    
    @sibia_bp.route('/chat', methods=['POST'])
    def chat_sibia():
        """Endpoint para chat con SIBIA"""
        try:
            data = request.get_json()
            pregunta = data.get('pregunta', '')
            
            if not pregunta:
                return jsonify({'error': 'Pregunta vacía'}), 400
            
            # Crear contexto básico
            contexto = crear_contexto_basico()
            
            # Procesar con SIBIA
            resultado = asistente_sibia_definitivo.procesar_pregunta(pregunta, contexto)
            
            return jsonify(resultado)
            
        except Exception as e:
            return jsonify({
                'error': f'Error procesando mensaje: {str(e)}',
                'motor': 'ERROR'
            }), 500
    
    @sibia_bp.route('/estadisticas', methods=['GET'])
    def estadisticas_sibia():
        """Estadísticas del asistente SIBIA"""
        try:
            stats = asistente_sibia_definitivo.obtener_estadisticas()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @sibia_bp.route('/info', methods=['GET'])
    def info_sibia():
        """Información del asistente SIBIA"""
        return jsonify({
            'nombre': 'SIBIA',
            'version': '5.0 Definitiva',
            'descripcion': 'Sistema Inteligente de Biogás con IA Avanzada',
            'capacidades': [
                'Machine Learning (XGBoost, Algoritmos Genéticos)',
                'Análisis de sensores en tiempo real',
                'Búsqueda de información en internet',
                'Información del clima',
                'Sistema de voz integrado',
                'Aprendizaje continuo',
                'Fórmulas transparentes',
                'Comparación de escenarios'
            ],
            'endpoints': [
                '/api/sibia/chat',
                '/api/sibia/estadisticas',
                '/api/sibia/info'
            ]
        })
    
    # Registrar blueprint
    app.register_blueprint(sibia_bp, url_prefix='/api/sibia')
    
    print("SUCCESS: Asistente SIBIA registrado exitosamente")
    print("ENDPOINTS disponibles:")
    print("   - POST /api/sibia/chat")
    print("   - GET /api/sibia/estadisticas")
    print("   - GET /api/sibia/info")
    
    return True

def crear_contexto_basico():
    """Crea contexto básico para SIBIA"""
    try:
        # Importar ToolContext
        from asistente_avanzado.core.asistente_sibia_definitivo import ToolContext
        
        # Crear contexto básico sin importar funciones del proyecto principal
        # para evitar problemas de inicialización
        contexto = ToolContext(
            stock_materiales_actual={},
            mezcla_diaria_calculada={},
            referencia_materiales={}
        )
        
        print("SUCCESS: Contexto básico creado")
        return contexto
        
    except Exception as e:
        print(f"ERROR: Error creando contexto: {e}")
        return None

def probar_integracion():
    """Prueba la integración"""
    print("Probando integración SIBIA...")
    
    try:
        from asistente_avanzado.core.asistente_sibia_definitivo import asistente_sibia_definitivo
        
        # Crear contexto
        contexto = crear_contexto_basico()
        
        # Probar pregunta
        resultado = asistente_sibia_definitivo.procesar_pregunta("Hola, ¿qué es SIBIA?", contexto)
        
        print(f"SUCCESS: Prueba exitosa:")
        print(f"   Motor: {resultado['motor']}")
        print(f"   Confianza: {resultado['confianza']:.0%}")
        print(f"   Latencia: {resultado['latencia_ms']:.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error en prueba: {e}")
        return False

if __name__ == "__main__":
    probar_integracion()