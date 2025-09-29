#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo temporal de funciones para SIBIA
Contiene las funciones básicas necesarias para el funcionamiento
"""

# Referencia de materiales base
REFERENCIA_MATERIALES = {
    "purin_cerdo": {
        "st_porcentaje": 8.5,
        "sv_porcentaje": 7.2,
        "ch4_porcentaje": 65.0,
        "densidad": 1.02
    },
    "purin_vaca": {
        "st_porcentaje": 12.0,
        "sv_porcentaje": 10.5,
        "ch4_porcentaje": 60.0,
        "densidad": 1.03
    },
    "purin_ave": {
        "st_porcentaje": 15.0,
        "sv_porcentaje": 12.8,
        "ch4_porcentaje": 70.0,
        "densidad": 1.05
    }
}

# Materiales base para cálculos
MATERIALES_BASE = {
    "purin_cerdo": {
        "nombre": "Purín de Cerdo",
        "st_porcentaje": 8.5,
        "sv_porcentaje": 7.2,
        "ch4_porcentaje": 65.0,
        "densidad": 1.02,
        "ph": 7.2,
        "nitrogeno": 0.8,
        "fosforo": 0.3,
        "potasio": 0.6
    },
    "purin_vaca": {
        "nombre": "Purín de Vaca",
        "st_porcentaje": 12.0,
        "sv_porcentaje": 10.5,
        "ch4_porcentaje": 60.0,
        "densidad": 1.03,
        "ph": 7.0,
        "nitrogeno": 1.2,
        "fosforo": 0.4,
        "potasio": 0.8
    },
    "purin_ave": {
        "nombre": "Purín de Ave",
        "st_porcentaje": 15.0,
        "sv_porcentaje": 12.8,
        "ch4_porcentaje": 70.0,
        "densidad": 1.05,
        "ph": 7.5,
        "nitrogeno": 1.8,
        "fosforo": 0.6,
        "potasio": 1.0
    }
}

def obtener_st_porcentaje(material, datos):
    """Obtener porcentaje de ST para un material"""
    try:
        # Usar datos del material base si están disponibles
        material_base = MATERIALES_BASE.get(material, {})
        st_base = material_base.get('st_porcentaje', 0)
        
        # Si hay datos específicos, usarlos
        if datos and 'st_porcentaje' in datos:
            return float(datos['st_porcentaje'])
        
        return st_base
    except Exception:
        return 0.0

def calcular_kw_tn_basico(st_porcentaje, sv_porcentaje, ch4_porcentaje):
    """Cálculo básico de KW/TN"""
    try:
        # Fórmula simplificada: KW/TN = (ST * SV * CH4) / 1000
        kw_tn = (st_porcentaje * sv_porcentaje * ch4_porcentaje) / 1000
        return round(kw_tn, 2)
    except Exception:
        return 0.0

def obtener_parametros_material(material):
    """Obtener parámetros de un material"""
    return MATERIALES_BASE.get(material, {})

def validar_material(material):
    """Validar si un material existe"""
    return material in MATERIALES_BASE

# Constantes para SA7
NOMBRE_SA7 = "purin_cerdo"
KW_GENERACION_SA7_DEFAULT = 694.0

def cargar_y_procesar_materiales_base(config):
    """Cargar y procesar materiales base"""
    try:
        return MATERIALES_BASE
    except Exception:
        return {}

def obtener_materiales_base():
    """Obtener materiales base"""
    return MATERIALES_BASE

# Configuración por defecto
CONFIG_DEFAULTS = {
    "biodigestor_1": {
        "capacidad_m3": 1000,
        "temperatura_optima": 35,
        "ph_optimo": 7.0,
        "trh_dias": 25
    },
    "biodigestor_2": {
        "capacidad_m3": 1000,
        "temperatura_optima": 35,
        "ph_optimo": 7.0,
        "trh_dias": 25
    }
}

# Función para calcular porcentaje de metano
def calcular_porcentaje_metano(resultado, consumo_chp):
    """
    Calcula el porcentaje de metano usando la fórmula correcta de la tabla de gestión:
    CH4% = ((Proteínas × 0.71) + (Lípidos × 0.68) + (Carbohidratos × 0.5)) / Total Biogás
    """
    try:
        # Obtener materiales
        materiales_solidos = resultado.get('materiales_solidos', {})
        materiales_liquidos = resultado.get('materiales_liquidos', {})
        
        # Variables para calcular metano ponderado
        total_metano_ponderado = 0.0
        total_cantidad = 0.0
        
        # Procesar materiales sólidos
        for mat, datos in materiales_solidos.items():
            cantidad = datos.get('cantidad_tn', 0)
            if cantidad > 0:
                # Obtener composición del material desde materiales_base_config.json
                try:
                    import json
                    with open('materiales_base_config.json', 'r', encoding='utf-8') as f:
                        materiales_config = json.load(f)
                    
                    material_config = materiales_config.get(mat, {})
                    proteinas = float(material_config.get('proteinas_calc', 0))
                    lipidos = float(material_config.get('lipidos_calc', 0))
                    carbohidratos = float(material_config.get('carbohidratos_calc', 0))
                    
                    # Calcular CH4% usando la fórmula correcta
                    total_biogas = proteinas + lipidos + carbohidratos
                    if total_biogas > 0:
                        ch4_porcentaje = ((proteinas * 0.71) + (lipidos * 0.68) + (carbohidratos * 0.5)) / total_biogas
                        total_metano_ponderado += ch4_porcentaje * cantidad
                        total_cantidad += cantidad
                except:
                    # Si no se puede obtener la configuración, usar valor por defecto
                    total_metano_ponderado += 0.65 * cantidad  # 65% por defecto
                    total_cantidad += cantidad
        
        # Procesar materiales líquidos
        for mat, datos in materiales_liquidos.items():
            cantidad = datos.get('cantidad_tn', 0)
            if cantidad > 0:
                # Obtener composición del material desde materiales_base_config.json
                try:
                    import json
                    with open('materiales_base_config.json', 'r', encoding='utf-8') as f:
                        materiales_config = json.load(f)
                    
                    material_config = materiales_config.get(mat, {})
                    proteinas = float(material_config.get('proteinas_calc', 0))
                    lipidos = float(material_config.get('lipidos_calc', 0))
                    carbohidratos = float(material_config.get('carbohidratos_calc', 0))
                    
                    # Calcular CH4% usando la fórmula correcta
                    total_biogas = proteinas + lipidos + carbohidratos
                    if total_biogas > 0:
                        ch4_porcentaje = ((proteinas * 0.71) + (lipidos * 0.68) + (carbohidratos * 0.5)) / total_biogas
                        total_metano_ponderado += ch4_porcentaje * cantidad
                        total_cantidad += cantidad
                except:
                    # Si no se puede obtener la configuración, usar valor por defecto
                    total_metano_ponderado += 0.65 * cantidad  # 65% por defecto
                    total_cantidad += cantidad
        
        # Calcular porcentaje de metano ponderado
        if total_cantidad > 0:
            porcentaje_metano = (total_metano_ponderado / total_cantidad) * 100
            return min(70.0, max(0.0, porcentaje_metano))
        else:
            return 0.0
        
    except Exception as e:
        print(f"Error calculando metano: {e}")
        return 0.0
