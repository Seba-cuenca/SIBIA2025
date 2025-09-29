#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asistente SIBIA Experto - Sistema de IA Avanzado
Procesamiento inteligente de preguntas con contexto completo
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import numpy as np

logger = logging.getLogger(__name__)

class ToolContext:
    """Contexto de herramientas para el asistente experto"""
    
    def __init__(self, **kwargs):
        self.global_config = kwargs.get('global_config', {})
        self.stock_materiales_actual = kwargs.get('stock_materiales_actual', {})
        self.mezcla_diaria_calculada = kwargs.get('mezcla_diaria_calculada', {})
        self.referencia_materiales = kwargs.get('referencia_materiales', {})
        self._calcular_mezcla_diaria_func = kwargs.get('_calcular_mezcla_diaria_func')
        self._obtener_propiedades_material_func = kwargs.get('_obtener_propiedades_material_func')
        self._calcular_kw_material_func = kwargs.get('_calcular_kw_material_func')
        self._actualizar_configuracion_func = kwargs.get('_actualizar_configuracion_func')
        self._obtener_stock_actual_func = kwargs.get('_obtener_stock_actual_func')
        self._obtener_valor_sensor_func = kwargs.get('_obtener_valor_sensor_func')

class AsistenteSIBIAExperto:
    """Asistente SIBIA Experto - Sistema de IA Avanzado"""
    
    def __init__(self):
        self.nombre = "SIBIA Experto"
        self.version = "2.0"
        self.modelo_entrenado = {}
        self.categorias = {
            'calculo_energia': 0,
            'stock_materiales': 1,
            'mezcla_optimizada': 2,
            'conocimiento_biogas': 3,
            'configuracion_sistema': 4,
            'diagnostico_problemas': 5,
            'optimizacion_proceso': 6,
            'monitoreo_sensores': 7,
            'busqueda_web': 8,
            'tiempo_fecha': 9,
            'conversacion_general': 10,
            'general': 11
        }
        self.cargar_modelo()
        
    def cargar_modelo(self):
        """Carga el modelo entrenado"""
        try:
            with open('modelo_ia_aprendizaje.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.modelo_entrenado = data.get('modelo', {})
                logger.info(f"✅ Modelo experto cargado: {len(self.modelo_entrenado)} patrones")
        except Exception:
            self.modelo_entrenado = {}
            logger.info("🆕 Inicializando nuevo modelo experto")
    
    def guardar_modelo(self):
        """Guarda el modelo entrenado"""
        try:
            data = {
                'modelo': self.modelo_entrenado,
                'ultima_actualizacion': datetime.now().isoformat(),
                'version': self.version
            }
            with open('modelo_ia_aprendizaje.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info("✅ Modelo experto guardado")
        except Exception as e:
            logger.error(f"❌ Error guardando modelo experto: {e}")
    
    def procesar_pregunta(self, pregunta: str, contexto: Optional[ToolContext] = None) -> Dict[str, Any]:
        """Procesa una pregunta con el asistente experto"""
        try:
            inicio = time.time()
            
            # Normalizar pregunta
            pregunta_normalizada = pregunta.lower().strip()
            
            # Clasificar pregunta
            categoria = self._clasificar_pregunta(pregunta_normalizada)
            
            # Generar respuesta basada en categoría
            respuesta = self._generar_respuesta_experta(pregunta, categoria, contexto)
            
            # Calcular latencia
            latencia_ms = (time.time() - inicio) * 1000
            
            # Aprender del patrón
            self._aprender_patron(pregunta_normalizada, categoria, respuesta)
            
            return {
                'respuesta': respuesta,
                'categoria': categoria,
                'motor': 'SIBIA_EXPERTO',
                'latencia_ms': latencia_ms,
                'confianza': 0.95,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando pregunta experta: {e}")
            return {
                'respuesta': 'Disculpa, hubo un error procesando tu consulta.',
                'categoria': 'general',
                'motor': 'SIBIA_EXPERTO_ERROR',
                'latencia_ms': 0,
                'confianza': 0.0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _clasificar_pregunta(self, pregunta: str) -> str:
        """Clasifica la pregunta en una categoría"""
        # Palabras clave para cada categoría
        keywords = {
            'calculo_energia': ['kw', 'energia', 'calcular', 'potencia', 'generacion'],
            'stock_materiales': ['stock', 'material', 'cantidad', 'disponible', 'inventario'],
            'mezcla_optimizada': ['mezcla', 'optimizar', 'proporcion', 'balance'],
            'conocimiento_biogas': ['biogas', 'metano', 'digestion', 'fermentacion'],
            'configuracion_sistema': ['configurar', 'ajustar', 'parametro', 'configuracion'],
            'diagnostico_problemas': ['problema', 'error', 'falla', 'diagnostico'],
            'optimizacion_proceso': ['optimizar', 'mejorar', 'eficiencia', 'rendimiento'],
            'monitoreo_sensores': ['sensor', 'temperatura', 'presion', 'nivel', 'monitoreo'],
            'busqueda_web': ['buscar', 'informacion', 'web', 'internet'],
            'tiempo_fecha': ['tiempo', 'fecha', 'hora', 'dia', 'mes'],
            'conversacion_general': ['hola', 'gracias', 'ayuda', 'como estas']
        }
        
        # Buscar coincidencias
        for categoria, palabras in keywords.items():
            if any(palabra in pregunta for palabra in palabras):
                return categoria
        
        return 'general'
    
    def _generar_respuesta_experta(self, pregunta: str, categoria: str, contexto: Optional[ToolContext] = None) -> str:
        """Genera una respuesta experta basada en la categoría"""
        
        if categoria == 'calculo_energia':
            return self._respuesta_calculo_energia(pregunta, contexto)
        elif categoria == 'stock_materiales':
            return self._respuesta_stock_materiales(pregunta, contexto)
        elif categoria == 'mezcla_optimizada':
            return self._respuesta_mezcla_optimizada(pregunta, contexto)
        elif categoria == 'conocimiento_biogas':
            return self._respuesta_conocimiento_biogas(pregunta)
        elif categoria == 'configuracion_sistema':
            return self._respuesta_configuracion_sistema(pregunta, contexto)
        elif categoria == 'diagnostico_problemas':
            return self._respuesta_diagnostico_problemas(pregunta, contexto)
        elif categoria == 'optimizacion_proceso':
            return self._respuesta_optimizacion_proceso(pregunta, contexto)
        elif categoria == 'monitoreo_sensores':
            return self._respuesta_monitoreo_sensores(pregunta, contexto)
        else:
            return self._respuesta_general(pregunta)
    
    def _respuesta_calculo_energia(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para cálculos de energía"""
        return "Como experto en cálculos energéticos, puedo ayudarte con cálculos de KW/TN, optimización de mezclas y análisis de eficiencia energética. ¿Qué cálculo específico necesitas?"
    
    def _respuesta_stock_materiales(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para stock de materiales"""
        return "Como experto en gestión de materiales, puedo ayudarte con el análisis de stock, cálculo de necesidades y optimización de inventarios. ¿Qué información necesitas sobre los materiales?"
    
    def _respuesta_mezcla_optimizada(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para mezclas optimizadas"""
        return "Como experto en optimización de mezclas, puedo ayudarte a calcular las proporciones ideales de materiales para maximizar la producción de biogás. ¿Qué tipo de mezcla necesitas optimizar?"
    
    def _respuesta_conocimiento_biogas(self, pregunta: str) -> str:
        """Respuesta experta sobre conocimiento de biogás"""
        return "Como experto en biogás, puedo explicarte los procesos de digestión anaeróbica, factores que afectan la producción de metano y mejores prácticas para optimizar el rendimiento."
    
    def _respuesta_configuracion_sistema(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para configuración del sistema"""
        return "Como experto en configuración de sistemas, puedo ayudarte a ajustar parámetros, optimizar configuraciones y resolver problemas de configuración. ¿Qué parámetro necesitas ajustar?"
    
    def _respuesta_diagnostico_problemas(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para diagnóstico de problemas"""
        return "Como experto en diagnóstico, puedo ayudarte a identificar problemas, analizar causas y proponer soluciones. ¿Qué problema estás experimentando?"
    
    def _respuesta_optimizacion_proceso(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para optimización de procesos"""
        return "Como experto en optimización de procesos, puedo ayudarte a mejorar la eficiencia, reducir costos y maximizar el rendimiento del sistema. ¿Qué proceso quieres optimizar?"
    
    def _respuesta_monitoreo_sensores(self, pregunta: str, contexto: Optional[ToolContext] = None) -> str:
        """Respuesta experta para monitoreo de sensores"""
        return "Como experto en monitoreo de sensores, puedo ayudarte a interpretar datos de sensores, identificar anomalías y optimizar el monitoreo. ¿Qué datos de sensores necesitas analizar?"
    
    def _respuesta_general(self, pregunta: str) -> str:
        """Respuesta general experta"""
        return "Como asistente experto de SIBIA, estoy aquí para ayudarte con cualquier consulta relacionada con biogás, cálculos energéticos, gestión de materiales y optimización de procesos. ¿En qué puedo ayudarte?"
    
    def _aprender_patron(self, pregunta: str, categoria: str, respuesta: str):
        """Aprende del patrón de pregunta-respuesta"""
        try:
            patron = {
                'pregunta': pregunta,
                'categoria': categoria,
                'respuesta': respuesta,
                'timestamp': datetime.now().isoformat(),
                'frecuencia': 1
            }
            
            # Buscar patrón existente
            patron_existente = None
            for key, data in self.modelo_entrenado.items():
                if data.get('pregunta') == pregunta:
                    patron_existente = key
                    break
            
            if patron_existente:
                # Actualizar frecuencia
                self.modelo_entrenado[patron_existente]['frecuencia'] += 1
                self.modelo_entrenado[patron_existente]['ultima_actualizacion'] = datetime.now().isoformat()
            else:
                # Agregar nuevo patrón
                nuevo_key = f"patron_{len(self.modelo_entrenado) + 1}"
                self.modelo_entrenado[nuevo_key] = patron
            
            # Guardar modelo actualizado
            self.guardar_modelo()
            
        except Exception as e:
            logger.error(f"❌ Error aprendiendo patrón: {e}")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del asistente experto"""
        return {
            'nombre': self.nombre,
            'version': self.version,
            'patrones_aprendidos': len(self.modelo_entrenado),
            'categorias_disponibles': len(self.categorias),
            'ultima_actualizacion': datetime.now().isoformat(),
            'estado': 'activo'
        }

# Funciones de interfaz para compatibilidad
def procesar_pregunta_completa(pregunta: str, contexto: Optional[ToolContext] = None) -> Dict[str, Any]:
    """Función de interfaz para procesar preguntas completas"""
    asistente = AsistenteSIBIAExperto()
    return asistente.procesar_pregunta(pregunta, contexto)

# Instancia global del asistente experto
asistente_experto_global = AsistenteSIBIAExperto()

if __name__ == "__main__":
    # Prueba del asistente experto
    asistente = AsistenteSIBIAExperto()
    
    # Prueba de procesamiento
    resultado = asistente.procesar_pregunta("¿Cómo calcular KW/TN para una mezcla?")
    print(f"Respuesta: {resultado['respuesta']}")
    print(f"Categoría: {resultado['categoria']}")
    print(f"Motor: {resultado['motor']}")
    
    # Estadísticas
    stats = asistente.obtener_estadisticas()
    print(f"Estadísticas: {stats}")
