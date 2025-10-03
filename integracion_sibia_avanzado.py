#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración del Asistente SIBIA Avanzado con el Proyecto Principal
Este archivo debe ser importado en app_CORREGIDO_OK_FINAL.py
"""

import sys
import os
from flask import Blueprint

# Agregar el directorio del asistente avanzado al path
asistente_path = os.path.join(os.path.dirname(__file__), 'asistente_avanzado')
sys.path.append(asistente_path)

# Importar blueprints del asistente avanzado
from asistente_avanzado.api.routes_chat_avanzado import chat_avanzado_bp
from asistente_avanzado.api.routes_aprendizaje import aprendizaje_bp
from asistente_avanzado.api.routes_formulas import formulas_bp
from asistente_avanzado.api.routes_escenarios_graficos import escenarios_bp, graficos_bp

def registrar_asistente_avanzado(app):
    """Registra todos los blueprints del asistente avanzado en la aplicación Flask"""
    
    # Registrar blueprints con prefijos
    app.register_blueprint(chat_avanzado_bp, url_prefix='/api/sibia/chat')
    app.register_blueprint(aprendizaje_bp, url_prefix='/api/sibia/aprendizaje')
    app.register_blueprint(formulas_bp, url_prefix='/api/sibia/formulas')
    app.register_blueprint(escenarios_bp, url_prefix='/api/sibia/escenarios')
    app.register_blueprint(graficos_bp, url_prefix='/api/sibia/graficos')
    
    print("✅ Asistente SIBIA Avanzado registrado exitosamente")
    print("📡 Endpoints disponibles:")
    print("   - /api/sibia/chat/mensaje")
    print("   - /api/sibia/aprendizaje/corregir")
    print("   - /api/sibia/formulas/calcular/energia")
    print("   - /api/sibia/escenarios/crear")
    print("   - /api/sibia/graficos/comparacion")

def crear_contexto_sibia():
    """Crea el contexto para el asistente SIBIA con datos del proyecto principal"""
    try:
        # Importar funciones del proyecto principal
        from app_CORREGIDO_OK_FINAL import (
            obtener_stock_actual,
            obtener_mezcla_calculada,
            leer_sensor_plc,
            obtener_propiedades_material,
            calcular_kw_material,
            REFERENCIA_MATERIALES
        )
        
        # Importar ToolContext del asistente
        from asistente_avanzado.core.asistente_sibia_definitivo import ToolContext
        
        # Obtener datos actuales
        stock_actual = obtener_stock_actual()
        mezcla_calculada = obtener_mezcla_calculada()
        
        # Crear contexto
        contexto = ToolContext(
            stock_materiales_actual=stock_actual,
            mezcla_diaria_calculada=mezcla_calculada,
            referencia_materiales=REFERENCIA_MATERIALES,
            _obtener_stock_actual_func=obtener_stock_actual,
            _obtener_valor_sensor_func=leer_sensor_plc,
            _obtener_propiedades_material_func=obtener_propiedades_material,
            _calcular_kw_material_func=calcular_kw_material
        )
        
        return contexto
        
    except ImportError as e:
        print(f"⚠️  No se pudieron importar todas las funciones del proyecto principal: {e}")
        # Crear contexto básico
        from asistente_avanzado.core.asistente_sibia_definitivo import ToolContext
        return ToolContext()
    except Exception as e:
        print(f"❌ Error creando contexto SIBIA: {e}")
        return None

def obtener_asistente_sibia():
    """Obtiene la instancia del asistente SIBIA"""
    try:
        from asistente_avanzado.core.asistente_sibia_definitivo import asistente_sibia_definitivo
        return asistente_sibia_definitivo
    except Exception as e:
        print(f"❌ Error obteniendo asistente SIBIA: {e}")
        return None

# Función de prueba para verificar la integración
def probar_integracion():
    """Prueba la integración del asistente avanzado"""
    print("🧪 Probando integración del Asistente SIBIA Avanzado...")
    
    try:
        # Obtener asistente
        asistente = obtener_asistente_sibia()
        if not asistente:
            print("❌ No se pudo obtener el asistente")
            return False
        
        # Crear contexto
        contexto = crear_contexto_sibia()
        
        # Probar pregunta simple
        resultado = asistente.procesar_pregunta("Hola, ¿qué es SIBIA?", contexto)
        
        print(f"✅ Prueba exitosa:")
        print(f"   Motor: {resultado['motor']}")
        print(f"   Confianza: {resultado['confianza']:.0%}")
        print(f"   Latencia: {resultado['latencia_ms']:.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

if __name__ == "__main__":
    # Ejecutar prueba si se ejecuta directamente
    probar_integracion()
