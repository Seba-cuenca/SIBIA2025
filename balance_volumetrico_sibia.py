#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Balance Volumétrico para SIBIA
Cálculos basados en datos reales del SCADA
"""

import pymysql
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Configuración
VOLUMEN_TOTAL_BIODIGESTOR = 4775  # m³ al 100% (dato real de planta)
NIVEL_SCADA_REFERENCIA = 87  # % nivel actual en SCADA

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calcular_volumen_m3(porcentaje_nivel: float) -> float:
    """Calcula volumen en m³ basado en porcentaje de nivel"""
    return (porcentaje_nivel / 100) * VOLUMEN_TOTAL_BIODIGESTOR

def calcular_porcentaje_nivel(volumen_m3: float) -> float:
    """Calcula porcentaje de nivel basado en volumen en m³"""
    return (volumen_m3 / VOLUMEN_TOTAL_BIODIGESTOR) * 100

def obtener_balance_volumetrico_biodigestor(biodigestor_id: str) -> Dict[str, Any]:
    """
    Obtiene balance volumétrico completo de un biodigestor
    biodigestor_id: '1' o '2'
    """
    try:
        # Mapeo de sensores según biodigestor
        sensores = {
            '1': {
                'nivel': '040LT01',
                'flujo_entrada': '040FT01',
                'presion': '040PT01'
            },
            '2': {
                'nivel': '050LT01', 
                'flujo_entrada': '050FT01',
                'presion': '050PT01'
            }
        }
        
        if biodigestor_id not in sensores:
            raise ValueError(f"Biodigestor {biodigestor_id} no válido")
        
        sensor_config = sensores[biodigestor_id]
        
        # Obtener datos de nivel (simular conexión real por ahora)
        nivel_porcentaje = obtener_nivel_real_scada(biodigestor_id)
        volumen_actual = calcular_volumen_m3(nivel_porcentaje)
        
        # Obtener flujo de entrada
        flujo_entrada = obtener_flujo_entrada_real(biodigestor_id)
        
        # Calcular métricas
        volumen_libre = VOLUMEN_TOTAL_BIODIGESTOR - volumen_actual
        porcentaje_libre = 100 - nivel_porcentaje
        
        # Estimaciones temporales
        tiempo_llenado_horas = volumen_libre / flujo_entrada if flujo_entrada > 0 else float('inf')
        volumen_diario_entrada = flujo_entrada * 24
        
        return {
            'biodigestor_id': biodigestor_id,
            'timestamp': datetime.now().isoformat(),
            'nivel': {
                'porcentaje': nivel_porcentaje,
                'volumen_m3': volumen_actual,
                'volumen_libre_m3': volumen_libre,
                'porcentaje_libre': porcentaje_libre,
                'sensor': sensor_config['nivel']
            },
            'flujo_entrada': {
                'valor_m3_h': flujo_entrada,
                'volumen_diario_m3': volumen_diario_entrada,
                'porcentaje_biodigestor_dia': (volumen_diario_entrada / VOLUMEN_TOTAL_BIODIGESTOR) * 100,
                'sensor': sensor_config['flujo_entrada']
            },
            'estimaciones': {
                'tiempo_llenado_completo_horas': tiempo_llenado_horas,
                'tiempo_llenado_completo_dias': tiempo_llenado_horas / 24,
                'capacidad_dias_actuales': volumen_actual / volumen_diario_entrada if volumen_diario_entrada > 0 else 0
            },
            'alertas': generar_alertas_volumetricas(nivel_porcentaje, flujo_entrada, tiempo_llenado_horas)
        }
        
    except Exception as e:
        logger.error(f"Error calculando balance volumétrico biodigestor {biodigestor_id}: {e}")
        return {
            'error': True,
            'mensaje': str(e),
            'biodigestor_id': biodigestor_id,
            'timestamp': datetime.now().isoformat()
        }

def obtener_nivel_real_scada(biodigestor_id: str) -> float:
    """
    Obtiene nivel real del SCADA
    Por ahora simula, pero debe conectarse a la base real
    """
    # TODO: Conectar a base de datos real de Grafana
    # Por ahora usar datos simulados más realistas
    
    if biodigestor_id == '1':
        # Simular nivel cercano al SCADA (87%)
        import random
        return NIVEL_SCADA_REFERENCIA + random.uniform(-2, 2)
    else:
        import random
        return NIVEL_SCADA_REFERENCIA + random.uniform(-3, 1)

def obtener_flujo_entrada_real(biodigestor_id: str) -> float:
    """
    Obtiene flujo de entrada real
    """
    # TODO: Conectar a base de datos real
    # Simular flujos realistas basados en capacidad
    import random
    
    if biodigestor_id == '1':
        return random.uniform(25, 45)  # m³/h
    else:
        return random.uniform(30, 50)  # m³/h

def generar_alertas_volumetricas(nivel_porcentaje: float, flujo_entrada: float, tiempo_llenado_horas: float) -> List[str]:
    """Genera alertas basadas en parámetros volumétricos"""
    alertas = []
    
    if nivel_porcentaje > 90:
        alertas.append("🔴 CRÍTICO: Nivel muy alto (>90%)")
    elif nivel_porcentaje > 85:
        alertas.append("🟡 ALERTA: Nivel alto (>85%)")
    
    if nivel_porcentaje < 60:
        alertas.append("🟡 ALERTA: Nivel bajo (<60%)")
    
    if flujo_entrada > 50:
        alertas.append("🟡 ALERTA: Flujo de entrada muy alto (>50 m³/h)")
    elif flujo_entrada < 10:
        alertas.append("🟡 ALERTA: Flujo de entrada muy bajo (<10 m³/h)")
    
    if tiempo_llenado_horas < 24:
        alertas.append("🔴 CRÍTICO: Biodigestor se llenará en menos de 24 horas")
    elif tiempo_llenado_horas < 48:
        alertas.append("🟡 ALERTA: Biodigestor se llenará en menos de 48 horas")
    
    if not alertas:
        alertas.append("✅ NORMAL: Todos los parámetros en rango")
    
    return alertas

def obtener_balance_completo_planta() -> Dict[str, Any]:
    """Obtiene balance volumétrico completo de la planta"""
    try:
        balance_1 = obtener_balance_volumetrico_biodigestor('1')
        balance_2 = obtener_balance_volumetrico_biodigestor('2')
        
        # Calcular totales de planta
        if not balance_1.get('error') and not balance_2.get('error'):
            volumen_total_actual = balance_1['nivel']['volumen_m3'] + balance_2['nivel']['volumen_m3']
            volumen_total_libre = balance_1['nivel']['volumen_libre_m3'] + balance_2['nivel']['volumen_libre_m3']
            flujo_total_entrada = balance_1['flujo_entrada']['valor_m3_h'] + balance_2['flujo_entrada']['valor_m3_h']
            
            return {
                'timestamp': datetime.now().isoformat(),
                'biodigestores': {
                    '1': balance_1,
                    '2': balance_2
                },
                'totales_planta': {
                    'volumen_total_disponible': VOLUMEN_TOTAL_BIODIGESTOR * 2,
                    'volumen_actual_m3': volumen_total_actual,
                    'volumen_libre_m3': volumen_total_libre,
                    'porcentaje_ocupacion_planta': (volumen_total_actual / (VOLUMEN_TOTAL_BIODIGESTOR * 2)) * 100,
                    'flujo_total_entrada_m3_h': flujo_total_entrada,
                    'capacidad_entrada_diaria_m3': flujo_total_entrada * 24
                },
                'estado_general': determinar_estado_general_planta(balance_1, balance_2)
            }
        else:
            return {
                'error': True,
                'mensaje': 'Error obteniendo datos de uno o ambos biodigestores',
                'biodigestores': {
                    '1': balance_1,
                    '2': balance_2
                }
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo balance completo: {e}")
        return {
            'error': True,
            'mensaje': str(e),
            'timestamp': datetime.now().isoformat()
        }

def determinar_estado_general_planta(balance_1: Dict, balance_2: Dict) -> str:
    """Determina estado general de la planta basado en ambos biodigestores"""
    if balance_1.get('error') or balance_2.get('error'):
        return 'ERROR'
    
    alertas_1 = balance_1.get('alertas', [])
    alertas_2 = balance_2.get('alertas', [])
    
    alertas_criticas = [a for a in alertas_1 + alertas_2 if '🔴 CRÍTICO' in a]
    alertas_normales = [a for a in alertas_1 + alertas_2 if '🟡 ALERTA' in a]
    
    if alertas_criticas:
        return 'CRÍTICO'
    elif alertas_normales:
        return 'ALERTA'
    else:
        return 'NORMAL'

# Funciones para integración con Flask
def endpoint_balance_biodigestor_1():
    """Endpoint para balance del biodigestor 1"""
    return obtener_balance_volumetrico_biodigestor('1')

def endpoint_balance_biodigestor_2():
    """Endpoint para balance del biodigestor 2"""
    return obtener_balance_volumetrico_biodigestor('2')

def endpoint_balance_completo_planta():
    """Endpoint para balance completo de la planta"""
    return obtener_balance_completo_planta()

def registrar_endpoints_balance_volumetrico(app):
    """
    Registra los endpoints de este módulo en la aplicación Flask.
    """
    app.add_url_rule('/balance_volumetrico_biodigestor_1', 'balance_volumetrico_biodigestor_1', endpoint_balance_biodigestor_1, methods=['GET'])
    app.add_url_rule('/balance_volumetrico_biodigestor_2', 'balance_volumetrico_biodigestor_2', endpoint_balance_biodigestor_2, methods=['GET'])
    app.add_url_rule('/balance_volumetrico_completo', 'balance_volumetrico_completo', endpoint_balance_completo_planta, methods=['GET'])
    logger.info("✅ Endpoints de balance volumétrico registrados.")


if __name__ == "__main__":
    # Prueba del módulo
    print("🧪 Probando módulo de balance volumétrico...")
    
    balance = obtener_balance_completo_planta()
    print(json.dumps(balance, indent=2, ensure_ascii=False))
