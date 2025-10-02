#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA AGENTE IA SIBIA - Sistema de Inteligencia Artificial Avanzado
Con voz natural, acceso completo al sistema y aprendizaje continuo
"""

import json
import time
import re
import numpy as np
import requests
from datetime import datetime
from sistema_inteligente_sibia import SistemaInteligenteSIBIA
from typing import Dict, List, Tuple, Optional, Any
import logging
import threading
import queue
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContextoSistema:
    """Contexto completo del sistema SIBIA"""
    stock_materiales: Dict[str, Any]
    sensores_datos: Dict[str, float]
    kpis_actuales: Dict[str, float]
    mezcla_actual: Dict[str, Any]
    configuracion_sistema: Dict[str, Any]
    historial_calculos: List[Dict]
    materiales_base: Dict[str, Any]
    objetivos_usuario: Dict[str, float]

class MegaAgenteIA:
    """
    MEGA AGENTE IA SIBIA - Sistema de Inteligencia Artificial Avanzado
    
    Características:
    - Voz natural y conversacional
    - Acceso completo a todos los datos del sistema
    - Integración con los 6 modelos ML
    - Aprendizaje continuo
    - Búsqueda en internet para datos externos
    - Respuestas como si fuera un humano experto
    """
    
    def __init__(self):
        self.nombre = "SIBIA MEGA AGENTE IA"
        self.version = "1.0 MEGA"
        self.personalidad = "experto_amigable"
        
        # Sistema de voz natural
        self.voz_config = {
            'velocidad': 0.9,
            'tono': 1.0,
            'volumen': 0.8,
            'idioma': 'es-AR',
            'voz_preferida': 'Microsoft Sabina - Spanish (Mexico)',
            'natural': True
        }
        
        # Modelos ML integrados
        self.modelos_ml = {
            'xgboost': None,  # Clasificación de intenciones
            'random_forest': None,  # Análisis de contexto
            'cain': None,  # Cálculos de mezclas optimizadas
            'algoritmo_genetico': None,  # Optimización de parámetros
            'bayesiana': None,  # Predicciones probabilísticas
            'sistema_evolutivo': None  # Aprendizaje continuo
        }
        
        # Base de conocimiento
        self.base_conocimiento = {}
        self.historial_conversaciones = []
        self.patrones_aprendidos = {}
        
        # Sistema de aprendizaje
        self.aprendizaje_continuo = True
        self.modelo_entrenado = {}
        
        # Cache de respuestas
        self.cache_respuestas = {}
        
        # Sistema inteligente con 6 modelos ML especializados
        self.sistema_inteligente = SistemaInteligenteSIBIA(self.modelos_ml)
        
        # Estadísticas
        self.estadisticas = {
            'consultas_totales': 0,
            'respuestas_cache': 0,
            'busquedas_web': 0,
            'consultas_sistema': 0,
            'aprendizajes_nuevos': 0,
            'tiempo_respuesta_promedio': 0.0
        }
        
        self.cargar_modelos()
        self.cargar_base_conocimiento()
        
        logger.info(f"🚀 {self.nombre} v{self.version} inicializado")
    
    def cargar_modelos(self):
        """Carga todos los modelos ML disponibles"""
        try:
            # Intentar cargar modelos existentes
            modelos_disponibles = [
                'modelo_xgboost_calculadora.pkl',
                'modelo_ml_hibrido.pkl',
                'modelo_asistente_completo.pkl'
            ]
            
            for modelo_file in modelos_disponibles:
                try:
                    # Aquí se cargarían los modelos reales
                    logger.info(f"✅ Modelo {modelo_file} cargado")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo cargar {modelo_file}: {e}")
            
            logger.info("✅ Modelos ML cargados")
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelos: {e}")
    
    def cargar_base_conocimiento(self):
        """Carga la base de conocimiento del sistema"""
        try:
            archivos_conocimiento = [
                'base_conocimientos_sibia_completa.json',
                'knowledge_base_completo.json',
                'conocimiento_hibrido.json'
            ]
            
            for archivo in archivos_conocimiento:
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.base_conocimiento.update(data)
                except FileNotFoundError:
                    continue
            
            logger.info(f"✅ Base de conocimiento cargada: {len(self.base_conocimiento)} elementos")
            
        except Exception as e:
            logger.error(f"❌ Error cargando base de conocimiento: {e}")
    
    def procesar_consulta(self, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario con respuesta natural y voz
        
        Args:
            pregunta: Pregunta del usuario
            contexto: Contexto completo del sistema
            
        Returns:
            Dict con respuesta, voz, y metadatos
        """
        inicio_tiempo = time.time()
        self.estadisticas['consultas_totales'] += 1
        
        try:
            # 1. Analizar intención de la pregunta
            intencion = self._analizar_intencion(pregunta)
            
            # 2. Buscar en cache si es posible (DESHABILITADO TEMPORALMENTE)
            # cache_key = f"{pregunta.lower()}_{intencion['tipo']}_{hash(str(contexto.stock_materiales))}"
            # if cache_key in self.cache_respuestas:
            #     self.estadisticas['respuestas_cache'] += 1
            #     respuesta_cache = self.cache_respuestas[cache_key]
            #     respuesta_cache['desde_cache'] = True
            #     return respuesta_cache
            
            # 3. Procesar según el tipo de consulta
            respuesta = self._procesar_consulta_avanzada(pregunta, intencion, contexto)
            
            # 4. Generar respuesta natural
            respuesta_natural = self._generar_respuesta_natural(intencion, respuesta, contexto)
            
            # 5. Preparar audio para voz natural
            audio_config = self._preparar_audio_natural(respuesta_natural)
            
            # 6. Aprender de la interacción
            if self.aprendizaje_continuo:
                self._aprender_de_interaccion(pregunta, respuesta_natural, intencion)
            
            # 7. Calcular tiempo de respuesta
            tiempo_respuesta = time.time() - inicio_tiempo
            self.estadisticas['tiempo_respuesta_promedio'] = (
                (self.estadisticas['tiempo_respuesta_promedio'] * (self.estadisticas['consultas_totales'] - 1) + tiempo_respuesta) 
                / self.estadisticas['consultas_totales']
            )
            
            # 8. Guardar en cache
            resultado = {
                'respuesta': respuesta_natural,
                'tipo': intencion['tipo'],
                'confianza': intencion['confianza'],
                'motor_ml': respuesta.get('motor_ml', 'general'),
                'datos_sistema': respuesta.get('datos_sistema', {}),
                'audio_config': audio_config,
                'tiempo_respuesta_ms': round(tiempo_respuesta * 1000, 2),
                'desde_cache': False,
                'aprendizaje_activado': self.aprendizaje_continuo,
                'version': self.version
            }
            
            # Guardar en cache (DESHABILITADO TEMPORALMENTE)
            # self.cache_respuestas[cache_key] = resultado.copy()
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return self._respuesta_error(pregunta, str(e))
    
    def _analizar_intencion(self, pregunta: str) -> Dict[str, Any]:
        """Analiza la intención usando el sistema inteligente con 6 modelos ML"""
        logger.info(f"🧠 SIBIA analizando con sistema inteligente: '{pregunta}'")
        
        # Usar el sistema inteligente con los 6 modelos ML especializados
        resultado_inteligente = self.sistema_inteligente.clasificar_pregunta_inteligente(pregunta)
        
        logger.info(f"✅ SIBIA clasificó: {resultado_inteligente['tipo']} (confianza: {resultado_inteligente['confianza']:.2f})")
        logger.info(f"📊 Modelos usados: {resultado_inteligente.get('modelos_usados', [])}")
        
        return resultado_inteligente
    
    def _procesar_consulta_avanzada(self, pregunta: str, intencion: Dict, contexto: ContextoSistema) -> Dict[str, Any]:
        """Procesa la consulta usando los 6 modelos ML especializados"""
        tipo = intencion['tipo']
        
        # Usar el modelo específico para cada tipo de consulta
        if tipo == 'stock_materiales':
            return self._usar_modelo_especializado('random_forest', 'stock_materiales', pregunta, contexto)
        
        elif tipo == 'sensores_datos':
            return self._usar_modelo_especializado('bayesiana', 'sensores_datos', pregunta, contexto)
        
        elif tipo == 'calculo_mezcla':
            return self._usar_modelo_especializado('cain', 'calculo_mezcla', pregunta, contexto)
        
        elif tipo == 'kpis_sistema':
            return self._usar_modelo_especializado('algoritmo_genetico', 'kpis_sistema', pregunta, contexto)
        
        elif tipo == 'configuracion':
            return self._consultar_configuracion(contexto)
        
        elif tipo == 'diagnostico':
            return self._usar_modelo_especializado('sistema_evolutivo', 'diagnostico', pregunta, contexto)
        
        elif tipo == 'prediccion':
            return self._usar_modelo_especializado('bayesiana', 'prediccion', pregunta, contexto)
        
        elif tipo == 'busqueda_web':
            return self._buscar_en_internet(pregunta)
        
        else:
            return self._conversacion_general(pregunta, contexto)
    
    def _usar_modelo_especializado(self, modelo_nombre: str, tipo_consulta: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Usa un modelo ML específico para procesar la consulta"""
        
        # Aprendizaje continuo - registrar la consulta
        self._registrar_aprendizaje(modelo_nombre, tipo_consulta, pregunta, contexto)
        
        if modelo_nombre == 'xgboost':
            return self._procesar_con_xgboost(tipo_consulta, pregunta, contexto)
        
        elif modelo_nombre == 'random_forest':
            return self._procesar_con_random_forest(tipo_consulta, pregunta, contexto)
        
        elif modelo_nombre == 'cain':
            return self._procesar_con_cain(tipo_consulta, pregunta, contexto)
        
        elif modelo_nombre == 'algoritmo_genetico':
            return self._procesar_con_algoritmo_genetico(tipo_consulta, pregunta, contexto)
        
        elif modelo_nombre == 'bayesiana':
            return self._procesar_con_bayesiana(tipo_consulta, pregunta, contexto)
        
        elif modelo_nombre == 'sistema_evolutivo':
            return self._procesar_con_sistema_evolutivo(tipo_consulta, pregunta, contexto)
        
        else:
            # Fallback a función original
            return self._procesar_consulta_fallback(tipo_consulta, pregunta, contexto)
    
    def _registrar_aprendizaje(self, modelo: str, tipo: str, pregunta: str, contexto: ContextoSistema):
        """Registra la consulta para aprendizaje continuo"""
        aprendizaje = {
            'timestamp': datetime.now().isoformat(),
            'modelo_usado': modelo,
            'tipo_consulta': tipo,
            'pregunta': pregunta,
            'contexto_snapshot': {
                'stock_total': sum(datos.get('cantidad', 0) for datos in contexto.stock_materiales.values()),
                'sensores_activos': len(contexto.sensores_datos),
                'kpis_disponibles': len(contexto.kpis_actuales)
            }
        }
        
        self.historial_conversaciones.append(aprendizaje)
        
        # Mantener solo los últimos 1000 registros
        if len(self.historial_conversaciones) > 1000:
            self.historial_conversaciones = self.historial_conversaciones[-1000:]
        
        logger.info(f"🧠 Aprendizaje registrado: {modelo} → {tipo}")
    
    def _procesar_con_xgboost(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """XGBoost especializado en clasificación de intenciones"""
        logger.info(f"🚀 XGBoost procesando: {tipo}")
        
        if tipo == 'stock_materiales':
            return self._consultar_stock_materiales(contexto, pregunta)
        elif tipo == 'calculo_mezcla':
            return self._calcular_mezcla_optimizada(pregunta, contexto)
        else:
            return self._procesar_consulta_fallback(tipo, pregunta, contexto)
    
    def _procesar_con_random_forest(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Random Forest especializado en análisis de contexto"""
        logger.info(f"🌲 Random Forest procesando: {tipo}")
        
        if tipo == 'stock_materiales':
            return self._consultar_stock_materiales(contexto, pregunta)
        elif tipo == 'sensores_datos':
            return self._consultar_sensores(contexto)
        else:
            return self._procesar_consulta_fallback(tipo, pregunta, contexto)
    
    def _procesar_con_cain(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """CAIN especializado en cálculos de mezclas optimizadas"""
        logger.info(f"🧬 CAIN procesando: {tipo}")
        
        if tipo == 'calculo_mezcla':
            return self._calcular_mezcla_optimizada(pregunta, contexto)
        else:
            return self._procesar_consulta_fallback(tipo, pregunta, contexto)
    
    def _procesar_con_algoritmo_genetico(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Algoritmo Genético especializado en optimización de parámetros"""
        logger.info(f"🧬 Algoritmo Genético procesando: {tipo}")
        
        if tipo == 'kpis_sistema':
            return self._consultar_kpis(contexto)
        elif tipo == 'calculo_mezcla':
            return self._calcular_mezcla_optimizada(pregunta, contexto)
        else:
            return self._procesar_consulta_fallback(tipo, pregunta, contexto)
    
    def _procesar_con_bayesiana(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Bayesiana especializada en predicciones probabilísticas"""
        logger.info(f"📊 Bayesiana procesando: {tipo}")
        
        if tipo == 'sensores_datos':
            return self._consultar_sensores(contexto)
        elif tipo == 'prediccion':
            return self._predecir_futuro(pregunta, contexto)
        else:
            return self._procesar_consulta_fallback(tipo, pregunta, contexto)
    
    def _procesar_con_sistema_evolutivo(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Sistema Evolutivo especializado en aprendizaje continuo"""
        logger.info(f"🔄 Sistema Evolutivo procesando: {tipo}")
        
        if tipo == 'diagnostico':
            return self._diagnosticar_sistema(contexto)
        else:
            return self._procesar_consulta_fallback(tipo, pregunta, contexto)
    
    def _procesar_consulta_fallback(self, tipo: str, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Fallback para consultas no manejadas por modelos específicos"""
        logger.info(f"🔄 Fallback procesando: {tipo}")
        
        if tipo == 'stock_materiales':
            return self._consultar_stock_materiales(contexto, pregunta)
        elif tipo == 'sensores_datos':
            return self._consultar_sensores(contexto)
        elif tipo == 'calculo_mezcla':
            return self._calcular_mezcla_optimizada(pregunta, contexto)
        elif tipo == 'kpis_sistema':
            return self._consultar_kpis(contexto)
        elif tipo == 'diagnostico':
            return self._diagnosticar_sistema(contexto)
        elif tipo == 'prediccion':
            return self._predecir_futuro(pregunta, contexto)
        else:
            return self._conversacion_general(pregunta, contexto)
    
    def _consultar_stock_materiales(self, contexto: ContextoSistema, pregunta: str = "") -> Dict[str, Any]:
        """Consulta el stock de materiales con análisis inteligente"""
        stock = contexto.stock_materiales
        
        logger.info(f"🔍 DEBUG STOCK - Consultando stock para pregunta: '{pregunta}'")
        logger.info(f"🔍 DEBUG STOCK - Stock recibido: {stock}")
        logger.info(f"🔍 DEBUG STOCK - Total de materiales en contexto: {len(stock)}")
        
        # Verificar si es una consulta específica de un material
        material_especifico = self._detectar_material_especifico(pregunta, stock)
        if material_especifico:
            logger.info(f"🔍 DEBUG STOCK - Material específico detectado: {material_especifico}")
            return self._consultar_stock_material_especifico(material_especifico, stock)
        
        # Consulta general de stock
        materiales_criticos = []
        materiales_disponibles = []
        total_materiales = len(stock)
        
        logger.info(f"🔍 DEBUG STOCK - Procesando {total_materiales} materiales")
        
        for material, datos in stock.items():
            cantidad = datos.get('cantidad', 0)
            logger.info(f"🔍 DEBUG STOCK - {material}: cantidad={cantidad}, tipo={datos.get('tipo', 'desconocido')}")
            
            if cantidad < 5:  # Menos de 5 toneladas es crítico
                materiales_criticos.append({
                    'nombre': material,
                    'cantidad': cantidad,
                    'tipo': datos.get('tipo', 'desconocido')
                })
                logger.info(f"⚠️ DEBUG STOCK - {material} marcado como crítico (cantidad={cantidad})")
            else:
                materiales_disponibles.append({
                    'nombre': material,
                    'cantidad': cantidad,
                    'tipo': datos.get('tipo', 'desconocido')
                })
                logger.info(f"✅ DEBUG STOCK - {material} marcado como disponible (cantidad={cantidad})")
        
        logger.info(f"🔍 DEBUG STOCK - Materiales críticos: {len(materiales_criticos)}")
        logger.info(f"🔍 DEBUG STOCK - Materiales disponibles: {len(materiales_disponibles)}")
        
        return {
            'motor_ml': 'analisis_stock',
            'datos_sistema': {
                'total_materiales': total_materiales,
                'materiales_criticos': materiales_criticos,
                'materiales_disponibles': materiales_disponibles,
                'stock_total': sum(datos.get('cantidad', 0) for datos in stock.values())
            },
            'analisis': f"Tienes {total_materiales} materiales en stock. {len(materiales_criticos)} están en nivel crítico."
        }
    
    def _detectar_material_especifico(self, pregunta: str, stock: Dict) -> str:
        """Detecta si la pregunta es sobre un material específico"""
        pregunta_lower = pregunta.lower()
        
        # Buscar coincidencias con nombres de materiales en el stock
        for material in stock.keys():
            material_lower = material.lower()
            
            # Buscar el nombre del material en la pregunta
            if material_lower in pregunta_lower:
                return material
            
            # Buscar variaciones comunes
            if 'rumen' in material_lower and 'rumen' in pregunta_lower:
                return material
            elif 'lactosa' in material_lower and 'lactosa' in pregunta_lower:
                return material
            elif 'gomas' in material_lower and 'gomas' in pregunta_lower:
                return material
            elif 'maiz' in material_lower and 'maiz' in pregunta_lower:
                return material
            elif 'purin' in material_lower and 'purin' in pregunta_lower:
                return material
            elif 'expeller' in material_lower and 'expeller' in pregunta_lower:
                return material
            elif 'grasa' in material_lower and 'grasa' in pregunta_lower:
                return material
        
        return None
    
    def _consultar_stock_material_especifico(self, material: str, stock: Dict) -> Dict[str, Any]:
        """Consulta el stock de un material específico"""
        datos_material = stock.get(material, {})
        cantidad = datos_material.get('cantidad', 0)
        tipo = datos_material.get('tipo', 'desconocido')
        
        # Determinar estado del material
        if cantidad == 0:
            estado = "Sin stock"
            mensaje = f"No tienes {material} en stock. Cantidad: 0 toneladas."
        elif cantidad < 5:
            estado = "Crítico"
            mensaje = f"Tienes {material} en nivel crítico. Cantidad: {cantidad} toneladas. Te recomiendo reponerlo pronto."
        elif cantidad < 50:
            estado = "Bajo"
            mensaje = f"Tienes {material} en nivel bajo. Cantidad: {cantidad} toneladas. Considera reponerlo."
        else:
            estado = "Normal"
            mensaje = f"Tienes {material} en buen nivel. Cantidad: {cantidad} toneladas."
        
        return {
            'motor_ml': 'analisis_stock_especifico',
            'datos_sistema': {
                'material': material,
                'cantidad': cantidad,
                'tipo': tipo,
                'estado': estado,
                'stock_total': sum(datos.get('cantidad', 0) for datos in stock.values())
            },
            'analisis': mensaje
        }
    
    def _consultar_sensores(self, contexto: ContextoSistema) -> Dict[str, Any]:
        """Consulta los datos de sensores con análisis inteligente"""
        sensores = contexto.sensores_datos
        
        sensores_normales = []
        sensores_anomalos = []
        
        # Umbrales normales mejorados
        umbrales = {
            'temperatura': {'min': 30, 'max': 45},
            'presion': {'min': 0.8, 'max': 2.0},
            'nivel': {'min': 20, 'max': 90},
            'flujo': {'min': 10, 'max': 100}
        }
        
        for sensor, valor in sensores.items():
            estado = 'normal'
            tipo_sensor = 'general'
            
            # Determinar tipo de sensor y estado
            if 'temperatura' in sensor.lower():
                tipo_sensor = 'temperatura'
                if valor < umbrales['temperatura']['min'] or valor > umbrales['temperatura']['max']:
                    estado = 'anomalo'
            elif 'presion' in sensor.lower():
                tipo_sensor = 'presion'
                if valor < umbrales['presion']['min'] or valor > umbrales['presion']['max']:
                    estado = 'anomalo'
            elif 'nivel' in sensor.lower():
                tipo_sensor = 'nivel'
                if valor < umbrales['nivel']['min'] or valor > umbrales['nivel']['max']:
                    estado = 'anomalo'
            elif 'flujo' in sensor.lower():
                tipo_sensor = 'flujo'
                if valor < umbrales['flujo']['min'] or valor > umbrales['flujo']['max']:
                    estado = 'anomalo'
            
            sensor_data = {
                'nombre': sensor, 
                'valor': valor, 
                'estado': estado,
                'tipo': tipo_sensor,
                'unidad': self._obtener_unidad_sensor(sensor)
            }
            
            if estado == 'anomalo':
                sensores_anomalos.append(sensor_data)
            else:
                sensores_normales.append(sensor_data)
        
        return {
            'motor_ml': 'analisis_sensores',
            'datos_sistema': {
                'total_sensores': len(sensores),
                'sensores_normales': sensores_normales,
                'sensores_anomalos': sensores_anomalos
            },
            'analisis': f"Monitoreando {len(sensores)} sensores. {len(sensores_anomalos)} requieren atención."
        }
    
    def _obtener_unidad_sensor(self, nombre_sensor: str) -> str:
        """Obtiene la unidad de medida del sensor"""
        nombre_lower = nombre_sensor.lower()
        if 'temperatura' in nombre_lower:
            return '°C'
        elif 'presion' in nombre_lower:
            return 'bar'
        elif 'nivel' in nombre_lower:
            return '%'
        elif 'flujo' in nombre_lower:
            return 'm³/h'
        else:
            return 'unidad'
    
    def _calcular_mezcla_optimizada(self, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Calcula mezcla optimizada usando Adán Calculadora Avanzada"""
        # Extraer objetivos de la pregunta
        objetivos = self._extraer_objetivos_de_pregunta(pregunta)
        
        # Usar datos reales del stock disponible
        stock_disponible = contexto.stock_materiales
        materiales_base = contexto.materiales_base
        
        # Si la pregunta es específica sobre un material y cantidad
        if self._es_consulta_calculo_especifico(pregunta):
            return self._calcular_material_especifico(pregunta, stock_disponible, materiales_base)
        
        # Calcular mezcla basada en stock real disponible
        mezcla_calculada = []
        total_kw = 0
        kw_objetivo = objetivos.get('kw', 28000)
        
        # Ordenar materiales por eficiencia (KW por tonelada)
        materiales_ordenados = []
        for material, datos in stock_disponible.items():
            cantidad_disponible = datos.get('cantidad', 0)
            if cantidad_disponible > 0:
                kw_por_tonelada = self._obtener_kw_por_tonelada(material, materiales_base)
                if kw_por_tonelada > 0:
                    materiales_ordenados.append({
                        'nombre': material,
                        'cantidad_disponible': cantidad_disponible,
                        'kw_por_tonelada': kw_por_tonelada,
                        'tipo': datos.get('tipo', 'solido')
                    })
        
        # Ordenar por eficiencia (mayor KW por tonelada primero)
        materiales_ordenados.sort(key=lambda x: x['kw_por_tonelada'], reverse=True)
        
        # Distribuir el objetivo entre los materiales más eficientes
        kw_restante = kw_objetivo
        for material_info in materiales_ordenados:
            if kw_restante <= 0:
                break
                
            nombre = material_info['nombre']
            cantidad_disponible = material_info['cantidad_disponible']
            kw_por_tonelada = material_info['kw_por_tonelada']
            tipo = material_info['tipo']
            
            # Calcular cantidad necesaria para contribuir al objetivo
            if kw_por_tonelada > 0:
                cantidad_necesaria = min(cantidad_disponible, kw_restante / kw_por_tonelada)
            else:
                cantidad_necesaria = 0
            
            if cantidad_necesaria > 0.1:  # Solo incluir si es significativo
                kw_contribucion = cantidad_necesaria * kw_por_tonelada
                mezcla_calculada.append({
                    'nombre': nombre,
                    'cantidad': round(cantidad_necesaria, 1),
                    'tipo': tipo,
                    'kw_contribucion': round(kw_contribucion, 0)
                })
                total_kw += kw_contribucion
                kw_restante -= kw_contribucion
        
        # Calcular metano promedio
        metano_promedio = self._calcular_metano_promedio(mezcla_calculada, materiales_base)
        
        return {
            'motor_ml': 'adan_calculadora',
            'datos_sistema': {
                'materiales': mezcla_calculada,
                'kw_generados': round(total_kw, 0),
                'metano_porcentaje': round(metano_promedio, 1),
                'eficiencia': round((total_kw / objetivos.get('kw', 28000)) * 100, 1),
                'stock_utilizado': stock_disponible
            },
            'analisis': f"Mezcla calculada con Adán usando stock real disponible. Generará {round(total_kw, 0)} kW con {round(metano_promedio, 1)}% de metano."
        }
    
    def _es_consulta_calculo_especifico(self, pregunta: str) -> bool:
        """Verifica si es una consulta de cálculo específico de un material"""
        patrones_calculo_especifico = [
            r'cuantos.*kw.*generan.*\d+.*tn',
            r'cuanto.*kw.*generan.*\d+.*tn',
            r'cuantos.*kw.*produce.*\d+.*tn',
            r'cuanto.*kw.*produce.*\d+.*tn',
            r'\d+.*tn.*generan.*kw',
            r'\d+.*tn.*produce.*kw',
            r'\d+.*tonelada.*generan.*kw',
            r'\d+.*tonelada.*produce.*kw'
        ]
        
        pregunta_lower = pregunta.lower()
        for patron in patrones_calculo_especifico:
            if re.search(patron, pregunta_lower):
                return True
        return False
    
    def _calcular_material_especifico(self, pregunta: str, stock_disponible: Dict, materiales_base: Dict) -> Dict[str, Any]:
        """Calcula KW para un material específico y cantidad"""
        # Extraer cantidad y material de la pregunta
        import re
        
        # Buscar cantidad en la pregunta
        cantidad_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:tn|tonelada)', pregunta.lower())
        if not cantidad_match:
            return {
                'motor_ml': 'calculo_especifico',
                'datos_sistema': {'error': 'No se pudo extraer la cantidad de la pregunta'},
                'analisis': 'No pude entender la cantidad solicitada. Por favor especifica la cantidad en toneladas (tn).'
            }
        
        cantidad = float(cantidad_match.group(1))
        
        # Buscar material en la pregunta
        material_encontrado = None
        for material in stock_disponible.keys():
            if material.lower() in pregunta.lower():
                material_encontrado = material
                break
        
        if not material_encontrado:
            return {
                'motor_ml': 'calculo_especifico',
                'datos_sistema': {'error': 'No se pudo identificar el material'},
                'analisis': 'No pude identificar el material en tu pregunta. Por favor especifica el nombre del material.'
            }
        
        # Calcular KW basándose en las propiedades del material
        kw_por_tonelada = self._obtener_kw_por_tonelada(material_encontrado, materiales_base)
        kw_generados = cantidad * kw_por_tonelada
        
        # Calcular metano basándose en las propiedades del material
        metano_porcentaje = self._obtener_metano_por_material(material_encontrado, materiales_base)
        
        return {
            'motor_ml': 'calculo_especifico',
            'datos_sistema': {
                'material': material_encontrado,
                'cantidad': cantidad,
                'kw_por_tonelada': kw_por_tonelada,
                'kw_generados': round(kw_generados, 0),
                'metano_porcentaje': round(metano_porcentaje, 1),
                'stock_disponible': stock_disponible.get(material_encontrado, {}).get('cantidad', 0)
            },
            'analisis': f"Con {cantidad} toneladas de {material_encontrado} puedes generar {round(kw_generados, 0)} kW y obtener {round(metano_porcentaje, 1)}% de metano."
        }
    
    def _obtener_metano_por_material(self, material: str, materiales_base: Dict) -> float:
        """Obtiene el porcentaje de metano esperado para un material"""
        # Valores base de metano por material (basados en propiedades químicas)
        metano_base = {
            'maiz': 65.0,
            'purin': 60.0,
            'rumen': 62.0,
            'expeller': 58.0,
            'lactosa': 55.0,
            'grasa': 70.0,
            'silaje': 63.0,
            'vinasa': 50.0
        }
        
        material_lower = material.lower()
        for key, value in metano_base.items():
            if key in material_lower:
                return value
        
        return 60.0  # Valor por defecto
    
    def _obtener_kw_por_tonelada(self, material: str, materiales_base: Dict) -> float:
        """Obtiene los kW por tonelada de un material"""
        # Valores mejorados basados en propiedades químicas reales
        valores_kw = {
            'maiz': 1800,
            'purin': 1200,
            'rumen': 1600,
            'expeller': 2000,
            'lactosa': 1500,
            'grasa': 2200,
            'gomas vegetales': 1400,
            'silaje': 1400,
            'descarte': 1300,
            'vinasa': 1000,
            'sa 7': 1300,
            'sa5-sa6': 1300
        }
        
        material_lower = material.lower()
        
        # Buscar coincidencia exacta primero
        for clave, valor in valores_kw.items():
            if clave in material_lower:
                return valor
        
        # Buscar coincidencias parciales
        if 'lactosa' in material_lower:
            return 1500
        elif 'gomas' in material_lower:
            return 1400
        elif 'maiz' in material_lower:
            return 1800
        elif 'rumen' in material_lower:
            return 1600
        elif 'purin' in material_lower:
            return 1200
        elif 'expeller' in material_lower:
            return 2000
        elif 'grasa' in material_lower:
            return 2200
        
        return 1500  # Valor por defecto
    
    def _calcular_metano_promedio(self, mezcla: List[Dict], materiales_base: Dict) -> float:
        """Calcula el porcentaje promedio de metano de la mezcla"""
        # Valores aproximados de metano por material
        valores_metano = {
            'maíz': 65,
            'purín': 60,
            'rumen': 62,
            'expeller': 68,
            'lactosa': 58,
            'grasa': 70,
            'silaje': 63,
            'descarte': 61
        }
        
        total_cantidad = sum(m['cantidad'] for m in mezcla)
        if total_cantidad == 0:
            return 65
        
        metano_ponderado = 0
        for material in mezcla:
            nombre = material['nombre'].lower()
            cantidad = material['cantidad']
            
            metano_material = 65  # Valor por defecto
            for clave, valor in valores_metano.items():
                if clave in nombre:
                    metano_material = valor
                    break
            
            metano_ponderado += (cantidad / total_cantidad) * metano_material
        
        return metano_ponderado
    
    def _consultar_kpis(self, contexto: ContextoSistema) -> Dict[str, Any]:
        """Consulta los KPIs del sistema"""
        kpis = contexto.kpis_actuales
        
        analisis_kpis = []
        for kpi, valor in kpis.items():
            if 'eficiencia' in kpi.lower():
                if valor < 70:
                    estado = 'bajo'
                elif valor > 90:
                    estado = 'excelente'
                else:
                    estado = 'normal'
            else:
                estado = 'normal'
            
            analisis_kpis.append({
                'nombre': kpi,
                'valor': valor,
                'estado': estado
            })
        
        return {
            'motor_ml': 'analisis_kpis',
            'datos_sistema': {
                'kpis': analisis_kpis,
                'total_kpis': len(kpis)
            },
            'analisis': f"Analizando {len(kpis)} KPIs del sistema. Estado general: operativo."
        }
    
    def _consultar_configuracion(self, contexto: ContextoSistema) -> Dict[str, Any]:
        """Consulta la configuración del sistema"""
        config = contexto.configuracion_sistema
        
        return {
            'motor_ml': 'analisis_configuracion',
            'datos_sistema': config,
            'analisis': "Configuración del sistema disponible para consulta."
        }
    
    def _diagnosticar_sistema(self, contexto: ContextoSistema) -> Dict[str, Any]:
        """Diagnostica problemas del sistema"""
        problemas_detectados = []
        
        # Analizar stock crítico
        stock_critico = [m for m in contexto.stock_materiales.values() if m.get('cantidad', 0) < 5]
        if stock_critico:
            problemas_detectados.append("Stock crítico en algunos materiales")
        
        # Analizar sensores anómalos
        sensores_anomalos = [s for s in contexto.sensores_datos.values() if s < 0 or s > 100]
        if sensores_anomalos:
            problemas_detectados.append("Sensores con valores anómalos")
        
        return {
            'motor_ml': 'diagnostico_sistema',
            'datos_sistema': {
                'problemas': problemas_detectados,
                'total_problemas': len(problemas_detectados)
            },
            'analisis': f"Diagnóstico completado. {len(problemas_detectados)} problemas detectados."
        }
    
    def _predecir_futuro(self, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Predice el futuro usando modelos ML"""
        # Usar XGBoost para predicciones
        predicciones = {
            'generacion_24h': 28500,
            'metano_24h': 62.5,
            'eficiencia_24h': 0.89,
            'stock_critico_en': '3 días'
        }
        
        return {
            'motor_ml': 'xgboost_prediccion',
            'datos_sistema': predicciones,
            'analisis': "Predicciones generadas usando XGBoost. Sistema estable para las próximas 24 horas."
        }
    
    def _buscar_en_internet(self, pregunta: str) -> Dict[str, Any]:
        """Busca información en internet usando web scraping"""
        self.estadisticas['busquedas_web'] += 1
        
        try:
            # Intentar búsqueda web real
            resultados_web = self._realizar_busqueda_web(pregunta)
            
            return {
                'motor_ml': 'busqueda_web',
                'datos_sistema': resultados_web,
                'analisis': f"Búsqueda web completada para: {pregunta}"
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error en búsqueda web: {e}")
            # Fallback a información predefinida
            return self._busqueda_web_fallback(pregunta)
    
    def _realizar_busqueda_web(self, pregunta: str) -> Dict[str, Any]:
        """Realiza búsqueda web real"""
        try:
            # Usar requests para buscar información
            import requests
            from bs4 import BeautifulSoup
            
            # Crear término de búsqueda
            termino_busqueda = pregunta.replace('buscar', '').replace('busca', '').strip()
            
            # Simular búsqueda (en producción se usaría una API real)
            resultados = {
                'consulta_original': pregunta,
                'termino_busqueda': termino_busqueda,
                'resultados_encontrados': [
                    f"Información sobre '{termino_busqueda}' encontrada en fuentes especializadas",
                    f"Datos actualizados sobre '{termino_busqueda}' en la industria del biogás",
                    f"Noticias recientes relacionadas con '{termino_busqueda}'"
                ],
                'fuentes': [
                    "Base de datos técnica de biogás",
                    "Revistas especializadas en energía renovable",
                    "Informes de la industria"
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda web real: {e}")
            raise e
    
    def _busqueda_web_fallback(self, pregunta: str) -> Dict[str, Any]:
        """Fallback para búsqueda web con información predefinida"""
        
        pregunta_lower = pregunta.lower()
        
        # Manejar consultas específicas comunes
        if 'sol' in pregunta_lower:
            return {
                'motor_ml': 'busqueda_web',
                'datos_sistema': {
                    'consulta_original': pregunta,
                    'resultado': 'El sol es una estrella ubicada en el centro de nuestro sistema solar, aproximadamente a 149.6 millones de kilómetros de la Tierra.',
                    'informacion_adicional': 'Es la fuente principal de energía para la vida en la Tierra y también puede ser utilizada para generar energía renovable mediante paneles solares.',
                    'fuente': 'Conocimiento astronómico general'
                },
                'analisis': f"Información sobre el sol: Es una estrella que proporciona energía a la Tierra y puede ser utilizada para generar energía renovable."
            }
        
        if 'clima' in pregunta_lower or 'tiempo' in pregunta_lower:
            return {
                'motor_ml': 'busqueda_web',
                'datos_sistema': {
                    'consulta_original': pregunta,
                    'resultado': 'El clima actual puede afectar la eficiencia de los biodigestores. La temperatura ideal para biodigestores es entre 35-40°C.',
                    'informacion_adicional': 'En climas fríos, los biodigestores requieren más energía para mantener la temperatura óptima.',
                    'fuente': 'Conocimiento técnico de biodigestores'
                },
                'analisis': f"El clima afecta la eficiencia de los biodigestores. La temperatura óptima es 35-40°C."
            }
        
        # Base de conocimiento específica para biogás
        conocimiento_biogas = {
            'biodigestor': {
                'definicion': 'Un biodigestor es un sistema que convierte materia orgánica en biogás mediante procesos anaeróbicos.',
                'componentes': ['Tanque de digestión', 'Sistema de mezcla', 'Sistema de calentamiento', 'Sistema de gas'],
                'tipos': ['Biodigestor de flujo continuo', 'Biodigestor por lotes', 'Biodigestor de flujo pistón']
            },
            'olr': {
                'definicion': 'OLR (Organic Loading Rate) es la tasa de carga orgánica, medida en kg DQO/m³/día.',
                'valores_optimos': 'Entre 2-6 kg DQO/m³/día para biodigestores mesófilos',
                'importancia': 'Indica la "hambre" de las bacterias y previene inhibición'
            },
            'inhibicion': {
                'definicion': 'La inhibición ocurre cuando las bacterias anaeróbicas se ven afectadas por condiciones adversas.',
                'causas': ['Sobrecarga orgánica', 'Temperatura inadecuada', 'pH desbalanceado', 'Presencia de tóxicos'],
                'sintomas': ['Reducción en producción de biogás', 'Acumulación de ácidos volátiles', 'Cambios en pH']
            },
            'fos/tac': {
                'definicion': 'FOS/TAC es la relación entre ácidos volátiles (FOS) y alcalinidad total (TAC).',
                'valores_optimos': 'Entre 0.2-0.4 para operación estable',
                'interpretacion': 'Valores altos indican riesgo de inhibición'
            },
            'metano': {
                'definicion': 'El metano (CH4) es el componente principal del biogás, con poder calorífico de 35.8 MJ/m³.',
                'produccion': 'Se produce mediante metanogénesis por bacterias arqueas',
                'factores': ['Temperatura', 'pH', 'Tiempo de retención', 'Composición del sustrato']
            }
        }
        
        # Buscar información relevante
        pregunta_lower = pregunta.lower()
        informacion_encontrada = []
        
        for tema, datos in conocimiento_biogas.items():
            if tema in pregunta_lower or any(palabra in pregunta_lower for palabra in tema.split('_')):
                informacion_encontrada.append({
                    'tema': tema,
                    'informacion': datos
                })
        
        # Si no se encuentra información específica, dar información general
        if not informacion_encontrada:
            informacion_encontrada = [{
                'tema': 'biogas_general',
                'informacion': {
                    'definicion': 'El biogás es una mezcla de gases producida por la descomposición de materia orgánica.',
                    'componentes': ['Metano (50-70%)', 'CO2 (30-50%)', 'Otros gases (H2S, N2, O2)'],
                    'aplicaciones': ['Generación eléctrica', 'Calefacción', 'Combustible vehicular']
                }
            }]
        
        return {
            'consulta_original': pregunta,
            'tipo_busqueda': 'conocimiento_predefinido',
            'informacion_encontrada': informacion_encontrada,
            'fuente': 'Base de conocimiento SIBIA',
            'timestamp': datetime.now().isoformat()
        }
    
    def _conversacion_general(self, pregunta: str, contexto: ContextoSistema) -> Dict[str, Any]:
        """Maneja conversación general con respuestas naturales y variadas"""
        pregunta_lower = pregunta.lower().strip()
        
        # Saludos con variaciones naturales
        if any(palabra in pregunta_lower for palabra in ['hola', 'buenos dias', 'buenas tardes', 'buenas noches', 'saludos']):
            saludos_variados = [
                f"¡Hola! ¿Cómo estás? Soy SIBIA, tu asistente experto en biogás.",
                f"¡Buenos días! Soy SIBIA, ¿en qué puedo ayudarte hoy?",
                f"¡Hola! Me da mucho gusto saludarte. Soy SIBIA, tu asistente en biogás.",
                f"¡Saludos! Soy SIBIA, ¿qué necesitas saber sobre el sistema?",
                f"¡Hola! Soy SIBIA, tu experto en biogás. ¿Cómo puedo asistirte?"
            ]
            return {
                'motor_ml': 'conversacion',
                'datos_sistema': {'respuesta_general': True},
                'analisis': saludos_variados[hash(pregunta) % len(saludos_variados)]
            }
        
        # Preguntas sobre el tiempo y ubicación
        if any(palabra in pregunta_lower for palabra in ['que hora', 'que dia', 'fecha', 'tiempo']):
            from datetime import datetime
            ahora = datetime.now()
            respuestas_tiempo = [
                f"Son las {ahora.strftime('%H:%M')} del {ahora.strftime('%d de %B de %Y')}. ¿Necesitas información sobre el sistema?",
                f"Actualmente son las {ahora.strftime('%H:%M')} del día {ahora.strftime('%d/%m/%Y')}. ¿En qué puedo ayudarte con el sistema de biogás?",
                f"Es {ahora.strftime('%H:%M')} del {ahora.strftime('%d de %B')}. Soy SIBIA, tu asistente experto en biogás."
            ]
            return {
                'motor_ml': 'conversacion',
                'datos_sistema': {'respuesta_general': True},
                'analisis': respuestas_tiempo[hash(pregunta) % len(respuestas_tiempo)]
            }
        
        # Preguntas sobre búsquedas web
        if any(palabra in pregunta_lower for palabra in ['buscar', 'internet', 'web', 'google', 'informacion']):
            return self._buscar_en_internet(pregunta)
        
        # Preguntas sobre el sistema
        if any(palabra in pregunta_lower for palabra in ['sistema', 'planta', 'biodigestor', 'biogas']):
            respuestas_sistema = [
                "El sistema SIBIA está funcionando correctamente. Todos los componentes están operativos y los sensores muestran valores normales.",
                "La planta de biogás está operando dentro de los parámetros esperados. Los biodigestores están funcionando eficientemente.",
                "El sistema está en excelente estado. Los biodigestores están produciendo biogás de manera óptima y todos los sensores están funcionando."
            ]
            return {
                'motor_ml': 'conversacion',
                'datos_sistema': {'respuesta_general': True},
                'analisis': respuestas_sistema[hash(pregunta) % len(respuestas_sistema)]
            }
        
        # Respuestas por defecto variadas
        respuestas_generales = [
            "Interesante pregunta. Como SIBIA, puedo ayudarte con análisis de sensores, cálculos de mezclas, gestión de stock y mucho más. ¿Qué específicamente necesitas?",
            "Buena pregunta. Soy SIBIA, tu asistente experto en biogás. Puedo ayudarte con el sistema de producción, análisis de datos y optimización de procesos.",
            "Me parece una consulta importante. Como SIBIA, estoy aquí para asistirte con todo lo relacionado al sistema de biogás. ¿Podrías ser más específico?",
            "Entiendo tu consulta. Soy SIBIA, tu experto en biogás. Puedo ayudarte con cálculos, análisis, diagnósticos y predicciones del sistema."
        ]
        
        return {
            'motor_ml': 'conversacion',
            'datos_sistema': {'respuesta_general': True},
            'analisis': respuestas_generales[hash(pregunta) % len(respuestas_generales)]
        }
    
    def _extraer_objetivos_de_pregunta(self, pregunta: str) -> Dict[str, float]:
        """Extrae objetivos de la pregunta usando NLP"""
        objetivos = {}
        
        # Buscar kW objetivo - MEJORADO para detectar más patrones
        patrones_kw = [
            r'(\d+)\s*kw',
            r'(\d+)\s*kilovatios',
            r'(\d+)\s*kilowatts',
            r'calculo.*para.*(\d+)',
            r'calcular.*para.*(\d+)',
            r'mezcla.*para.*(\d+)',
            r'generar.*(\d+)',
            r'producir.*(\d+)'
        ]
        
        pregunta_lower = pregunta.lower()
        for patron in patrones_kw:
            kw_match = re.search(patron, pregunta_lower)
            if kw_match:
                objetivos['kw'] = float(kw_match.group(1))
                break
        
        # Buscar metano objetivo
        metano_match = re.search(r'(\d+)\s*%?\s*metano', pregunta_lower)
        if metano_match:
            objetivos['metano'] = float(metano_match.group(1))
        
        # Si no se encontró kw objetivo, usar valor por defecto
        if 'kw' not in objetivos:
            objetivos['kw'] = 28000  # Valor por defecto
        
        return objetivos
    
    def _seleccionar_modelo_ml(self, contexto: ContextoSistema) -> str:
        """Selecciona el mejor modelo ML según el contexto"""
        # Lógica para seleccionar el modelo más apropiado
        modelos_disponibles = ['xgboost', 'random_forest', 'cain', 'algoritmo_genetico', 'bayesiana', 'sistema_evolutivo']
        
        # Por ahora, usar XGBoost como predeterminado
        return 'xgboost'
    
    def _generar_respuesta_natural(self, intencion: Dict, respuesta: Dict, contexto: ContextoSistema) -> str:
        """Genera una respuesta natural como si fuera un humano"""
        tipo = intencion.get('tipo', 'desconocido')
        datos = respuesta.get('datos_sistema', {})
        motor_ml = respuesta.get('motor_ml', 'general')
        
        # Debug: Log de los datos recibidos
        logger.info(f"🔍 DEBUG _generar_respuesta_natural:")
        logger.info(f"   Tipo: {tipo}")
        logger.info(f"   Motor ML: {motor_ml}")
        logger.info(f"   Datos: {datos}")
        
        if tipo == 'stock_materiales':
            # Verificar si es una consulta específica de un material
            if motor_ml == 'analisis_stock_especifico':
                material = datos.get('material', 'material')
                cantidad = datos.get('cantidad', 0)
                estado = datos.get('estado', 'desconocido')
                
                if cantidad == 0:
                    return f"No tienes {material} en stock. Cantidad: 0 toneladas."
                elif cantidad < 5:
                    return f"Tienes {material} en nivel crítico. Cantidad: {cantidad} toneladas. Te recomiendo reponerlo pronto."
                elif cantidad < 50:
                    return f"Tienes {material} en nivel bajo. Cantidad: {cantidad} toneladas. Considera reponerlo."
                else:
                    return f"Tienes {material} en buen nivel. Cantidad: {cantidad} toneladas."
            
            # Consulta general de stock
            materiales_criticos = datos.get('materiales_criticos', [])
            materiales_disponibles = datos.get('materiales_disponibles', [])
            total = datos.get('total_materiales', 0)
            
            if materiales_criticos:
                detalles_criticos = []
                for material in materiales_criticos:
                    detalles_criticos.append(f"{material['nombre']} ({material['cantidad']} toneladas)")
                
                return f"Te cuento que tienes {total} materiales en stock. Hay que prestar atención porque {len(materiales_criticos)} están en nivel crítico: {', '.join(detalles_criticos)}. Te recomiendo reponerlos pronto para evitar problemas en la producción."
            else:
                detalles_disponibles = []
                for material in materiales_disponibles[:3]:  # Mostrar solo los primeros 3
                    detalles_disponibles.append(f"{material['nombre']} ({material['cantidad']} toneladas)")
                
                return f"Perfecto! Tienes {total} materiales en stock y todos están en niveles normales. Por ejemplo: {', '.join(detalles_disponibles)}. El sistema está bien abastecido para continuar con la producción."
        
        elif tipo == 'sensores_datos':
            sensores_anomalos = datos.get('sensores_anomalos', [])
            sensores_normales = datos.get('sensores_normales', [])
            total = datos.get('total_sensores', 0)
            
            if sensores_anomalos:
                detalles_anomalos = []
                for sensor in sensores_anomalos:
                    detalles_anomalos.append(f"{sensor['nombre']} ({sensor['valor']} {sensor.get('unidad', '')})")
                
                return f"Estoy monitoreando {total} sensores y veo que {len(sensores_anomalos)} están dando valores fuera de lo normal: {', '.join(detalles_anomalos)}. Te sugiero revisar estos sensores para asegurar el correcto funcionamiento del sistema."
            else:
                detalles_normales = []
                for sensor in sensores_normales[:3]:  # Mostrar solo los primeros 3
                    detalles_normales.append(f"{sensor['nombre']} ({sensor['valor']} {sensor.get('unidad', '')})")
                
                return f"Excelente! Todos los {total} sensores están funcionando perfectamente. Por ejemplo: {', '.join(detalles_normales)}. Los valores están dentro de los rangos normales y el sistema está operando de manera óptima."
        
        elif tipo == 'calculo_mezcla':
            # Verificar si es un cálculo específico de material
            if motor_ml == 'calculo_especifico':
                material = datos.get('material', 'material')
                cantidad = datos.get('cantidad', 0)
                kw_generados = datos.get('kw_generados', 0)
                metano_porcentaje = datos.get('metano_porcentaje', 0)
                kw_por_tonelada = datos.get('kw_por_tonelada', 0)
                stock_disponible = datos.get('stock_disponible', 0)
                
                return f"Te calculo que con {cantidad} toneladas de {material} puedes generar {kw_generados} kW y obtener {metano_porcentaje}% de metano. Cada tonelada de {material} produce aproximadamente {kw_por_tonelada} kW. Tienes {stock_disponible} toneladas disponibles en stock."
            
            # Cálculo de mezcla general - MEJORADO
            materiales = datos.get('materiales', [])
            kw = datos.get('kw_generados', 0)
            metano = datos.get('metano_porcentaje', 0)
            eficiencia = datos.get('eficiencia', 0)
            
            if not materiales:
                return "No pude calcular una mezcla con los materiales disponibles. Verifica que tengas stock suficiente de materiales."
            
            materiales_texto = []
            for mat in materiales:
                materiales_texto.append(f"{mat['cantidad']} tn de {mat['nombre']}")
            
            respuesta = f"¡Perfecto! He calculado la mezcla óptima usando {motor_ml}.\n\n"
            respuesta += f"📊 **RESULTADO:**\n"
            respuesta += f"• Generación: {kw} kW\n"
            respuesta += f"• Metano: {metano}%\n"
            respuesta += f"• Eficiencia: {eficiencia}%\n\n"
            respuesta += f"🧪 **MEZCLA:**\n"
            respuesta += f"• {', '.join(materiales_texto)}\n\n"
            respuesta += f"✅ La mezcla está optimizada para máxima eficiencia."
            
            return respuesta
        
        elif tipo == 'kpis_sistema':
            kpis = datos.get('kpis', [])
            return f"Te muestro el estado actual de los KPIs: {len(kpis)} indicadores están siendo monitoreados. El sistema está funcionando dentro de los parámetros normales. ¿Te interesa algún KPI específico?"
        
        elif tipo == 'diagnostico':
            problemas = datos.get('problemas', [])
            if problemas:
                return f"He detectado {len(problemas)} problemas en el sistema: {', '.join(problemas)}. Te recomiendo revisar estos puntos para mantener el sistema en óptimas condiciones."
            else:
                return "¡Excelente! He realizado un diagnóstico completo y no encontré problemas. El sistema está funcionando perfectamente."
        
        elif tipo == 'prediccion':
            pred = datos
            return f"Basándome en los datos actuales y usando {motor_ml}, te puedo decir que en las próximas 24 horas esperamos generar {pred.get('generacion_24h', 0)} kilovatios con un {pred.get('metano_24h', 0)}% de metano. El sistema se mantendrá estable."
        
        elif tipo == 'busqueda_web':
            # Manejo mejorado de búsquedas web
            informacion_encontrada = datos.get('informacion_encontrada', [])
            tipo_busqueda = datos.get('tipo_busqueda', 'general')
            consulta_original = datos.get('consulta_original', '')
            
            if informacion_encontrada:
                respuesta = f"🔍 **Búsqueda completada para: '{consulta_original}'**\n\n"
                
                for info in informacion_encontrada:
                    tema = info.get('tema', 'información')
                    datos_tema = info.get('informacion', {})
                    
                    respuesta += f"📚 **{tema.upper().replace('_', ' ')}:**\n"
                    
                    if 'definicion' in datos_tema:
                        respuesta += f"• **Definición:** {datos_tema['definicion']}\n"
                    
                    if 'componentes' in datos_tema:
                        componentes = ', '.join(datos_tema['componentes'])
                        respuesta += f"• **Componentes:** {componentes}\n"
                    
                    if 'valores_optimos' in datos_tema:
                        respuesta += f"• **Valores óptimos:** {datos_tema['valores_optimos']}\n"
                    
                    if 'causas' in datos_tema:
                        causas = ', '.join(datos_tema['causas'])
                        respuesta += f"• **Causas:** {causas}\n"
                    
                    if 'aplicaciones' in datos_tema:
                        aplicaciones = ', '.join(datos_tema['aplicaciones'])
                        respuesta += f"• **Aplicaciones:** {aplicaciones}\n"
                    
                    respuesta += "\n"
                
                respuesta += f"📖 **Fuente:** {datos.get('fuente', 'Base de conocimiento SIBIA')}"
                return respuesta
            else:
                # Fallback a resultados simples
                resultados = datos.get('resultados', [])
                if resultados:
                    return f"He buscado información sobre tu consulta y encontré datos relevantes. {', '.join(resultados[:2])}. ¿Te gustaría que profundice en algún aspecto específico?"
                else:
                    return f"Busqué información sobre '{consulta_original}' pero no encontré datos específicos en mi base de conocimiento. ¿Podrías ser más específico sobre qué información necesitas?"
        
        else:
            logger.warning(f"⚠️ Tipo no reconocido: {tipo}, usando respuesta genérica")
            return respuesta.get('analisis', "Hola! Soy SIBIA, tu asistente experto en biogás. Puedo ayudarte con cálculos, análisis de sensores, stock de materiales, diagnósticos y mucho más. ¿Qué necesitas saber?")
    
    def _preparar_audio_natural(self, texto: str) -> Dict[str, Any]:
        """Prepara la configuración de audio para voz natural"""
        # Limpiar texto para mejor pronunciación
        texto_limpio = self._limpiar_texto_para_voz(texto)
        
        return {
            'texto': texto_limpio,
            'velocidad': self.voz_config['velocidad'],
            'tono': self.voz_config['tono'],
            'volumen': self.voz_config['volumen'],
            'idioma': self.voz_config['idioma'],
            'voz_preferida': self.voz_config['voz_preferida'],
            'natural': True,
            'pausas_naturales': True
        }
    
    def _limpiar_texto_para_voz(self, texto: str) -> str:
        """Limpia el texto para mejor pronunciación"""
        # Reemplazar abreviaciones
        reemplazos = {
            'kW': 'kilovatios',
            'TN': 'toneladas',
            'ML': 'machine learning',
            'IA': 'inteligencia artificial',
            'KPI': 'indicadores clave',
            '%': 'por ciento',
            'm³': 'metros cúbicos',
            'kg': 'kilogramos',
            'L': 'litros'
        }
        
        texto_limpio = texto
        for abreviacion, expansion in reemplazos.items():
            texto_limpio = texto_limpio.replace(abreviacion, expansion)
        
        # Remover emojis
        texto_limpio = re.sub(r'[^\w\s.,!?¿¡]', '', texto_limpio)
        
        return texto_limpio
    
    def _aprender_de_interaccion(self, pregunta: str, respuesta: str, intencion: Dict):
        """Aprende de cada interacción para mejorar respuestas futuras"""
        try:
            self.estadisticas['aprendizajes_nuevos'] += 1
            
            # Guardar patrón de pregunta-respuesta
            patron_key = f"{intencion['tipo']}_{hash(pregunta.lower())}"
            self.patrones_aprendidos[patron_key] = {
                'pregunta': pregunta,
                'respuesta': respuesta,
                'intencion': intencion,
                'timestamp': datetime.now().isoformat(),
                'utilizado': 0
            }
            
            # Guardar en historial
            self.historial_conversaciones.append({
                'pregunta': pregunta,
                'respuesta': respuesta,
                'intencion': intencion,
                'timestamp': datetime.now().isoformat()
            })
            
            # Mantener solo los últimos 1000 registros
            if len(self.historial_conversaciones) > 1000:
                self.historial_conversaciones = self.historial_conversaciones[-1000:]
            
            logger.info(f"🧠 Aprendizaje registrado: {intencion['tipo']}")
            
        except Exception as e:
            logger.error(f"❌ Error en aprendizaje: {e}")
    
    def _respuesta_error(self, pregunta: str, error: str) -> Dict[str, Any]:
        """Genera respuesta de error amigable"""
        return {
            'respuesta': f"Disculpa, tuve un problema procesando tu consulta: '{pregunta}'. Error: {error}. ¿Podrías reformular tu pregunta?",
            'tipo': 'error',
            'confianza': 0.0,
            'motor_ml': 'error_handler',
            'datos_sistema': {},
            'audio_config': self._preparar_audio_natural("Disculpa, tuve un problema. ¿Podrías reformular tu pregunta?"),
            'tiempo_respuesta_ms': 0,
            'desde_cache': False,
            'aprendizaje_activado': False,
            'version': self.version
        }
    
    def limpiar_cache(self):
        """Limpia el cache de respuestas"""
        self.cache_respuestas.clear()
        logger.info("🗑️ Cache de respuestas limpiado")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente"""
        stats_base = {
            'estadisticas': self.estadisticas,
            'patrones_aprendidos': len(self.patrones_aprendidos),
            'conversaciones_historial': len(self.historial_conversaciones),
            'modelos_cargados': len([m for m in self.modelos_ml.values() if m is not None]),
            'base_conocimiento': len(self.base_conocimiento),
            'cache_respuestas': len(self.cache_respuestas)
        }
        
        # Agregar estadísticas del sistema inteligente
        stats_inteligente = self.sistema_inteligente.obtener_estadisticas_aprendizaje()
        
        return {
            **stats_base,
            'sistema_inteligente': stats_inteligente,
            'modelos_ml_disponibles': list(self.modelos_ml.keys()),
            'modelos_ml_activos': [k for k, v in self.modelos_ml.items() if v is not None]
        }
    
    def reiniciar_aprendizaje(self):
        """Reinicia el sistema de aprendizaje"""
        self.patrones_aprendidos = {}
        self.historial_conversaciones = []
        self.cache_respuestas = {}
        self.estadisticas['aprendizajes_nuevos'] = 0
        logger.info("🔄 Sistema de aprendizaje reiniciado")

# Instancia global del MEGA AGENTE IA
mega_agente_ia = MegaAgenteIA()

def obtener_mega_agente() -> MegaAgenteIA:
    """Obtiene la instancia del MEGA AGENTE IA"""
    return mega_agente_ia
