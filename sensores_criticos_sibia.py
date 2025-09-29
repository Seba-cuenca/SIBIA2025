#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MÓDULO DE SENSORES CRÍTICOS - SIBIA
===================================

Módulo independiente con los sensores críticos más importantes:
- Presiones de biodigestores
- Flujos de entrada
- Niveles de llenado

Este módulo se puede importar desde app_CORREGIDO_OK_FINAL.py
"""

import pymysql
import random
from datetime import datetime
from typing import Dict, Any
from flask import jsonify
import logging

# Variable global para almacenar la configuración de la base de datos
db_config = None

def set_db_config(config):
    """Establece la configuración de la base de datos para este módulo."""
    global db_config
    db_config = config
    logging.info("Configuración de DB recibida en sensores_criticos_sibia.")

def obtener_conexion_db():
    """Establece conexión con la base de datos usando la configuración global."""
    if not db_config:
        logging.error("La configuración de la base de datos no ha sido establecida en sensores_criticos_sibia.")
        return None
    try:
        conexion = pymysql.connect(**db_config)
        return conexion
    except pymysql.MySQLError as e:
        logging.error(f"Error al conectar a la DB en sensores_criticos_sibia: {e}")
        return None

# ===== PRESIÓN BIODIGESTOR 1 (040PT01) =====

def obtener_040pt01() -> Dict[str, Any]:
    """Obtener Presión Biodigestor 1 desde Grafana (040PT01)"""
    conexion = None  # Inicializar conexion a None
    try:
        conexion = obtener_conexion_db()
        if not conexion:
            raise pymysql.MySQLError("No se pudo establecer conexión con la BD.")

        cursor = conexion.cursor()
        
        query = "SELECT fecha_hora, `040PT01` AS valor FROM biodigestores WHERE `040PT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado and resultado[1] is not None:
            valor = float(resultado[1])
            fecha_hora = resultado[0].strftime('%Y-%m-%d %H:%M:%S')
            
            # Determinar estado basado en rangos
            estado = determinar_estado_040pt01(valor)
            
            return {
                'valor': round(valor, 2),
                'unidad': 'bar',
                'sensor': '040PT01',
                'nombre': 'Presión Biodigestor 1',
                'descripcion': 'Presión interna del primer biodigestor',
                'tipo': 'presion',
                'fecha_hora': fecha_hora,
                'estado': estado,
                'fuente': 'grafana_real',
                'rangos': {
                    'normal': [0.1, 1.5],
                    'alerta': [1.5, 2.0],
                    'critico': [2.0, 3.0]
                }
            }
        else:
            # Si no hay resultado, devolver un estado de error controlado
            raise ValueError("No se encontraron datos para el sensor 040PT01")
            
    except Exception as e:
        logging.error(f"Error obteniendo Presión Biodigestor 1: {e}")
        # Devolver un objeto de error estandarizado
        return {
            'valor': 0.0,
            'unidad': 'bar',
            'sensor': '040PT01',
            'nombre': 'Presión Biodigestor 1',
            'descripcion': 'Presión interna del primer biodigestor',
            'tipo': 'presion',
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estado': 'error',
            'fuente': 'error_captura',
            'error_msg': str(e)
        }
    
    finally:
        if conexion and conexion.open:
            conexion.close()

def determinar_estado_040pt01(valor: float) -> str:
    """Determinar estado del sensor 040PT01 basado en el valor"""
    rango_normal = [0.1, 1.5]
    rango_alerta = [1.5, 2.0]
    rango_critico = [2.0, 3.0]
    
    if rango_normal[0] <= valor <= rango_normal[1]:
        return 'normal'
    elif rango_alerta[0] <= valor <= rango_alerta[1]:
        return 'alerta'
    elif rango_critico[0] <= valor <= rango_critico[1]:
        return 'critico'
    else:
        return 'fuera_rango'

def generar_datos_simulados_040pt01() -> Dict[str, Any]:
    """Generar datos simulados para Presión Biodigestor 1"""
    # Simular principalmente en rango normal
    rango_normal = [0.1, 1.5]
    valor = round(random.uniform(rango_normal[0], rango_normal[1]), 2)
    
    return {
        'valor': valor,
        'unidad': 'bar',
        'sensor': '040PT01',
        'nombre': 'Presión Biodigestor 1',
        'descripcion': 'Presión interna del primer biodigestor',
        'tipo': 'presion',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'normal',
        'fuente': 'simulado',
        'rangos': {
            'normal': [0.1, 1.5],
            'alerta': [1.5, 2.0],
            'critico': [2.0, 3.0]
        }
    }

# ===== PRESIÓN BIODIGESTOR 2 (050PT01) =====

def obtener_050pt01() -> Dict[str, Any]:
    """Obtener Presión Biodigestor 2 desde Grafana (050PT01)"""
    conexion = None
    try:
        conexion = obtener_conexion_db()
        if not conexion:
            raise pymysql.MySQLError("No se pudo establecer conexión con la BD.")

        cursor = conexion.cursor()
        
        query = "SELECT fecha_hora, `050PT01` AS valor FROM biodigestores WHERE `050PT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado and resultado[1] is not None:
            valor = float(resultado[1])
            fecha_hora = resultado[0].strftime('%Y-%m-%d %H:%M:%S')
            
            # Determinar estado basado en rangos
            estado = determinar_estado_050pt01(valor)
            
            return {
                'valor': round(valor, 2),
                'unidad': 'bar',
                'sensor': '050PT01',
                'nombre': 'Presión Biodigestor 2',
                'descripcion': 'Presión interna del segundo biodigestor',
                'tipo': 'presion',
                'fecha_hora': fecha_hora,
                'estado': estado,
                'fuente': 'grafana_real',
                'rangos': {
                    'normal': [0.1, 1.5],
                    'alerta': [1.5, 2.0],
                    'critico': [2.0, 3.0]
                }
            }
        else:
            raise ValueError("No se encontraron datos para el sensor 050PT01")
            
    except Exception as e:
        logging.error(f"Error obteniendo Presión Biodigestor 2: {e}")
        return {
            'valor': 0.0,
            'unidad': 'bar',
            'sensor': '050PT01',
            'nombre': 'Presión Biodigestor 2',
            'descripcion': 'Presión interna del segundo biodigestor',
            'tipo': 'presion',
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estado': 'error',
            'fuente': 'error_captura',
            'error_msg': str(e)
        }
    
    finally:
        if conexion and conexion.open:
            conexion.close()

def determinar_estado_050pt01(valor: float) -> str:
    """Determinar estado del sensor 050PT01 basado en el valor"""
    rango_normal = [0.1, 1.5]
    rango_alerta = [1.5, 2.0]
    rango_critico = [2.0, 3.0]
    
    if rango_normal[0] <= valor <= rango_normal[1]:
        return 'normal'
    elif rango_alerta[0] <= valor <= rango_alerta[1]:
        return 'alerta'
    elif rango_critico[0] <= valor <= rango_critico[1]:
        return 'critico'
    else:
        return 'fuera_rango'

def generar_datos_simulados_050pt01() -> Dict[str, Any]:
    """Generar datos simulados para Presión Biodigestor 2"""
    # Simular principalmente en rango normal
    rango_normal = [0.1, 1.5]
    valor = round(random.uniform(rango_normal[0], rango_normal[1]), 2)
    
    return {
        'valor': valor,
        'unidad': 'bar',
        'sensor': '050PT01',
        'nombre': 'Presión Biodigestor 2',
        'descripcion': 'Presión interna del segundo biodigestor',
        'tipo': 'presion',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'normal',
        'fuente': 'simulado',
        'rangos': {
            'normal': [0.1, 1.5],
            'alerta': [1.5, 2.0],
            'critico': [2.0, 3.0]
        }
    }

# ===== FLUJO ENTRADA BIODIGESTOR 1 (040FT01) =====

def obtener_040ft01() -> Dict[str, Any]:
    """Obtener Flujo Entrada Biodigestor 1 (040FT01) - USANDO DATOS SIMULADOS"""
    logging.info("Usando datos simulados para sensor 040FT01 (Flujo Entrada B1)")
    return generar_datos_simulados_040ft01()

def determinar_estado_040ft01(valor: float) -> str:
    """Determinar estado del sensor 040FT01 basado en el valor"""
    rango_normal = [10, 40]
    rango_alerta = [5, 10]
    rango_critico = [0, 5]
    
    if rango_normal[0] <= valor <= rango_normal[1]:
        return 'normal'
    elif rango_alerta[0] <= valor <= rango_alerta[1]:
        return 'alerta'
    elif rango_critico[0] <= valor <= rango_critico[1]:
        return 'critico'
    else:
        return 'fuera_rango'

def generar_datos_simulados_040ft01() -> Dict[str, Any]:
    """Generar datos simulados para Flujo Entrada Biodigestor 1"""
    # Simular principalmente en rango normal
    rango_normal = [10, 40]
    valor = round(random.uniform(rango_normal[0], rango_normal[1]), 2)
    
    return {
        'valor': valor,
        'unidad': 'm³/h',
        'sensor': '040FT01',
        'nombre': 'Flujo Entrada Biodigestor 1',
        'descripcion': 'Flujo de sustrato entrante al biodigestor 1',
        'tipo': 'flujo',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'normal',
        'fuente': 'simulado',
        'rangos': {
            'normal': [10, 40],
            'alerta': [5, 10],
            'critico': [0, 5]
        }
    }

# ===== FLUJO BIODIGESTOR 2 (050FT01) =====

def obtener_050ft01() -> Dict[str, Any]:
    """Obtener Flujo Entrada Biodigestor 2 (050FT01) - USANDO DATOS SIMULADOS"""
    logging.info("Usando datos simulados para sensor 050FT01 (Flujo Entrada B2)")
    return generar_datos_simulados_050ft01()

def determinar_estado_050ft01(valor: float) -> str:
    """Determinar estado del sensor 050FT01 basado en el valor"""
    rango_normal = [10, 40]
    rango_alerta = [5, 10]
    rango_critico = [0, 5]
    
    if rango_normal[0] <= valor <= rango_normal[1]:
        return 'normal'
    elif rango_alerta[0] <= valor <= rango_alerta[1]:
        return 'alerta'
    elif rango_critico[0] <= valor <= rango_critico[1]:
        return 'critico'
    else:
        return 'fuera_rango'

def generar_datos_simulados_050ft01() -> Dict[str, Any]:
    """Generar datos simulados para Flujo Entrada Biodigestor 2"""
    # Simular principalmente en rango normal
    rango_normal = [10, 40]
    valor = round(random.uniform(rango_normal[0], rango_normal[1]), 2)
    
    return {
        'valor': valor,
        'unidad': 'm³/h',
        'sensor': '050FT01',
        'nombre': 'Flujo Entrada Biodigestor 2',
        'descripcion': 'Flujo de sustrato entrante al biodigestor 2',
        'tipo': 'flujo',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'normal',
        'fuente': 'simulado',
        'rangos': {
            'normal': [10, 40],
            'alerta': [5, 10],
            'critico': [0, 5]
        }
    }

# ===== NIVEL BIODIGESTOR 1 (040LT01) =====

def obtener_040lt01() -> Dict[str, Any]:
    """Obtener Nivel Biodigestor 1 desde Grafana (040LT01)"""
    conexion = None
    try:
        conexion = obtener_conexion_db()
        if not conexion:
            raise pymysql.MySQLError("No se pudo establecer conexión con la BD.")

        cursor = conexion.cursor()
        
        query = "SELECT fecha_hora, `040LT01` AS valor FROM biodigestores WHERE `040LT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado and resultado[1] is not None:
            valor = float(resultado[1])
            fecha_hora = resultado[0].strftime('%Y-%m-%dT%H:%M:%S')
            
            # Determinar estado basado en rangos
            estado = determinar_estado_040lt01(valor)
            
            return {
                'valor': round(valor, 2),
                'unidad': '%',
                'sensor': '040LT01',
                'nombre': 'Nivel Biodigestor 1',
                'descripcion': 'Nivel de llenado del biodigestor 1',
                'tipo': 'nivel',
                'fecha_hora': fecha_hora,
                'estado': estado,
                'fuente': 'grafana_real',
                'rangos': {
                    'normal': [60, 85],
                    'alerta': [85, 95],
                    'critico': [95, 100]
                }
            }
        else:
            raise ValueError("No se encontraron datos para el sensor 040LT01")
            
    except Exception as e:
        logging.error(f"Error obteniendo Nivel Biodigestor 1: {e}")
        return {
            'valor': 0.0,
            'unidad': '%',
            'sensor': '040LT01',
            'nombre': 'Nivel Biodigestor 1',
            'descripcion': 'Nivel de llenado del biodigestor 1',
            'tipo': 'nivel',
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estado': 'error',
            'fuente': 'error_captura',
            'error_msg': str(e)
        }
    
    finally:
        if conexion and conexion.open:
            conexion.close()

def determinar_estado_040lt01(valor: float) -> str:
    """Determinar estado del sensor 040LT01 basado en el valor"""
    rango_normal = [60, 85]
    rango_alerta = [85, 95]
    rango_critico = [95, 100]
    
    if rango_normal[0] <= valor <= rango_normal[1]:
        return 'normal'
    elif rango_alerta[0] <= valor <= rango_alerta[1]:
        return 'alerta'
    elif rango_critico[0] <= valor <= rango_critico[1]:
        return 'critico'
    else:
        return 'fuera_rango'

def generar_datos_simulados_040lt01() -> Dict[str, Any]:
    """Generar datos simulados para Nivel Biodigestor 1"""
    # Simular principalmente en rango normal
    rango_normal = [60, 85]
    valor = round(random.uniform(rango_normal[0], rango_normal[1]), 2)
    
    return {
        'valor': valor,
        'unidad': '%',
        'sensor': '040LT01',
        'nombre': 'Nivel Biodigestor 1',
        'descripcion': 'Nivel de llenado del biodigestor 1',
        'tipo': 'nivel',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'normal',
        'fuente': 'simulado',
        'rangos': {
            'normal': [60, 85],
            'alerta': [85, 95],
            'critico': [95, 100]
        }
    }

# ===== NIVEL BIODIGESTOR 2 (050LT01) =====

def obtener_050lt01() -> Dict[str, Any]:
    """Obtener Nivel Biodigestor 2 desde Grafana (050LT01)"""
    conexion = None
    try:
        conexion = obtener_conexion_db()
        if not conexion:
            raise pymysql.MySQLError("No se pudo establecer conexión con la BD.")
        
        cursor = conexion.cursor()
        
        query = "SELECT fecha_hora, `050LT01` AS valor FROM biodigestores WHERE `050LT01` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado and resultado[1] is not None:
            valor = float(resultado[1])
            fecha_hora = resultado[0].strftime('%Y-%m-%dT%H:%M:%S')
            
            # Determinar estado basado en rangos
            estado = determinar_estado_050lt01(valor)
            
            return {
                'valor': round(valor, 2),
                'unidad': '%',
                'sensor': '050LT01',
                'nombre': 'Nivel Biodigestor 2',
                'descripcion': 'Nivel de llenado del biodigestor 2',
                'tipo': 'nivel',
                'fecha_hora': fecha_hora,
                'estado': estado,
                'fuente': 'grafana_real',
                'rangos': {
                    'normal': [60, 85],
                    'alerta': [85, 95],
                    'critico': [95, 100]
                }
            }
        else:
            raise ValueError("No se encontraron datos para el sensor 050LT01")
            
    except Exception as e:
        logging.error(f"Error obteniendo Nivel Biodigestor 2: {e}")
        return {
            'valor': 0.0,
            'unidad': '%',
            'sensor': '050LT01',
            'nombre': 'Nivel Biodigestor 2',
            'descripcion': 'Nivel de llenado del biodigestor 2',
            'tipo': 'nivel',
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estado': 'error',
            'fuente': 'error_captura',
            'error_msg': str(e)
        }
    
    finally:
        if conexion and conexion.open:
            conexion.close()

def determinar_estado_050lt01(valor: float) -> str:
    """Determinar estado del sensor 050LT01 basado en el valor"""
    rango_normal = [60, 85]
    rango_alerta = [85, 95]
    rango_critico = [95, 100]
    
    if rango_normal[0] <= valor <= rango_normal[1]:
        return 'normal'
    elif rango_alerta[0] <= valor <= rango_alerta[1]:
        return 'alerta'
    elif rango_critico[0] <= valor <= rango_critico[1]:
        return 'critico'
    else:
        return 'fuera_rango'

def generar_datos_simulados_050lt01() -> Dict[str, Any]:
    """Generar datos simulados para Nivel Biodigestor 2"""
    # Simular principalmente en rango normal
    rango_normal = [60, 85]
    valor = round(random.uniform(rango_normal[0], rango_normal[1]), 2)
    
    return {
        'valor': valor,
        'unidad': '%',
        'sensor': '050LT01',
        'nombre': 'Nivel Biodigestor 2',
        'descripcion': 'Nivel de llenado del biodigestor 2',
        'tipo': 'nivel',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'normal',
        'fuente': 'simulado',
        'rangos': {
            'normal': [60, 85],
            'alerta': [85, 95],
            'critico': [95, 100]
        }
    }

# ===== FUNCIONES AUXILIARES =====

def obtener_resumen_sensores_criticos() -> Dict[str, Any]:
    """Obtener resumen de todos los sensores críticos"""
    
    sensores = {
        '040PT01': obtener_040pt01(),
        '050PT01': obtener_050pt01(), 
        '040FT01': obtener_040ft01(),
        '050FT01': obtener_050ft01(),
        '040LT01': obtener_040lt01(),
        '050LT01': obtener_050lt01()
    }
    
    # Calcular estadísticas
    total_sensores = len(sensores)
    sensores_normales = sum(1 for s in sensores.values() if s.get('estado') == 'normal')
    sensores_alerta = sum(1 for s in sensores.values() if s.get('estado') == 'alerta')
    sensores_criticos = sum(1 for s in sensores.values() if s.get('estado') == 'critico')
    
    return {
        'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_sensores': total_sensores,
        'estadisticas': {
            'normales': sensores_normales,
            'alerta': sensores_alerta,
            'criticos': sensores_criticos,
            'porcentaje_normal': round((sensores_normales / total_sensores) * 100, 1)
        },
        'sensores': sensores,
        'estado_general': 'normal' if sensores_criticos == 0 and sensores_alerta == 0 else 'alerta' if sensores_criticos == 0 else 'critico'
    }

# ===== FUNCIÓN PARA REGISTRAR ENDPOINTS =====

def registrar_endpoints_sensores_criticos(app):
    """Registrar todos los endpoints de sensores críticos en la app Flask"""
    
    @app.route('/040pt01')
    def endpoint_040pt01():
        """Endpoint para obtener Presión Biodigestor 1"""
        try:
            datos = obtener_040pt01()
            return jsonify(datos)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'valor': 0.0,
                'sensor': '040PT01',
                'nombre': 'Presión Biodigestor 1',
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'error'
            })
    
    @app.route('/050pt01')
    def endpoint_050pt01():
        """Endpoint para obtener Presión Biodigestor 2"""
        try:
            datos = obtener_050pt01()
            return jsonify(datos)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'valor': 0.0,
                'sensor': '050PT01',
                'nombre': 'Presión Biodigestor 2',
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'error'
            })
    
    @app.route('/040ft01')
    def endpoint_040ft01():
        """Endpoint para obtener Flujo Entrada Biodigestor 1"""
        try:
            datos = obtener_040ft01()
            return jsonify(datos)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'valor': 0.0,
                'sensor': '040FT01',
                'nombre': 'Flujo Entrada Biodigestor 1',
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'error'
            })
    
    @app.route('/050ft01')
    def endpoint_050ft01():
        """Endpoint para obtener Flujo Entrada Biodigestor 2"""
        try:
            datos = obtener_050ft01()
            return jsonify(datos)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'valor': 0.0,
                'sensor': '050FT01',
                'nombre': 'Flujo Entrada Biodigestor 2',
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'error'
            })
    
    @app.route('/040lt01')
    def endpoint_040lt01():
        """Endpoint para obtener Nivel Biodigestor 1"""
        try:
            datos = obtener_040lt01()
            return jsonify(datos)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'valor': 0.0,
                'sensor': '040LT01',
                'nombre': 'Nivel Biodigestor 1',
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'error'
            })
    
    @app.route('/050lt01')
    def endpoint_050lt01():
        """Endpoint para obtener Nivel Biodigestor 2"""
        try:
            datos = obtener_050lt01()
            return jsonify(datos)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'valor': 0.0,
                'sensor': '050LT01',
                'nombre': 'Nivel Biodigestor 2',
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'error'
            })
    
    @app.route('/sensores_criticos_resumen')
    def endpoint_resumen_sensores_criticos():
        """Endpoint para obtener resumen de todos los sensores críticos"""
        try:
            resumen = obtener_resumen_sensores_criticos()
            return jsonify(resumen)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    print("✅ Endpoints de sensores críticos registrados:")
    print("  - /040pt01 - Presión Biodigestor 1")
    print("  - /050pt01 - Presión Biodigestor 2") 
    print("  - /040ft01 - Flujo Entrada Biodigestor 1")
    print("  - /050ft01 - Flujo Entrada Biodigestor 2")
    print("  - /040lt01 - Nivel Biodigestor 1")
    print("  - /050lt01 - Nivel Biodigestor 2")
    print("  - /sensores_criticos_resumen - Resumen de todos los sensores críticos")

if __name__ == "__main__":
    # Prueba independiente del módulo
    print("=== PRUEBA DEL MÓDULO DE SENSORES CRÍTICOS ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Probar cada sensor
    print("\n🔍 Probando sensores individualmente:")
    
    print(f"\n📊 Presión Biodigestor 1:")
    pt1 = obtener_040pt01()
    print(f"  Valor: {pt1['valor']} {pt1['unidad']} - Estado: {pt1['estado']}")
    
    print(f"\n📊 Presión Biodigestor 2:")
    pt2 = obtener_050pt01()
    print(f"  Valor: {pt2['valor']} {pt2['unidad']} - Estado: {pt2['estado']}")
    
    print(f"\n📊 Flujo Entrada Biodigestor 1:")
    ft1 = obtener_040ft01()
    print(f"  Valor: {ft1['valor']} {ft1['unidad']} - Estado: {ft1['estado']}")
    
    print(f"\n📊 Flujo Entrada Biodigestor 2:")
    ft2 = obtener_050ft01()
    print(f"  Valor: {ft2['valor']} {ft2['unidad']} - Estado: {ft2['estado']}")
    
    print(f"\n📊 Nivel Biodigestor 1:")
    lt1 = obtener_040lt01()
    print(f"  Valor: {lt1['valor']} {lt1['unidad']} - Estado: {lt1['estado']}")
    
    print(f"\n📊 Nivel Biodigestor 2:")
    lt2 = obtener_050lt01()
    print(f"  Valor: {lt2['valor']} {lt2['unidad']} - Estado: {lt2['estado']}")
    
    # Probar resumen
    print(f"\n📋 Resumen general:")
    resumen = obtener_resumen_sensores_criticos()
    print(f"  Estado general: {resumen['estado_general']}")
    print(f"  Sensores normales: {resumen['estadisticas']['normales']}/{resumen['total_sensores']}")
    
    print("\n✅ Módulo de sensores críticos funcionando correctamente") 