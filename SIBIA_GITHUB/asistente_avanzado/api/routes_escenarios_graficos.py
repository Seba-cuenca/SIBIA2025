#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints API para el Sistema de Comparación y Gráficos
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar los sistemas de comparación y gráficos
from asistente_avanzado.core.sistema_comparacion_graficos import sistema_comparacion, sistema_graficos

# Blueprint para escenarios
escenarios_bp = Blueprint('escenarios', __name__)

@escenarios_bp.route('/crear', methods=['POST'])
def crear_escenario():
    """Crea un nuevo escenario"""
    try:
        data = request.get_json()
        
        nombre = data.get('nombre', '')
        descripcion = data.get('descripcion', '')
        parametros = data.get('parametros', {})
        resultado = data.get('resultado', 0)
        unidad = data.get('unidad', 'KW')
        tipo_calculo = data.get('tipo_calculo', 'energia')
        
        if not nombre:
            return jsonify({'error': 'El nombre es requerido'}), 400
        
        escenario = sistema_comparacion.crear_escenario(
            nombre=nombre,
            descripcion=descripcion,
            parametros=parametros,
            resultado=resultado,
            unidad=unidad,
            tipo_calculo=tipo_calculo
        )
        
        return jsonify({
            'exito': True,
            'escenario_id': escenario.id,
            'mensaje': 'Escenario creado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@escenarios_bp.route('/listar', methods=['GET'])
def listar_escenarios():
    """Lista escenarios guardados"""
    try:
        tipo = request.args.get('tipo')
        escenarios = sistema_comparacion.listar_escenarios(tipo)
        
        return jsonify({
            'exito': True,
            'escenarios': escenarios,
            'total': len(escenarios)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@escenarios_bp.route('/obtener/<escenario_id>', methods=['GET'])
def obtener_escenario(escenario_id):
    """Obtiene un escenario específico"""
    try:
        escenario = sistema_comparacion.obtener_escenario(escenario_id)
        
        if escenario:
            from asistente_avanzado.core.sistema_comparacion_graficos import asdict
            return jsonify({
                'exito': True,
                'escenario': asdict(escenario)
            })
        else:
            return jsonify({'error': 'Escenario no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@escenarios_bp.route('/comparar', methods=['POST'])
def comparar_escenarios():
    """Compara múltiples escenarios"""
    try:
        data = request.get_json()
        ids_escenarios = data.get('ids_escenarios', [])
        
        if len(ids_escenarios) < 2:
            return jsonify({'error': 'Se necesitan al menos 2 escenarios para comparar'}), 400
        
        comparacion = sistema_comparacion.comparar_escenarios(ids_escenarios)
        
        return jsonify({
            'exito': True,
            'comparacion': comparacion
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@escenarios_bp.route('/eliminar/<escenario_id>', methods=['DELETE'])
def eliminar_escenario(escenario_id):
    """Elimina un escenario"""
    try:
        exito = sistema_comparacion.eliminar_escenario(escenario_id)
        
        return jsonify({
            'exito': exito,
            'mensaje': 'Escenario eliminado exitosamente' if exito else 'Escenario no encontrado'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Blueprint para gráficos
graficos_bp = Blueprint('graficos', __name__)

@graficos_bp.route('/comparacion', methods=['POST'])
def generar_grafico_comparacion():
    """Genera gráfico de comparación de escenarios"""
    try:
        data = request.get_json()
        escenarios = data.get('escenarios', [])
        
        if not escenarios:
            return jsonify({'error': 'No se proporcionaron escenarios'}), 400
        
        grafico = sistema_graficos.generar_grafico_comparacion(escenarios)
        
        if grafico:
            return jsonify({
                'exito': True,
                'grafico_base64': grafico,
                'mensaje': 'Gráfico generado exitosamente'
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'No se pudo generar el gráfico. Verificar que matplotlib esté instalado.'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graficos_bp.route('/prediccion', methods=['POST'])
def generar_grafico_prediccion():
    """Genera gráfico de predicción"""
    try:
        data = request.get_json()
        
        temperatura = data.get('temperatura', 37.0)
        presion = data.get('presion', 1.2)
        prediccion = data.get('prediccion', 1000)
        
        grafico = sistema_graficos.generar_grafico_prediccion(
            temperatura, presion, prediccion
        )
        
        if grafico:
            return jsonify({
                'exito': True,
                'grafico_base64': grafico,
                'mensaje': 'Gráfico de predicción generado exitosamente'
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'No se pudo generar el gráfico'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graficos_bp.route('/materiales', methods=['POST'])
def generar_grafico_materiales():
    """Genera gráfico de rendimiento por materiales"""
    try:
        data = request.get_json()
        materiales = data.get('materiales', {})
        
        if not materiales:
            return jsonify({'error': 'No se proporcionaron materiales'}), 400
        
        grafico = sistema_graficos.generar_grafico_rendimiento_material(materiales)
        
        if grafico:
            return jsonify({
                'exito': True,
                'grafico_base64': grafico,
                'mensaje': 'Gráfico de materiales generado exitosamente'
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'No se pudo generar el gráfico'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graficos_bp.route('/mezcla', methods=['POST'])
def generar_grafico_mezcla():
    """Genera gráfico de composición de mezcla"""
    try:
        data = request.get_json()
        materiales = data.get('materiales', {})
        
        if not materiales:
            return jsonify({'error': 'No se proporcionaron materiales'}), 400
        
        grafico = sistema_graficos.generar_grafico_mezcla(materiales)
        
        if grafico:
            return jsonify({
                'exito': True,
                'grafico_base64': grafico,
                'mensaje': 'Gráfico de mezcla generado exitosamente'
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'No se pudo generar el gráfico'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graficos_bp.route('/sensibilidad', methods=['POST'])
def generar_grafico_sensibilidad():
    """Genera gráfico de análisis de sensibilidad"""
    try:
        data = request.get_json()
        
        parametro = data.get('parametro', 'temperatura')
        valores = data.get('valores', [])
        resultados = data.get('resultados', [])
        
        if len(valores) != len(resultados) or len(valores) < 2:
            return jsonify({'error': 'Valores y resultados deben tener la misma longitud (mínimo 2)'}), 400
        
        grafico = sistema_graficos.generar_grafico_sensibilidad(parametro, valores, resultados)
        
        if grafico:
            return jsonify({
                'exito': True,
                'grafico_base64': grafico,
                'mensaje': 'Gráfico de sensibilidad generado exitosamente'
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'No se pudo generar el gráfico'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graficos_bp.route('/disponibilidad', methods=['GET'])
def verificar_disponibilidad_graficos():
    """Verifica si los gráficos están disponibles"""
    try:
        disponible = sistema_graficos.graficos_disponibles
        
        return jsonify({
            'exito': True,
            'graficos_disponibles': disponible,
            'mensaje': 'Matplotlib disponible' if disponible else 'Matplotlib no disponible'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
