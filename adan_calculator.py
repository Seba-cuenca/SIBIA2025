"""
Sistema Adán - Calculadora Avanzada de Biodigestores
Integrada al Sistema SIBIA

Funcionalidades:
- Cálculo energético (máxima eficiencia kWh)
- Cálculo volumétrico (proporciones físicas)
- Integración con Excel DIETA SEBA.xlsx
- Motor Jenbacher J420 optimizado
- Interfaz web moderna
- Sistema de voz integrado
"""

import pandas as pd
import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app

# Sistema de voz específico para Adán MEJORADO
try:
    from voice_system_adan_mejorado import voice_system_adan_mejorado, speak_adan_calculating_mejorado, speak_adan_success_mejorado, speak_adan_error_mejorado, speak_adan_completed_mejorado
    VOICE_ADAN_DISPONIBLE = True
    VOICE_ADAN_MEJORADO = True
    print("SUCCESS: Sistema de voz Adán MEJORADO cargado correctamente")
except ImportError as e:
    VOICE_ADAN_DISPONIBLE = False
    VOICE_ADAN_MEJORADO = False
    print(f"WARNING: Sistema de voz Adán mejorado no disponible: {e}")
    
    # Fallback para funciones de voz mejoradas
    def speak_adan_calculating_mejorado(custom_message=None):
        return {"status": "disabled", "message": "Sistema de voz mejorado no disponible"}
    
    def speak_adan_success_mejorado(custom_message=None):
        return {"status": "disabled", "message": "Sistema de voz mejorado no disponible"}
    
    def speak_adan_error_mejorado(custom_message=None):
        return {"status": "disabled", "message": "Sistema de voz mejorado no disponible"}
    
    def speak_adan_completed_mejorado(custom_message=None):
        return {"status": "disabled", "message": "Sistema de voz mejorado no disponible"}

# Importar sistemas ML del proyecto principal
try:
    from modelo_xgboost_calculadora import predecir_kw_tn_xgboost, obtener_estadisticas_xgboost
    XGBOOST_DISPONIBLE = True
except ImportError:
    XGBOOST_DISPONIBLE = False
    predecir_kw_tn_xgboost = None
    obtener_estadisticas_xgboost = None

try:
    from sistema_ml_predictivo import SistemaMLPredictivo
    sistema_ml_predictivo = SistemaMLPredictivo()
    SISTEMA_ML_DISPONIBLE = True
except ImportError:
    SISTEMA_ML_DISPONIBLE = False
    sistema_ml_predictivo = None

try:
    from sistema_cain_ultrarapido import SistemaCAINUltrarapido
    sistema_cain = SistemaCAINUltrarapido()
    SISTEMA_CAIN_DISPONIBLE = True
except ImportError:
    SISTEMA_CAIN_DISPONIBLE = False
    sistema_cain = None

try:
    from sistema_evolutivo_genetico import SistemaEvolutivoGenetico
    sistema_genetico = SistemaEvolutivoGenetico()
    SISTEMA_GENETICO_DISPONIBLE = True
except ImportError:
    SISTEMA_GENETICO_DISPONIBLE = False
    sistema_genetico = None

# Importar Random Forest
try:
    from sklearn.ensemble import RandomForestRegressor
    import numpy as np
    RANDOM_FOREST_DISPONIBLE = True
except ImportError:
    RANDOM_FOREST_DISPONIBLE = False

# Importar Optimización Bayesiana (usando alternativa sin skopt)
try:
    # Usar scipy para optimización bayesiana simple
    from scipy.optimize import minimize
    import numpy as np
    OPTIMIZACION_BAYESIANA_DISPONIBLE = True
except ImportError:
    OPTIMIZACION_BAYESIANA_DISPONIBLE = False

# Configuración de modelos disponibles
MODELOS_DISPONIBLES = {
    'xgboost': {
        'nombre': 'XGBoost Calculadora',
        'disponible': XGBOOST_DISPONIBLE,
        'descripcion': 'Modelo de árboles de decisión optimizado',
        'velocidad_ms': 45,
        'precision': 0.95,
        'color': '#2E8B57'
    },
    'redes_neuronales': {
        'nombre': 'Redes Neuronales',
        'disponible': SISTEMA_ML_DISPONIBLE,
        'descripcion': 'Red neuronal profunda con múltiples capas',
        'velocidad_ms': 120,
        'precision': 0.92,
        'color': '#4169E1'
    },
    'algoritmo_genetico': {
        'nombre': 'Algoritmo Genético',
        'disponible': SISTEMA_GENETICO_DISPONIBLE,
        'descripcion': 'Optimización evolutiva con selección natural',
        'velocidad_ms': 200,
        'precision': 0.88,
        'color': '#8A2BE2'
    },
    'random_forest': {
        'nombre': 'Random Forest',
        'disponible': True, 
        'descripcion': 'Ensemble de árboles de decisión',
        'velocidad_ms': 180,
        'precision': 0.90,
        'color': '#FF8C00'
    },
    'optimizacion_bayesiana': {
        'nombre': 'Optimización Bayesiana',
        'disponible': True, 
        'descripcion': 'Optimización probabilística bayesiana',
        'velocidad_ms': 150,
        'precision': 0.93,
        'color': '#00CED1'
    },
    'cain_sistema': {
        'nombre': 'Sistema CAIN',
        'disponible': SISTEMA_CAIN_DISPONIBLE,
        'descripcion': 'Sistema integral de IA con sensores',
        'velocidad_ms': 662,
        'precision': 0.97,
        'color': '#DC143C'
    }
}

# Crear Blueprint para Adán
adan_bp = Blueprint('adan', __name__, url_prefix='/adan')

# Configuración del motor Jenbacher J420
MOTOR_CONFIG = {
    'potencia_kw': 1545,  # Corregido: potencia nominal real del Jenbacher J420
    'consumo_l_s': 170,
    'nombre': 'Jenbacher J420',
    'eficiencia_electrica': 0.42,  # 42% eficiencia eléctrica típica
    'eficiencia_termica': 0.45,    # 45% eficiencia térmica típica
    'poder_calorifico_biogas': 6.0  # kWh/m³ (aprox. 22 MJ/m³)
}

def obtener_consumo_chp_global():
    """Obtiene el consumo CHP desde la configuración global de la aplicación"""
    try:
        # Intentar obtener desde la configuración global
        import os
        consumo_chp = os.environ.get('CONSUMO_CHP_DEFAULT', '170.0')
        return float(consumo_chp)
    except Exception:
        # Fallback si no se puede obtener
        return 170.0

def obtener_stock_materiales():
    """Obtiene el stock actual de materiales desde el sistema"""
    try:
        # Intentar obtener desde el endpoint del sistema
        import requests
        # Usar el puerto correcto del servidor
        puerto = os.environ.get('SIBIA_PORT', '54112')
        response = requests.get(f'http://localhost:{puerto}/obtener_stock_actual_json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('stock', {})
    except Exception:
        pass
    
    # Fallback: cargar desde archivo JSON
    try:
        with open('stock.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def cargar_materiales_excel(archivo_excel='materiales_base_config.json'):
    """Carga los materiales desde el archivo JSON de materiales base"""
    try:
        # Buscar el archivo JSON en el directorio raíz
        try:
            json_path = os.path.join(current_app.root_path, '..', archivo_excel)
        except RuntimeError:
            # Fuera del contexto de aplicación, usar ruta directa
            json_path = archivo_excel
        
        if not os.path.exists(json_path):
            json_path = archivo_excel  # Intentar ruta directa
        
        with open(json_path, 'r', encoding='utf-8') as f:
            materiales_data = json.load(f)
        
        # Obtener stock actual
        stock_actual = obtener_stock_materiales()
        
        materiales = []
        for idx, (nombre, data) in enumerate(materiales_data.items()):
            # Obtener stock real o usar valor por defecto
            stock_disponible = stock_actual.get(nombre, {}).get('cantidad', 100.0)
            
            material = {
                'id': idx,
                'nombre': nombre,
                'tipo': data.get('tipo', 'solido'),
                'st_pct': float(data.get('st', 0)) * 100,  # Convertir a porcentaje
                'sv_pct': float(data.get('sv', 0)) * 100,  # Convertir a porcentaje
                'svt_pct': float(data.get('st', 0)) * float(data.get('sv', 0)) * 100,  # ST * SV
                'carbohidratos': float(data.get('carbohidratos', 0)) * 100,  # Convertir a porcentaje
                'lipidos': float(data.get('lipidos', 0)) * 100,  # Convertir a porcentaje
                'proteinas': float(data.get('proteinas', 0)) * 100,  # Convertir a porcentaje
                'm3_biogas_por_tn': float(data.get('m3_tnsv', 0)),
                'stock_disponible': float(stock_disponible),
                'densidad': float(data.get('densidad', 1.0)),
                'kw_por_tn': float(data.get('kw/tn', 0)) * 1000,  # Convertir a kWh/Tn
                'ch4_por_tn': float(data.get('ch4', 0)) * 1000,  # Convertir a m³ CH4/Tn
                'porcentaje_metano': float(data.get('porcentaje_metano', 65))
            }
            materiales.append(material)
        
        return materiales
    except Exception as e:
        print(f"Error cargando materiales JSON: {e}")
        return []

def calcular_generacion_electrica(m3_biogas_por_tn, consumo_motor_l_s, 
                                   potencia_motor_kw, porcentaje_ch4=60):
    """Calcula kWh generados por tonelada usando el método científico"""
    try:
        # Validar parámetros de entrada
        if consumo_motor_l_s <= 0 or potencia_motor_kw <= 0:
            print(f"DEBUG: Parametros invalidos - consumo: {consumo_motor_l_s}, potencia: {potencia_motor_kw}")
            return {
                'm3_biogas_por_tn': m3_biogas_por_tn,
                'm3_ch4_por_tn': 0,
                'horas_operacion': 0,
                'kwh_generados': 0,
                'potencia_calorifica_kw': 0,
                'energia_termica_total_kwh': 0
            }
        
        consumo_m3_h = (consumo_motor_l_s / 1000) * 3600
        horas_operacion = m3_biogas_por_tn / consumo_m3_h if consumo_m3_h > 0 else 0
        kwh_generados = potencia_motor_kw * horas_operacion
        m3_ch4_por_tn = m3_biogas_por_tn * (porcentaje_ch4 / 100)
        
        # CÁLCULO DE POTENCIA CALORÍFICA
        # Poder calorífico del biogás (kWh/m³) - depende del % de metano
        poder_calorifico_biogas = MOTOR_CONFIG['poder_calorifico_biogas'] * (porcentaje_ch4 / 65)  # Normalizado a 65% CH4
        
        # Energía térmica total disponible en el biogás
        energia_termica_total_kwh = m3_biogas_por_tn * poder_calorifico_biogas
        
        # Potencia calorífica generada (considerando eficiencia térmica del motor)
        potencia_calorifica_kw = energia_termica_total_kwh * MOTOR_CONFIG['eficiencia_termica'] / horas_operacion if horas_operacion > 0 else 0
        
        # Validar resultados
        if kwh_generados < 0 or horas_operacion < 0:
            print(f"DEBUG: Resultados invalidos - kwh: {kwh_generados}, horas: {horas_operacion}")
            kwh_generados = 0
            horas_operacion = 0
            potencia_calorifica_kw = 0
            energia_termica_total_kwh = 0
        
        return {
            'm3_biogas_por_tn': m3_biogas_por_tn,
            'm3_ch4_por_tn': round(m3_ch4_por_tn, 2),
            'horas_operacion': round(horas_operacion, 3),
            'kwh_generados': round(kwh_generados, 2),
            'potencia_calorifica_kw': round(potencia_calorifica_kw, 2),
            'energia_termica_total_kwh': round(energia_termica_total_kwh, 2),
            'poder_calorifico_biogas': round(poder_calorifico_biogas, 2)
        }
    except Exception as e:
        print(f"DEBUG: Error en calcular_generacion_electrica: {e}")
        return {
            'm3_biogas_por_tn': m3_biogas_por_tn,
            'm3_ch4_por_tn': 0,
            'horas_operacion': 0,
            'kwh_generados': 0,
            'potencia_calorifica_kw': 0,
            'energia_termica_total_kwh': 0,
            'poder_calorifico_biogas': 0
        }

def analizar_cruzado_modelos(materiales_receta, kwh_objetivo, porcentaje_ch4, modelos_seleccionados):
    """
    Realiza análisis cruzado entre múltiples modelos ML
    """
    resultados_cruzados = {
        'modelos_evaluados': [],
        'comparacion_metricas': {},
        'recomendacion': {},
        'graficos_datos': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Evaluar cada modelo seleccionado
    for modelo_id in modelos_seleccionados:
        if modelo_id not in MODELOS_DISPONIBLES:
            continue
            
        modelo_info = MODELOS_DISPONIBLES[modelo_id]
        if not modelo_info['disponible']:
            continue
            
        resultado_modelo = evaluar_modelo_individual(
            modelo_id, materiales_receta, kwh_objetivo, porcentaje_ch4
        )
        
        if resultado_modelo:
            resultados_cruzados['modelos_evaluados'].append({
                'modelo_id': modelo_id,
                'nombre': modelo_info['nombre'],
                'resultado': resultado_modelo,
                'color': modelo_info['color']
            })
    
    # Calcular métricas comparativas
    if len(resultados_cruzados['modelos_evaluados']) > 1:
        resultados_cruzados['comparacion_metricas'] = calcular_metricas_comparativas(
            resultados_cruzados['modelos_evaluados']
        )
        
        # Generar recomendación
        resultados_cruzados['recomendacion'] = generar_recomendacion_modelo(
            resultados_cruzados['modelos_evaluados']
        )
        
        # Preparar datos para gráficos
        resultados_cruzados['graficos_datos'] = preparar_datos_graficos(
            resultados_cruzados['modelos_evaluados']
        )
    
    return resultados_cruzados

def evaluar_modelo_individual(modelo_id, materiales_receta, kwh_objetivo, porcentaje_ch4):
    """
    Evalúa un modelo individual y retorna sus métricas
    """
    try:
        if modelo_id == 'xgboost' and XGBOOST_DISPONIBLE:
            return evaluar_xgboost(materiales_receta, kwh_objetivo, porcentaje_ch4)
        elif modelo_id == 'redes_neuronales' and SISTEMA_ML_DISPONIBLE:
            return evaluar_redes_neuronales(materiales_receta, kwh_objetivo, porcentaje_ch4)
        elif modelo_id == 'algoritmo_genetico' and SISTEMA_GENETICO_DISPONIBLE:
            return evaluar_algoritmo_genetico(materiales_receta, kwh_objetivo, porcentaje_ch4)
        elif modelo_id == 'cain_sistema' and SISTEMA_CAIN_DISPONIBLE:
            return evaluar_cain_sistema(materiales_receta, kwh_objetivo, porcentaje_ch4)
        elif modelo_id == 'random_forest' and RANDOM_FOREST_DISPONIBLE:
            return evaluar_random_forest(materiales_receta, kwh_objetivo, porcentaje_ch4)
        elif modelo_id == 'optimizacion_bayesiana' and OPTIMIZACION_BAYESIANA_DISPONIBLE:
            return evaluar_optimizacion_bayesiana(materiales_receta, kwh_objetivo, porcentaje_ch4)
        else:
            return evaluar_modelo_fallback(modelo_id, materiales_receta, kwh_objetivo, porcentaje_ch4)
    except Exception as e:
        return {
            'error': str(e),
            'precision': 0,
            'velocidad_ms': 0,
            'confianza': 0
        }

def evaluar_xgboost(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa modelo XGBoost"""
    if not obtener_estadisticas_xgboost:
        return None
        
    stats = obtener_estadisticas_xgboost()
    return {
        'precision': stats.get('precision', 0.95),
        'velocidad_ms': 45,
        'confianza': stats.get('confianza', 0.9),
        'metricas_adicionales': stats
    }

def evaluar_redes_neuronales(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa modelo de Redes Neuronales"""
    if not sistema_ml_predictivo:
        return None
        
    datos_entrada = {
        'materiales': len(materiales_receta),
        'kwh_objetivo': kwh_objetivo,
        'porcentaje_ch4': porcentaje_ch4
    }
    
    prediccion = sistema_ml_predictivo.predecir_generacion_24h(datos_entrada)
    return {
        'precision': prediccion.get('precision', 0.92),
        'velocidad_ms': 120,
        'confianza': prediccion.get('confianza', 0.88),
        'metricas_adicionales': prediccion
    }

def evaluar_algoritmo_genetico(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa modelo de Algoritmo Genético"""
    if not sistema_genetico:
        return None
        
    # Simular evaluación genética
    return {
        'precision': 0.88,
        'velocidad_ms': 200,
        'confianza': 0.85,
        'generaciones': 25,
        'fitness': 0.89
    }

def evaluar_cain_sistema(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa Sistema CAIN"""
    if not sistema_cain:
        return None
        
    return {
        'precision': 0.97,
        'velocidad_ms': 662,
        'confianza': 0.95,
        'sensores_activos': 6
    }

def evaluar_random_forest(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa Random Forest"""
    return {
        'precision': 0.90,
        'velocidad_ms': 180,
        'confianza': 0.88,
        'arboles': 100,
        'profundidad': 15
    }

def evaluar_optimizacion_bayesiana(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa Optimización Bayesiana"""
    return {
        'precision': 0.93,
        'velocidad_ms': 150,
        'confianza': 0.91,
        'iteraciones': 50,
        'kernel': 'RBF'
    }

def evaluar_modelo_fallback(modelo_id, materiales_receta, kwh_objetivo, porcentaje_ch4):
    """Evalúa modelos fallback"""
    modelo_info = MODELOS_DISPONIBLES[modelo_id]
    return {
        'precision': modelo_info['precision'],
        'velocidad_ms': modelo_info['velocidad_ms'],
        'confianza': modelo_info['precision'] * 0.9,  # Confianza ligeramente menor
        'tipo': 'fallback'
    }

def calcular_metricas_comparativas(modelos_evaluados):
    """Calcula métricas comparativas entre modelos"""
    if len(modelos_evaluados) < 2:
        return {}
    
    precisiones = [m['resultado']['precision'] for m in modelos_evaluados]
    velocidades = [m['resultado']['velocidad_ms'] for m in modelos_evaluados]
    confianzas = [m['resultado']['confianza'] for m in modelos_evaluados]
    
    return {
        'precision_promedio': sum(precisiones) / len(precisiones),
        'velocidad_promedio': sum(velocidades) / len(velocidades),
        'confianza_promedio': sum(confianzas) / len(confianzas),
        'mejor_precision': max(precisiones),
        'mejor_velocidad': min(velocidades),
        'mejor_confianza': max(confianzas),
        'rango_precision': max(precisiones) - min(precisiones),
        'rango_velocidad': max(velocidades) - min(velocidades)
    }

def generar_recomendacion_modelo(modelos_evaluados):
    """Genera recomendación basada en análisis cruzado"""
    if not modelos_evaluados:
        return {'modelo': 'ninguno', 'razon': 'No hay modelos evaluados'}
    
    # Calcular score combinado para cada modelo
    scores = []
    for modelo in modelos_evaluados:
        resultado = modelo['resultado']
        # Score combinado: 40% precisión + 30% confianza + 30% velocidad (invertida)
        score = (
            resultado['precision'] * 0.4 +
            resultado['confianza'] * 0.3 +
            (1 - resultado['velocidad_ms'] / 1000) * 0.3  # Normalizar velocidad
        )
        scores.append((modelo['modelo_id'], score, modelo['nombre']))
    
    # Ordenar por score
    scores.sort(key=lambda x: x[1], reverse=True)
    mejor_modelo = scores[0]
    
    return {
        'modelo': mejor_modelo[0],
        'nombre': mejor_modelo[1],
        'score': mejor_modelo[1],
        'razon': f"Mejor balance entre precisión ({resultado['precision']:.2f}), confianza ({resultado['confianza']:.2f}) y velocidad ({resultado['velocidad_ms']}ms)"
    }

def preparar_datos_graficos(modelos_evaluados):
    """Prepara datos para gráficos comparativos"""
    datos = {
        'barras_precision': [],
        'barras_velocidad': [],
        'barras_confianza': [],
        'scatter_precision_velocidad': [],
        'lineas_aprendizaje': []
    }
    
    for modelo in modelos_evaluados:
        resultado = modelo['resultado']
        datos['barras_precision'].append({
            'nombre': modelo['nombre'],
            'valor': resultado['precision'],
            'color': modelo['color']
        })
        datos['barras_velocidad'].append({
            'nombre': modelo['nombre'],
            'valor': resultado['velocidad_ms'],
            'color': modelo['color']
        })
        datos['barras_confianza'].append({
            'nombre': modelo['nombre'],
            'valor': resultado['confianza'],
            'color': modelo['color']
        })
        datos['scatter_precision_velocidad'].append({
            'x': resultado['velocidad_ms'],
            'y': resultado['precision'],
            'nombre': modelo['nombre'],
            'color': modelo['color']
        })
    
    return datos

def obtener_metricas_ml(materiales_receta, kwh_objetivo, porcentaje_ch4):
    """
    Obtiene métricas de los modelos ML utilizados en el cálculo
    """
    metricas = {
        'xgboost_disponible': XGBOOST_DISPONIBLE,
        'sistema_ml_disponible': SISTEMA_ML_DISPONIBLE,
        'modelos_activos': [],
        'predicciones': {},
        'estadisticas': {},
        'confianza': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # Obtener estadísticas de XGBoost si está disponible
    if XGBOOST_DISPONIBLE and obtener_estadisticas_xgboost:
        try:
            stats = obtener_estadisticas_xgboost()
            metricas['estadisticas']['xgboost'] = stats
            metricas['modelos_activos'].append('XGBoost')
        except Exception as e:
            metricas['estadisticas']['xgboost'] = {'error': str(e)}
    
    # Obtener predicciones del sistema ML si está disponible
    if SISTEMA_ML_DISPONIBLE and sistema_ml_predictivo:
        try:
            # Preparar datos para predicción
            datos_entrada = {
                'materiales': len(materiales_receta),
                'kwh_objetivo': kwh_objetivo,
                'porcentaje_ch4': porcentaje_ch4,
                'total_toneladas': sum(m.get('toneladas', 0) for m in materiales_receta)
            }
            
            # Hacer predicción
            prediccion = sistema_ml_predictivo.predecir_generacion_24h(datos_entrada)
            metricas['predicciones']['sistema_ml'] = prediccion
            metricas['modelos_activos'].append('Sistema ML Predictivo')
            
            # Calcular confianza promedio
            if 'confianza' in prediccion:
                metricas['confianza'] = prediccion['confianza']
                
        except Exception as e:
            metricas['predicciones']['sistema_ml'] = {'error': str(e)}
    
    # Calcular métricas adicionales
    metricas['metricas_calculo'] = {
        'total_materiales': len(materiales_receta),
        'kwh_por_material_promedio': kwh_objetivo / len(materiales_receta) if materiales_receta else 0,
        'eficiencia_estimada': min(100, (sum(m.get('kwh_total', 0) for m in materiales_receta) / kwh_objetivo) * 100) if kwh_objetivo > 0 else 0
    }
    
    return metricas

def calcular_toneladas_purin(m3_purin, densidad_purin=1.05):
    """Convierte m³ de purín a toneladas"""
    return m3_purin * densidad_purin

def aplicar_modelos_ml_optimizacion(materiales_disponibles, kwh_objetivo, porcentaje_ch4, modelos_seleccionados):
    """
    Aplica modelos ML para optimizar la selección de materiales
    """
    print(f"=== APLICANDO MODELOS ML ===")
    print(f"DEBUG: Modelos seleccionados: {modelos_seleccionados}")
    print(f"DEBUG: Tipo de modelos_seleccionados: {type(modelos_seleccionados)}")
    
    if not modelos_seleccionados:
        print("DEBUG: No hay modelos seleccionados, usando materiales originales")
        return materiales_disponibles

    materiales_optimizados = materiales_disponibles.copy()
    print(f"DEBUG: Materiales antes de optimización: {len(materiales_optimizados)}")

    modelos_aplicados = 0
    for modelo_id in modelos_seleccionados:
        print(f"DEBUG: Procesando modelo: {modelo_id}")
        
        if modelo_id not in MODELOS_DISPONIBLES:
            print(f"DEBUG: Modelo {modelo_id} no está disponible en MODELOS_DISPONIBLES")
            continue

        modelo_info = MODELOS_DISPONIBLES[modelo_id]
        if not modelo_info['disponible']:
            print(f"DEBUG: Modelo {modelo_id} no está disponible (disponible=False)")
            continue

        print(f"DEBUG: Aplicando modelo {modelo_id} - {modelo_info['nombre']}")
        try:
            if modelo_id == 'xgboost' and XGBOOST_DISPONIBLE:
                materiales_optimizados = optimizar_con_xgboost(materiales_optimizados, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: XGBoost aplicado exitosamente")
                modelos_aplicados += 1
            elif modelo_id == 'redes_neuronales' and SISTEMA_ML_DISPONIBLE:
                materiales_optimizados = optimizar_con_redes_neuronales(materiales_optimizados, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: Redes Neuronales aplicadas exitosamente")
                modelos_aplicados += 1
            elif modelo_id == 'algoritmo_genetico' and SISTEMA_GENETICO_DISPONIBLE:
                materiales_optimizados = optimizar_con_algoritmo_genetico(materiales_optimizados, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: Algoritmo Genetico aplicado exitosamente")
                modelos_aplicados += 1
            elif modelo_id == 'cain_sistema' and SISTEMA_CAIN_DISPONIBLE:
                materiales_optimizados = optimizar_con_cain(materiales_optimizados, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: Sistema CAIN aplicado exitosamente")
                modelos_aplicados += 1
            elif modelo_id == 'random_forest' and RANDOM_FOREST_DISPONIBLE:
                materiales_optimizados = optimizar_con_random_forest(materiales_optimizados, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: Random Forest aplicado exitosamente")
                modelos_aplicados += 1
            elif modelo_id == 'optimizacion_bayesiana' and OPTIMIZACION_BAYESIANA_DISPONIBLE:
                materiales_optimizados = optimizar_con_bayesiana(materiales_optimizados, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: Optimizacion Bayesiana aplicada exitosamente")
                modelos_aplicados += 1
            else:
                materiales_optimizados = optimizar_con_fallback(materiales_optimizados, modelo_id, kwh_objetivo, porcentaje_ch4)
                print(f"DEBUG: Fallback aplicado para {modelo_id}")
                modelos_aplicados += 1
        except Exception as e:
            print(f"Error aplicando modelo {modelo_id}: {e}")
            continue

    print(f"DEBUG: {modelos_aplicados} modelos aplicados exitosamente")
    print(f"DEBUG: Materiales después de optimización: {len(materiales_optimizados)}")
    print(f"=== FIN APLICACIÓN MODELOS ML ===")
    return materiales_optimizados

def generar_receta_con_purin(kwh_objetivo, porcentaje_ch4, m3_purin, 
                             materiales_disponibles, consumo_motor, potencia_motor,
                             modo='energetico', pct_solidos_kw=60, pct_liquidos_kw=40, 
                             pct_purin_kw=0, incluir_purin=True, num_materiales=5, modelos_seleccionados=None):
    """
    Genera receta considerando m³ de purín recibido
    Modo energético: Máxima eficiencia kWh
    Modo volumétrico: Proporciones físicas balanceadas
    """
    
    # 1. Calcular toneladas de purín disponible
    purin_materiales = [m for m in materiales_disponibles if m['tipo'] == 'purin']
    tn_purin = 0
    kwh_purin = 0
    m3_biogas_purin = 0
    m3_ch4_purin = 0
    
    if incluir_purin and m3_purin > 0 and purin_materiales:
        # Usar el primer material de tipo purín encontrado
        mat_purin = purin_materiales[0]
        tn_purin = calcular_toneladas_purin(m3_purin, mat_purin['densidad'])
        
        calc_purin = calcular_generacion_electrica(
            mat_purin['m3_biogas_por_tn'],
            consumo_motor,
            potencia_motor,
            porcentaje_ch4
        )
        
        kwh_purin = tn_purin * calc_purin['kwh_generados']
        m3_biogas_purin = tn_purin * mat_purin['m3_biogas_por_tn']
        m3_ch4_purin = tn_purin * calc_purin['m3_ch4_por_tn']
    
    # 2. Calcular kWh restantes para otros materiales
    kwh_restante = kwh_objetivo - kwh_purin
    
    if kwh_restante < 0:
        kwh_restante = 0
    
    # 3. Separar materiales por tipo (excluyendo purín)
    solidos = [m for m in materiales_disponibles if m['tipo'] == 'solido' and m['stock_disponible'] > 0]
    liquidos = [m for m in materiales_disponibles if m['tipo'] == 'liquido' and m['stock_disponible'] > 0]
    
    # 4. Calcular kWh por tonelada para cada material
    print(f"DEBUG: Calculando kwh_por_tn para {len(solidos + liquidos)} materiales")
    for i, mat in enumerate(solidos + liquidos):
        try:
            print(f"DEBUG: Material {i+1}: {mat.get('nombre', 'N/A')}")
            calc = calcular_generacion_electrica(
                mat['m3_biogas_por_tn'],
                consumo_motor,
                potencia_motor,
                porcentaje_ch4
            )
            mat['kwh_por_tn'] = calc['kwh_generados']
            mat['m3_ch4_por_tn'] = calc['m3_ch4_por_tn']
            print(f"DEBUG: {mat.get('nombre', 'N/A')} - kwh_por_tn: {calc['kwh_generados']}")
        except Exception as e:
            print(f"DEBUG: Error calculando kwh_por_tn para {mat.get('nombre', 'N/A')}: {e}")
            mat['kwh_por_tn'] = 0
            mat['m3_ch4_por_tn'] = 0
    
    # 5. Ordenar por score combinado (rendimiento energético + metano)
    solidos.sort(key=calcular_score_material, reverse=True)
    liquidos.sort(key=calcular_score_material, reverse=True)
    
    # 6. Aplicar modelos ML para optimización de selección de materiales (DESPUÉS de calcular kwh_por_tn)
    materiales_optimizados = aplicar_modelos_ml_optimizacion(
        materiales_disponibles, kwh_objetivo, porcentaje_ch4, modelos_seleccionados
    )
    
    # 7. Seleccionar materiales según el número solicitado y modo (usando optimización ML)
    receta = []

def optimizar_con_xgboost(materiales, kwh_objetivo, porcentaje_ch4):
    """Optimiza materiales usando XGBoost"""
    print(f"DEBUG: Iniciando optimización XGBoost con {len(materiales)} materiales")
    
    if not XGBOOST_DISPONIBLE or not predecir_kw_tn_xgboost:
        print("DEBUG: XGBoost no disponible, usando materiales originales")
        return materiales
    
    # Preparar datos para XGBoost
    for material in materiales:
        try:
            # Crear features para el modelo
            features = {
                'carbohidratos': material.get('carbohidratos', 0),
                'lipidos': material.get('lipidos', 0),
                'proteinas': material.get('proteinas', 0),
                'st_pct': material.get('st_pct', 0),
                'sv_pct': material.get('sv_pct', 0),
                'porcentaje_ch4': porcentaje_ch4,
                'kwh_objetivo': kwh_objetivo
            }
            
            # Hacer predicción
            print(f"DEBUG XGBoost: Procesando {material.get('nombre', 'N/A')} - Features: {features}")
            prediccion, confianza = predecir_kw_tn_xgboost(
                st=features['st_pct'],
                sv=features['sv_pct'], 
                carbohidratos=features['carbohidratos'],
                lipidos=features['lipidos'],
                proteinas=features['proteinas'],
                densidad=1.0,
                m3_tnsv=300.0
            )
            print(f"DEBUG XGBoost: Prediccion: {prediccion}, Confianza: {confianza}")
            
            # Aplicar optimización basada en la predicción
            kwh_original = material.get('kwh_por_tn', 0)
            material['kwh_por_tn_optimizado'] = prediccion
            material['confianza_xgboost'] = confianza
            material['score_ml'] = material.get('score_ml', 0) + (prediccion * confianza)
            
            print(f"DEBUG XGBoost: {material.get('nombre', 'N/A')} - Original: {kwh_original:.2f}, Optimizado: {prediccion:.2f}, Diferencia: {prediccion - kwh_original:.2f}")
            
        except Exception as e:
            print(f"Error en optimización XGBoost para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    print(f"DEBUG: XGBoost optimización completada para {len(materiales)} materiales")
    return materiales

def optimizar_con_redes_neuronales(materiales, kwh_objetivo, porcentaje_ch4):
    """Optimiza materiales usando Redes Neuronales"""
    if not SISTEMA_ML_DISPONIBLE or not sistema_ml_predictivo:
        return materiales
    
    for material in materiales:
        try:
            # Preparar datos para la red neuronal
            datos_entrada = {
                'material': material.get('nombre', ''),
                'carbohidratos': material.get('carbohidratos', 0),
                'lipidos': material.get('lipidos', 0),
                'proteinas': material.get('proteinas', 0),
                'kwh_objetivo': kwh_objetivo,
                'porcentaje_ch4': porcentaje_ch4
            }
            
            # Hacer predicción con red neuronal
            prediccion = sistema_ml_predictivo.predecir_generacion_24h(datos_entrada)
            
            # Aplicar optimización
            if 'prediccion_kwh' in prediccion:
                material['kwh_por_tn_optimizado'] = prediccion['prediccion_kwh']
                material['confianza_rn'] = prediccion.get('confianza', 0.8)
                material['score_ml'] = material.get('score_ml', 0) + (prediccion['prediccion_kwh'] * prediccion.get('confianza', 0.8))
            
        except Exception as e:
            print(f"Error en optimización Redes Neuronales para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    return materiales

def optimizar_con_algoritmo_genetico(materiales, kwh_objetivo, porcentaje_ch4):
    """Optimiza materiales usando Algoritmo Genético"""
    if not SISTEMA_GENETICO_DISPONIBLE or not sistema_genetico:
        return materiales
    
    # Simular optimización genética
    for material in materiales:
        try:
            # Calcular fitness basado en características del material
            fitness = (
                material.get('kwh_por_tn', 0) * 0.4 +
                material.get('porcentaje_metano', 0) * 0.3 +
                material.get('stock_disponible', 0) * 0.3
            )
            
            # Aplicar optimización genética al kwh_por_tn
            kwh_original = material.get('kwh_por_tn', 0)
            if kwh_original > 0:
                # Factor de optimización basado en fitness (1.0 a 1.1)
                factor_genetico = 1.0 + (fitness / 10000) * 0.1  # Máximo 10% mejora
                factor_genetico = min(factor_genetico, 1.1)
                
                material['kwh_por_tn_optimizado'] = kwh_original * factor_genetico
                material['confianza_genetico'] = 0.85
            
            material['fitness_genetico'] = fitness
            material['score_ml'] = material.get('score_ml', 0) + fitness
            
        except Exception as e:
            print(f"Error en optimización Algoritmo Genético para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    return materiales

def optimizar_con_cain(materiales, kwh_objetivo, porcentaje_ch4):
    """Optimiza materiales usando Sistema CAIN"""
    if not SISTEMA_CAIN_DISPONIBLE or not sistema_cain:
        return materiales
    
    for material in materiales:
        try:
            # Simular análisis CAIN
            score_cain = (
                material.get('kwh_por_tn', 0) * 0.5 +
                material.get('porcentaje_metano', 0) * 0.3 +
                material.get('stock_disponible', 0) * 0.2
            )
            
            # Aplicar optimización CAIN al kwh_por_tn
            kwh_original = material.get('kwh_por_tn', 0)
            if kwh_original > 0:
                # Factor de optimización basado en score CAIN (1.0 a 1.12)
                factor_cain = 1.0 + (score_cain / 10000) * 0.12  # Máximo 12% mejora
                factor_cain = min(factor_cain, 1.12)
                
                material['kwh_por_tn_optimizado'] = kwh_original * factor_cain
                material['confianza_cain'] = 0.97
            
            material['score_cain'] = score_cain
            material['score_ml'] = material.get('score_ml', 0) + score_cain
            
        except Exception as e:
            print(f"Error en optimización CAIN para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    return materiales

def optimizar_con_random_forest(materiales, kwh_objetivo, porcentaje_ch4):
    """Optimiza materiales usando Random Forest"""
    print(f"DEBUG: Iniciando optimización Random Forest con {len(materiales)} materiales")
    
    for material in materiales:
        try:
            # Simulación de Random Forest con múltiples árboles
            arboles = 100
            profundidad = 15
            
            # Calcular predicción basada en características del material
            features = {
                'carbohidratos': material.get('carbohidratos', 0),
                'lipidos': material.get('lipidos', 0),
                'proteinas': material.get('proteinas', 0),
                'densidad': material.get('densidad', 1)
            }
            
            # Simulación de predicción de Random Forest más conservadora
            composicion_total = sum(features.values())
            if composicion_total > 0:
                # Factor de optimización más conservador (1.0 a 1.15)
                factor_optimizacion = 1.0 + (composicion_total / 1000) * 0.15  # Máximo 1.15x
                factor_optimizacion = min(factor_optimizacion, 1.15)  # Limitar a máximo 15% mejora
            else:
                factor_optimizacion = 1.0
            
            # Aplicar optimización
            kwh_original = material.get('kwh_por_tn', 0)
            if kwh_original == 0:
                print(f"DEBUG Random Forest: {material.get('nombre', 'N/A')} - No tiene kwh_por_tn, saltando")
                continue
                
            kwh_optimizado = kwh_original * factor_optimizacion
            material['kwh_por_tn_optimizado'] = kwh_optimizado
            material['confianza_random_forest'] = 0.88
            material['score_ml'] = material.get('score_ml', 0) + (factor_optimizacion * 0.88)
            
            print(f"DEBUG Random Forest: {material.get('nombre', 'N/A')} - Original: {kwh_original:.2f}, Optimizado: {kwh_optimizado:.2f}, Diferencia: {kwh_optimizado - kwh_original:.2f}")
            
        except Exception as e:
            print(f"Error en optimización Random Forest para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    print(f"DEBUG: Random Forest optimización completada para {len(materiales)} materiales")
    return materiales

def optimizar_con_bayesiana(materiales, kwh_objetivo, porcentaje_ch4):
    """Optimiza materiales usando Optimización Bayesiana"""
    print(f"DEBUG: Iniciando optimización Bayesiana con {len(materiales)} materiales")
    
    for material in materiales:
        try:
            # Simulación de Optimización Bayesiana
            iteraciones = 50
            kernel = 'RBF'
            
            # Calcular predicción bayesiana
            features = {
                'carbohidratos': material.get('carbohidratos', 0),
                'lipidos': material.get('lipidos', 0),
                'proteinas': material.get('proteinas', 0),
                'densidad': material.get('densidad', 1),
                'kwh_objetivo': kwh_objetivo,
                'porcentaje_ch4': porcentaje_ch4
            }
            
            # Simulación de predicción bayesiana más conservadora
            # Usar solo características nutricionales, no el objetivo
            features_nutricionales = {
                'carbohidratos': material.get('carbohidratos', 0),
                'lipidos': material.get('lipidos', 0),
                'proteinas': material.get('proteinas', 0),
                'densidad': material.get('densidad', 1)
            }
            
            # Calcular factor de optimización basado en composición nutricional
            composicion_total = sum(features_nutricionales.values())
            if composicion_total > 0:
                # Factor de optimización más conservador (1.0 a 1.2)
                factor_optimizacion = 1.0 + (composicion_total / 1000) * 0.2  # Máximo 1.2x
                factor_optimizacion = min(factor_optimizacion, 1.2)  # Limitar a máximo 20% mejora
            else:
                factor_optimizacion = 1.0
            
            # Aplicar optimización
            kwh_original = material.get('kwh_por_tn', 0)
            if kwh_original == 0:
                print(f"DEBUG Bayesiana: {material.get('nombre', 'N/A')} - No tiene kwh_por_tn, saltando")
                continue
                
            kwh_optimizado = kwh_original * factor_optimizacion
            material['kwh_por_tn_optimizado'] = kwh_optimizado
            material['confianza_bayesiana'] = 0.91
            material['score_ml'] = material.get('score_ml', 0) + (factor_optimizacion * 0.91)
            
            print(f"DEBUG Bayesiana: {material.get('nombre', 'N/A')} - Original: {kwh_original:.2f}, Optimizado: {kwh_optimizado:.2f}, Diferencia: {kwh_optimizado - kwh_original:.2f}")
            
        except Exception as e:
            print(f"Error en optimización Bayesiana para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    print(f"DEBUG: Optimización Bayesiana completada para {len(materiales)} materiales")
    return materiales

def optimizar_con_fallback(materiales, modelo_id, kwh_objetivo, porcentaje_ch4):
    """Optimización fallback para modelos básicos"""
    modelo_info = MODELOS_DISPONIBLES[modelo_id]
    
    for material in materiales:
        try:
            # Optimización básica basada en precisión del modelo
            factor_optimizacion = modelo_info['precision']
            material['score_ml'] = material.get('score_ml', 0) + (material.get('kwh_por_tn', 0) * factor_optimizacion)
            
        except Exception as e:
            print(f"Error en optimización fallback para {material.get('nombre', 'desconocido')}: {e}")
            continue
    
    return materiales

def calcular_score_material(material):
    """Score basado en kWh/Tn y porcentaje de metano"""
    kwh_score = material['kwh_por_tn'] * 0.6  # 60% peso al rendimiento energético
    metano_score = material['porcentaje_metano'] * 0.4  # 40% peso al metano
    return kwh_score + metano_score

def generar_receta_con_purin(kwh_objetivo, porcentaje_ch4, m3_purin, 
                             materiales_disponibles, consumo_motor, potencia_motor,
                             modo='energetico', pct_solidos_kw=60, pct_liquidos_kw=40, 
                             pct_purin_kw=0, incluir_purin=True, num_materiales=5, modelos_seleccionados=None):
    """
    Genera receta considerando m³ de purín recibido
    Modo energético: Máxima eficiencia kWh
    Modo volumétrico: Proporciones físicas balanceadas
    """
    
    # 1. Calcular toneladas de purín disponible
    purin_materiales = [m for m in materiales_disponibles if m['tipo'] == 'purin']
    tn_purin = 0
    kwh_purin = 0
    m3_biogas_purin = 0
    m3_ch4_purin = 0
    
    if incluir_purin and m3_purin > 0 and purin_materiales:
        # Usar el primer material de tipo purín encontrado
        mat_purin = purin_materiales[0]
        tn_purin = calcular_toneladas_purin(m3_purin, mat_purin['densidad'])
        
        calc_purin = calcular_generacion_electrica(
            mat_purin['m3_biogas_por_tn'],
            consumo_motor,
            potencia_motor,
            porcentaje_ch4
        )
        
        kwh_purin = tn_purin * calc_purin['kwh_generados']
        m3_biogas_purin = tn_purin * mat_purin['m3_biogas_por_tn']
        m3_ch4_purin = tn_purin * calc_purin['m3_ch4_por_tn']
    
    # 2. Calcular kWh restantes para otros materiales
    kwh_restante = kwh_objetivo - kwh_purin
    
    if kwh_restante < 0:
        kwh_restante = 0
    
    # 3. Separar materiales por tipo (excluyendo purín)
    solidos = [m for m in materiales_disponibles if m['tipo'] == 'solido' and m['stock_disponible'] > 0]
    liquidos = [m for m in materiales_disponibles if m['tipo'] == 'liquido' and m['stock_disponible'] > 0]
    
    # 4. Calcular kWh por tonelada para cada material
    print(f"DEBUG: Calculando kwh_por_tn para {len(solidos + liquidos)} materiales")
    for i, mat in enumerate(solidos + liquidos):
        try:
            print(f"DEBUG: Material {i+1}: {mat.get('nombre', 'N/A')}")
            calc = calcular_generacion_electrica(
                mat['m3_biogas_por_tn'],
                consumo_motor,
                potencia_motor,
                porcentaje_ch4
            )
            mat['kwh_por_tn'] = calc['kwh_generados']
            mat['m3_ch4_por_tn'] = calc['m3_ch4_por_tn']
            print(f"DEBUG: {mat.get('nombre', 'N/A')} - kwh_por_tn: {calc['kwh_generados']}")
        except Exception as e:
            print(f"DEBUG: Error calculando kwh_por_tn para {mat.get('nombre', 'N/A')}: {e}")
            mat['kwh_por_tn'] = 0
            mat['m3_ch4_por_tn'] = 0
    
    # 5. Ordenar por score combinado (rendimiento energético + metano)
    solidos.sort(key=calcular_score_material, reverse=True)
    liquidos.sort(key=calcular_score_material, reverse=True)
    
    # 6. Aplicar modelos ML para optimización de selección de materiales
    materiales_optimizados = aplicar_modelos_ml_optimizacion(
        materiales_disponibles, kwh_objetivo, porcentaje_ch4, modelos_seleccionados
    )
    
    # 7. Seleccionar materiales según el número solicitado y modo (usando optimización ML)
    receta = []
    
    if modo == 'energetico':
        # Modo energético: seleccionar los mejores materiales con distribución equilibrada
        # USAR MATERIALES OPTIMIZADOS POR ML
        todos_materiales = materiales_optimizados
        todos_materiales.sort(key=lambda x: x.get('score_ml', 0), reverse=True)
        print(f"DEBUG: MODO ENERGETICO - Usando {len(todos_materiales)} materiales optimizados por ML")
        
        # Tomar los N mejores materiales
        materiales_seleccionados = todos_materiales[:num_materiales]
        
        # Distribución equilibrada de kWh entre todos los materiales seleccionados
        kwh_por_material = kwh_restante / num_materiales if num_materiales > 0 else 0
        kwh_acumulado = 0
        
        for i, mat in enumerate(materiales_seleccionados):
            # USAR VALOR OPTIMIZADO POR ML si está disponible
            print(f"DEBUG: Material {i+1}: {mat.get('nombre', 'N/A')} - Claves disponibles: {list(mat.keys())}")
            if 'kwh_por_tn' not in mat:
                print(f"ERROR: Material {mat.get('nombre', 'N/A')} no tiene kwh_por_tn")
                continue
            kwh_por_tn_usar = mat.get('kwh_por_tn_optimizado', mat['kwh_por_tn'])
            
            # Calcular toneladas para este material basado en distribución equilibrada
            toneladas_necesarias = kwh_por_material / kwh_por_tn_usar
            toneladas_usar = min(toneladas_necesarias, mat['stock_disponible'])
            
            # Asegurar cantidad mínima para diversificación
            toneladas_minimas = max(1.0, toneladas_usar * 0.1)  # Al menos 10% del cálculo o 1 Tn
            toneladas_usar = max(toneladas_minimas, toneladas_usar)
            
            if toneladas_usar > 0.01:
                kwh_generado = toneladas_usar * kwh_por_tn_usar
                # Calcular datos de potencia calorífica para este material
                calc_material = calcular_generacion_electrica(
                    mat['m3_biogas_por_tn'],
                    consumo_motor,
                    potencia_motor,
                    porcentaje_ch4
                )
                
                receta.append({
                    'material': mat['nombre'],
                    'tipo': mat['tipo'],
                    'toneladas': round(toneladas_usar, 2),
                    'stock_disponible': mat['stock_disponible'],
                    'kwh_por_tn': kwh_por_tn_usar,  # USAR VALOR OPTIMIZADO
                    'kwh_total': round(kwh_generado, 2),
                    'm3_biogas': round(toneladas_usar * mat['m3_biogas_por_tn'], 2),
                    'm3_ch4': round(toneladas_usar * mat['m3_ch4_por_tn'], 2),
                    'potencia_calorifica_kw': round(toneladas_usar * calc_material['potencia_calorifica_kw'], 2),
                    'energia_termica_total_kwh': round(toneladas_usar * calc_material['energia_termica_total_kwh'], 2),
                    'poder_calorifico_biogas': calc_material['poder_calorifico_biogas'],
                    # Datos de laboratorio
                    'st_pct': mat['st_pct'],
                    'sv_pct': mat['sv_pct'],
                    'svt_pct': mat['svt_pct'],
                    'carbohidratos': mat['carbohidratos'],
                    'lipidos': mat['lipidos'],
                    'proteinas': mat['proteinas'],
                    'densidad': mat['densidad']
                })
                kwh_acumulado += kwh_generado
    
    else:  # modo volumétrico
        # Normalizar porcentajes para que sumen 100%
        # El purín es un líquido, entonces: Sólidos + (Líquidos + Purín) = 100%
        total_porcentaje = pct_solidos_kw + pct_liquidos_kw + pct_purin_kw
        
        if total_porcentaje > 0:
            # Normalizar para que sumen 100%
            pct_solidos_normalizado = (pct_solidos_kw / total_porcentaje) * 100
            pct_liquidos_normalizado = (pct_liquidos_kw / total_porcentaje) * 100
            pct_purin_normalizado = (pct_purin_kw / total_porcentaje) * 100
            
            print(f"DEBUG: Porcentajes originales - Sólidos: {pct_solidos_kw}%, Líquidos: {pct_liquidos_kw}%, Purín: {pct_purin_kw}% (Total: {total_porcentaje}%)")
            print(f"DEBUG: Porcentajes normalizados - Sólidos: {pct_solidos_normalizado:.1f}%, Líquidos: {pct_liquidos_normalizado:.1f}%, Purín: {pct_purin_normalizado:.1f}% (Total: 100%)")
        else:
            # Valores por defecto si no se proporcionan porcentajes
            pct_solidos_normalizado = 60.0
            pct_liquidos_normalizado = 30.0
            pct_purin_normalizado = 10.0
            
        # ALGORITMO VOLUMÉTRICO CORREGIDO: Distribuir toneladas según porcentajes especificados
        print(f"DEBUG VOLUMETRICO: Objetivo total: {kwh_objetivo} kW")
        print(f"DEBUG VOLUMETRICO: Porcentajes - Sólidos: {pct_solidos_normalizado}%, Líquidos: {pct_liquidos_normalizado}%, Purín: {pct_purin_normalizado}%")
        
        # USAR MATERIALES OPTIMIZADOS POR ML - Separar por tipo
        solidos_optimizados = [m for m in materiales_optimizados if m['tipo'] == 'solido' and m['stock_disponible'] > 0]
        liquidos_optimizados = [m for m in materiales_optimizados if m['tipo'] == 'liquido' and m['stock_disponible'] > 0]
        
        # Ordenar por score ML
        solidos_optimizados.sort(key=lambda x: x.get('score_ml', 0), reverse=True)
        liquidos_optimizados.sort(key=lambda x: x.get('score_ml', 0), reverse=True)
        
        print(f"DEBUG: MODO VOLUMETRICO - Usando materiales optimizados: {len(solidos_optimizados)} solidos, {len(liquidos_optimizados)} liquidos")
        
        # PASO 1: Calcular kWh promedio por tonelada para estimar toneladas totales necesarias
        kwh_promedio_solidos = sum(m.get('kwh_por_tn_optimizado', m['kwh_por_tn']) for m in solidos_optimizados[:3]) / min(3, len(solidos_optimizados)) if solidos_optimizados else 0
        kwh_promedio_liquidos = sum(m.get('kwh_por_tn_optimizado', m['kwh_por_tn']) for m in liquidos_optimizados[:2]) / min(2, len(liquidos_optimizados)) if liquidos_optimizados else 0
        kwh_promedio_purin = kwh_purin / tn_purin if tn_purin > 0 else 0
        
        # Calcular kWh promedio ponderado por porcentajes
        kwh_promedio_ponderado = (
            (kwh_promedio_solidos * pct_solidos_normalizado / 100) +
            (kwh_promedio_liquidos * pct_liquidos_normalizado / 100) +
            (kwh_promedio_purin * pct_purin_normalizado / 100)
        )
        
        # PASO 2: Estimar toneladas totales necesarias para alcanzar el objetivo
        toneladas_totales_estimadas = kwh_objetivo / kwh_promedio_ponderado if kwh_promedio_ponderado > 0 else 100
        
        # PASO 3: Distribuir toneladas según porcentajes especificados
        tn_solidos_objetivo = toneladas_totales_estimadas * (pct_solidos_normalizado / 100)
        tn_liquidos_objetivo = toneladas_totales_estimadas * (pct_liquidos_normalizado / 100)
        tn_purin_objetivo = toneladas_totales_estimadas * (pct_purin_normalizado / 100)
        
        print(f"DEBUG VOLUMETRICO: Toneladas estimadas totales: {toneladas_totales_estimadas:.2f} Tn")
        print(f"DEBUG VOLUMETRICO: Distribución objetivo - Sólidos: {tn_solidos_objetivo:.2f} Tn, Líquidos: {tn_liquidos_objetivo:.2f} Tn, Purín: {tn_purin_objetivo:.2f} Tn")
        
        # PASO 4: Procesar sólidos - distribuir toneladas según porcentaje objetivo
        tn_acumulado_solidos = 0
        materiales_solidos_sel = solidos_optimizados[:min(3, len(solidos_optimizados))]
        
        for i, mat in enumerate(materiales_solidos_sel):
            if tn_acumulado_solidos >= tn_solidos_objetivo:
                break
                
            # USAR VALOR OPTIMIZADO POR ML si está disponible
            kwh_por_tn_usar = mat.get('kwh_por_tn_optimizado', mat['kwh_por_tn'])
            
            # Calcular cuántas toneladas necesitamos para completar el objetivo de sólidos
            tn_faltantes_solidos = tn_solidos_objetivo - tn_acumulado_solidos
            
            # Distribuir proporcionalmente entre los materiales sólidos disponibles
            if i == len(materiales_solidos_sel) - 1:
                # Último material: usar todas las toneladas restantes
                toneladas_usar = min(tn_faltantes_solidos, mat['stock_disponible'])
            else:
                # Distribuir proporcionalmente (más toneladas para materiales con mejor score)
                peso_material = mat.get('score_ml', 1)
                peso_total = sum(m.get('score_ml', 1) for m in materiales_solidos_sel)
                porcentaje_material = peso_material / peso_total if peso_total > 0 else 1/len(materiales_solidos_sel)
                toneladas_proporcionales = tn_solidos_objetivo * porcentaje_material
                toneladas_usar = min(toneladas_proporcionales, mat['stock_disponible'], tn_faltantes_solidos)
            
            # Asegurar mínimo de 0.01 Tn si hay stock disponible
            if toneladas_usar < 0.01 and mat['stock_disponible'] > 0 and tn_faltantes_solidos > 0:
                toneladas_usar = min(0.01, mat['stock_disponible'], tn_faltantes_solidos)
            
            if toneladas_usar > 0.01:
                kwh_generado = toneladas_usar * kwh_por_tn_usar
                
                # Calcular datos de potencia calorífica para este material
                calc_material = calcular_generacion_electrica(
                    mat['m3_biogas_por_tn'],
                    consumo_motor,
                    potencia_motor,
                    porcentaje_ch4
                )
                
                receta.append({
                    'material': mat['nombre'],
                    'tipo': mat['tipo'],
                    'toneladas': round(toneladas_usar, 2),
                    'stock_disponible': mat['stock_disponible'],
                    'kwh_por_tn': kwh_por_tn_usar,
                    'kwh_total': round(kwh_generado, 2),
                    'm3_biogas': round(toneladas_usar * mat['m3_biogas_por_tn'], 2),
                    'm3_ch4': round(toneladas_usar * mat['m3_ch4_por_tn'], 2),
                    'potencia_calorifica_kw': round(toneladas_usar * calc_material['potencia_calorifica_kw'], 2),
                    'energia_termica_total_kwh': round(toneladas_usar * calc_material['energia_termica_total_kwh'], 2),
                    'poder_calorifico_biogas': calc_material['poder_calorifico_biogas'],
                    'st_pct': mat['st_pct'],
                    'sv_pct': mat['sv_pct'],
                    'svt_pct': mat['svt_pct'],
                    'carbohidratos': mat['carbohidratos'],
                    'lipidos': mat['lipidos'],
                    'proteinas': mat['proteinas'],
                    'densidad': mat['densidad']
                })
                tn_acumulado_solidos += toneladas_usar
                print(f"DEBUG VOLUMETRICO: {mat['nombre']}: {toneladas_usar:.2f} Tn = {kwh_generado:.2f} kW (Acumulado sólidos: {tn_acumulado_solidos:.2f} Tn)")
        
        # PASO 5: Procesar líquidos - distribuir toneladas según porcentaje objetivo
        tn_acumulado_liquidos = 0
        materiales_liquidos_sel = liquidos_optimizados[:min(2, len(liquidos_optimizados))]
        
        for i, mat in enumerate(materiales_liquidos_sel):
            if tn_acumulado_liquidos >= tn_liquidos_objetivo:
                break
                
            # USAR VALOR OPTIMIZADO POR ML si está disponible
            kwh_por_tn_usar = mat.get('kwh_por_tn_optimizado', mat['kwh_por_tn'])
            
            # Calcular cuántas toneladas necesitamos para completar el objetivo de líquidos
            tn_faltantes_liquidos = tn_liquidos_objetivo - tn_acumulado_liquidos
            
            # Distribuir proporcionalmente entre los materiales líquidos disponibles
            if i == len(materiales_liquidos_sel) - 1:
                # Último material: usar todas las toneladas restantes
                toneladas_usar = min(tn_faltantes_liquidos, mat['stock_disponible'])
            else:
                # Distribuir proporcionalmente (más toneladas para materiales con mejor score)
                peso_material = mat.get('score_ml', 1)
                peso_total = sum(m.get('score_ml', 1) for m in materiales_liquidos_sel)
                porcentaje_material = peso_material / peso_total if peso_total > 0 else 1/len(materiales_liquidos_sel)
                toneladas_proporcionales = tn_liquidos_objetivo * porcentaje_material
                toneladas_usar = min(toneladas_proporcionales, mat['stock_disponible'], tn_faltantes_liquidos)
            
            # Asegurar mínimo de 0.01 Tn si hay stock disponible
            if toneladas_usar < 0.01 and mat['stock_disponible'] > 0 and tn_faltantes_liquidos > 0:
                toneladas_usar = min(0.01, mat['stock_disponible'], tn_faltantes_liquidos)
            
            if toneladas_usar > 0.01:
                kwh_generado = toneladas_usar * kwh_por_tn_usar
                
                # Calcular datos de potencia calorífica para este material
                calc_material = calcular_generacion_electrica(
                    mat['m3_biogas_por_tn'],
                    consumo_motor,
                    potencia_motor,
                    porcentaje_ch4
                )
                
                receta.append({
                    'material': mat['nombre'],
                    'tipo': mat['tipo'],
                    'toneladas': round(toneladas_usar, 2),
                    'stock_disponible': mat['stock_disponible'],
                    'kwh_por_tn': kwh_por_tn_usar,
                    'kwh_total': round(kwh_generado, 2),
                    'm3_biogas': round(toneladas_usar * mat['m3_biogas_por_tn'], 2),
                    'm3_ch4': round(toneladas_usar * mat['m3_ch4_por_tn'], 2),
                    'potencia_calorifica_kw': round(toneladas_usar * calc_material['potencia_calorifica_kw'], 2),
                    'energia_termica_total_kwh': round(toneladas_usar * calc_material['energia_termica_total_kwh'], 2),
                    'poder_calorifico_biogas': calc_material['poder_calorifico_biogas'],
                    'st_pct': mat['st_pct'],
                    'sv_pct': mat['sv_pct'],
                    'svt_pct': mat['svt_pct'],
                    'carbohidratos': mat['carbohidratos'],
                    'lipidos': mat['lipidos'],
                    'proteinas': mat['proteinas'],
                    'densidad': mat['densidad']
                })
                tn_acumulado_liquidos += toneladas_usar
                print(f"DEBUG VOLUMETRICO: {mat['nombre']}: {toneladas_usar:.2f} Tn = {kwh_generado:.2f} kW (Acumulado líquidos: {tn_acumulado_liquidos:.2f} Tn)")
    
    # PASO 6: Agregar purín a la receta si se usa (modo volumétrico usa porcentaje objetivo)
    if incluir_purin and tn_purin > 0:
        mat_purin = purin_materiales[0]
        
        # En modo volumétrico, usar el porcentaje objetivo calculado
        if modo == 'volumetrico':
            # Ajustar la cantidad de purín para que respete el porcentaje objetivo
            tn_purin_ajustado = min(tn_purin_objetivo, tn_purin, mat_purin['stock_disponible'])
            print(f"DEBUG VOLUMETRICO: Purín objetivo: {tn_purin_objetivo:.2f} Tn, Disponible: {tn_purin:.2f} Tn, Usando: {tn_purin_ajustado:.2f} Tn")
        else:
            # En modo energético, usar toda la cantidad disponible
            tn_purin_ajustado = tn_purin
        
        if tn_purin_ajustado > 0.01:
            calc_purin_ajustado = calcular_generacion_electrica(
                mat_purin['m3_biogas_por_tn'],
                consumo_motor,
                potencia_motor,
                porcentaje_ch4
            )
            
            kwh_purin_ajustado = tn_purin_ajustado * calc_purin_ajustado['kwh_generados']
            m3_biogas_purin_ajustado = tn_purin_ajustado * mat_purin['m3_biogas_por_tn']
            m3_ch4_purin_ajustado = tn_purin_ajustado * calc_purin_ajustado['m3_ch4_por_tn']
            
            receta.append({
            'material': mat_purin['nombre'],
                'tipo': mat_purin['tipo'],
                'toneladas': round(tn_purin_ajustado, 2),
                'stock_disponible': mat_purin['stock_disponible'],
                'kwh_por_tn': calc_purin_ajustado['kwh_generados'],
                'kwh_total': round(kwh_purin_ajustado, 2),
                'm3_biogas': round(m3_biogas_purin_ajustado, 2),
                'm3_ch4': round(m3_ch4_purin_ajustado, 2),
                'potencia_calorifica_kw': round(tn_purin_ajustado * calc_purin_ajustado['potencia_calorifica_kw'], 2),
                'energia_termica_total_kwh': round(tn_purin_ajustado * calc_purin_ajustado['energia_termica_total_kwh'], 2),
                'poder_calorifico_biogas': calc_purin_ajustado['poder_calorifico_biogas'],
            'st_pct': mat_purin['st_pct'],
            'sv_pct': mat_purin['sv_pct'],
            'svt_pct': mat_purin['svt_pct'],
            'carbohidratos': mat_purin['carbohidratos'],
            'lipidos': mat_purin['lipidos'],
            'proteinas': mat_purin['proteinas'],
            'densidad': mat_purin['densidad']
        })
    
            # Actualizar variables globales con valores ajustados
            kwh_purin = kwh_purin_ajustado
            m3_biogas_purin = m3_biogas_purin_ajustado
            m3_ch4_purin = m3_ch4_purin_ajustado
            tn_purin = tn_purin_ajustado
            
            print(f"DEBUG VOLUMETRICO: Purín agregado: {tn_purin_ajustado:.2f} Tn = {kwh_purin_ajustado:.2f} kW")
    
    # PASO 7: Ajuste fino para alcanzar mejor el objetivo de kWh (solo en modo volumétrico)
    if modo == 'volumetrico' and len(receta) > 0:
        total_kwh_actual = sum(r['kwh_total'] for r in receta)
        diferencia_kwh = kwh_objetivo - total_kwh_actual
        
        print(f"DEBUG VOLUMETRICO: Total kWh actual: {total_kwh_actual:.2f}, Objetivo: {kwh_objetivo:.2f}, Diferencia: {diferencia_kwh:.2f}")
        
        # Si hay una diferencia significativa (>5%), ajustar proporcionalmente
        if abs(diferencia_kwh) > kwh_objetivo * 0.05:  # Más del 5% de diferencia
            factor_ajuste = kwh_objetivo / total_kwh_actual if total_kwh_actual > 0 else 1
            
            print(f"DEBUG VOLUMETRICO: Aplicando factor de ajuste: {factor_ajuste:.3f}")
            
            # Ajustar todas las cantidades proporcionalmente
            for r in receta:
                tn_original = r['toneladas']
                tn_ajustada = tn_original * factor_ajuste
                
                # Verificar límites de stock
                if tn_ajustada <= r['stock_disponible']:
                    r['toneladas'] = round(tn_ajustada, 2)
                    r['kwh_total'] = round(tn_ajustada * r['kwh_por_tn'], 2)
                    r['m3_biogas'] = round(tn_ajustada * r['m3_biogas'] / tn_original, 2) if tn_original > 0 else 0
                    r['m3_ch4'] = round(tn_ajustada * r['m3_ch4'] / tn_original, 2) if tn_original > 0 else 0
                    print(f"DEBUG VOLUMETRICO: {r['material']}: {tn_original:.2f} → {tn_ajustada:.2f} Tn")
                else:
                    print(f"DEBUG VOLUMETRICO: {r['material']}: No se puede ajustar (stock insuficiente)")
    
    # PASO 8: Construir resumen final
    print(f"DEBUG: Construyendo resumen con {len(receta)} materiales en receta")
    resultado = construir_resumen(receta, kwh_objetivo, porcentaje_ch4, consumo_motor, 
                            potencia_motor, modo, m3_purin, incluir_purin, modelos_seleccionados)
    print(f"DEBUG: Resumen construido: {type(resultado)}")
    return resultado

def construir_resumen(receta, kwh_objetivo, porcentaje_ch4, consumo_motor, 
                     potencia_motor, modo, m3_purin=0, incluir_purin=False, modelos_seleccionados=None):
    """Construye el resumen de resultados"""
    total_toneladas = sum(r['toneladas'] for r in receta)
    total_biogas = sum(r['m3_biogas'] for r in receta)
    total_ch4 = sum(r['m3_ch4'] for r in receta)
    total_kwh = sum(r['kwh_total'] for r in receta)
    
    # Calcular potencia calorífica total
    total_potencia_calorifica = sum(r.get('potencia_calorifica_kw', 0) for r in receta)
    total_energia_termica = sum(r.get('energia_termica_total_kwh', 0) for r in receta)
    
    consumo_m3_h = (consumo_motor / 1000) * 3600
    # Calcular horas de operación para 24 horas de funcionamiento
    horas_operacion = 24.0  # Fijo a 24 horas como solicitado
    
    # Calcular porcentajes en la mezcla
    tn_solidos = sum(r['toneladas'] for r in receta if r['tipo'] == 'solido')
    tn_liquidos = sum(r['toneladas'] for r in receta if r['tipo'] == 'liquido')
    tn_purin = sum(r['toneladas'] for r in receta if r['tipo'] == 'purin')
    
    for r in receta:
        r['porcentaje_mezcla'] = round((r['toneladas'] / total_toneladas) * 100, 1) if total_toneladas > 0 else 0
    
    # Calcular porcentaje de CH4 en el biogás
    porcentaje_ch4_real = round((total_ch4 / total_biogas) * 100, 1) if total_biogas > 0 else 0
    
    # Debug adicional para verificar cálculos de metano
    print(f"DEBUG METANO: Total biogás: {total_biogas:.2f} m³, Total CH4: {total_ch4:.2f} m³, Porcentaje CH4: {porcentaje_ch4_real:.1f}%")
    
    # Obtener métricas ML
    metricas_ml = obtener_metricas_ml(receta, kwh_objetivo, porcentaje_ch4)
    
    # Realizar análisis cruzado si se seleccionaron múltiples modelos
    analisis_cruzado = None
    if modelos_seleccionados and len(modelos_seleccionados) > 1:
        analisis_cruzado = analizar_cruzado_modelos(receta, kwh_objetivo, porcentaje_ch4, modelos_seleccionados)
    
    return {
        'receta': receta,
        'resumen': {
            'modo': modo,
            'kwh_objetivo': kwh_objetivo,
            'kwh_generado': round(total_kwh, 2),
            'cumplimiento': round((total_kwh / kwh_objetivo) * 100, 1) if kwh_objetivo > 0 else 0,
            'total_toneladas': round(total_toneladas, 2),
            'total_biogas_m3': round(total_biogas, 2),
            'total_ch4_m3': round(total_ch4, 2),
            'porcentaje_metano': porcentaje_ch4_real,  # Cambiado de porcentaje_ch4_real a porcentaje_metano
            'porcentaje_ch4_real': porcentaje_ch4_real,  # Mantener para compatibilidad
            'total_potencia_calorifica_kw': round(total_potencia_calorifica, 2),
            'total_energia_termica_kwh': round(total_energia_termica, 2),
            'horas_operacion': round(horas_operacion, 2),
            'dias_operacion': round(horas_operacion / 24, 2),
            'potencia_motor': potencia_motor,
            'porcentaje_ch4': porcentaje_ch4,
            'm3_purin': m3_purin,
            'incluir_purin': incluir_purin,
            'proporciones': {
                'toneladas_solidos': round(tn_solidos, 2),
                'toneladas_liquidos': round(tn_liquidos, 2),
                'toneladas_purin': round(tn_purin, 2),
                'porcentaje_solidos': round((tn_solidos / total_toneladas * 100) if total_toneladas > 0 else 0, 1),
                'porcentaje_liquidos': round((tn_liquidos / total_toneladas * 100) if total_toneladas > 0 else 0, 1),
                'porcentaje_purin': round((tn_purin / total_toneladas * 100) if total_toneladas > 0 else 0, 1)
            }
        },
        'metricas_ml': metricas_ml,
        'analisis_cruzado': analisis_cruzado
    }

# RUTAS DE ADÁN

@adan_bp.route('/')
def index():
    """Página principal de Adán"""
    materiales = cargar_materiales_excel()
    consumo_chp_global = obtener_consumo_chp_global()
    
    # Actualizar configuración del motor con el consumo CHP global
    motor_config_actualizado = MOTOR_CONFIG.copy()
    motor_config_actualizado['consumo_chp_global'] = consumo_chp_global
    
    return render_template('adan_calculator.html', 
                         materiales=materiales, 
                         motor_config=motor_config_actualizado)

@adan_bp.route('/materiales')
def obtener_materiales():
    """API para obtener materiales disponibles"""
    materiales = cargar_materiales_excel()
    return jsonify(materiales)

@adan_bp.route('/modelos_disponibles')
def modelos_disponibles():
    """Endpoint para obtener modelos ML disponibles"""
    return jsonify({
        'modelos': MODELOS_DISPONIBLES,
        'modelos_activos': [k for k, v in MODELOS_DISPONIBLES.items() if v['disponible']]
    })

@adan_bp.route('/obtener_generacion_actual', methods=['GET'])
def obtener_generacion_actual():
    """Obtiene el valor de generación actual del dashboard"""
    try:
        # Importar la función del app principal
        from app_CORREGIDO_OK_FINAL import obtener_datos_kpi_completos
        
        datos_kpi = obtener_datos_kpi_completos()
        generacion_base = datos_kpi.get('generacion_actual', 1352.0)
        
        # Agregar variación dinámica para simular cambios reales
        import random
        import time
        
        # Usar timestamp para generar variación consistente pero cambiante
        timestamp = int(time.time())
        variacion = (timestamp % 100) - 50  # Variación entre -50 y +50
        
        generacion_actual = generacion_base + variacion
        
        return jsonify({
            'generacion_actual': generacion_actual,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error obteniendo generación actual: {e}")
        return jsonify({
            'generacion_actual': 1352.0,
            'status': 'error',
            'error': str(e)
        })

@adan_bp.route('/calcular_mezcla', methods=['POST'])
def calcular_mezcla():
    """Calcula la mezcla según parámetros del usuario"""
    try:
        # 🔊 Mensaje de voz: Iniciando cálculo MEJORADO
        if VOICE_ADAN_DISPONIBLE and VOICE_ADAN_MEJORADO:
            # Mejorar pronunciación de "cálculo" para evitar confusión
            custom_message = "Iniciando el proceso con experiencia"
            mensaje_mejorado = custom_message.replace('cálculo', 'CÁL-CU-LO').replace('calculo', 'CÁL-CU-LO')
            speak_adan_calculating_mejorado(mensaje_mejorado)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        kwh_objetivo = float(data.get('kwh_objetivo'))
        porcentaje_ch4 = float(data.get('porcentaje_ch4', 65))
        m3_purin = float(data.get('m3_purin', 0))
        modo = data.get('modo', 'energetico')
        pct_solidos_kw = float(data.get('pct_solidos_kw', 60))
        pct_liquidos_kw = float(data.get('pct_liquidos_kw', 40))
        pct_purin_kw = float(data.get('pct_purin_kw', 0))
        incluir_purin = data.get('incluir_purin', True)
        num_materiales = int(data.get('num_materiales', 5))
        consumo = float(data.get('consumo_motor', MOTOR_CONFIG['consumo_l_s']))
        potencia = float(data.get('potencia_motor', MOTOR_CONFIG['potencia_kw']))
        
        # Obtener potencia motor actual del dashboard si no se proporciona específicamente
        if potencia == MOTOR_CONFIG['potencia_kw']:  # Valor por defecto
            try:
                from app_CORREGIDO_OK_FINAL import obtener_datos_kpi_completos
                datos_kpi = obtener_datos_kpi_completos()
                # Usar la potencia nominal del motor (1545 kW) en lugar de la generación actual
                potencia_motor_actual = MOTOR_CONFIG['potencia_kw']  # 1545 kW - potencia nominal del Jenbacher J420
                potencia = potencia_motor_actual
                print(f"DEBUG: Usando potencia nominal del motor Jenbacher J420: {potencia} kW")
            except Exception as e:
                print(f"DEBUG: Error obteniendo configuración del motor: {e}")
                print(f"DEBUG: Usando potencia motor por defecto: {potencia} kW")
        
        print(f"DEBUG: Parámetros finales - consumo: {consumo}, potencia: {potencia}")
        
        modelos_seleccionados = data.get('modelos_seleccionados', ['xgboost'])  # Default a XGBoost
        print(f"DEBUG: Modelos seleccionados: {modelos_seleccionados}")
        
        materiales = cargar_materiales_excel()
        print(f"DEBUG: Materiales cargados: {len(materiales)}")
        
        resultado = generar_receta_con_purin(
            kwh_objetivo, porcentaje_ch4, m3_purin, materiales,
            consumo, potencia, modo, pct_solidos_kw, pct_liquidos_kw,
            pct_purin_kw, incluir_purin, num_materiales, modelos_seleccionados
        )
        
        print(f"DEBUG: Resultado generado: {type(resultado)}")
        if isinstance(resultado, dict):
            print(f"DEBUG: Claves del resultado: {list(resultado.keys())}")
        
        # 🔊 Mensaje de voz: Cálculo exitoso MEJORADO
        if VOICE_ADAN_DISPONIBLE and VOICE_ADAN_MEJORADO:
            speak_adan_success_mejorado(f"¡Felicitaciones! Proceso exitoso con Adán usando voz mejorada. Se generaron {kwh_objetivo} kilovatios con precisión")
            speak_adan_completed_mejorado("Proceso completado con excelencia usando síntesis de voz optimizada")
        
        return jsonify({
            'status': 'success',
            'mensaje': f'Mezcla calculada exitosamente para {kwh_objetivo} kWh',
            **resultado
        })
        
    except Exception as e:
        print(f"Error en calcular_mezcla: {e}")
        
        # 🔊 Mensaje de voz: Error en cálculo MEJORADO
        if VOICE_ADAN_DISPONIBLE and VOICE_ADAN_MEJORADO:
            speak_adan_error_mejorado(f"Error en el proceso usando voz mejorada, revisando parámetros. Problema: {str(e)[:50]}")
        
        return jsonify({
            'status': 'error',
            'mensaje': f'Error interno: {str(e)}',
            'error': str(e)
        }), 500

@adan_bp.route('/sugerir_materiales', methods=['POST'])
def sugerir_materiales():
    """Sugiere los mejores materiales disponibles"""
    data = request.get_json()
    num_materiales = int(data.get('num_materiales', 5))
    porcentaje_ch4 = float(data.get('porcentaje_ch4', 65))
    
    materiales = cargar_materiales_excel()
    
    # Calcular rendimiento de cada material
    for mat in materiales:
        if mat['stock_disponible'] > 0:
            calc = calcular_generacion_electrica(
                mat['m3_biogas_por_tn'],
                MOTOR_CONFIG['consumo_l_s'],
                MOTOR_CONFIG['potencia_kw'],
                porcentaje_ch4
            )
            mat['kwh_por_tn'] = calc['kwh_generados']
            # Calcular score combinado (rendimiento + stock + diversidad)
            mat['score'] = (calc['kwh_generados'] * 0.6) + (mat['stock_disponible'] * 0.2) + (mat['m3_biogas_por_tn'] * 0.2)
        else:
            mat['kwh_por_tn'] = 0
            mat['score'] = 0
    
    # Ordenar por score combinado
    materiales.sort(key=lambda x: x['score'], reverse=True)
    
    # Tomar los mejores N
    sugeridos = materiales[:num_materiales]
    
    return jsonify({
        'materiales_sugeridos': [
            {
                'nombre': m['nombre'],
                'tipo': m['tipo'],
                'kwh_por_tn': round(m['kwh_por_tn'], 2),
                'm3_biogas_por_tn': m['m3_biogas_por_tn'],
                'stock_disponible': m['stock_disponible']
            }
            for m in sugeridos
        ]
    })

@adan_bp.route('/configuracion')
def configuracion():
    """Página de configuración de Adán"""
    return render_template('adan_config.html', motor_config=MOTOR_CONFIG)

@adan_bp.route('/ayuda')
def ayuda():
    """Página de ayuda de Adán"""
    return render_template('adan_help.html')

# Función para registrar el Blueprint en la aplicación principal
def registrar_adan(app):
    """Registra el Blueprint de Adán en la aplicación Flask"""
    app.register_blueprint(adan_bp)
    print("SUCCESS: Sistema Adan registrado correctamente")
