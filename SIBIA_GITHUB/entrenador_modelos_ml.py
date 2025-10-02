#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Entrenamiento de Modelos ML para MEGA AGENTE IA
Entrena los modelos con respuestas específicas de la aplicación SIBIA
"""

import json
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb

logger = logging.getLogger(__name__)

class EntrenadorModelosML:
    """
    Entrenador de modelos ML específicos para el MEGA AGENTE IA
    """
    
    def __init__(self):
        self.modelos_entrenados = {}
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='spanish')
        self.datos_entrenamiento = self._cargar_datos_entrenamiento()
        
    def _cargar_datos_entrenamiento(self) -> Dict[str, List[Dict]]:
        """Carga datos de entrenamiento específicos de SIBIA"""
        return {
            'stock_materiales': [
                {
                    'pregunta': '¿Cuánto stock tengo de maíz?',
                    'respuesta': 'Tienes 15.5 toneladas de maíz disponible en stock',
                    'categoria': 'stock_materiales',
                    'datos_contexto': {'material': 'maíz', 'cantidad': 15.5}
                },
                {
                    'pregunta': '¿Qué materiales están en nivel crítico?',
                    'respuesta': 'Los materiales en nivel crítico son purín con 2 toneladas y expeller con 1 tonelada',
                    'categoria': 'stock_materiales',
                    'datos_contexto': {'materiales_criticos': ['purín', 'expeller']}
                },
                {
                    'pregunta': '¿Cuál es mi inventario total?',
                    'respuesta': 'Tu inventario total es de 45.2 toneladas distribuidas en 12 materiales diferentes',
                    'categoria': 'stock_materiales',
                    'datos_contexto': {'total_toneladas': 45.2, 'total_materiales': 12}
                },
                {
                    'pregunta': '¿Tengo suficiente purín para la producción?',
                    'respuesta': 'Tienes 8 toneladas de purín, suficiente para 2 días de producción normal',
                    'categoria': 'stock_materiales',
                    'datos_contexto': {'material': 'purín', 'cantidad': 8, 'dias_produccion': 2}
                },
                {
                    'pregunta': '¿Cuánto rumen queda disponible?',
                    'respuesta': 'Quedan 12 toneladas de rumen disponible en el stock',
                    'categoria': 'stock_materiales',
                    'datos_contexto': {'material': 'rumen', 'cantidad': 12}
                }
            ],
            
            'sensores_datos': [
                {
                    'pregunta': '¿Cómo están los sensores de temperatura?',
                    'respuesta': 'Los sensores de temperatura están funcionando normal, registrando 38°C en el digestor principal',
                    'categoria': 'sensores_datos',
                    'datos_contexto': {'sensor': 'temperatura', 'valor': 38, 'unidad': '°C', 'estado': 'normal'}
                },
                {
                    'pregunta': '¿Qué valor tiene el sensor de presión?',
                    'respuesta': 'El sensor de presión está registrando 1.2 bar, dentro del rango normal de operación',
                    'categoria': 'sensores_datos',
                    'datos_contexto': {'sensor': 'presión', 'valor': 1.2, 'unidad': 'bar', 'estado': 'normal'}
                },
                {
                    'pregunta': '¿Hay algún sensor con problemas?',
                    'respuesta': 'El sensor de nivel del tanque secundario está dando lecturas anómalas, recomiendo revisión',
                    'categoria': 'sensores_datos',
                    'datos_contexto': {'sensor': 'nivel', 'ubicacion': 'tanque secundario', 'estado': 'anomalo'}
                },
                {
                    'pregunta': '¿Cuál es el flujo actual del biogás?',
                    'respuesta': 'El flujo de biogás es de 45 m³/hora, excelente para la producción actual',
                    'categoria': 'sensores_datos',
                    'datos_contexto': {'sensor': 'flujo', 'valor': 45, 'unidad': 'm³/h', 'estado': 'excelente'}
                },
                {
                    'pregunta': '¿Todos los sensores están funcionando bien?',
                    'respuesta': 'Sí, todos los 8 sensores están funcionando correctamente y dentro de parámetros normales',
                    'categoria': 'sensores_datos',
                    'datos_contexto': {'total_sensores': 8, 'estado_general': 'normal'}
                }
            ],
            
            'calculo_mezcla': [
                {
                    'pregunta': '¿Qué mezcla necesito para 28000 kW?',
                    'respuesta': 'Para generar 28000 kW necesitas: 15 toneladas de maíz, 12 toneladas de purín, 8 toneladas de rumen y 5 toneladas de expeller',
                    'categoria': 'calculo_mezcla',
                    'datos_contexto': {'kw_objetivo': 28000, 'mezcla': {'maíz': 15, 'purín': 12, 'rumen': 8, 'expeller': 5}}
                },
                {
                    'pregunta': '¿Cómo optimizo la mezcla para máximo metano?',
                    'respuesta': 'Para máximo metano usa: 20% purín, 30% rumen, 25% maíz y 25% expeller. Esto te dará 65% de metano',
                    'categoria': 'calculo_mezcla',
                    'datos_contexto': {'objetivo': 'maximo_metano', 'porcentajes': {'purín': 20, 'rumen': 30, 'maíz': 25, 'expeller': 25}, 'metano_esperado': 65}
                },
                {
                    'pregunta': '¿Cuál es la mejor mezcla para eficiencia energética?',
                    'respuesta': 'La mezcla más eficiente es: 40% maíz, 25% rumen, 20% purín y 15% expeller. Eficiencia del 89%',
                    'categoria': 'calculo_mezcla',
                    'datos_contexto': {'objetivo': 'eficiencia', 'porcentajes': {'maíz': 40, 'rumen': 25, 'purín': 20, 'expeller': 15}, 'eficiencia': 89}
                },
                {
                    'pregunta': '¿Qué pasa si uso solo materiales sólidos?',
                    'respuesta': 'Usando solo sólidos (maíz y expeller) generarías 22000 kW pero con menor eficiencia. Te recomiendo incluir al menos 30% de líquidos',
                    'categoria': 'calculo_mezcla',
                    'datos_contexto': {'tipo_materiales': 'solo_solidos', 'kw_generados': 22000, 'recomendacion': 'incluir_liquidos'}
                },
                {
                    'pregunta': '¿Cómo calculo la mezcla para modo volumétrico?',
                    'respuesta': 'En modo volumétrico distribuyes: 50% sólidos (maíz y expeller) y 50% líquidos (purín y rumen). Total 40 toneladas',
                    'categoria': 'calculo_mezcla',
                    'datos_contexto': {'modo': 'volumetrico', 'distribucion': {'solidos': 50, 'liquidos': 50}, 'total_toneladas': 40}
                }
            ],
            
            'kpis_sistema': [
                {
                    'pregunta': '¿Cómo están los KPIs del sistema?',
                    'respuesta': 'Los KPIs están excelentes: Generación 28500 kW, Eficiencia 89%, Metano 62%, Consumo 120 kW',
                    'categoria': 'kpis_sistema',
                    'datos_contexto': {'generacion': 28500, 'eficiencia': 89, 'metano': 62, 'consumo': 120, 'estado': 'excelente'}
                },
                {
                    'pregunta': '¿Cuál es la eficiencia actual?',
                    'respuesta': 'La eficiencia actual es del 89%, muy por encima del objetivo del 80%. El sistema está funcionando óptimamente',
                    'categoria': 'kpis_sistema',
                    'datos_contexto': {'eficiencia_actual': 89, 'objetivo': 80, 'estado': 'optimo'}
                },
                {
                    'pregunta': '¿Estoy cumpliendo con la generación objetivo?',
                    'respuesta': 'Sí, estás generando 28500 kW superando el objetivo de 28000 kW. Excelente rendimiento',
                    'categoria': 'kpis_sistema',
                    'datos_contexto': {'generacion_actual': 28500, 'objetivo': 28000, 'cumplimiento': 'superado'}
                },
                {
                    'pregunta': '¿Cómo está la calidad del metano?',
                    'respuesta': 'La calidad del metano es excelente con 62%, dentro del rango óptimo de 60-65%',
                    'categoria': 'kpis_sistema',
                    'datos_contexto': {'calidad_metano': 62, 'rango_optimo': '60-65%', 'estado': 'excelente'}
                },
                {
                    'pregunta': '¿Hay algún KPI que necesite atención?',
                    'respuesta': 'Todos los KPIs están en verde. El sistema está funcionando perfectamente sin problemas',
                    'categoria': 'kpis_sistema',
                    'datos_contexto': {'estado_general': 'verde', 'problemas': 'ninguno'}
                }
            ],
            
            'diagnostico': [
                {
                    'pregunta': '¿Hay algún problema en el sistema?',
                    'respuesta': 'No detecto problemas críticos. Solo recomiendo revisar el stock de purín que está bajo',
                    'categoria': 'diagnostico',
                    'datos_contexto': {'problemas_criticos': 0, 'recomendaciones': ['revisar_stock_purin']}
                },
                {
                    'pregunta': '¿Por qué está baja la eficiencia?',
                    'respuesta': 'La eficiencia está baja por temperatura del digestor a 28°C. Necesitas calentar a 35°C mínimo',
                    'categoria': 'diagnostico',
                    'datos_contexto': {'problema': 'eficiencia_baja', 'causa': 'temperatura_baja', 'solucion': 'calentar_digestor'}
                },
                {
                    'pregunta': '¿Qué está causando el bajo metano?',
                    'respuesta': 'El metano bajo se debe a exceso de purín en la mezcla. Reduce purín al 20% y aumenta maíz al 40%',
                    'categoria': 'diagnostico',
                    'datos_contexto': {'problema': 'metano_bajo', 'causa': 'exceso_purin', 'solucion': 'ajustar_mezcla'}
                },
                {
                    'pregunta': '¿El sistema necesita mantenimiento?',
                    'respuesta': 'El sistema está funcionando bien. Solo recomiendo limpieza de sensores en 2 semanas',
                    'categoria': 'diagnostico',
                    'datos_contexto': {'mantenimiento_critico': False, 'mantenimiento_preventivo': 'limpieza_sensores'}
                },
                {
                    'pregunta': '¿Hay alertas activas?',
                    'respuesta': 'Hay 2 alertas menores: temperatura del tanque auxiliar y nivel de purín bajo. Nada crítico',
                    'categoria': 'diagnostico',
                    'datos_contexto': {'alertas_activas': 2, 'nivel': 'menor', 'tipos': ['temperatura', 'nivel']}
                }
            ],
            
            'prediccion': [
                {
                    'pregunta': '¿Qué va a pasar mañana con la producción?',
                    'respuesta': 'Mañana esperamos generar 29000 kW con 63% de metano. El sistema se mantendrá estable',
                    'categoria': 'prediccion',
                    'datos_contexto': {'periodo': 'mañana', 'kw_predicho': 29000, 'metano_predicho': 63, 'estabilidad': 'estable'}
                },
                {
                    'pregunta': '¿Cuándo necesitaré reponer materiales?',
                    'respuesta': 'Necesitarás reponer purín en 3 días y expeller en 5 días. El resto está bien',
                    'categoria': 'prediccion',
                    'datos_contexto': {'reposiciones': {'purín': 3, 'expeller': 5}, 'otros_materiales': 'ok'}
                },
                {
                    'pregunta': '¿Cómo será la eficiencia la próxima semana?',
                    'respuesta': 'La eficiencia se mantendrá entre 87-91% toda la semana. Pronóstico muy positivo',
                    'categoria': 'prediccion',
                    'datos_contexto': {'periodo': 'semana', 'eficiencia_rango': '87-91%', 'pronostico': 'positivo'}
                },
                {
                    'pregunta': '¿Habrá problemas de temperatura?',
                    'respuesta': 'No, la temperatura se mantendrá estable entre 35-40°C. Condiciones óptimas',
                    'categoria': 'prediccion',
                    'datos_contexto': {'problemas_temperatura': False, 'rango_temperatura': '35-40°C', 'condiciones': 'optimas'}
                },
                {
                    'pregunta': '¿Cuál es la tendencia de producción?',
                    'respuesta': 'La tendencia es ascendente. Esperamos un aumento del 5% en producción la próxima semana',
                    'categoria': 'prediccion',
                    'datos_contexto': {'tendencia': 'ascendente', 'aumento_esperado': '5%', 'periodo': 'semana'}
                }
            ],
            
            'conversacion': [
                {
                    'pregunta': 'Hola SIBIA',
                    'respuesta': '¡Hola! Soy SIBIA, tu asistente experto en biogás. ¿En qué puedo ayudarte hoy?',
                    'categoria': 'conversacion',
                    'datos_contexto': {'tipo': 'saludo', 'personalidad': 'amigable'}
                },
                {
                    'pregunta': '¿Qué puedes hacer?',
                    'respuesta': 'Puedo ayudarte con cálculos de mezclas, análisis de sensores, gestión de stock, diagnósticos del sistema, predicciones y mucho más. ¿Qué necesitas?',
                    'categoria': 'conversacion',
                    'datos_contexto': {'tipo': 'capacidades', 'servicios': ['calculos', 'sensores', 'stock', 'diagnosticos', 'predicciones']}
                },
                {
                    'pregunta': 'Gracias',
                    'respuesta': '¡De nada! Estoy aquí para ayudarte siempre que lo necesites. ¿Hay algo más en lo que pueda asistirte?',
                    'categoria': 'conversacion',
                    'datos_contexto': {'tipo': 'agradecimiento', 'disponibilidad': 'siempre'}
                },
                {
                    'pregunta': '¿Cómo estás?',
                    'respuesta': '¡Muy bien! Mi sistema está funcionando perfectamente y estoy listo para ayudarte con cualquier consulta sobre biogás',
                    'categoria': 'conversacion',
                    'datos_contexto': {'tipo': 'estado', 'funcionamiento': 'perfecto'}
                },
                {
                    'pregunta': '¿Eres inteligente?',
                    'respuesta': 'Sí, uso inteligencia artificial avanzada con 6 modelos de machine learning para darte las mejores respuestas sobre tu sistema de biogás',
                    'categoria': 'conversacion',
                    'datos_contexto': {'tipo': 'capacidad_ia', 'modelos_ml': 6}
                }
            ]
        }
    
    def entrenar_todos_los_modelos(self) -> Dict[str, Any]:
        """Entrena todos los modelos ML con los datos específicos de SIBIA"""
        resultados = {}
        
        try:
            # Preparar datos para entrenamiento
            preguntas = []
            categorias = []
            respuestas = []
            
            for categoria, datos in self.datos_entrenamiento.items():
                for item in datos:
                    preguntas.append(item['pregunta'])
                    categorias.append(item['categoria'])
                    respuestas.append(item['respuesta'])
            
            # Vectorizar preguntas
            X = self.vectorizer.fit_transform(preguntas)
            y = np.array(categorias)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Entrenar XGBoost
            logger.info("🚀 Entrenando modelo XGBoost...")
            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            xgb_model.fit(X_train, y_train)
            xgb_pred = xgb_model.predict(X_test)
            xgb_accuracy = accuracy_score(y_test, xgb_pred)
            
            self.modelos_entrenados['xgboost'] = {
                'modelo': xgb_model,
                'accuracy': xgb_accuracy,
                'categorias': list(set(categorias))
            }
            
            # Entrenar Random Forest
            logger.info("🚀 Entrenando modelo Random Forest...")
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            rf_model.fit(X_train, y_train)
            rf_pred = rf_model.predict(X_test)
            rf_accuracy = accuracy_score(y_test, rf_pred)
            
            self.modelos_entrenados['random_forest'] = {
                'modelo': rf_model,
                'accuracy': rf_accuracy,
                'categorias': list(set(categorias))
            }
            
            # Guardar modelos
            self._guardar_modelos()
            
            resultados = {
                'status': 'success',
                'modelos_entrenados': len(self.modelos_entrenados),
                'total_datos': len(preguntas),
                'categorias': list(set(categorias)),
                'accuracy_xgboost': xgb_accuracy,
                'accuracy_random_forest': rf_accuracy,
                'vectorizer_features': X.shape[1]
            }
            
            logger.info(f"✅ Entrenamiento completado: {len(self.modelos_entrenados)} modelos")
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            resultados = {
                'status': 'error',
                'error': str(e)
            }
        
        return resultados
    
    def _guardar_modelos(self):
        """Guarda los modelos entrenados"""
        try:
            # Guardar modelos
            with open('modelos_mega_agente.pkl', 'wb') as f:
                pickle.dump(self.modelos_entrenados, f)
            
            # Guardar vectorizer
            with open('vectorizer_mega_agente.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            # Guardar datos de entrenamiento
            with open('datos_entrenamiento_mega_agente.json', 'w', encoding='utf-8') as f:
                json.dump(self.datos_entrenamiento, f, indent=4, ensure_ascii=False)
            
            logger.info("✅ Modelos guardados exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error guardando modelos: {e}")
    
    def cargar_modelos_entrenados(self) -> bool:
        """Carga modelos previamente entrenados"""
        try:
            with open('modelos_mega_agente.pkl', 'rb') as f:
                self.modelos_entrenados = pickle.load(f)
            
            with open('vectorizer_mega_agente.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            logger.info(f"✅ Modelos cargados: {len(self.modelos_entrenados)} modelos")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron cargar modelos: {e}")
            return False
    
    def predecir_categoria(self, pregunta: str) -> Dict[str, Any]:
        """Predice la categoría de una pregunta usando los modelos entrenados"""
        try:
            if not self.modelos_entrenados:
                return {'categoria': 'conversacion', 'confianza': 0.5, 'modelo': 'default'}
            
            # Vectorizar pregunta
            X = self.vectorizer.transform([pregunta])
            
            # Usar XGBoost para predicción
            if 'xgboost' in self.modelos_entrenados:
                modelo = self.modelos_entrenados['xgboost']['modelo']
                probabilidades = modelo.predict_proba(X)[0]
                categorias = self.modelos_entrenados['xgboost']['categorias']
                
                # Encontrar la categoría con mayor probabilidad
                max_idx = np.argmax(probabilidades)
                categoria = categorias[max_idx]
                confianza = probabilidades[max_idx]
                
                return {
                    'categoria': categoria,
                    'confianza': float(confianza),
                    'modelo': 'xgboost',
                    'todas_probabilidades': dict(zip(categorias, probabilidades))
                }
            
            return {'categoria': 'conversacion', 'confianza': 0.5, 'modelo': 'fallback'}
            
        except Exception as e:
            logger.error(f"❌ Error en predicción: {e}")
            return {'categoria': 'conversacion', 'confianza': 0.5, 'modelo': 'error'}
    
    def obtener_respuesta_ejemplo(self, categoria: str) -> str:
        """Obtiene una respuesta de ejemplo para una categoría"""
        if categoria in self.datos_entrenamiento and self.datos_entrenamiento[categoria]:
            return self.datos_entrenamiento[categoria][0]['respuesta']
        return "No tengo información específica sobre esa categoría."

# Instancia global del entrenador
entrenador_modelos = EntrenadorModelosML()

def obtener_entrenador() -> EntrenadorModelosML:
    """Obtiene la instancia del entrenador de modelos"""
    return entrenador_modelos
