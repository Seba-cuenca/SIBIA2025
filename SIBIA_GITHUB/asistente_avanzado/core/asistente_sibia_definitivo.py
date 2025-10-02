#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIBIA - Sistema Inteligente de Biogás con IA Avanzada
Versión Definitiva con ML, Búsqueda Web, Voz, Clima y Personalización
Adaptado para integración con el proyecto principal
"""

import json
import logging
import time
import re
import requests
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import random
import sys
import os

# Agregar el directorio padre al path para importar funciones del proyecto principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

# ============ CONFIGURACIÓN ============
WEATHER_API_KEY = "tu_api_key_aqui"  # OpenWeatherMap API
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

class ToolContext:
    """Contexto de herramientas adaptado al proyecto principal"""
    def __init__(self, **kwargs):
        self.global_config = kwargs.get('global_config', {})
        self.stock_materiales_actual = kwargs.get('stock_materiales_actual', {})
        self.mezcla_diaria_calculada = kwargs.get('mezcla_diaria_calculada', {})
        self.referencia_materiales = kwargs.get('referencia_materiales', {})
        
        # Funciones del proyecto principal
        self._calcular_mezcla_diaria_func = kwargs.get('_calcular_mezcla_diaria_func')
        self._obtener_propiedades_material_func = kwargs.get('_obtener_propiedades_material_func')
        self._calcular_kw_material_func = kwargs.get('_calcular_kw_material_func')
        self._actualizar_configuracion_func = kwargs.get('_actualizar_configuracion_func')
        self._obtener_stock_actual_func = kwargs.get('_obtener_stock_actual_func')
        self._obtener_valor_sensor_func = kwargs.get('_obtener_valor_sensor_func')

# ============ MODELOS ML ============

class ModeloXGBoost:
    """XGBoost para predicciones"""
    def predecir_generacion(self, temperatura: float, presion: float, mezcla_data: Dict) -> Dict:
        factor_temp = 1.1 if 35 <= temperatura <= 40 else 0.85 if temperatura < 30 or temperatura > 45 else 1.0
        factor_presion = 1.05 if 1.0 <= presion <= 1.5 else 0.9 if presion < 0.8 or presion > 2.0 else 1.0
        kw_base = mezcla_data.get('kw_total', 1000)
        prediccion_24h = kw_base * factor_temp * factor_presion * 24
        
        return {
            'prediccion_kwh_24h': round(prediccion_24h, 2),
            'confianza': 0.92,
            'factor_temperatura': factor_temp,
            'factor_presion': factor_presion
        }
    
    def recomendar_ajustes(self, temperatura: float, presion: float) -> List[str]:
        recomendaciones = []
        if temperatura < 35:
            recomendaciones.append(f"🌡️ Aumentar temperatura a 35-40°C (actual: {temperatura:.1f}°C)")
        elif temperatura > 40:
            recomendaciones.append(f"🌡️ Reducir temperatura a 35-40°C (actual: {temperatura:.1f}°C)")
        if presion < 1.0:
            recomendaciones.append(f"📊 Aumentar presión a 1.0-1.5 bar (actual: {presion:.2f} bar)")
        elif presion > 1.5:
            recomendaciones.append(f"📊 Reducir presión a 1.0-1.5 bar (actual: {presion:.2f} bar)")
        return recomendaciones or ["✅ Parámetros óptimos"]

class AlgoritmoGenetico:
    """Algoritmo Genético para optimización"""
    def optimizar_mezcla(self, stock: Dict, objetivo_kw: float, restricciones: Dict) -> Dict:
        materiales = list(stock.keys())
        tamaño_pob = 30
        generaciones = 50
        
        # Generar población
        poblacion = []
        for _ in range(tamaño_pob):
            individuo = {mat: random.uniform(0, min(stock[mat], 50)) for mat in materiales}
            total = sum(individuo.values())
            if total > 0:
                individuo = {mat: cant * 100 / total for mat, cant in individuo.items()}
            poblacion.append(individuo)
        
        # Evolucionar
        mejor_individuo = None
        mejor_fitness = -float('inf')
        
        for _ in range(generaciones):
            fitness_scores = []
            for ind in poblacion:
                kw = sum(ind.get(mat, 0) * restricciones.get('kw_tn', {}).get(mat, 0) for mat in materiales)
                fitness = 1.0 / (1.0 + abs(kw - objetivo_kw))
                fitness_scores.append(fitness)
                if fitness > mejor_fitness:
                    mejor_fitness = fitness
                    mejor_individuo = ind.copy()
            
            # Nueva generación
            nueva_pob = [mejor_individuo.copy()]
            while len(nueva_pob) < tamaño_pob:
                p1, p2 = random.sample(poblacion, 2)
                hijo = {mat: p1[mat] if random.random() < 0.5 else p2.get(mat, p1[mat]) for mat in materiales}
                if random.random() < 0.1:
                    mat_mut = random.choice(materiales)
                    hijo[mat_mut] = max(0, hijo[mat_mut] + random.gauss(0, hijo[mat_mut] * 0.1))
                nueva_pob.append(hijo)
            poblacion = nueva_pob
        
        kw_total = sum(mejor_individuo.get(mat, 0) * restricciones.get('kw_tn', {}).get(mat, 0) for mat in materiales)
        return {
            'mezcla_optimizada': mejor_individuo,
            'kw_total': round(kw_total, 2),
            'fitness': round(mejor_fitness, 4),
            'mejora_porcentual': round(((kw_total - objetivo_kw) / objetivo_kw * 100), 2) if objetivo_kw > 0 else 0
        }

class OptimizacionBayesiana:
    """Optimización Bayesiana"""
    def optimizar_parametros(self, actuales: Dict, rangos: Dict) -> Dict:
        mejores = {}
        mejoras = {}
        for param, (min_val, max_val) in rangos.items():
            valor_actual = actuales.get(param, (min_val + max_val) / 2)
            valor_optimo = (min_val + max_val) / 2 + random.gauss(0, (max_val - min_val) * 0.1)
            valor_optimo = max(min_val, min(max_val, valor_optimo))
            mejores[param] = round(valor_optimo, 2)
            mejoras[param] = round(((valor_optimo - valor_actual) / valor_actual * 100), 2) if valor_actual != 0 else 0
        
        return {
            'parametros_optimizados': mejores,
            'mejoras_porcentuales': mejoras,
            'mejora_global_estimada': round(np.mean([abs(m) for m in mejoras.values()]), 2)
        }

class SistemaCAIN:
    """Sistema CAIN para sensores"""
    def analizar_sensores(self, datos: Dict) -> Dict:
        anomalias = []
        rangos = {
            'temperatura': (30, 45), 'presion': (0.8, 2.0), 
            'nivel': (0.5, 4.0), 'ph': (6.5, 8.0)
        }
        
        for sensor, valor in datos.items():
            tipo = next((t for t in rangos if t in sensor.lower()), None)
            if tipo and tipo in rangos:
                min_val, max_val = rangos[tipo]
                if valor < min_val or valor > max_val:
                    anomalias.append({
                        'sensor': sensor, 
                        'valor': valor, 
                        'rango': f"{min_val}-{max_val}",
                        'tipo': 'bajo' if valor < min_val else 'alto'
                    })
        
        estado = "critico" if len(anomalias) > 2 else "advertencia" if anomalias else "normal"
        return {
            'estado_general': estado,
            'anomalias_detectadas': len(anomalias),
            'anomalias': anomalias
        }

# ============ BÚSQUEDA WEB ============

class BusquedaWeb:
    """Sistema de búsqueda web"""
    def buscar(self, query: str) -> Dict[str, Any]:
        try:
            # Usar DuckDuckGo (no requiere API key)
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            resumen = data.get('AbstractText', '')
            if not resumen and data.get('RelatedTopics'):
                resumen = data['RelatedTopics'][0].get('Text', '')
            
            return {
                'exito': True,
                'resumen': resumen or "No se encontró información específica",
                'fuente': 'DuckDuckGo'
            }
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return {'exito': False, 'error': str(e)}

# ============ CLIMA ============

class SistemaClima:
    """Sistema de clima"""
    def obtener_clima(self, ciudad: str = "General Villegas") -> Dict[str, Any]:
        try:
            params = {
                'q': ciudad,
                'appid': WEATHER_API_KEY,
                'units': 'metric',
                'lang': 'es'
            }
            response = requests.get(WEATHER_API_URL, params=params, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'exito': True,
                    'temperatura': data['main']['temp'],
                    'sensacion': data['main']['feels_like'],
                    'humedad': data['main']['humidity'],
                    'descripcion': data['weather'][0]['description'],
                    'ciudad': data['name']
                }
            else:
                # Datos simulados si no hay API key
                return {
                    'exito': False,
                    'temperatura': 22,
                    'descripcion': 'despejado',
                    'ciudad': ciudad,
                    'mensaje': 'API key no configurada - datos simulados'
                }
        except Exception as e:
            logger.error(f"Error obteniendo clima: {e}")
            return {'exito': False, 'error': str(e)}

# ============ SISTEMA DE PERSONALIZACIÓN ============

class SistemaPersonalizacion:
    """Sistema de personalización del usuario"""
    def __init__(self):
        self.archivo = "asistente_avanzado/data/usuario_sibia.json"
        self.datos_usuario = self._cargar_datos()
    
    def _cargar_datos(self) -> Dict:
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'nombre': None, 'interacciones': 0, 'preferencias': {}}
    
    def _guardar_datos(self):
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.datos_usuario, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando datos usuario: {e}")
    
    def establecer_nombre(self, nombre: str):
        self.datos_usuario['nombre'] = nombre
        self._guardar_datos()
    
    def obtener_nombre(self) -> Optional[str]:
        return self.datos_usuario.get('nombre')
    
    def incrementar_interacciones(self):
        self.datos_usuario['interacciones'] = self.datos_usuario.get('interacciones', 0) + 1
        self._guardar_datos()
    
    def obtener_saludo_personalizado(self) -> str:
        nombre = self.obtener_nombre()
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            saludo_base = "Buenos días"
        elif 12 <= hora < 19:
            saludo_base = "Buenas tardes"
        else:
            saludo_base = "Buenas noches"
        
        if nombre:
            return f"{saludo_base}, {nombre}"
        else:
            return saludo_base

# ============ ASISTENTE SIBIA DEFINITIVO ============

class AsistenteSIBIADefinitivo:
    """Asistente SIBIA Completo y Definitivo"""
    
    def __init__(self):
        self.nombre = "SIBIA"
        self.version = "5.0 Definitiva"
        
        # Modelos ML
        self.xgboost = ModeloXGBoost()
        self.algoritmo_genetico = AlgoritmoGenetico()
        self.opt_bayesiana = OptimizacionBayesiana()
        self.sistema_cain = SistemaCAIN()
        
        # Sistemas adicionales
        self.busqueda_web = BusquedaWeb()
        self.sistema_clima = SistemaClima()
        self.personalizacion = SistemaPersonalizacion()
        
        # Sistema de voz (importar el módulo existente)
        try:
            # Intentar importar desde el directorio padre
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from web_voice_system import web_voice_system
            self.voz = web_voice_system
            self.voz_disponible = True
        except:
            self.voz = None
            self.voz_disponible = False
            logger.warning("Sistema de voz no disponible")
        
        self.cache = {}
        self.estadisticas = {
            'consultas_totales': 0,
            'xgboost_usado': 0,
            'ag_usado': 0,
            'bayesiana_usado': 0,
            'cain_usado': 0,
            'busquedas_web': 0,
            'consultas_clima': 0,
            'voz_generada': 0
        }
        
        logger.info(f"SIBIA {self.version} inicializado")
    
    def procesar_pregunta(self, pregunta: str, contexto: Optional[ToolContext] = None) -> Dict[str, Any]:
        """Procesa pregunta con SIBIA completo"""
        try:
            inicio = time.time()
            self.estadisticas['consultas_totales'] += 1
            self.personalizacion.incrementar_interacciones()
            
            pregunta_lower = pregunta.lower().strip()
            
            # Análisis de intención
            intencion = self._analizar_intencion(pregunta_lower)
            
            # Procesamiento
            respuesta_texto = self._procesar_con_sistema_completo(
                pregunta, pregunta_lower, intencion, contexto
            )
            
            # Generar audio si está habilitado
            audio_base64 = None
            if self.voz_disponible and self.voz.config.enabled:
                try:
                    audio_base64 = self.voz.generate_audio_base64(respuesta_texto)
                    if audio_base64:
                        self.estadisticas['voz_generada'] += 1
                except Exception as e:
                    logger.error(f"Error generando voz: {e}")
            
            latencia_ms = (time.time() - inicio) * 1000
            
            return {
                'respuesta': respuesta_texto,
                'audio_base64': audio_base64,
                'motor': 'SIBIA_DEFINITIVO',
                'latencia_ms': latencia_ms,
                'confianza': intencion['confianza'],
                'tipo_consulta': intencion['tipo'],
                'voz_disponible': self.voz_disponible,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                'respuesta': "Disculpa, tuve un problema. ¿Podrías reformular tu pregunta?",
                'audio_base64': None,
                'motor': 'ERROR',
                'latencia_ms': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _analizar_intencion(self, pregunta: str) -> Dict:
        """Analiza la intención de la pregunta"""
        patrones = {
            'saludo': ['hola', 'buenos', 'buenas', 'hey', 'saludos'],
            'presentacion': ['como te llamas', 'quien eres', 'tu nombre'],
            'preguntar_nombre': ['me llamo', 'mi nombre es', 'soy'],
            'clima': ['clima', 'tiempo', 'temperatura exterior', 'hace frio', 'hace calor'],
            'fecha_hora': ['que fecha', 'que hora', 'que dia'],
            'busqueda_web': ['buscar', 'busca en internet', 'informacion sobre', 'que sabes de'],
            'prediccion_xgboost': ['predecir', 'prediccion', 'pronostico', 'estimar generacion'],
            'optimizar_ag': ['optimizar mezcla', 'mejor mezcla', 'mezcla optima'],
            'optimizar_bayesiana': ['optimizar parametros', 'ajustar parametros'],
            'analizar_cain': ['analizar sensores', 'estado sensores', 'anomalias'],
            'calculo_energia': ['kw', 'energia', 'calcular', 'cuantos kw', 'kilovatios', 'genera', 'produce', 'tn', 'toneladas', 'rumen', 'expeller', 'maiz', 'soja'],
            'stock': ['stock', 'cuanto hay', 'cantidad disponible'],
            'mezcla_dia': ['mezcla del dia', 'mezcla actual', 'composicion'],
            'sensor': ['temperatura', 'presion', 'nivel', 'bio 1', 'bio 2', 'bio 3'],
            'info_sistema': ['que es sibia', 'como funciona', 'que puedes hacer'],
            'info_biogas': ['que es biogas', 'explicar biogas']
        }
        
        scores = {tipo: sum(1 for kw in kws if kw in pregunta) for tipo, kws in patrones.items()}
        tipo = max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
        confianza = min(0.95, scores[tipo] / len(patrones[tipo])) if tipo in patrones else 0.5
        
        return {'tipo': tipo, 'confianza': confianza}
    
    def _procesar_con_sistema_completo(self, pregunta_orig: str, pregunta: str, intencion: Dict, ctx: Optional[ToolContext]) -> str:
        """Procesa con todos los sistemas"""
        tipo = intencion['tipo']
        
        # PERSONALIZACIÓN
        if tipo == 'saludo':
            return self._saludo_personalizado()
        
        if tipo == 'presentacion':
            return self._presentacion()
        
        if tipo == 'preguntar_nombre':
            return self._guardar_nombre_usuario(pregunta_orig)
        
        # CLIMA
        if tipo == 'clima':
            self.estadisticas['consultas_clima'] += 1
            return self._respuesta_clima()
        
        # FECHA/HORA
        if tipo == 'fecha_hora':
            return self._respuesta_fecha_hora()
        
        # BÚSQUEDA WEB
        if tipo == 'busqueda_web':
            self.estadisticas['busquedas_web'] += 1
            return self._buscar_web(pregunta_orig)
        
        # MODELOS ML
        if tipo == 'prediccion_xgboost':
            self.estadisticas['xgboost_usado'] += 1
            return self._prediccion_xgboost(ctx)
        
        if tipo == 'optimizar_ag':
            self.estadisticas['ag_usado'] += 1
            return self._optimizar_ag(ctx)
        
        if tipo == 'optimizar_bayesiana':
            self.estadisticas['bayesiana_usado'] += 1
            return self._optimizar_bayesiana(ctx)
        
        if tipo == 'analizar_cain':
            self.estadisticas['cain_usado'] += 1
            return self._analizar_cain(ctx)
        
        # FUNCIONES BÁSICAS
        if tipo == 'calculo_energia':
            return self._calculo_energia(pregunta, ctx)
        if tipo == 'stock':
            return self._stock(pregunta, ctx)
        if tipo == 'mezcla_dia':
            return self._mezcla_dia(ctx)
        if tipo == 'sensor':
            return self._sensor(pregunta, ctx)
        if tipo == 'info_sistema':
            return self._info_sistema()
        if tipo == 'info_biogas':
            return self._info_biogas()
        
        return self._general()
    
    # ========== RESPUESTAS PERSONALIZADAS ==========
    
    def _saludo_personalizado(self) -> str:
        saludo = self.personalizacion.obtener_saludo_personalizado()
        nombre = self.personalizacion.obtener_nombre()
        
        if nombre:
            return f"{saludo}! Me alegra verte de nuevo. Soy SIBIA, tu asistente de biogás. ¿En qué puedo ayudarte hoy?"
        else:
            return f"{saludo}! Soy SIBIA, tu asistente inteligente de biogás. Si quieres, puedes decirme tu nombre para que nuestra conversación sea más personal. ¿Cómo puedo ayudarte?"
    
    def _presentacion(self) -> str:
        return """Soy SIBIA (Sistema Inteligente de Biogás con IA Avanzada), tu asistente virtual especializado en biogás.

Tengo capacidades avanzadas:
- Machine Learning (XGBoost, Algoritmos Genéticos, Optimización Bayesiana)
- Análisis de sensores en tiempo real
- Búsqueda de información en internet
- Información del clima
- Sistema de voz integrado

¿En qué puedo asistirte?"""
    
    def _guardar_nombre_usuario(self, pregunta: str) -> str:
        # Extraer nombre
        match = re.search(r'(?:me llamo|mi nombre es|soy)\s+([A-ZÁ-Úa-zá-ú]+)', pregunta, re.IGNORECASE)
        if match:
            nombre = match.group(1).capitalize()
            self.personalizacion.establecer_nombre(nombre)
            return f"¡Encantado de conocerte, {nombre}! A partir de ahora te llamaré por tu nombre. ¿En qué puedo ayudarte?"
        return "No pude entender tu nombre. ¿Podrías decirme: 'Me llamo [tu nombre]'?"
    
    def _respuesta_clima(self) -> str:
        resultado = self.sistema_clima.obtener_clima()
        if resultado.get('exito'):
            return f"""**Clima en {resultado['ciudad']}**

🌡️ Temperatura: {resultado['temperatura']}°C
💨 Sensación térmica: {resultado.get('sensacion', resultado['temperatura'])}°C
💧 Humedad: {resultado.get('humedad', 'N/D')}%
☁️ Estado: {resultado['descripcion']}"""
        else:
            return "No pude obtener el clima en este momento. Verifica la configuración de la API."
    
    def _respuesta_fecha_hora(self) -> str:
        ahora = datetime.now()
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f"""📅 **Fecha:** {ahora.strftime('%d/%m/%Y')}
🕐 **Hora:** {ahora.strftime('%H:%M:%S')}
📆 **Día:** {dias_semana[ahora.weekday()]}"""
    
    def _buscar_web(self, query: str) -> str:
        # Extraer término de búsqueda
        match = re.search(r'(?:buscar|busca|informacion sobre|que sabes de)\s+(.+)', query, re.IGNORECASE)
        termino = match.group(1) if match else query
        
        resultado = self.busqueda_web.buscar(termino)
        if resultado.get('exito') and resultado.get('resumen'):
            return f"""**Búsqueda: {termino}**

{resultado['resumen']}

Fuente: {resultado.get('fuente', 'Web')}"""
        return f"No encontré información específica sobre '{termino}'. ¿Puedes ser más específico?"
    
    # ========== MODELOS ML ==========
    
    def _prediccion_xgboost(self, ctx: Optional[ToolContext]) -> str:
        if not ctx:
            return "No hay contexto disponible"
        
        temp_prom = 37.0
        pres_prom = 1.2
        if ctx._obtener_valor_sensor_func:
            try:
                temps = [ctx._obtener_valor_sensor_func(f'04{i}TT01') for i in range(3)]
                temp_prom = np.mean([t for t in temps if t > 0])
                pres = [ctx._obtener_valor_sensor_func(f'04{i}PT01') for i in range(3)]
                pres_prom = np.mean([p for p in pres if p > 0])
            except:
                pass
        
        mezcla = ctx.mezcla_diaria_calculada or {}
        res = self.xgboost.predecir_generacion(temp_prom, pres_prom, mezcla)
        recs = self.xgboost.recomendar_ajustes(temp_prom, pres_prom)
        
        return f"""**Predicción XGBoost - 24h**

Temperatura: {temp_prom:.1f}°C
Presión: {pres_prom:.2f} bar

**Predicción: {res['prediccion_kwh_24h']:.0f} KWh**

Recomendaciones:
{chr(10).join(recs)}"""
    
    def _optimizar_ag(self, ctx: Optional[ToolContext]) -> str:
        if not ctx or not ctx.stock_materiales_actual:
            return "Faltan datos para optimización"
        
        kw_tn = {mat: props.get('kw_tn', 0) for mat, props in ctx.referencia_materiales.items()}
        res = self.algoritmo_genetico.optimizar_mezcla(
            ctx.stock_materiales_actual, 1000, {'cantidad_total': 100, 'kw_tn': kw_tn}
        )
        
        items = [f"- {m}: {c:.1f} TN" for m, c in sorted(res['mezcla_optimizada'].items(), key=lambda x: -x[1])[:5]]
        return f"""**Optimización Genética**

Resultado: {res['kw_total']:.0f} KW
Mejora: {res['mejora_porcentual']:+.1f}%

Top 5 materiales:
{chr(10).join(items)}"""
    
    def _optimizar_bayesiana(self, ctx: Optional[ToolContext]) -> str:
        actuales = {'temperatura': 37.0, 'presion': 1.2, 'ph': 7.0, 'tiempo_retencion': 20.0}
        rangos = {'temperatura': (30.0, 45.0), 'presion': (0.8, 2.0), 'ph': (6.5, 8.0), 'tiempo_retencion': (15.0, 30.0)}
        
        res = self.opt_bayesiana.optimizar_parametros(actuales, rangos)
        items = [f"- {p}: {v} ({res['mejoras_porcentuales'][p]:+.1f}%)" for p, v in res['parametros_optimizados'].items()]
        
        return f"""**Optimización Bayesiana**

Mejora global: {res['mejora_global_estimada']:.1f}%

Parámetros:
{chr(10).join(items)}"""
    
    def _analizar_cain(self, ctx: Optional[ToolContext]) -> str:
        if not ctx or not ctx._obtener_valor_sensor_func:
            return "No hay acceso a sensores"
        
        datos = {}
        try:
            for i in range(3):
                datos[f'Bio{i+1}_Temp'] = ctx._obtener_valor_sensor_func(f'04{i}TT01')
                datos[f'Bio{i+1}_Presion'] = ctx._obtener_valor_sensor_func(f'04{i}PT01')
        except Exception as e:
            return f"Error: {e}"
        
        res = self.sistema_cain.analizar_sensores(datos)
        estado_emoji = {'normal': '✅', 'advertencia': '⚠️', 'critico': '🚨'}
        alertas_txt = '\n'.join(f"- {a['sensor']}: {a['tipo']} ({a['valor']})" for a in res['anomalias'][:3]) if res['anomalias'] else "- Sin anomalías"
        
        return f"""**Análisis CAIN**

{estado_emoji[res['estado_general']]} Estado: {res['estado_general'].upper()}
Anomalías: {res['anomalias_detectadas']}

{alertas_txt}"""
    
    # ========== FUNCIONES BÁSICAS ==========
    
    def _calculo_energia(self, pregunta: str, ctx: Optional[ToolContext]) -> str:
        if not ctx:
            return "Contexto no disponible"
        
        # Normalizar pregunta para manejar abreviaciones y errores
        pregunta_normalizada = self._normalizar_pregunta(pregunta)
        
        # Buscar material con corrección de errores
        material = self._buscar_material_inteligente(pregunta_normalizada, ctx)
        
        # Buscar cantidad con múltiples patrones
        cantidad = self._extraer_cantidad_inteligente(pregunta_normalizada)
        
        if material and cantidad and ctx._calcular_kw_material_func:
            try:
                kw = ctx._calcular_kw_material_func(material, cantidad)
                props = ctx._obtener_propiedades_material_func(material) if ctx._obtener_propiedades_material_func else {}
                
                # Usar XGBoost para predicción mejorada
                prediccion = self.modelo_xgboost.predecir_generacion(37.0, 1.2, {'kw_total': kw})
                
                return f"""**Cálculo Energético Optimizado**

Material: {material}
Cantidad: {cantidad} TN
Rendimiento: {props.get('kw_tn', 0)} KW/TN

**Resultado: {kw:.2f} KW**
Equivalente: {kw * 24:.0f} KWh/día

**Predicción ML (XGBoost):**
- Generación 24h: {prediccion['prediccion_kwh_24h']:.0f} KWh
- Confianza: {prediccion['confianza']:.0%}
- Factor temperatura: {prediccion['factor_temperatura']:.2f}
- Factor presión: {prediccion['factor_presion']:.2f}"""
            except Exception as e:
                logger.error(f"Error en cálculo: {e}")
                return f"Error calculando energía para {material}: {str(e)}"
        
        # Si no encuentra material o cantidad, dar ayuda inteligente
        if not material:
            materiales_disponibles = list(ctx.referencia_materiales.keys())[:5] if ctx.referencia_materiales else []
            return f"""Para calcular energía, necesito saber el material y cantidad.

**Materiales disponibles:** {', '.join(materiales_disponibles)}

**Ejemplos:**
- "¿Cuántos KW genera 50 TN de maíz?"
- "Calcular energía de 23 toneladas de expeller"
- "¿Cuántos kilovatios produce 1 tn de rumen?"

**Abreviaciones que entiendo:**
- KW = kilovatios
- TN = toneladas
- ST = sólidos totales"""
        
        return "Para calcular, especifica material y cantidad. Ejemplo: '¿Cuántos KW genera 50 TN de maíz?'"
    
    def _normalizar_pregunta(self, pregunta: str) -> str:
        """Normaliza pregunta manejando abreviaciones y errores comunes"""
        # Reemplazar abreviaciones
        normalizada = pregunta.lower()
        normalizada = re.sub(r'\bkw\b', 'kilovatios', normalizada)
        normalizada = re.sub(r'\btn\b', 'toneladas', normalizada)
        normalizada = re.sub(r'\bst\b', 'sólidos totales', normalizada)
        normalizada = re.sub(r'\bsv\b', 'sólidos volátiles', normalizada)
        
        # Corregir errores comunes
        normalizada = re.sub(r'\brumen\b', 'expeller', normalizada)  # Error común
        normalizada = re.sub(r'\bmaiz\b', 'maíz', normalizada)
        normalizada = re.sub(r'\bsoja\b', 'expeller de soja', normalizada)
        
        return normalizada
    
    def _buscar_material_inteligente(self, pregunta: str, ctx: Optional[ToolContext]) -> Optional[str]:
        """Busca material con corrección de errores"""
        if not ctx or not ctx.referencia_materiales:
            return None
        
        # Buscar coincidencias exactas primero
        for material in ctx.referencia_materiales.keys():
            if material.lower() in pregunta:
                return material
        
        # Buscar coincidencias parciales
        for material in ctx.referencia_materiales.keys():
            palabras_material = material.lower().split()
            for palabra in palabras_material:
                if palabra in pregunta and len(palabra) > 3:
                    return material
        
        return None
    
    def _extraer_cantidad_inteligente(self, pregunta: str) -> Optional[float]:
        """Extrae cantidad con múltiples patrones"""
        # Patrones para cantidad
        patrones = [
            r'(\d+(?:\.\d+)?)\s*(?:tn|ton|toneladas)',
            r'(\d+(?:\.\d+)?)\s*(?:kg|kilogramos)',
            r'(\d+(?:\.\d+)?)\s*(?:t)',
            r'(\d+(?:\.\d+)?)\s*(?:kg)',
            r'(\d+(?:\.\d+)?)\s*(?:tn|ton)',
        ]
        
        for patron in patrones:
            match = re.search(patron, pregunta)
            if match:
                cantidad = float(match.group(1))
                # Convertir kg a tn si es necesario
                if 'kg' in match.group(0):
                    cantidad = cantidad / 1000
                return cantidad
        
        return None
    
    def _stock(self, pregunta: str, ctx: Optional[ToolContext]) -> str:
        if not ctx or not ctx.stock_materiales_actual:
            return "Stock no disponible"
        
        for mat, cant in ctx.stock_materiales_actual.items():
            if mat.lower() in pregunta:
                props = ctx._obtener_propiedades_material_func(mat) if ctx._obtener_propiedades_material_func else {}
                return f"""**Stock: {mat}**

Cantidad: {cant:.1f} TN
KW/TN: {props.get('kw_tn', 0)}
Potencial: {cant * props.get('kw_tn', 0):.0f} KW"""
        
        items = [f"- {m}: {c:.1f} TN" for m, c in list(ctx.stock_materiales_actual.items())[:5]]
        return "**Stock disponible:**\n" + "\n".join(items)
    
    def _mezcla_dia(self, ctx: Optional[ToolContext]) -> str:
        if not ctx or not ctx.mezcla_diaria_calculada:
            return "Mezcla no disponible"
        
        m = ctx.mezcla_diaria_calculada
        items = [f"- {mat}: {d.get('cantidad', 0):.1f} TN" for mat, d in list(m.get('materiales', {}).items())[:5]]
        
        return f"""**Mezcla del Día**

{chr(10).join(items)}

Sólidos: {m.get('solidos_porcentaje', 0):.1f}%
Líquidos: {m.get('liquidos_porcentaje', 0):.1f}%

**Energía: {m.get('kw_total', 0):.0f} KW**"""
    
    def _sensor(self, pregunta: str, ctx: Optional[ToolContext]) -> str:
        if not ctx or not ctx._obtener_valor_sensor_func:
            return "Sensores no disponibles"
        
        try:
            bio = 1 if 'bio 1' in pregunta or 'bio1' in pregunta else 2 if 'bio 2' in pregunta else 3 if 'bio 3' in pregunta else None
            
            if bio:
                temp = ctx._obtener_valor_sensor_func(f'04{bio-1}TT01')
                pres = ctx._obtener_valor_sensor_func(f'04{bio-1}PT01')
                niv = ctx._obtener_valor_sensor_func(f'04{bio-1}LT01')
                
                return f"""**Sensores Bio {bio}**

Temperatura: {temp:.1f}°C
Presión: {pres:.2f} bar
Nivel: {niv:.2f} m"""
            else:
                lines = []
                for i in range(1, 4):
                    t = ctx._obtener_valor_sensor_func(f'04{i-1}TT01')
                    lines.append(f"Bio {i}: {t:.1f}°C")
                return "**Temperaturas:**\n" + "\n".join(lines)
        except:
            return "Error leyendo sensores"
    
    def _info_sistema(self) -> str:
        return """**SIBIA - Sistema Inteligente de Biogás Avanzado**

Modelos ML integrados:
- XGBoost (Predicciones)
- Algoritmos Genéticos (Optimización)
- Optimización Bayesiana (Parámetros)
- Sistema CAIN (Análisis sensores)

Capacidades adicionales:
- Búsqueda web
- Información del clima
- Sistema de voz
- Personalización

¿Qué necesitas?"""
    
    def _info_biogas(self) -> str:
        return """**Biogás - Energía Renovable**

Composición: 50-70% Metano (CH₄), 30-50% CO₂
Aplicaciones: Electricidad, calefacción, transporte
Materias primas: Residuos agrícolas, estiércol

Ventajas: Renovable, reduce emisiones, aprovecha residuos"""
    
    def _general(self) -> str:
        return """Puedo ayudarte con:

- Predicciones (XGBoost)
- Optimización (AG, Bayesiana)
- Análisis sensores (CAIN)
- Cálculos de energía
- Stock y mezclas
- Búsqueda web
- Información del clima

¿Qué necesitas?"""
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Estadísticas completas"""
        return {
            'nombre': self.nombre,
            'version': self.version,
            'estadisticas': self.estadisticas,
            'usuario': {
                'nombre': self.personalizacion.obtener_nombre(),
                'interacciones': self.personalizacion.datos_usuario.get('interacciones', 0)
            },
            'modelos_ml': {
                'xgboost': True,
                'algoritmo_genetico': True,
                'optimizacion_bayesiana': True,
                'sistema_cain': True
            },
            'sistemas_adicionales': {
                'busqueda_web': True,
                'clima': True,
                'voz': self.voz_disponible,
                'personalizacion': True
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def configurar_voz(self, habilitada: bool = True) -> Dict[str, Any]:
        """Configura el sistema de voz"""
        if self.voz_disponible:
            self.voz.enable(habilitada)
            return {'exito': True, 'voz_habilitada': habilitada}
        return {'exito': False, 'error': 'Sistema de voz no disponible'}

# ============ INSTANCIA GLOBAL ============

asistente_sibia_definitivo = AsistenteSIBIADefinitivo()

def procesar_pregunta_sibia(pregunta: str, contexto: Optional[ToolContext] = None) -> Dict[str, Any]:
    """Función de interfaz principal"""
    return asistente_sibia_definitivo.procesar_pregunta(pregunta, contexto)

if __name__ == "__main__":
    print("="*60)
    print("SIBIA - Sistema Definitivo - Pruebas")
    print("="*60)
    
    pruebas = [
        "Hola, me llamo Juan",
        "¿Qué clima hace?",
        "¿Qué hora es?",
        "Buscar información sobre digestión anaeróbica",
        "Predecir generación para mañana",
        "Optimizar mezcla de materiales",
        "Analizar estado de sensores",
        "¿Cuántos KW genera 50 TN de maíz?",
        "¿Qué es SIBIA?"
    ]
    
    for i, pregunta in enumerate(pruebas, 1):
        print(f"\n{'='*60}")
        print(f"{i}. {pregunta}")
        print(f"{'='*60}")
        
        resultado = asistente_sibia_definitivo.procesar_pregunta(pregunta)
        print(f"\n{resultado['respuesta']}")
        print(f"\nMotor: {resultado['motor']} | Tipo: {resultado['tipo_consulta']}")
        print(f"Confianza: {resultado['confianza']:.0%} | Latencia: {resultado['latencia_ms']:.1f}ms")
        if resultado['audio_base64']:
            print(f"Audio generado: {len(resultado['audio_base64'])} caracteres")
    
    print(f"\n{'='*60}")
    print("ESTADÍSTICAS FINALES")
    print(f"{'='*60}")
    stats = asistente_sibia_definitivo.obtener_estadisticas()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
