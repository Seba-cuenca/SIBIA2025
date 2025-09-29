#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo XGBoost para Clasificación de Preguntas del Asistente IA
Reemplaza Random Forest con XGBoost para mejor rendimiento
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import json
import os
from datetime import datetime

# Importaciones de ML
try:
    import xgboost as xgb
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
    XGBOOST_DISPONIBLE = True
except ImportError as e:
    XGBOOST_DISPONIBLE = False
    print(f"⚠️ XGBoost no disponible para clasificación: {e}")

logger = logging.getLogger(__name__)

class ModeloXGBoostClasificacion:
    """Modelo XGBoost para clasificación inteligente de preguntas"""
    
    def __init__(self):
        self.modelo = None
        self.vectorizer = None
        self.categorias = [
            'CALCULO_ENERGIA', 'STOCK_MATERIALES', 'MEZCLA_OPTIMIZADA', 
            'CONOCIMIENTO_BIOGAS', 'CONFIGURACION_SISTEMA', 'DIAGNOSTICO_PROBLEMAS',
            'OPTIMIZACION_PROCESO', 'MONITOREO_SENSORES', 'BUSQUEDA_WEB',
            'TIEMPO_FECHA', 'CONVERSACION_GENERAL', 'GENERAL'
        ]
        self.modelo_entrenado = False
        self.archivo_modelo = 'modelo_xgboost_clasificacion.pkl'
        self.archivo_vectorizer = 'vectorizer_xgboost_clasificacion.pkl'
        
    def _crear_datos_entrenamiento(self) -> Tuple[List[str], List[str]]:
        """Crear datos de entrenamiento para clasificación de preguntas"""
        
        datos_entrenamiento = [
            # Cálculos de energía
            ("calcular mezcla para 30000 kw", "CALCULO_ENERGIA"),
            ("mezcla óptima para 25000 kilovatios", "CALCULO_ENERGIA"),
            ("cuántos kw genera 5 toneladas de purín", "CALCULO_ENERGIA"),
            ("energía de 10 tn de expeller", "CALCULO_ENERGIA"),
            ("calcular kw de 3 tn de maíz", "CALCULO_ENERGIA"),
            ("potencial energético del estiércol", "CALCULO_ENERGIA"),
            ("generación de biogás por material", "CALCULO_ENERGIA"),
            ("eficiencia energética de la mezcla", "CALCULO_ENERGIA"),
            
            # Stock de materiales
            ("cuánto stock hay de purín", "STOCK_MATERIALES"),
            ("stock disponible de expeller", "STOCK_MATERIALES"),
            ("cantidad de maíz en almacén", "STOCK_MATERIALES"),
            ("materiales disponibles", "STOCK_MATERIALES"),
            ("inventario de materiales", "STOCK_MATERIALES"),
            ("qué materiales tengo", "STOCK_MATERIALES"),
            ("stock actual de todos los materiales", "STOCK_MATERIALES"),
            ("cantidad de estiércol disponible", "STOCK_MATERIALES"),
            
            # Mezcla optimizada
            ("mezcla óptima para el día", "MEZCLA_OPTIMIZADA"),
            ("planificar mezcla diaria", "MEZCLA_OPTIMIZADA"),
            ("generar mezcla equilibrada", "MEZCLA_OPTIMIZADA"),
            ("optimizar proporciones de materiales", "MEZCLA_OPTIMIZADA"),
            ("balance ideal sólidos líquidos", "MEZCLA_OPTIMIZADA"),
            ("mezcla recomendada", "MEZCLA_OPTIMIZADA"),
            ("proporción óptima de purín", "MEZCLA_OPTIMIZADA"),
            ("distribución perfecta de materiales", "MEZCLA_OPTIMIZADA"),
            
            # Conocimiento técnico de biogás
            ("qué es un biodigestor", "CONOCIMIENTO_BIOGAS"),
            ("cómo funciona la digestión anaerobia", "CONOCIMIENTO_BIOGAS"),
            ("qué es el biogás", "CONOCIMIENTO_BIOGAS"),
            ("temperatura óptima del biodigestor", "CONOCIMIENTO_BIOGAS"),
            ("ph óptimo para digestión", "CONOCIMIENTO_BIOGAS"),
            ("tiempo de retención hidráulico", "CONOCIMIENTO_BIOGAS"),
            ("proceso de metanogénesis", "CONOCIMIENTO_BIOGAS"),
            ("factores que afectan la producción", "CONOCIMIENTO_BIOGAS"),
            
            # Configuración del sistema
            ("configuración actual de la planta", "CONFIGURACION_SISTEMA"),
            ("parámetros del sistema", "CONFIGURACION_SISTEMA"),
            ("ajustes de configuración", "CONFIGURACION_SISTEMA"),
            ("configurar biodigestor", "CONFIGURACION_SISTEMA"),
            ("parámetros óptimos", "CONFIGURACION_SISTEMA"),
            ("configuración recomendada", "CONFIGURACION_SISTEMA"),
            ("ajustes del sistema", "CONFIGURACION_SISTEMA"),
            ("configuración de sensores", "CONFIGURACION_SISTEMA"),
            
            # Diagnóstico de problemas
            ("diagnosticar problemas del biodigestor", "DIAGNOSTICO_PROBLEMAS"),
            ("por qué baja la producción", "DIAGNOSTICO_PROBLEMAS"),
            ("problemas en la digestión", "DIAGNOSTICO_PROBLEMAS"),
            ("análisis de fallas", "DIAGNOSTICO_PROBLEMAS"),
            ("diagnóstico del sistema", "DIAGNOSTICO_PROBLEMAS"),
            ("identificar problemas", "DIAGNOSTICO_PROBLEMAS"),
            ("análisis de rendimiento", "DIAGNOSTICO_PROBLEMAS"),
            ("detectar anomalías", "DIAGNOSTICO_PROBLEMAS"),
            
            # Optimización del proceso
            ("optimizar proceso de digestión", "OPTIMIZACION_PROCESO"),
            ("mejorar eficiencia del biodigestor", "OPTIMIZACION_PROCESO"),
            ("optimizar producción de biogás", "OPTIMIZACION_PROCESO"),
            ("maximizar generación de energía", "OPTIMIZACION_PROCESO"),
            ("optimizar mezcla de materiales", "OPTIMIZACION_PROCESO"),
            ("mejorar rendimiento", "OPTIMIZACION_PROCESO"),
            ("optimizar parámetros", "OPTIMIZACION_PROCESO"),
            ("aumentar eficiencia", "OPTIMIZACION_PROCESO"),
            
            # Monitoreo de sensores
            ("lecturas de sensores", "MONITOREO_SENSORES"),
            ("datos de temperatura", "MONITOREO_SENSORES"),
            ("valores de ph", "MONITOREO_SENSORES"),
            ("monitoreo en tiempo real", "MONITOREO_SENSORES"),
            ("estado de los sensores", "MONITOREO_SENSORES"),
            ("datos de presión", "MONITOREO_SENSORES"),
            ("lecturas actuales", "MONITOREO_SENSORES"),
            ("monitoreo del sistema", "MONITOREO_SENSORES"),
            
            # Búsqueda web
            ("capital de francia", "BUSQUEDA_WEB"),
            ("clima en buenos aires", "BUSQUEDA_WEB"),
            ("noticias de energía renovable", "BUSQUEDA_WEB"),
            ("últimas noticias", "BUSQUEDA_WEB"),
            ("información del clima", "BUSQUEDA_WEB"),
            ("búsqueda en internet", "BUSQUEDA_WEB"),
            ("información general", "BUSQUEDA_WEB"),
            ("datos externos", "BUSQUEDA_WEB"),
            
            # Tiempo y fecha
            ("qué hora es", "TIEMPO_FECHA"),
            ("fecha actual", "TIEMPO_FECHA"),
            ("día de la semana", "TIEMPO_FECHA"),
            ("hora actual", "TIEMPO_FECHA"),
            ("qué fecha es hoy", "TIEMPO_FECHA"),
            ("día actual", "TIEMPO_FECHA"),
            ("fecha y hora", "TIEMPO_FECHA"),
            ("tiempo actual", "TIEMPO_FECHA"),
            
            # Conversación general
            ("hola", "CONVERSACION_GENERAL"),
            ("cómo estás", "CONVERSACION_GENERAL"),
            ("gracias", "CONVERSACION_GENERAL"),
            ("adiós", "CONVERSACION_GENERAL"),
            ("buenos días", "CONVERSACION_GENERAL"),
            ("quién eres", "CONVERSACION_GENERAL"),
            ("qué haces", "CONVERSACION_GENERAL"),
            ("buenas tardes", "CONVERSACION_GENERAL"),
            
            # General
            ("ayuda", "GENERAL"),
            ("información", "GENERAL"),
            ("qué puedes hacer", "GENERAL"),
            ("capacidades", "GENERAL"),
            ("funciones disponibles", "GENERAL"),
            ("cómo usar el sistema", "GENERAL"),
            ("manual de uso", "GENERAL"),
            ("instrucciones", "GENERAL")
        ]
        
        preguntas = [item[0] for item in datos_entrenamiento]
        categorias = [item[1] for item in datos_entrenamiento]
        
        return preguntas, categorias
    
    def entrenar_modelo(self) -> bool:
        """Entrenar modelo XGBoost para clasificación"""
        if not XGBOOST_DISPONIBLE:
            logger.error("XGBoost no disponible para entrenamiento")
            return False
        
        try:
            logger.info("🚀 Entrenando modelo XGBoost para clasificación de preguntas...")
            
            # Crear datos de entrenamiento
            preguntas, categorias_texto = self._crear_datos_entrenamiento()
            
            logger.info(f"📊 Datos preparados: {len(preguntas)} preguntas, {len(set(categorias_texto))} categorías")
            
            # Crear mapeo de categorías texto -> números
            categorias_unicas = sorted(set(categorias_texto))
            self.categoria_to_num = {cat: i for i, cat in enumerate(categorias_unicas)}
            self.num_to_categoria = {i: cat for cat, i in self.categoria_to_num.items()}
            
            # Convertir categorías texto a números
            categorias_numericas = [self.categoria_to_num[cat] for cat in categorias_texto]
            
            # Crear vectorizador TF-IDF
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                stop_words=None,  # Sin stop words para español
                ngram_range=(1, 3),  # Incluir trigramas para mejor contexto
                min_df=1,
                max_df=0.95
            )
            
            # Vectorizar preguntas
            X = self.vectorizer.fit_transform(preguntas)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, categorias_numericas, test_size=0.2, random_state=42, stratify=categorias_numericas
            )
            
            # Convertir sparse matrices a dense para XGBoost
            X_train = X_train.toarray()
            X_test = X_test.toarray()
            
            # Crear modelo XGBoost
            self.modelo = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='mlogloss',
                early_stopping_rounds=20
            )
            
            # Entrenar modelo
            self.modelo.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False
            )
            
            # Evaluar modelo
            y_pred = self.modelo.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"✅ Modelo XGBoost entrenado exitosamente:")
            logger.info(f"   📊 Precisión: {accuracy:.2%}")
            logger.info(f"   📊 Categorías: {len(set(categorias_texto))}")
            logger.info(f"   📊 Ejemplos entrenamiento: {len(X_train)}")
            logger.info(f"   📊 Ejemplos prueba: {len(X_test)}")
            
            # Guardar modelo y mapeos
            self._guardar_modelo()
            
            self.modelo_entrenado = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo XGBoost: {e}")
            return False
    
    def clasificar_pregunta(self, pregunta: str) -> Tuple[str, float]:
        """
        Clasificar una pregunta usando XGBoost
        
        Returns:
            Tuple[str, float]: (categoria, confianza)
        """
        if not self.modelo_entrenado or not self.modelo or not self.vectorizer:
            return "GENERAL", 0.0
        
        try:
            # Vectorizar pregunta
            X = self.vectorizer.transform([pregunta])
            
            # Convertir a dense array
            X = X.toarray()
            
            # Hacer predicción (devuelve número)
            categoria_num = self.modelo.predict(X)[0]
            
            # Convertir número a categoría texto
            categoria = self.num_to_categoria.get(categoria_num, "GENERAL")
            
            # Obtener probabilidades
            probabilidades = self.modelo.predict_proba(X)[0]
            confianza = max(probabilidades)
            
            return categoria, confianza
            
        except Exception as e:
            logger.error(f"Error clasificando pregunta: {e}")
            return "GENERAL", 0.0
    
    def _guardar_modelo(self):
        """Guardar modelo, vectorizador y mapeos"""
        try:
            if self.modelo and self.vectorizer:
                joblib.dump(self.modelo, self.archivo_modelo)
                joblib.dump(self.vectorizer, self.archivo_vectorizer)
                
                # Guardar mapeos
                mapeos = {
                    'categoria_to_num': self.categoria_to_num,
                    'num_to_categoria': self.num_to_categoria
                }
                joblib.dump(mapeos, 'mapeos_xgboost_clasificacion.pkl')
                
                logger.info(f"💾 Modelo XGBoost guardado: {self.archivo_modelo}")
        except Exception as e:
            logger.error(f"Error guardando modelo: {e}")
    
    def _cargar_modelo(self) -> bool:
        """Cargar modelo, vectorizador y mapeos existentes"""
        try:
            if (os.path.exists(self.archivo_modelo) and 
                os.path.exists(self.archivo_vectorizer) and
                os.path.exists('mapeos_xgboost_clasificacion.pkl')):
                
                self.modelo = joblib.load(self.archivo_modelo)
                self.vectorizer = joblib.load(self.archivo_vectorizer)
                
                # Cargar mapeos
                mapeos = joblib.load('mapeos_xgboost_clasificacion.pkl')
                self.categoria_to_num = mapeos['categoria_to_num']
                self.num_to_categoria = mapeos['num_to_categoria']
                
                self.modelo_entrenado = True
                logger.info("✅ Modelo XGBoost cargado exitosamente")
                return True
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
        return False
    
    def inicializar(self) -> bool:
        """Inicializar modelo (cargar existente o entrenar nuevo)"""
        if not XGBOOST_DISPONIBLE:
            logger.warning("⚠️ XGBoost no disponible - usando clasificación básica")
            return False
        
        # Intentar cargar modelo existente
        if self._cargar_modelo():
            return True
        
        # Si no existe, entrenar nuevo modelo
        logger.info("🆕 No se encontró modelo existente, entrenando nuevo...")
        return self.entrenar_modelo()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del modelo"""
        if not self.modelo_entrenado:
            return {"estado": "no_entrenado"}
        
        try:
            # Obtener importancia de características
            importancia = self.modelo.feature_importances_
            top_features = np.argsort(importancia)[-10:][::-1]
            
            return {
                "estado": "entrenado",
                "categorias": len(self.categorias),
                "caracteristicas": len(importancia),
                "top_features": top_features.tolist(),
                "archivo_modelo": self.archivo_modelo,
                "archivo_vectorizer": self.archivo_vectorizer
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"estado": "error", "error": str(e)}

# Instancia global del modelo
modelo_clasificacion_xgboost = ModeloXGBoostClasificacion()

def clasificar_pregunta_xgboost(pregunta: str) -> Tuple[str, float]:
    """Función principal para clasificar preguntas con XGBoost"""
    return modelo_clasificacion_xgboost.clasificar_pregunta(pregunta)

def inicializar_modelo_clasificacion() -> bool:
    """Inicializar el modelo de clasificación"""
    return modelo_clasificacion_xgboost.inicializar()

def obtener_estadisticas_clasificacion() -> Dict[str, Any]:
    """Obtener estadísticas del modelo de clasificación"""
    return modelo_clasificacion_xgboost.obtener_estadisticas()

# Ejemplo de uso
if __name__ == "__main__":
    print("🚀 Pruebas del Modelo XGBoost para Clasificación de Preguntas")
    print("=" * 70)
    
    # Inicializar modelo
    if inicializar_modelo_clasificacion():
        print("✅ Modelo inicializado correctamente")
        
        # Probar clasificación
        preguntas_prueba = [
            "calcular mezcla para 30000 kw",
            "cuánto stock hay de purín",
            "qué es un biodigestor",
            "hola, cómo estás",
            "optimizar proceso de digestión"
        ]
        
        print("\n📊 PRUEBAS DE CLASIFICACIÓN:")
        print("-" * 50)
        
        for pregunta in preguntas_prueba:
            categoria, confianza = clasificar_pregunta_xgboost(pregunta)
            print(f"❓ '{pregunta}'")
            print(f"   🎯 Categoría: {categoria}")
            print(f"   📈 Confianza: {confianza:.2%}")
            print()
        
        # Mostrar estadísticas
        stats = obtener_estadisticas_clasificacion()
        print("📈 ESTADÍSTICAS DEL MODELO:")
        print(f"   Estado: {stats.get('estado', 'N/A')}")
        print(f"   Categorías: {stats.get('categorias', 'N/A')}")
        print(f"   Características: {stats.get('caracteristicas', 'N/A')}")
        
    else:
        print("❌ Error inicializando modelo")
