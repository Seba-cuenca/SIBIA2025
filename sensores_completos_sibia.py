"""
SIBIA - Módulo de Sensores Completos
Implementación de todos los sensores restantes identificados
Fecha: 21/06/2025
"""

import json
import random
from datetime import datetime
from typing import Dict, Any, List
import pymysql
import logging
from flask import jsonify, current_app

# Variable global para almacenar la configuración de la base de datos
db_config = None

def set_db_config(config):
    """Establece la configuración de la base de datos para este módulo."""
    global db_config
    db_config = config
    logging.info("Configuración de DB recibida en sensores_completos_sibia.")

def obtener_conexion_db():
    """Establece conexión con la base de datos usando la configuración global."""
    if not db_config:
        logging.error("La configuración de la base de datos no ha sido establecida en sensores_completos_sibia.")
        return None
    try:
        conexion = pymysql.connect(**db_config)
        return conexion
    except pymysql.MySQLError as e:
        logging.error(f"Error al conectar a la DB en sensores_completos_sibia: {e}")
        return None

# =============================================================================
# SENSORES DE PRESIÓN
# =============================================================================

def obtener_presion_linea_gas() -> Dict[str, Any]:
    """Obtiene datos de presión de línea de gas (Sensor mapeado a 080PIT01)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `080PIT01` as valor, fecha_hora FROM biodigestores WHERE `080PIT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    return {
                        'sensor_id': '070PT01',
                        'nombre': 'Presión Línea de Gas',
                        'valor': float(resultado[0]),
                        'unidad': 'bar',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if 1.0 <= float(resultado[0]) <= 3.0 else 'ALERTA',
                        'rango_operativo': '1.0 - 3.0 bar',
                        'tipo': 'presion',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo presión línea de gas: {e}")
    
    # Datos simulados o de error si falla la consulta
    return {
        'sensor_id': '070PT01',
        'nombre': 'Presión Línea de Gas',
        'valor': 0.0,
        'unidad': 'bar',
        'timestamp': datetime.now().isoformat(),
        'estado': 'ERROR',
        'rango_operativo': '1.0 - 3.0 bar',
        'tipo': 'presion',
        'fuente': 'ERROR_DB'
    }

def generar_datos_simulados_presion_linea() -> Dict[str, Any]:
    """Genera datos simulados para presión de línea de gas"""
    valor = round(random.uniform(1.5, 2.8), 2)
    return {
        'sensor_id': '070PT01',
        'nombre': 'Presión Línea de Gas',
        'valor': valor,
        'unidad': 'bar',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 1.0 <= valor <= 3.0 else 'ALERTA',
        'rango_operativo': '1.0 - 3.0 bar',
        'tipo': 'presion',
        'fuente': 'SIMULADO'
    }

# =============================================================================
# SENSORES DE FLUJO
# =============================================================================

def obtener_flujo_biogas() -> Dict[str, Any]:
    """Obtiene datos de flujo de biogás (Sensor mapeado a 090FIT01)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `090FIT01` as valor, fecha_hora FROM biodigestores WHERE `090FIT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    return {
                        'sensor_id': '070FT01',
                        'nombre': 'Flujo de Biogás',
                        'valor': float(resultado[0]),
                        'unidad': 'm³/h',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if 100 <= float(resultado[0]) <= 500 else 'ALERTA',
                        'rango_operativo': '100 - 500 m³/h',
                        'tipo': 'flujo',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo flujo de biogás: {e}")
    
    return {
        'sensor_id': '070FT01',
        'nombre': 'Flujo de Biogás',
        'valor': 0.0,
        'unidad': 'm³/h',
        'timestamp': datetime.now().isoformat(),
        'estado': 'ERROR',
        'rango_operativo': '100 - 500 m³/h',
        'tipo': 'flujo',
        'fuente': 'ERROR_DB'
    }

def generar_datos_simulados_flujo_biogas() -> Dict[str, Any]:
    """Genera datos simulados para flujo de biogás"""
    valor = round(random.uniform(200, 450), 1)
    return {
        'sensor_id': '070FT01',
        'nombre': 'Flujo de Biogás',
        'valor': valor,
        'unidad': 'm³/h',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 100 <= valor <= 500 else 'ALERTA',
        'rango_operativo': '100 - 500 m³/h',
        'tipo': 'flujo',
        'fuente': 'SIMULADO'
    }

# =============================================================================
# SENSORES DE pH
# =============================================================================

def obtener_ph_biodigestor_1() -> Dict[str, Any]:
    """Obtiene datos de pH Biodigestor 1 (040AT01) - NO IMPLEMENTADO EN DB"""
    logging.warning("Intento de acceso a sensor no implementado en DB: 040AT01 (pH Biodigestor 1)")
    return {
        'sensor_id': '040AT01',
        'nombre': 'pH Biodigestor 1',
        'valor': 0.0,
        'unidad': 'pH',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NO_IMPLEMENTADO',
        'rango_operativo': '6.8 - 7.8 pH',
        'tipo': 'ph',
        'fuente': 'SISTEMA'
    }

def obtener_ph_biodigestor_2() -> Dict[str, Any]:
    """Obtiene datos de pH Biodigestor 2 (050AT01) - NO IMPLEMENTADO EN DB"""
    logging.warning("Intento de acceso a sensor no implementado en DB: 050AT01 (pH Biodigestor 2)")
    return {
        'sensor_id': '050AT01',
        'nombre': 'pH Biodigestor 2',
        'valor': 0.0,
        'unidad': 'pH',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NO_IMPLEMENTADO',
        'rango_operativo': '6.8 - 7.8 pH',
        'tipo': 'ph',
        'fuente': 'SISTEMA'
    }

def generar_datos_simulados_ph(biodigestor: int) -> Dict[str, Any]:
    """Genera datos simulados para pH"""
    valor = round(random.uniform(7.0, 7.6), 2)
    return {
        'sensor_id': f'0{biodigestor+3}0AT01',
        'nombre': f'pH Biodigestor {biodigestor}',
        'valor': valor,
        'unidad': 'pH',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 6.8 <= valor <= 7.8 else 'ALERTA',
        'rango_operativo': '6.8 - 7.8 pH',
        'tipo': 'ph',
        'fuente': 'SIMULADO'
    }

# =============================================================================
# SENSORES DE TEMPERATURA ADICIONALES
# =============================================================================

def obtener_temperatura_adicional_biodigestor_1() -> Dict[str, Any]:
    """Obtiene temperatura adicional Biodigestor 1 (040TT02) - NO IMPLEMENTADO EN DB"""
    logging.warning("Intento de acceso a sensor no implementado en DB: 040TT02 (Temp Adicional B1)")
    return {
        'sensor_id': '040TT02',
        'nombre': 'Temperatura Adicional Biodigestor 1',
        'valor': 0.0,
        'unidad': '°C',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NO_IMPLEMENTADO',
        'rango_operativo': '35 - 42 °C',
        'tipo': 'temperatura',
        'fuente': 'SISTEMA'
    }

def obtener_temperatura_adicional_biodigestor_2() -> Dict[str, Any]:
    """Obtiene temperatura adicional Biodigestor 2 (050TT02) - NO IMPLEMENTADO EN DB"""
    logging.warning("Intento de acceso a sensor no implementado en DB: 050TT02 (Temp Adicional B2)")
    return {
        'sensor_id': '050TT02',
        'nombre': 'Temperatura Adicional Biodigestor 2',
        'valor': 0.0,
        'unidad': '°C',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NO_IMPLEMENTADO',
        'rango_operativo': '35 - 42 °C',
        'tipo': 'temperatura',
        'fuente': 'SISTEMA'
    }

def obtener_temperatura_linea_gas() -> Dict[str, Any]:
    """Obtiene temperatura línea de gas (070TT01)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `070TT01` as valor, fecha_hora FROM biodigestores WHERE `070TT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado:
                    valor = float(resultado[0])
                    return {
                        'sensor_id': '070TT01',
                        'nombre': 'Temperatura Línea de Gas',
                        'valor': valor,
                        'unidad': '°C',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if 25 <= valor <= 45 else 'ALERTA',
                        'rango_operativo': '25 - 45 °C',
                        'tipo': 'temperatura',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo temperatura línea de gas: {e}")
    
    return generar_datos_simulados_temperatura_linea_gas()

def generar_datos_simulados_temperatura_adicional(biodigestor: int) -> Dict[str, Any]:
    """Genera datos simulados para temperatura adicional"""
    valor = round(random.uniform(36, 40), 1)
    return {
        'sensor_id': f'0{biodigestor+3}0TT02',
        'nombre': f'Temperatura Adicional Biodigestor {biodigestor}',
        'valor': valor,
        'unidad': '°C',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 35 <= valor <= 42 else 'ALERTA',
        'rango_operativo': '35 - 42 °C',
        'tipo': 'temperatura',
        'fuente': 'SIMULADO'
    }

def generar_datos_simulados_temperatura_linea_gas() -> Dict[str, Any]:
    """Genera datos simulados para temperatura línea de gas"""
    valor = round(random.uniform(30, 40), 1)
    return {
        'sensor_id': '070TT01',
        'nombre': 'Temperatura Línea de Gas',
        'valor': valor,
        'unidad': '°C',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 25 <= valor <= 45 else 'ALERTA',
        'rango_operativo': '25 - 45 °C',
        'tipo': 'temperatura',
        'fuente': 'SIMULADO'
    }

# =============================================================================
# SENSORES DE ENERGÍA ADICIONALES
# =============================================================================

def obtener_generacion_secundaria() -> Dict[str, Any]:
    """Obtiene datos de generación secundaria (070FIT02AO1) - NO IMPLEMENTADO EN DB"""
    logging.warning("Intento de acceso a sensor no implementado en DB: 070FIT02AO1 (Gen Secundaria)")
    return {
        'sensor_id': '070FIT02AO1',
        'nombre': 'Generación Secundaria',
        'valor': 0.0,
        'unidad': 'kW',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NO_IMPLEMENTADO',
        'rango_operativo': 'N/A',
        'tipo': 'potencia',
        'fuente': 'SISTEMA'
    }

def obtener_generacion_terciaria() -> Dict[str, Any]:
    """Obtiene datos de generación terciaria (070FIT03AO1) - NO IMPLEMENTADO EN DB"""
    logging.warning("Intento de acceso a sensor no implementado en DB: 070FIT03AO1 (Gen Terciaria)")
    return {
        'sensor_id': '070FIT03AO1',
        'nombre': 'Generación Terciaria',
        'valor': 0.0,
        'unidad': 'kW',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NO_IMPLEMENTADO',
        'rango_operativo': 'N/A',
        'tipo': 'potencia',
        'fuente': 'SISTEMA'
    }

def generar_datos_simulados_generacion_secundaria() -> Dict[str, Any]:
    """Genera datos simulados para generación secundaria"""
    valor = round(random.uniform(200, 600), 1)
    return {
        'sensor_id': '070FIT02AO1',
        'nombre': 'Generación Secundaria',
        'valor': valor,
        'unidad': 'kW',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if valor > 0 else 'ALERTA',
        'rango_operativo': '> 0 kW',
        'tipo': 'energia',
        'fuente': 'SIMULADO'
    }

def generar_datos_simulados_generacion_terciaria() -> Dict[str, Any]:
    """Genera datos simulados para generación terciaria"""
    valor = round(random.uniform(150, 500), 1)
    return {
        'sensor_id': '070FIT03AO1',
        'nombre': 'Generación Terciaria',
        'valor': valor,
        'unidad': 'kW',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if valor > 0 else 'ALERTA',
        'rango_operativo': '> 0 kW',
        'tipo': 'energia',
        'fuente': 'SIMULADO'
    }

# =============================================================================
# SENSORES DE GASES ADICIONALES
# =============================================================================

def obtener_oxigeno_secundario() -> Dict[str, Any]:
    """Obtiene datos de Oxígeno Secundario (mapeado a 070AIT01AO1)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `070AIT01AO1` as valor, fecha_hora FROM biodigestores WHERE `070AIT01AO1` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    valor = float(resultado[0])
                    return {
                        'sensor_id': '070AIT02AO1',
                        'nombre': 'Oxígeno Secundario',
                        'valor': valor,
                        'unidad': '%',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if valor < 2.0 else 'ALERTA',
                        'rango_operativo': '< 2.0 %',
                        'tipo': 'gas',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo Oxígeno Secundario: {e}")
    
    return {
        'sensor_id': '070AIT02AO1',
        'nombre': 'Oxígeno Secundario',
        'valor': 0.0,
        'unidad': '%',
        'timestamp': datetime.now().isoformat(),
        'estado': 'ERROR',
        'rango_operativo': '0 - 2 %',
        'tipo': 'concentracion_gas',
        'fuente': 'ERROR_DB'
    }

def obtener_metano_secundario() -> Dict[str, Any]:
    """Obtiene datos de Metano Secundario (mapeado a 070AIT01AO2)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `070AIT01AO2` as valor, fecha_hora FROM biodigestores WHERE `070AIT01AO2` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    valor = float(resultado[0])
                    return {
                        'sensor_id': '070AIT02AO2',
                        'nombre': 'Metano Secundario',
                        'valor': valor,
                        'unidad': '%',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if 55 <= valor <= 70 else 'ALERTA',
                        'rango_operativo': '55 - 70 %',
                        'tipo': 'gas',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo Metano Secundario: {e}")
    
    return {
        'sensor_id': '070AIT02AO2',
        'nombre': 'Metano Secundario',
        'valor': 0.0,
        'unidad': '%',
        'timestamp': datetime.now().isoformat(),
        'estado': 'ERROR',
        'rango_operativo': '50 - 70 %',
        'tipo': 'concentracion_gas',
        'fuente': 'ERROR_DB'
    }

def obtener_co2_secundario() -> Dict[str, Any]:
    """Obtiene datos de CO2 Secundario (mapeado a 070AIT01AO3)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `070AIT01AO3` as valor, fecha_hora FROM biodigestores WHERE `070AIT01AO3` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    valor = float(resultado[0])
                    return {
                        'sensor_id': '070AIT02AO3',
                        'nombre': 'CO2 Secundario',
                        'valor': valor,
                        'unidad': '%',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if 25 <= valor <= 40 else 'ALERTA',
                        'rango_operativo': '25 - 40 %',
                        'tipo': 'gas',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo CO2 Secundario: {e}")
    
    return {
        'sensor_id': '070AIT02AO3',
        'nombre': 'CO2 Secundario',
        'valor': 0.0,
        'unidad': '%',
        'timestamp': datetime.now().isoformat(),
        'estado': 'ERROR',
        'rango_operativo': '30 - 50 %',
        'tipo': 'concentracion_gas',
        'fuente': 'ERROR_DB'
    }

def obtener_h2s_secundario() -> Dict[str, Any]:
    """Obtiene datos de H2S Secundario (mapeado a 070AIT01AO4)"""
    try:
        conexion = obtener_conexion_db()
        if conexion:
            with conexion.cursor() as cursor:
                query = """
                SELECT `070AIT01AO4` as valor, fecha_hora FROM biodigestores WHERE `070AIT01AO4` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1
                """
                cursor.execute(query)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    valor = float(resultado[0])
                    return {
                        'sensor_id': '070AIT02AO4',
                        'nombre': 'H2S Secundario',
                        'valor': valor,
                        'unidad': 'ppm',
                        'timestamp': resultado[1].strftime('%Y-%m-%dT%H:%M:%S'),
                        'estado': 'NORMAL' if valor < 1000 else 'ALERTA',
                        'rango_operativo': '< 1000 ppm',
                        'tipo': 'gas',
                        'fuente': 'SCADA'
                    }
    except Exception as e:
        logging.error(f"Error obteniendo H2S Secundario: {e}")
    
    return {
        'sensor_id': '070AIT02AO4',
        'nombre': 'H2S Secundario',
        'valor': 0.0,
        'unidad': 'ppm',
        'timestamp': datetime.now().isoformat(),
        'estado': 'ERROR',
        'rango_operativo': '0 - 1000 ppm',
        'tipo': 'concentracion_gas',
        'fuente': 'ERROR_DB'
    }

def generar_datos_simulados_oxigeno_secundario() -> Dict[str, Any]:
    """Genera datos simulados para oxígeno secundario"""
    valor = round(random.uniform(0.5, 1.8), 2)
    return {
        'sensor_id': '070AIT02AO1',
        'nombre': 'Oxígeno Secundario',
        'valor': valor,
        'unidad': '%',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if valor < 2.0 else 'ALERTA',
        'rango_operativo': '< 2.0 %',
        'tipo': 'gas',
        'fuente': 'SIMULADO'
    }

def generar_datos_simulados_metano_secundario() -> Dict[str, Any]:
    """Genera datos simulados para metano secundario"""
    valor = round(random.uniform(58, 68), 1)
    return {
        'sensor_id': '070AIT02AO2',
        'nombre': 'Metano Secundario',
        'valor': valor,
        'unidad': '%',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 55 <= valor <= 70 else 'ALERTA',
        'rango_operativo': '55 - 70 %',
        'tipo': 'gas',
        'fuente': 'SIMULADO'
    }

def generar_datos_simulados_co2_secundario() -> Dict[str, Any]:
    """Genera datos simulados para CO2 secundario"""
    valor = round(random.uniform(28, 38), 1)
    return {
        'sensor_id': '070AIT02AO3',
        'nombre': 'CO2 Secundario',
        'valor': valor,
        'unidad': '%',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if 25 <= valor <= 40 else 'ALERTA',
        'rango_operativo': '25 - 40 %',
        'tipo': 'gas',
        'fuente': 'SIMULADO'
    }

def generar_datos_simulados_h2s_secundario() -> Dict[str, Any]:
    """Genera datos simulados para H2S secundario"""
    valor = round(random.uniform(200, 800), 0)
    return {
        'sensor_id': '070AIT02AO4',
        'nombre': 'H2S Secundario',
        'valor': valor,
        'unidad': 'ppm',
        'timestamp': datetime.now().isoformat(),
        'estado': 'NORMAL' if valor < 1000 else 'ALERTA',
        'rango_operativo': '< 1000 ppm',
        'tipo': 'gas',
        'fuente': 'SIMULADO'
    }

# =============================================================================
# FUNCIÓN PRINCIPAL DE RESUMEN
# =============================================================================

def obtener_todos_los_sensores_completos() -> Dict[str, Any]:
    """Obtiene datos de todos los sensores implementados"""
    try:
        # Sensores de presión
        presion_linea = obtener_presion_linea_gas()
        
        # Sensores de flujo
        flujo_biogas = obtener_flujo_biogas()
        
        # Sensores de pH
        ph_bio1 = obtener_ph_biodigestor_1()
        ph_bio2 = obtener_ph_biodigestor_2()
        
        # Temperaturas adicionales
        temp_add_bio1 = obtener_temperatura_adicional_biodigestor_1()
        temp_add_bio2 = obtener_temperatura_adicional_biodigestor_2()
        temp_linea_gas = obtener_temperatura_linea_gas()
        
        # Generación adicional
        gen_secundaria = obtener_generacion_secundaria()
        gen_terciaria = obtener_generacion_terciaria()
        
        # Gases adicionales
        o2_secundario = obtener_oxigeno_secundario()
        ch4_secundario = obtener_metano_secundario()
        co2_secundario = obtener_co2_secundario()
        h2s_secundario = obtener_h2s_secundario()
        
        # Contar estados
        todos_sensores = [
            presion_linea, flujo_biogas, ph_bio1, ph_bio2,
            temp_add_bio1, temp_add_bio2, temp_linea_gas,
            gen_secundaria, gen_terciaria, o2_secundario,
            ch4_secundario, co2_secundario, h2s_secundario
        ]
        
        total_sensores = len(todos_sensores)
        sensores_normales = len([s for s in todos_sensores if s['estado'] == 'NORMAL'])
        sensores_alerta = total_sensores - sensores_normales
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_sensores': total_sensores,
            'sensores_normales': sensores_normales,
            'sensores_alerta': sensores_alerta,
            'estado_general': 'NORMAL' if sensores_alerta == 0 else 'ALERTA',
            'sensores': {
                'presion': {
                    'linea_gas': presion_linea
                },
                'flujo': {
                    'biogas': flujo_biogas
                },
                'ph': {
                    'biodigestor_1': ph_bio1,
                    'biodigestor_2': ph_bio2
                },
                'temperatura': {
                    'adicional_biodigestor_1': temp_add_bio1,
                    'adicional_biodigestor_2': temp_add_bio2,
                    'linea_gas': temp_linea_gas
                },
                'energia': {
                    'generacion_secundaria': gen_secundaria,
                    'generacion_terciaria': gen_terciaria
                },
                'gases': {
                    'oxigeno_secundario': o2_secundario,
                    'metano_secundario': ch4_secundario,
                    'co2_secundario': co2_secundario,
                    'h2s_secundario': h2s_secundario
                }
            }
        }
        
    except Exception as e:
        logging.error(f"Error obteniendo todos los sensores: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'estado_general': 'ERROR'
        }

# =============================================================================
# FUNCIONES DE INTEGRACIÓN FLASK
# =============================================================================

def registrar_endpoints_sensores_completos(app):
    """Registra todos los endpoints de este módulo en la aplicación Flask."""
    
    @app.route('/070pt01')
    def presion_linea_gas():
        """Endpoint para presión de línea de gas"""
        return jsonify(obtener_presion_linea_gas())

    @app.route('/070ft01')
    def flujo_biogas():
        """Endpoint para flujo de biogás"""
        return jsonify(obtener_flujo_biogas())

    @app.route('/040at01')
    def ph_biodigestor_1():
        """Endpoint para pH Biodigestor 1"""
        return jsonify(obtener_ph_biodigestor_1())

    @app.route('/050at01')
    def ph_biodigestor_2():
        """Endpoint para pH Biodigestor 2"""
        return jsonify(obtener_ph_biodigestor_2())

    @app.route('/040tt02')
    def temperatura_adicional_biodigestor_1():
        """Endpoint para temperatura adicional Biodigestor 1"""
        return jsonify(obtener_temperatura_adicional_biodigestor_1())

    @app.route('/050tt02')
    def temperatura_adicional_biodigestor_2():
        """Endpoint para temperatura adicional Biodigestor 2"""
        return jsonify(obtener_temperatura_adicional_biodigestor_2())

    @app.route('/070tt01')
    def temperatura_linea_gas():
        """Endpoint para temperatura línea de gas"""
        return jsonify(obtener_temperatura_linea_gas())

    @app.route('/070fit02ao1')
    def generacion_secundaria():
        """Endpoint para generación secundaria"""
        return jsonify(obtener_generacion_secundaria())

    @app.route('/070fit03ao1')
    def generacion_terciaria():
        """Endpoint para generación terciaria"""
        return jsonify(obtener_generacion_terciaria())

    @app.route('/070ait02ao1')
    def oxigeno_secundario():
        """Endpoint para oxígeno secundario"""
        return jsonify(obtener_oxigeno_secundario())

    @app.route('/070ait02ao2')
    def metano_secundario():
        """Endpoint para metano secundario"""
        return jsonify(obtener_metano_secundario())

    @app.route('/070ait02ao3')
    def co2_secundario():
        """Endpoint para CO2 secundario"""
        return jsonify(obtener_co2_secundario())

    @app.route('/070ait02ao4')
    def h2s_secundario():
        """Endpoint para H2S secundario"""
        return jsonify(obtener_h2s_secundario())
        
    @app.route('/sensores_completos_resumen')
    def sensores_completos_resumen():
        """Devuelve un resumen de todos los sensores completos."""
        try:
            datos = obtener_todos_los_sensores_completos()
            return jsonify(datos)
        except Exception as e:
            logging.error(f"Error en endpoint /sensores_completos_resumen: {e}")
            return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Prueba de funcionamiento
    print("🧪 Probando módulo de sensores completos...")
    resultado = obtener_todos_los_sensores_completos()
    print(f"📊 Total sensores: {resultado.get('total_sensores', 0)}")
    print(f"✅ Estado general: {resultado.get('estado_general', 'DESCONOCIDO')}")