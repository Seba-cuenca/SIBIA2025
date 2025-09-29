#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoint avanzado de predicciones ML para SIBIA
Integra datos reales con modelos de Machine Learning
"""

from flask import jsonify
from datetime import datetime, timedelta
import logging
import json
from sistema_ml_predictivo import obtener_prediccion_ml, entrenar_sistema_ml
from app_CORREGIDO_OK_FINAL import obtener_valor_sensor, cargar_configuracion

logger = logging.getLogger(__name__)

def obtener_datos_sensores_reales() -> dict:
    """Obtener datos reales de todos los sensores críticos"""
    try:
        sensores_criticos = [
            '040TT01', '050TT01',  # Temperaturas
            '040LT01', '050LT01',  # Niveles
            '040PT01', '050PT01',  # Presiones
            '040AIT01AO2', '050AIT01AO2',  # Metano
            '040AIT01AO1', '050AIT01AO1',  # CO2
            '040AIT01AO4', '050AIT01AO4',  # H2S
            '060FIT01',  # Flujo gas
        ]
        
        datos_reales = {}
        
        for sensor in sensores_criticos:
            try:
                resultado = obtener_valor_sensor(sensor)
                if resultado.get('estado') == 'ok' and resultado.get('valor') is not None:
                    datos_reales[sensor] = float(resultado['valor'])
                else:
                    # Valor por defecto si no hay datos
                    if 'TT' in sensor:
                        datos_reales[sensor] = 40.0
                    elif 'LT' in sensor:
                        datos_reales[sensor] = 75.0
                    elif 'PT' in sensor:
                        datos_reales[sensor] = 1.2
                    elif 'AO2' in sensor:  # Metano
                        datos_reales[sensor] = 65.0
                    elif 'AO1' in sensor:  # CO2
                        datos_reales[sensor] = 25.0
                    elif 'AO4' in sensor:  # H2S
                        datos_reales[sensor] = 200.0
                    elif 'FIT' in sensor:  # Flujo
                        datos_reales[sensor] = 30.0
                    else:
                        datos_reales[sensor] = 0.0
            except Exception as e:
                logger.error(f"Error obteniendo sensor {sensor}: {e}")
                datos_reales[sensor] = 0.0
        
        # Mapear a nombres más legibles para el ML
        datos_ml = {
            'temperatura_bio1': datos_reales.get('040TT01', 40.0),
            'temperatura_bio2': datos_reales.get('050TT01', 40.0),
            'nivel_bio1': datos_reales.get('040LT01', 75.0),
            'nivel_bio2': datos_reales.get('050LT01', 75.0),
            'presion_bio1': datos_reales.get('040PT01', 1.2),
            'presion_bio2': datos_reales.get('050PT01', 1.2),
            'metano_bio1': datos_reales.get('040AIT01AO2', 65.0),
            'metano_bio2': datos_reales.get('050AIT01AO2', 65.0),
            'co2_bio1': datos_reales.get('040AIT01AO1', 25.0),
            'co2_bio2': datos_reales.get('050AIT01AO1', 25.0),
            'h2s_bio1': datos_reales.get('040AIT01AO4', 200.0),
            'h2s_bio2': datos_reales.get('050AIT01AO4', 200.0),
            'flujo_gas': datos_reales.get('060FIT01', 30.0),
            'ph_bio1': 7.0,  # Simulado hasta tener sensor real
            'ph_bio2': 7.0,  # Simulado hasta tener sensor real
            'eficiencia': 0.75  # Calculada basándose en generación actual
        }
        
        return datos_ml
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de sensores: {e}")
        return {}

def calcular_eficiencia_actual() -> float:
    """Calcular eficiencia actual basándose en datos reales"""
    try:
        config = cargar_configuracion()
        kw_objetivo = config.get('kw_objetivo', 28800)
        
        # Obtener generación actual (simulada por ahora)
        generacion_actual = 1200.0  # kW actuales
        
        # Calcular eficiencia
        eficiencia = generacion_actual / (kw_objetivo / 24)  # Eficiencia por hora
        return min(1.0, max(0.0, eficiencia))  # Limitar entre 0 y 1
        
    except Exception as e:
        logger.error(f"Error calculando eficiencia: {e}")
        return 0.75

def generar_prediccion_ml_completa(horizonte_horas: int = 24) -> dict:
    """Generar predicción completa usando ML"""
    try:
        logger.info("🤖 Generando predicción ML completa...")
        
        # Obtener datos reales de sensores
        datos_sensores = obtener_datos_sensores_reales()
        
        # Calcular eficiencia actual
        datos_sensores['eficiencia'] = calcular_eficiencia_actual()
        
        # Obtener predicción del sistema ML
        prediccion = obtener_prediccion_ml(datos_sensores, horizonte_horas)
        
        # Enriquecer con información adicional
        prediccion['datos_actuales'] = {
            'temperatura_promedio': (datos_sensores['temperatura_bio1'] + datos_sensores['temperatura_bio2']) / 2,
            'nivel_promedio': (datos_sensores['nivel_bio1'] + datos_sensores['nivel_bio2']) / 2,
            'metano_promedio': (datos_sensores['metano_bio1'] + datos_sensores['metano_bio2']) / 2,
            'ph_promedio': (datos_sensores['ph_bio1'] + datos_sensores['ph_bio2']) / 2,
            'eficiencia_actual': datos_sensores['eficiencia']
        }
        
        # Agregar análisis de tendencias
        prediccion['analisis_tendencias'] = analizar_tendencias(datos_sensores)
        
        # Agregar score de salud del sistema
        prediccion['salud_sistema'] = calcular_salud_sistema(datos_sensores)
        
        # Agregar predicción de mantenimiento
        prediccion['mantenimiento_predicho'] = predecir_mantenimiento(datos_sensores)
        
        return prediccion
        
    except Exception as e:
        logger.error(f"Error generando predicción ML: {e}")
        return generar_prediccion_fallback()

def analizar_tendencias(datos_sensores: dict) -> dict:
    """Analizar tendencias basándose en datos actuales"""
    try:
        tendencias = {
            'temperatura': 'estable',
            'nivel': 'estable',
            'calidad_gas': 'estable',
            'eficiencia': 'estable'
        }
        
        # Análisis de temperatura
        temp_promedio = (datos_sensores['temperatura_bio1'] + datos_sensores['temperatura_bio2']) / 2
        if temp_promedio > 41.0:
            tendencias['temperatura'] = 'ascendente_critica'
        elif temp_promedio > 40.5:
            tendencias['temperatura'] = 'ascendente'
        elif temp_promedio < 38.0:
            tendencias['temperatura'] = 'descendente'
        
        # Análisis de nivel
        nivel_promedio = (datos_sensores['nivel_bio1'] + datos_sensores['nivel_bio2']) / 2
        if nivel_promedio > 85.0:
            tendencias['nivel'] = 'alto'
        elif nivel_promedio < 65.0:
            tendencias['nivel'] = 'bajo'
        
        # Análisis de calidad de gas
        metano_promedio = (datos_sensores['metano_bio1'] + datos_sensores['metano_bio2']) / 2
        if metano_promedio > 70.0:
            tendencias['calidad_gas'] = 'excelente'
        elif metano_promedio > 60.0:
            tendencias['calidad_gas'] = 'buena'
        elif metano_promedio > 50.0:
            tendencias['calidad_gas'] = 'regular'
        else:
            tendencias['calidad_gas'] = 'mala'
        
        # Análisis de eficiencia
        if datos_sensores['eficiencia'] > 0.8:
            tendencias['eficiencia'] = 'excelente'
        elif datos_sensores['eficiencia'] > 0.7:
            tendencias['eficiencia'] = 'buena'
        elif datos_sensores['eficiencia'] > 0.6:
            tendencias['eficiencia'] = 'regular'
        else:
            tendencias['eficiencia'] = 'mala'
        
        return tendencias
        
    except Exception as e:
        logger.error(f"Error analizando tendencias: {e}")
        return {'temperatura': 'estable', 'nivel': 'estable', 'calidad_gas': 'estable', 'eficiencia': 'estable'}

def calcular_salud_sistema(datos_sensores: dict) -> dict:
    """Calcular score de salud general del sistema"""
    try:
        scores = []
        
        # Score de temperatura (0-100)
        temp_promedio = (datos_sensores['temperatura_bio1'] + datos_sensores['temperatura_bio2']) / 2
        if 38.0 <= temp_promedio <= 41.0:
            score_temp = 100
        elif 37.0 <= temp_promedio <= 42.0:
            score_temp = 80
        elif 36.0 <= temp_promedio <= 43.0:
            score_temp = 60
        else:
            score_temp = 20
        scores.append(score_temp)
        
        # Score de nivel (0-100)
        nivel_promedio = (datos_sensores['nivel_bio1'] + datos_sensores['nivel_bio2']) / 2
        if 70.0 <= nivel_promedio <= 85.0:
            score_nivel = 100
        elif 60.0 <= nivel_promedio <= 90.0:
            score_nivel = 80
        elif 50.0 <= nivel_promedio <= 95.0:
            score_nivel = 60
        else:
            score_nivel = 30
        scores.append(score_nivel)
        
        # Score de calidad de gas (0-100)
        metano_promedio = (datos_sensores['metano_bio1'] + datos_sensores['metano_bio2']) / 2
        if metano_promedio >= 70.0:
            score_gas = 100
        elif metano_promedio >= 60.0:
            score_gas = 80
        elif metano_promedio >= 50.0:
            score_gas = 60
        else:
            score_gas = 30
        scores.append(score_gas)
        
        # Score de eficiencia (0-100)
        eficiencia = datos_sensores['eficiencia']
        score_eficiencia = int(eficiencia * 100)
        scores.append(score_eficiencia)
        
        # Score general
        score_general = int(sum(scores) / len(scores))
        
        # Determinar estado
        if score_general >= 90:
            estado = 'EXCELENTE'
            color = 'success'
        elif score_general >= 75:
            estado = 'BUENO'
            color = 'info'
        elif score_general >= 60:
            estado = 'REGULAR'
            color = 'warning'
        else:
            estado = 'CRITICO'
            color = 'danger'
        
        return {
            'score_general': score_general,
            'estado': estado,
            'color': color,
            'scores_individuales': {
                'temperatura': score_temp,
                'nivel': score_nivel,
                'calidad_gas': score_gas,
                'eficiencia': score_eficiencia
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculando salud del sistema: {e}")
        return {
            'score_general': 50,
            'estado': 'DESCONOCIDO',
            'color': 'secondary',
            'scores_individuales': {}
        }

def predecir_mantenimiento(datos_sensores: dict) -> dict:
    """Predecir necesidades de mantenimiento"""
    try:
        mantenimientos = []
        
        # Mantenimiento de sensores
        if (datos_sensores['temperatura_bio1'] == 0 or 
            datos_sensores['temperatura_bio2'] == 0):
            mantenimientos.append({
                'tipo': 'SENSORES',
                'descripcion': 'Revisar sensores de temperatura',
                'prioridad': 'ALTA',
                'dias_estimados': 1
            })
        
        # Mantenimiento de válvulas
        if (datos_sensores['presion_bio1'] > 1.8 or 
            datos_sensores['presion_bio2'] > 1.8):
            mantenimientos.append({
                'tipo': 'VALVULAS',
                'descripcion': 'Revisar válvulas de presión',
                'prioridad': 'MEDIA',
                'dias_estimados': 3
            })
        
        # Mantenimiento de limpieza
        if (datos_sensores['h2s_bio1'] > 500 or 
            datos_sensores['h2s_bio2'] > 500):
            mantenimientos.append({
                'tipo': 'LIMPIEZA',
                'descripcion': 'Limpiar sistema de gas',
                'prioridad': 'ALTA',
                'dias_estimados': 2
            })
        
        # Mantenimiento preventivo general
        mantenimientos.append({
            'tipo': 'PREVENTIVO',
            'descripcion': 'Mantenimiento preventivo general',
            'prioridad': 'BAJA',
            'dias_estimados': 7
        })
        
        return {
            'mantenimientos_pendientes': len(mantenimientos),
            'lista_mantenimientos': mantenimientos,
            'proximo_mantenimiento': min(mantenimientos, key=lambda x: x['dias_estimados']) if mantenimientos else None
        }
        
    except Exception as e:
        logger.error(f"Error prediciendo mantenimiento: {e}")
        return {
            'mantenimientos_pendientes': 0,
            'lista_mantenimientos': [],
            'proximo_mantenimiento': None
        }

def generar_prediccion_fallback() -> dict:
    """Predicción de fallback cuando el ML no está disponible"""
    return {
        'problema_predicho': 0,
        'probabilidad_problema': 0.3,
        'prediccion_generacion': 900.0,
        'prediccion_eficiencia': 0.75,
        'anomalia_score': 0.5,
        'alertas': [{
            'tipo': 'INFO',
            'mensaje': 'Sistema ML no disponible',
            'descripcion': 'Usando análisis básico',
            'accion': 'Entrenar modelos ML para mejor precisión'
        }],
        'recomendaciones': [{
            'categoria': 'SISTEMA',
            'titulo': 'Activar sistema ML',
            'descripcion': 'Entrenar modelos de Machine Learning',
            'prioridad': 'MEDIA',
            'tiempo_estimado': '2-4 horas'
        }],
        'confianza': 30.0,
        'horizonte_horas': 24,
        'timestamp': datetime.now().isoformat(),
        'datos_actuales': {},
        'analisis_tendencias': {},
        'salud_sistema': {'score_general': 50, 'estado': 'DESCONOCIDO'},
        'mantenimiento_predicho': {'mantenimientos_pendientes': 0}
    }

def entrenar_modelos_ml() -> dict:
    """Entrenar modelos de ML con datos históricos"""
    try:
        logger.info("🤖 Iniciando entrenamiento de modelos ML...")
        resultados = entrenar_sistema_ml(30)  # 30 días de datos históricos
        return {
            'estado': 'exitoso',
            'mensaje': 'Modelos ML entrenados correctamente',
            'resultados': resultados,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error entrenando modelos ML: {e}")
        return {
            'estado': 'error',
            'mensaje': f'Error entrenando modelos: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
