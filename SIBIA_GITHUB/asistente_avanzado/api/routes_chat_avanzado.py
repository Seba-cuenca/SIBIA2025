#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints API para el Asistente SIBIA Avanzado
Integración con el proyecto principal
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar el asistente avanzado
from asistente_avanzado.core.asistente_sibia_definitivo import asistente_sibia_definitivo, ToolContext

# Blueprint para el chat avanzado
chat_avanzado_bp = Blueprint('chat_avanzado', __name__)

@chat_avanzado_bp.route('/mensaje', methods=['POST'])
def procesar_mensaje_avanzado():
    """Procesa un mensaje con el asistente SIBIA avanzado"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        
        if not pregunta:
            return jsonify({'error': 'Pregunta vacía'}), 400
        
        # Construir contexto con datos del proyecto principal
        contexto = construir_contexto_proyecto()
        
        # Procesar con SIBIA avanzado
        resultado = asistente_sibia_definitivo.procesar_pregunta(pregunta, contexto)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'error': f'Error procesando mensaje: {str(e)}',
            'motor': 'ERROR'
        }), 500

@chat_avanzado_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas_avanzadas():
    """Obtiene estadísticas del asistente avanzado"""
    try:
        stats = asistente_sibia_definitivo.obtener_estadisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_avanzado_bp.route('/configurar_voz', methods=['POST'])
def configurar_voz():
    """Configura el sistema de voz"""
    try:
        data = request.get_json()
        habilitada = data.get('habilitada', True)
        
        resultado = asistente_sibia_definitivo.configurar_voz(habilitada)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def construir_contexto_proyecto():
    """Construye el contexto con datos del proyecto principal"""
    try:
        # Importar funciones del proyecto principal
        from app_CORREGIDO_OK_FINAL import (
            obtener_stock_actual,
            obtener_mezcla_calculada,
            leer_sensor_plc,
            obtener_propiedades_material,
            calcular_kw_material,
            REFERENCIA_MATERIALES
        )
        
        # Obtener datos actuales
        stock_actual = obtener_stock_actual()
        mezcla_calculada = obtener_mezcla_calculada()
        
        # Crear contexto
        contexto = ToolContext(
            stock_materiales_actual=stock_actual,
            mezcla_diaria_calculada=mezcla_calculada,
            referencia_materiales=REFERENCIA_MATERIALES,
            _obtener_stock_actual_func=obtener_stock_actual,
            _obtener_valor_sensor_func=leer_sensor_plc,
            _obtener_propiedades_material_func=obtener_propiedades_material,
            _calcular_kw_material_func=calcular_kw_material
        )
        
        return contexto
        
    except ImportError as e:
        # Si no se pueden importar las funciones, crear contexto básico
        return ToolContext(
            stock_materiales_actual={},
            mezcla_diaria_calculada={},
            referencia_materiales={}
        )
    except Exception as e:
        return ToolContext()
