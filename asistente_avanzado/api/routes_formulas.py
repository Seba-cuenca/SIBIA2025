#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints API para el Sistema de Fórmulas y Cálculos
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar el sistema de fórmulas
from asistente_avanzado.core.sistema_formulas_calculos import sistema_formulas

# Blueprint para fórmulas
formulas_bp = Blueprint('formulas', __name__)

@formulas_bp.route('/calcular/energia', methods=['POST'])
def calcular_energia_con_formula():
    """Calcula energía de un material mostrando la fórmula"""
    try:
        data = request.get_json()
        
        cantidad = data.get('cantidad')
        material = data.get('material')
        nombre_material = data.get('nombre_material', material)
        
        if not cantidad or not material:
            return jsonify({'error': 'Faltan cantidad o material'}), 400
        
        # Obtener rendimiento del material (simulado por ahora)
        rendimientos = {
            'estiercol': 9.5,
            'maiz': 8.5,
            'purin': 3.2,
            'silaje': 7.8,
            'estiércol': 9.5,
            'maíz': 8.5,
            'purín': 3.2
        }
        
        kw_tn = rendimientos.get(material.lower(), 5.0)
        
        # Calcular con fórmula
        formula = sistema_formulas.calcular_energia_material(
            cantidad, kw_tn, nombre_material
        )
        
        # Calcular equivalencia hogares
        formula_hogares = sistema_formulas.calcular_equivalencia_hogares(formula.resultado)
        
        return jsonify({
            'exito': True,
            'resultado': formula.resultado,
            'unidad': formula.unidad,
            'formula': {
                'nombre': formula.nombre,
                'formula_texto': formula.formula_texto,
                'variables': formula.variables,
                'pasos': formula.pasos,
                'descripcion': formula.descripcion
            },
            'equivalencia_hogares': formula_hogares.resultado,
            'energia_diaria_kwh': formula.resultado * 24
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulas_bp.route('/calcular/prediccion', methods=['POST'])
def calcular_prediccion_con_formulas():
    """Calcula predicción con todas las fórmulas"""
    try:
        data = request.get_json()
        
        temperatura = data.get('temperatura', 37.0)
        presion = data.get('presion', 1.2)
        energia_base = data.get('energia_base', 1000)
        
        # Calcular con fórmulas
        formula_pred, formula_temp, formula_pres = sistema_formulas.calcular_prediccion_xgboost(
            energia_base, temperatura, presion
        )
        
        return jsonify({
            'exito': True,
            'prediccion_kwh': formula_pred.resultado,
            'formulas': {
                'temperatura': {
                    'factor': formula_temp.resultado,
                    'pasos': formula_temp.pasos,
                    'descripcion': formula_temp.descripcion
                },
                'presion': {
                    'factor': formula_pres.resultado,
                    'pasos': formula_pres.pasos,
                    'descripcion': formula_pres.descripcion
                },
                'prediccion': {
                    'formula': formula_pred.formula_texto,
                    'pasos': formula_pred.pasos,
                    'variables': formula_pred.variables
                }
            },
            'confianza': 0.92
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulas_bp.route('/calcular/mezcla', methods=['POST'])
def calcular_mezcla_con_formulas():
    """Calcula energía total de mezcla mostrando fórmulas"""
    try:
        data = request.get_json()
        materiales = data.get('materiales', {})
        
        if not materiales:
            return jsonify({'error': 'No se proporcionaron materiales'}), 400
        
        # Calcular con fórmula
        formula = sistema_formulas.calcular_energia_total_mezcla(materiales)
        
        return jsonify({
            'exito': True,
            'resultado': formula.resultado,
            'unidad': formula.unidad,
            'formula': {
                'nombre': formula.nombre,
                'formula_texto': formula.formula_texto,
                'variables': formula.variables,
                'pasos': formula.pasos,
                'descripcion': formula.descripcion
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulas_bp.route('/calcular/porcentaje', methods=['POST'])
def calcular_porcentaje_con_formula():
    """Calcula porcentaje mostrando fórmula"""
    try:
        data = request.get_json()
        
        componente = data.get('componente', 0)
        total = data.get('total', 0)
        nombre_componente = data.get('nombre_componente', 'Componente')
        
        if total <= 0:
            return jsonify({'error': 'El total debe ser mayor a 0'}), 400
        
        # Calcular con fórmula
        formula = sistema_formulas.calcular_porcentaje(
            componente, total, nombre_componente
        )
        
        return jsonify({
            'exito': True,
            'resultado': formula.resultado,
            'unidad': formula.unidad,
            'formula': {
                'nombre': formula.nombre,
                'formula_texto': formula.formula_texto,
                'variables': formula.variables,
                'pasos': formula.pasos,
                'descripcion': formula.descripcion
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulas_bp.route('/listado', methods=['GET'])
def obtener_listado_formulas():
    """Obtiene listado de todas las fórmulas disponibles"""
    try:
        formulas = []
        for key, value in sistema_formulas.formulas_definidas.items():
            formulas.append({
                'id': key,
                'nombre': value['nombre'],
                'formula_texto': value['formula_texto'],
                'descripcion': value['descripcion']
            })
        
        return jsonify({
            'exito': True,
            'formulas': formulas,
            'total': len(formulas)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulas_bp.route('/formatear/html', methods=['POST'])
def formatear_formula_html():
    """Formatea una fórmula para mostrar en HTML"""
    try:
        data = request.get_json()
        
        # Crear objeto FormulaCalculo desde los datos
        from asistente_avanzado.core.sistema_formulas_calculos import FormulaCalculo
        
        formula = FormulaCalculo(
            nombre=data.get('nombre', ''),
            formula_latex=data.get('formula_latex', ''),
            formula_texto=data.get('formula_texto', ''),
            variables=data.get('variables', {}),
            resultado=data.get('resultado', 0),
            unidad=data.get('unidad', ''),
            pasos=data.get('pasos', []),
            descripcion=data.get('descripcion', '')
        )
        
        html = sistema_formulas.formatear_formula_html(formula)
        
        return jsonify({
            'exito': True,
            'html': html
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
