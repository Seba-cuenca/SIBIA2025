#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAPEO COMPLETO DE SENSORES GRAFANA - SIBIA
===========================================

Este archivo contiene el mapeo completo de todos los sensores identificados
en la base de datos de Grafana y proporciona un sistema para agregar nuevos
sensores de forma organizada.
"""

from datetime import datetime
from typing import Dict, List, Any
import json

# =============================================================================
# MAPEO ACTUAL DE SENSORES IDENTIFICADOS
# =============================================================================

SENSORES_IDENTIFICADOS = {
    
    # GENERACIÓN DE ENERGÍA
    "energia": {
        "070FIT01AO1": {
            "nombre": "Generación Eléctrica Principal",
            "descripcion": "Generación de energía eléctrica en kW",
            "unidad": "kW",
            "tipo": "flujo_energia",
            "rango_normal": [1200, 1400],
            "implementado": True,
            "endpoint": "/generacion_actual",
            "query": "SELECT fecha_hora, 070FIT01AO1 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        }
    },
    
    # CALIDAD DE GASES
    "gases": {
        "070AIT01AO2": {
            "nombre": "Calidad de Metano (CH4)",
            "descripcion": "Porcentaje de metano en el biogás",
            "unidad": "% CH4",
            "tipo": "calidad_gas",
            "rango_normal": [50, 65],
            "implementado": True,
            "endpoint": "/metano_actual",
            "query": "SELECT fecha_hora, 070AIT01AO2/1.0 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        },
        "070AIT01AO4": {
            "nombre": "Sulfídrico (H2S)",
            "descripcion": "Concentración de sulfuro de hidrógeno",
            "unidad": "ppm",
            "tipo": "calidad_gas",
            "rango_normal": [0, 200],
            "implementado": True,
            "endpoint": "/h2s_actual",
            "query": "SELECT fecha_hora, 070AIT01AO4 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        },
        "070AIT01AO1": {
            "nombre": "Oxígeno (O2)",
            "descripcion": "Concentración de oxígeno en el biogás",
            "unidad": "% O2",
            "tipo": "calidad_gas",
            "rango_normal": [0, 5],
            "implementado": True,
            "endpoint": "/oxigeno_biodigestores",
            "query": "SELECT fecha_hora, 070AIT01AO1/1.0 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        },
        "070AIT01AO3": {
            "nombre": "Dióxido de Carbono (CO2)",
            "descripcion": "Concentración de dióxido de carbono",
            "unidad": "% CO2",
            "tipo": "calidad_gas",
            "rango_normal": [30, 45],
            "implementado": True,
            "endpoint": "/dioxido_carbono_biodigestores",
            "query": "SELECT fecha_hora, 070AIT01AO3 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        }
    },
    
    # TEMPERATURAS
    "temperaturas": {
        "040TT01": {
            "nombre": "Temperatura Biodigestor 1",
            "descripcion": "Temperatura interna del primer biodigestor",
            "unidad": "°C",
            "tipo": "temperatura",
            "rango_normal": [35, 42],
            "implementado": True,
            "endpoint": "/temperatura_biodigestor_1",
            "query": "SELECT fecha_hora, 040TT01 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        },
        "050TT01": {
            "nombre": "Temperatura Biodigestor 2",
            "descripcion": "Temperatura interna del segundo biodigestor",
            "unidad": "°C",
            "tipo": "temperatura",
            "rango_normal": [35, 42],
            "implementado": True,
            "endpoint": "/temperatura_biodigestor_2",
            "query": "SELECT fecha_hora, 050TT01 AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        }
    }
}

# =============================================================================
# SENSORES POTENCIALES (PATRONES COMUNES EN SISTEMAS SCADA)
# =============================================================================

SENSORES_POTENCIALES = {
    
    # PRESIONES (PT - Pressure Transmitter)
    "presiones": {
        "040PT01": {
            "nombre": "Presión Biodigestor 1",
            "descripcion": "Presión interna del primer biodigestor",
            "unidad": "bar",
            "tipo": "presion",
            "rango_estimado": [0, 2],
            "implementado": False
        },
        "050PT01": {
            "nombre": "Presión Biodigestor 2",
            "descripcion": "Presión interna del segundo biodigestor",
            "unidad": "bar",
            "tipo": "presion",
            "rango_estimado": [0, 2],
            "implementado": False
        },
        "070PT01": {
            "nombre": "Presión Línea de Gas",
            "descripcion": "Presión en la línea principal de biogás",
            "unidad": "bar",
            "tipo": "presion",
            "rango_estimado": [0, 1.5],
            "implementado": False
        }
    },
    
    # FLUJOS (FT - Flow Transmitter)
    "flujos": {
        "040FT01": {
            "nombre": "Flujo Entrada Biodigestor 1",
            "descripcion": "Flujo de sustrato entrante al biodigestor 1",
            "unidad": "m³/h",
            "tipo": "flujo_liquido",
            "rango_estimado": [0, 50],
            "implementado": False
        },
        "050FT01": {
            "nombre": "Flujo Entrada Biodigestor 2",
            "descripcion": "Flujo de sustrato entrante al biodigestor 2",
            "unidad": "m³/h",
            "tipo": "flujo_liquido",
            "rango_estimado": [0, 50],
            "implementado": False
        },
        "070FT01": {
            "nombre": "Flujo de Biogás",
            "descripcion": "Flujo volumétrico de biogás producido",
            "unidad": "m³/h",
            "tipo": "flujo_gas",
            "rango_estimado": [0, 200],
            "implementado": False
        }
    },
    
    # NIVELES (LT - Level Transmitter)
    "niveles": {
        "040LT01": {
            "nombre": "Nivel Biodigestor 1",
            "descripcion": "Nivel de llenado del biodigestor 1",
            "unidad": "%",
            "tipo": "nivel",
            "rango_estimado": [0, 100],
            "implementado": False
        },
        "050LT01": {
            "nombre": "Nivel Biodigestor 2",
            "descripcion": "Nivel de llenado del biodigestor 2",
            "unidad": "%",
            "tipo": "nivel",
            "rango_estimado": [0, 100],
            "implementado": False
        }
    },
    
    # pH Y CONDUCTIVIDAD
    "calidad_agua": {
        "040AT01": {
            "nombre": "pH Biodigestor 1",
            "descripcion": "pH del sustrato en biodigestor 1",
            "unidad": "pH",
            "tipo": "ph",
            "rango_estimado": [6.5, 8.5],
            "implementado": False
        },
        "050AT01": {
            "nombre": "pH Biodigestor 2",
            "descripcion": "pH del sustrato en biodigestor 2",
            "unidad": "pH",
            "tipo": "ph",
            "rango_estimado": [6.5, 8.5],
            "implementado": False
        }
    }
}

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def generar_config_completa():
    """Generar configuración completa de sensores"""
    config = {
        "fecha_generacion": datetime.now().isoformat(),
        "version": "1.0",
        "sensores_implementados": SENSORES_IDENTIFICADOS,
        "sensores_potenciales": SENSORES_POTENCIALES,
        "resumen": {
            "total_implementados": sum(len(categoria) for categoria in SENSORES_IDENTIFICADOS.values()),
            "total_potenciales": sum(len(categoria) for categoria in SENSORES_POTENCIALES.values()),
            "categorias_implementadas": list(SENSORES_IDENTIFICADOS.keys()),
            "categorias_potenciales": list(SENSORES_POTENCIALES.keys())
        }
    }
    
    return config

def obtener_sensores_por_tipo(tipo: str, incluir_potenciales: bool = False) -> Dict[str, Any]:
    """Obtener sensores filtrados por tipo"""
    sensores = {}
    
    # Buscar en sensores implementados
    for categoria, sensores_cat in SENSORES_IDENTIFICADOS.items():
        for sensor_id, sensor_info in sensores_cat.items():
            if sensor_info.get('tipo') == tipo:
                sensores[sensor_id] = {**sensor_info, 'categoria': categoria, 'estado': 'implementado'}
    
    # Buscar en sensores potenciales si se solicita
    if incluir_potenciales:
        for categoria, sensores_cat in SENSORES_POTENCIALES.items():
            for sensor_id, sensor_info in sensores_cat.items():
                if sensor_info.get('tipo') == tipo:
                    sensores[sensor_id] = {**sensor_info, 'categoria': categoria, 'estado': 'potencial'}
    
    return sensores

def generar_queries_sql_nuevos() -> List[str]:
    """Generar queries SQL para probar sensores potenciales"""
    queries = []
    
    for categoria, sensores_cat in SENSORES_POTENCIALES.items():
        for sensor_id, sensor_info in sensores_cat.items():
            query = f"SELECT fecha_hora, `{sensor_id}` AS valor FROM biodigestores WHERE `{sensor_id}` IS NOT NULL ORDER BY fecha_hora DESC LIMIT 5"
            queries.append({
                'sensor': sensor_id,
                'nombre': sensor_info['nombre'],
                'query': query,
                'categoria': categoria
            })
    
    return queries

def generar_template_endpoint(sensor_id: str, sensor_info: Dict[str, Any]) -> str:
    """Generar template de código para un nuevo endpoint"""
    
    template = f'''
def obtener_{sensor_id.lower()}() -> Dict[str, Any]:
    """Obtener {sensor_info['nombre']} desde Grafana ({sensor_id})"""
    try:
        if not MYSQL_DISPONIBLE:
            return generar_datos_simulados_{sensor_id.lower()}()
        
        config_grafana = obtener_conexion_db()
        conexion = pymysql.connect(**config_grafana)
        cursor = conexion.cursor()
        
        query = "SELECT fecha_hora, `{sensor_id}` AS valor FROM biodigestores ORDER BY fecha_hora DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado and resultado[1] is not None:
            valor = float(resultado[1])
            fecha_hora = resultado[0].strftime('%Y-%m-%d %H:%M:%S')
            
            return {{
                'valor': round(valor, 2),
                'unidad': '{sensor_info['unidad']}',
                'sensor': '{sensor_id}',
                'nombre': '{sensor_info['nombre']}',
                'fecha_hora': fecha_hora,
                'estado': 'conectado',
                'fuente': 'grafana_real'
            }}
        else:
            return generar_datos_simulados_{sensor_id.lower()}()
            
    except Exception as e:
        logger.error(f"Error obteniendo {sensor_info['nombre']}: {{e}}")
        return generar_datos_simulados_{sensor_id.lower()}()
    
    finally:
        if 'conexion' in locals():
            conexion.close()

def generar_datos_simulados_{sensor_id.lower()}() -> Dict[str, Any]:
    """Generar datos simulados para {sensor_info['nombre']}"""
    import random
    
    rango = {sensor_info.get('rango_estimado', [0, 100])}
    valor = round(random.uniform(rango[0], rango[1]), 2)
    
    return {{
        'valor': valor,
        'unidad': '{sensor_info['unidad']}',
        'sensor': '{sensor_id}',
        'nombre': '{sensor_info['nombre']}',
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'simulado',
        'fuente': 'simulado'
    }}

@app.route('/{sensor_id.lower()}')
def {sensor_id.lower()}_endpoint():
    """Endpoint para obtener {sensor_info['nombre']}"""
    try:
        datos = obtener_{sensor_id.lower()}()
        return jsonify(datos)
    except Exception as e:
        return jsonify({{
            'error': str(e),
            'valor': 0.0,
            'sensor': '{sensor_id}',
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }})
'''
    
    return template

def mostrar_resumen_sensores():
    """Mostrar resumen completo de sensores"""
    config = generar_config_completa()
    
    print("=" * 80)
    print("MAPEO COMPLETO DE SENSORES - SIBIA GRAFANA")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Versión: {config['version']}")
    
    print(f"\n📊 RESUMEN:")
    print(f"  - Sensores implementados: {config['resumen']['total_implementados']}")
    print(f"  - Sensores potenciales: {config['resumen']['total_potenciales']}")
    print(f"  - Total identificados: {config['resumen']['total_implementados'] + config['resumen']['total_potenciales']}")
    
    print(f"\n✅ SENSORES IMPLEMENTADOS:")
    for categoria, sensores in SENSORES_IDENTIFICADOS.items():
        print(f"\n  📁 {categoria.upper()}:")
        for sensor_id, info in sensores.items():
            print(f"    {sensor_id:<15} - {info['nombre']} ({info['unidad']})")
    
    print(f"\n🔍 SENSORES POTENCIALES:")
    for categoria, sensores in SENSORES_POTENCIALES.items():
        print(f"\n  📁 {categoria.upper()}:")
        for sensor_id, info in sensores.items():
            print(f"    {sensor_id:<15} - {info['nombre']} ({info['unidad']})")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Mostrar resumen
    mostrar_resumen_sensores()
    
    # Generar archivo de configuración
    config = generar_config_completa()
    with open('mapeo_sensores_completo.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Configuración guardada en: mapeo_sensores_completo.json")
    
    # Generar queries de prueba
    queries = generar_queries_sql_nuevos()
    with open('queries_sensores_potenciales.json', 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    
    print(f"🔍 Queries de prueba guardadas en: queries_sensores_potenciales.json") 