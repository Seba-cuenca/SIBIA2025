#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints API para el Sistema de Aprendizaje Continuo
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar el sistema de aprendizaje
from asistente_avanzado.core.sistema_aprendizaje_continuo import sistema_aprendizaje

# Blueprint para el aprendizaje
aprendizaje_bp = Blueprint('aprendizaje', __name__)

@aprendizaje_bp.route('/corregir', methods=['POST'])
def corregir_respuesta():
    """Permite al usuario corregir una respuesta del asistente"""
    try:
        data = request.get_json()
        
        pregunta = data.get('pregunta', '')
        respuesta_incorrecta = data.get('respuesta_incorrecta', '')
        respuesta_correcta = data.get('respuesta_correcta', '')
        contexto = data.get('contexto', {})
        
        if not all([pregunta, respuesta_incorrecta, respuesta_correcta]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        # Agregar corrección al sistema de aprendizaje
        exito = sistema_aprendizaje.agregar_correccion(
            pregunta=pregunta,
            respuesta_original=respuesta_incorrecta,
            respuesta_correcta=respuesta_correcta,
            contexto=contexto
        )
        
        return jsonify({
            'exito': exito,
            'mensaje': '¡Gracias! He aprendido esta corrección.' if exito else 'Error al guardar la corrección'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aprendizaje_bp.route('/buscar', methods=['POST'])
def buscar_conocimiento():
    """Busca en el conocimiento aprendido"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        
        if not pregunta:
            return jsonify({'error': 'Pregunta vacía'}), 400
        
        # Buscar en el conocimiento
        entrada = sistema_aprendizaje.buscar_conocimiento(pregunta)
        
        if entrada:
            return jsonify({
                'encontrado': True,
                'respuesta': entrada.respuesta_correcta,
                'confianza': entrada.confianza,
                'veces_usada': entrada.veces_consultada,
                'tags': entrada.tags,
                'timestamp': entrada.timestamp
            })
        else:
            return jsonify({'encontrado': False})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aprendizaje_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas_aprendizaje():
    """Obtiene estadísticas del sistema de aprendizaje"""
    try:
        stats = sistema_aprendizaje.obtener_estadisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aprendizaje_bp.route('/sugerencias', methods=['POST'])
def obtener_sugerencias():
    """Obtiene sugerencias contextuales"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        limite = data.get('limite', 3)
        
        if not pregunta:
            return jsonify({'error': 'Pregunta vacía'}), 400
        
        sugerencias = sistema_aprendizaje.obtener_sugerencias_contextuales(pregunta, limite)
        
        return jsonify({
            'sugerencias': sugerencias,
            'total': len(sugerencias)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aprendizaje_bp.route('/exportar', methods=['GET'])
def exportar_conocimiento():
    """Exporta el conocimiento aprendido"""
    try:
        archivo = request.args.get('archivo', 'conocimiento_export.json')
        exito = sistema_aprendizaje.exportar_conocimiento(archivo)
        
        return jsonify({
            'exito': exito,
            'archivo': archivo,
            'mensaje': 'Conocimiento exportado exitosamente' if exito else 'Error al exportar'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@aprendizaje_bp.route('/limpiar', methods=['POST'])
def limpiar_conocimiento():
    """Limpia entradas antiguas del conocimiento"""
    try:
        data = request.get_json()
        dias = data.get('dias', 90)
        
        eliminadas = sistema_aprendizaje.limpiar_entradas_antiguas(dias)
        
        return jsonify({
            'exito': True,
            'entradas_eliminadas': eliminadas,
            'mensaje': f'Se eliminaron {eliminadas} entradas antiguas'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
