#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora Matemática para SIBIA
Procesa operaciones matemáticas básicas y avanzadas
"""

import re
import math
import logging

logger = logging.getLogger(__name__)

class CalculadoraMatematica:
    """Calculadora matemática inteligente"""
    
    def __init__(self):
        self.operaciones_basicas = {
            'suma': '+',
            'sumar': '+',
            'más': '+',
            'adición': '+',
            'resta': '-',
            'restar': '-',
            'menos': '-',
            'sustracción': '-',
            'multiplicación': '*',
            'multiplicar': '*',
            'por': '*',
            'veces': '*',
            'división': '/',
            'dividir': '/',
            'entre': '/',
            'potencia': '**',
            'elevado': '**',
            'raíz': 'sqrt',
            'porcentaje': '%'
        }
        
        self.palabras_numeros = {
            'cero': 0, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,
            'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10,
            'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14, 'quince': 15,
            'dieciséis': 16, 'diecisiete': 17, 'dieciocho': 18, 'diecinueve': 19,
            'veinte': 20, 'treinta': 30, 'cuarenta': 40, 'cincuenta': 50,
            'sesenta': 60, 'setenta': 70, 'ochenta': 80, 'noventa': 90,
            'cien': 100, 'mil': 1000, 'millón': 1000000
        }
    
    def es_operacion_matematica(self, texto):
        """Detecta si el texto contiene una operación matemática"""
        texto_lower = texto.lower()
        
        # Corregir errores ortográficos comunes
        texto_lower = self._corregir_errores_ortograficos(texto_lower)
        
        # Patrones de operaciones matemáticas
        patrones = [
            r'\d+\s*[+\-*/]\s*\d+',  # 2+4, 5-3, etc.
            r'\d+\s*(más|menos|por|entre)\s*\d+',  # 2 más 4, 5 menos 3
            r'(cuánto|cuanto)\s*es\s*\d+\s*(más|menos|por|entre|suma|resta|multiplica|divide)\s*\d+',
            r'\d+\s*(suma|resta|multiplica|divide)\s*\d+',
            r'(sumar|restar|multiplicar|dividir)\s*\d+\s*(y|con|por)\s*\d+',
            r'raíz\s*(cuadrada|)\s*de\s*\d+',
            r'\d+\s*elevado\s*a\s*\d+',
            r'\d+\s*al\s*cuarto\s*de\s*\d+',
            r'porcentaje\s*de\s*\d+',
            r'\d+\s*por\s*ciento',
            # Patrones específicos para "x"
            r'\d+\s*x\s*\d+',  # 2x4, 3x5, etc.
            r'(cuánto|cuanto)\s*es\s*\d+\s*x\s*\d+',  # cuanto es 2x4
            r'\d+\s*x\s*\d+',  # 2x4, 3x5, etc.
            r'(cuánto|cuanto)\s*es\s*\d+\s*x\s*\d+'  # cuanto es 2x4
        ]
        
        for patron in patrones:
            if re.search(patron, texto_lower):
                return True
        
        return False
    
    def _corregir_errores_ortograficos(self, texto):
        """Corrige errores ortográficos comunes en preguntas matemáticas"""
        correcciones = {
            # Errores comunes en operaciones
            r'\b2x\b': '2 por',
            r'\b3x\b': '3 por',
            r'\b4x\b': '4 por',
            r'\b5x\b': '5 por',
            r'\b6x\b': '6 por',
            r'\b7x\b': '7 por',
            r'\b8x\b': '8 por',
            r'\b9x\b': '9 por',
            r'\b1x\b': '1 por',
            r'\b0x\b': '0 por',
            
            # Errores en palabras
            r'\bcuanto\b': 'cuánto',
            r'\bcuanto\s*es\b': 'cuánto es',
            r'\bcuanto\s*da\b': 'cuánto da',
            r'\bcuanto\s*vale\b': 'cuánto vale',
            
            # Errores en operaciones
            r'\bmas\b': 'más',
            r'\bmenos\b': 'menos',  # Ya está bien
            r'\bpor\b': 'por',      # Ya está bien
            r'\bentre\b': 'entre',   # Ya está bien
            
            # Errores en números escritos
            r'\bdos\s*x\b': 'dos por',
            r'\btres\s*x\b': 'tres por',
            r'\bcuatro\s*x\b': 'cuatro por',
            r'\bcinco\s*x\b': 'cinco por',
            r'\bseis\s*x\b': 'seis por',
            r'\bsiete\s*x\b': 'siete por',
            r'\bocho\s*x\b': 'ocho por',
            r'\bnueve\s*x\b': 'nueve por',
            r'\buno\s*x\b': 'uno por',
            r'\bcero\s*x\b': 'cero por'
        }
        
        texto_corregido = texto
        for error, correccion in correcciones.items():
            texto_corregido = re.sub(error, correccion, texto_corregido, flags=re.IGNORECASE)
        
        return texto_corregido
    
    def extraer_numeros_y_operacion(self, texto):
        """Extrae números y operación del texto"""
        texto_lower = texto.lower()
        
        # Corregir errores ortográficos comunes
        texto_lower = self._corregir_errores_ortograficos(texto_lower)
        
        # Convertir palabras a números
        for palabra, numero in self.palabras_numeros.items():
            texto_lower = texto_lower.replace(palabra, str(numero))
        
        # Buscar números
        numeros = re.findall(r'\d+(?:\.\d+)?', texto_lower)
        
        # Verificar si es raíz cuadrada (solo necesita un número)
        if 'raíz' in texto_lower:
            if len(numeros) < 1:
                return None, None, None
            try:
                num1 = float(numeros[0])
                return num1, None, 'sqrt'
            except ValueError:
                return None, None, None
        
        # Verificar si es porcentaje
        if 'porcentaje' in texto_lower or 'por ciento' in texto_lower:
            if len(numeros) < 2:
                return None, None, None
            try:
                num1 = float(numeros[0])  # Porcentaje
                num2 = float(numeros[1])  # Número base
                return num1, num2, '%'
            except ValueError:
                return None, None, None
        
        # Operaciones normales (necesitan dos números)
        if len(numeros) < 2:
            return None, None, None
        
        try:
            num1 = float(numeros[0])
            num2 = float(numeros[1])
        except ValueError:
            return None, None, None
        
        # Buscar operación
        operacion = None
        
        # Operaciones con símbolos
        if '+' in texto_lower or 'más' in texto_lower or 'suma' in texto_lower:
            operacion = '+'
        elif '-' in texto_lower or 'menos' in texto_lower or 'resta' in texto_lower:
            operacion = '-'
        elif '*' in texto_lower or 'por' in texto_lower or 'multiplica' in texto_lower or 'veces' in texto_lower or 'x' in texto_lower:
            operacion = '*'
        elif '/' in texto_lower or 'entre' in texto_lower or 'divide' in texto_lower:
            operacion = '/'
        elif 'elevado' in texto_lower or 'al' in texto_lower:
            operacion = '**'
        elif 'raíz' in texto_lower:
            operacion = 'sqrt'
        elif 'porcentaje' in texto_lower or 'por ciento' in texto_lower:
            operacion = '%'
        
        return num1, num2, operacion
    
    def calcular(self, num1, num2, operacion):
        """Realiza el cálculo matemático"""
        try:
            if operacion == '+':
                resultado = num1 + num2
                operacion_texto = "suma"
            elif operacion == '-':
                resultado = num1 - num2
                operacion_texto = "resta"
            elif operacion == '*':
                resultado = num1 * num2
                operacion_texto = "multiplicación"
            elif operacion == '/':
                if num2 == 0:
                    return None, "No se puede dividir por cero"
                resultado = num1 / num2
                operacion_texto = "división"
            elif operacion == '**':
                resultado = num1 ** num2
                operacion_texto = "potencia"
            elif operacion == 'sqrt':
                if num1 < 0:
                    return None, "No se puede calcular la raíz cuadrada de un número negativo"
                resultado = math.sqrt(num1)
                operacion_texto = "raíz cuadrada"
            elif operacion == '%':
                resultado = (num1 * num2) / 100
                operacion_texto = "porcentaje"
            else:
                return None, "Operación no reconocida"
            
            return resultado, operacion_texto
            
        except Exception as e:
            logger.error(f"Error en cálculo: {e}")
            return None, f"Error en el cálculo: {str(e)}"
    
    def formatear_resultado(self, num1, num2, operacion, resultado, operacion_texto):
        """Formatea el resultado de manera amigable"""
        if resultado is None:
            return f"❌ {operacion_texto}"
        
        # Formatear números
        if resultado == int(resultado):
            resultado_formateado = int(resultado)
        else:
            resultado_formateado = round(resultado, 2)
        
        # Respuesta corta y directa
        if operacion == 'sqrt':
            return f"🧮 **Raíz cuadrada de {num1} = {resultado_formateado}**"
        elif operacion == '%':
            return f"🧮 **{num1}% de {num2} = {resultado_formateado}**"
        else:
            return f"🧮 **{num1} {operacion} {num2} = {resultado_formateado}**"
    
    def procesar_calculo(self, texto):
        """Procesa una consulta matemática completa"""
        if not self.es_operacion_matematica(texto):
            return None
        
        num1, num2, operacion = self.extraer_numeros_y_operacion(texto)
        
        if num1 is None or operacion is None:
            return None
        
        # Para raíz cuadrada, num2 puede ser None
        if operacion != 'sqrt' and num2 is None:
            return None
        
        resultado, operacion_texto = self.calcular(num1, num2, operacion)
        
        if resultado is None:
            return f"❌ {operacion_texto}"
        
        return self.formatear_resultado(num1, num2, operacion, resultado, operacion_texto)

# Instancia global
calculadora = CalculadoraMatematica()

def procesar_consulta_matematica(texto):
    """Función principal para procesar consultas matemáticas"""
    return calculadora.procesar_calculo(texto)

# Ejemplos de uso
if __name__ == "__main__":
    # Pruebas
    pruebas = [
        "cuanto es 2 por 4",
        "cuánto es 5 más 3",
        "10 menos 7",
        "15 entre 3",
        "raíz cuadrada de 16",
        "2 elevado a 3",
        "20 por ciento de 100"
    ]
    
    print("🧮 Pruebas de Calculadora Matemática")
    print("=" * 50)
    
    for prueba in pruebas:
        resultado = procesar_consulta_matematica(prueba)
        print(f"📝 Pregunta: {prueba}")
        print(f"✅ Respuesta: {resultado}")
        print()