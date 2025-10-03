#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENDPOINT DE ANÁLISIS QUÍMICO PARA BIODIGESTORES
===============================================

Endpoint Flask para el sistema de análisis químico y prevención de inhibición
de biodigestores.

Autor: SIBIA - Sistema Inteligente de Biogás Avanzado
"""

from flask import Blueprint, request, jsonify
import json
import logging
from datetime import datetime
import traceback

# Importar clases del sistema
from sistema_analisis_quimico_biodigestores import AnalisisQuimicoBiodigestores
from modelo_ml_inhibicion_biodigestores import ModeloMLInhibicionBiodigestores

# Configurar logging
logger = logging.getLogger(__name__)

# Crear Blueprint
analisis_quimico_bp = Blueprint('analisis_quimico', __name__, url_prefix='/analisis_quimico')

# Instancias globales
sistema_analisis = AnalisisQuimicoBiodigestores()
modelo_ml = ModeloMLInhibicionBiodigestores()

@analisis_quimico_bp.route('/analizar_inhibicion', methods=['POST'])
def analizar_inhibicion():
    """
    Analiza inhibición de biodigestores usando datos químicos
    """
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Realizar análisis completo
        resultado = sistema_analisis.analizar_inhibicion_completa(datos)
        
        # Agregar predicción ML si el modelo está entrenado
        if modelo_ml.entrenado:
            prediccion_ml = modelo_ml.predecir(datos)
            resultado['prediccion_ml'] = prediccion_ml
        
        return jsonify({
            'status': 'success',
            'resultado': resultado,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en análisis de inhibición: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@analisis_quimico_bp.route('/calcular_olr', methods=['POST'])
def calcular_olr():
    """
    Calcula la tasa de carga orgánica (OLR)
    """
    try:
        datos = request.get_json()
        
        carga_organica = datos.get('carga_organica', 0)
        volumen_digestor = datos.get('volumen_digestor', 0)
        
        if volumen_digestor <= 0:
            return jsonify({'error': 'Volumen del digestor debe ser mayor a 0'}), 400
        
        olr = sistema_analisis.calcular_olr(carga_organica, volumen_digestor)
        
        return jsonify({
            'status': 'success',
            'olr': olr,
            'unidad': 'kg COD/m³/día',
            'interpretacion': _interpretar_olr(olr)
        })
        
    except Exception as e:
        logger.error(f"Error calculando OLR: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/calcular_fos_tac', methods=['POST'])
def calcular_fos_tac():
    """
    Calcula la relación FOS/TAC
    """
    try:
        datos = request.get_json()
        
        fos = datos.get('fos', 0)
        tac = datos.get('tac', 0)
        
        if tac <= 0:
            return jsonify({'error': 'TAC debe ser mayor a 0'}), 400
        
        fos_tac = sistema_analisis.calcular_fos_tac(fos, tac)
        
        return jsonify({
            'status': 'success',
            'fos_tac': fos_tac,
            'interpretacion': _interpretar_fos_tac(fos_tac)
        })
        
    except Exception as e:
        logger.error(f"Error calculando FOS/TAC: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/evaluar_parametro', methods=['POST'])
def evaluar_parametro():
    """
    Evalúa un parámetro químico específico
    """
    try:
        datos = request.get_json()
        
        parametro = datos.get('parametro')
        valor = datos.get('valor')
        
        if not parametro or valor is None:
            return jsonify({'error': 'Parámetro y valor son requeridos'}), 400
        
        resultado = sistema_analisis.evaluar_parametro(parametro, valor)
        
        return jsonify({
            'status': 'success',
            'resultado': resultado
        })
        
    except Exception as e:
        logger.error(f"Error evaluando parámetro: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/entrenar_modelo', methods=['POST'])
def entrenar_modelo():
    """
    Entrena el modelo ML para predicción de inhibición
    """
    try:
        datos_entrenamiento = request.get_json()
        
        if not datos_entrenamiento:
            return jsonify({'error': 'No se recibieron datos de entrenamiento'}), 400
        
        # Entrenar modelo
        resultado = modelo_ml.entrenar_modelo()
        
        return jsonify({
            'status': 'success',
            'resultado': resultado
        })
        
    except Exception as e:
        logger.error(f"Error entrenando modelo: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/predecir_inhibicion', methods=['POST'])
def predecir_inhibicion():
    """
    Predice inhibición usando modelo ML
    """
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        if not modelo_ml.entrenado:
            return jsonify({'error': 'Modelo no entrenado'}), 400
        
        prediccion = modelo_ml.predecir(datos)
        
        return jsonify({
            'status': 'success',
            'prediccion': prediccion
        })
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/generar_reporte', methods=['POST'])
def generar_reporte():
    """
    Genera reporte químico completo
    """
    try:
        datos_sensores = request.get_json()
        
        if not datos_sensores:
            return jsonify({'error': 'No se recibieron datos de sensores'}), 400
        
        reporte = sistema_analisis.generar_reporte_quimico(datos_sensores)
        
        return jsonify({
            'status': 'success',
            'reporte': reporte
        })
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/parametros_disponibles', methods=['GET'])
def obtener_parametros_disponibles():
    """
    Obtiene lista de parámetros químicos disponibles
    """
    try:
        return jsonify({
            'status': 'success',
            'parametros': sistema_analisis.parametros_quimicos
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo parámetros: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/estadisticas_sistema', methods=['GET'])
def obtener_estadisticas_sistema():
    """
    Obtiene estadísticas del sistema de análisis
    """
    try:
        estadisticas = sistema_analisis.obtener_estadisticas_sistema()
        
        return jsonify({
            'status': 'success',
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': str(e)}), 500

@analisis_quimico_bp.route('/historial_analisis', methods=['GET'])
def obtener_historial_analisis():
    """
    Obtiene historial de análisis realizados
    """
    try:
        limite = request.args.get('limite', 10, type=int)
        
        historial = sistema_analisis.historial_analisis[-limite:]
        
        return jsonify({
            'status': 'success',
            'historial': historial,
            'total': len(sistema_analisis.historial_analisis)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({'error': str(e)}), 500

# Funciones auxiliares
def _interpretar_olr(olr: float) -> str:
    """
    Interpreta el valor de OLR
    """
    if olr < 1.0:
        return "OLR muy bajo - bacterias con hambre"
    elif olr <= 4.0:
        return "OLR óptimo - condiciones ideales"
    elif olr <= 6.0:
        return "OLR alto - riesgo de inhibición"
    else:
        return "OLR crítico - inhibición inminente"

def _interpretar_fos_tac(fos_tac: float) -> str:
    """
    Interpreta el valor de FOS/TAC
    """
    if fos_tac < 0.1:
        return "FOS/TAC muy bajo - sistema estable"
    elif fos_tac <= 0.3:
        return "FOS/TAC óptimo - equilibrio ideal"
    elif fos_tac <= 0.5:
        return "FOS/TAC alto - riesgo de inhibición"
    else:
        return "FOS/TAC crítico - inhibición severa"

# Inicializar modelo al cargar el módulo
try:
    logger.info("Inicializando modelo ML de inhibición...")
    modelo_ml.entrenar_modelo()
    logger.info("Modelo ML inicializado correctamente")
except Exception as e:
    logger.error(f"Error inicializando modelo ML: {e}")

if __name__ == "__main__":
    # Ejemplo de uso del endpoint
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(analisis_quimico_bp)
    
    # Datos de ejemplo
    datos_ejemplo = {
        'ph': 7.2,
        'temperatura': 37.5,
        'h2s': 25,
        'co2': 35,
        'o2': 0.2,
        'ta': 2500,
        'vfa_total': 400,
        'acetato': 200,
        'propionato': 100,
        'nitrogeno_total': 150,
        'fosforo_total': 30,
        'produccion_ch4': 120,
        'contenido_ch4': 62,
        'carga_organica': 150,
        'volumen_digestor': 50
    }
    
    with app.test_client() as client:
        response = client.post('/analisis_quimico/analizar_inhibicion', 
                             json=datos_ejemplo)
        print("Respuesta del análisis:")
        print(json.dumps(response.get_json(), indent=2, ensure_ascii=False))
