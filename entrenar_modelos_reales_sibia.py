#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrenamiento de Modelos ML Reales para SIBIA
Dataset de 300 preguntas y respuestas específicas del sistema
"""

import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntrenadorSIBIA:
    """Entrenador de modelos ML reales para SIBIA"""
    
    def __init__(self):
        self.dataset = self._crear_dataset_300()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        self.label_encoder = LabelEncoder()
        self.modelos_entrenados = {}
        
    def _crear_dataset_300(self):
        """Crea dataset de 300 preguntas y respuestas específicas de SIBIA"""
        dataset = []
        
        # STOCK DE MATERIALES (100 preguntas)
        materiales = ['Rumen', 'Lactosa', 'Maiz', 'Purin', 'Expeller', 'Gomas vegetales', 'Grasa', 'Silaje']
        variaciones_stock = [
            'STOCK DE {}', 'CUANTO {} HAY', 'CUANTO {} TENEMOS', 'CANTIDAD DE {}',
            'CUANTO {} DISPONIBLE', 'CUANTO {} EN PLANTA', 'CUANTO {} RESTANTE',
            'CUANTO {} QUEDA', 'CUANTO {} EN INVENTARIO', 'CUANTO {} EN STOCK'
        ]
        
        for material in materiales:
            for variacion in variaciones_stock:
                pregunta = variacion.format(material.upper())
                dataset.append({
                    'pregunta': pregunta,
                    'tipo': 'stock_materiales',
                    'material_especifico': material.lower(),
                    'respuesta_esperada': f'Stock de {material}'
                })
        
        # CÁLCULOS DE MEZCLA (80 preguntas)
        calculos_kw = [
            'CUANTOS KW GENERAN {}TN DE {}', 'CUANTO KW PRODUCE {}TN DE {}',
            'CUANTA ENERGIA GENERA {}TN DE {}', 'CUANTOS KILOVATIOS DA {}TN DE {}',
            'CUANTA POTENCIA PRODUCE {}TN DE {}', 'CUANTO KW DA {}TN DE {}',
            'CUANTA ENERGIA DA {}TN DE {}', 'CUANTA POTENCIA DA {}TN DE {}'
        ]
        
        cantidades = ['1', '2', '3', '5', '10', '15', '20', '25']
        for material in materiales[:5]:  # Primeros 5 materiales
            for cantidad in cantidades:
                for calculo in calculos_kw:
                    pregunta = calculo.format(cantidad, material.upper())
                    dataset.append({
                        'pregunta': pregunta,
                        'tipo': 'calculo_mezcla',
                        'cantidad': cantidad,
                        'material': material.lower(),
                        'respuesta_esperada': f'Cálculo de {cantidad}TN de {material}'
                    })
        
        # SENSORES Y SISTEMA (60 preguntas)
        sensores = ['temperatura', 'presion', 'nivel', 'flujo', 'digestor', 'tanque', 'biogas']
        variaciones_sensores = [
            'COMO ESTA LA {}', 'COMO ESTA EL {}', 'COMO ESTAN LOS {}',
            'ESTADO DE LA {}', 'ESTADO DEL {}', 'ESTADO DE LOS {}',
            'VALOR DE LA {}', 'VALOR DEL {}', 'VALOR DE LOS {}',
            'MEDICION DE LA {}', 'MEDICION DEL {}', 'MEDICION DE LOS {}'
        ]
        
        for sensor in sensores:
            for variacion in variaciones_sensores:
                pregunta = variacion.format(sensor.upper())
                dataset.append({
                    'pregunta': pregunta,
                    'tipo': 'sensores_datos',
                    'sensor': sensor.lower(),
                    'respuesta_esperada': f'Estado de {sensor}'
                })
        
        # CONVERSACIÓN Y AYUDA (40 preguntas)
        conversaciones = [
            'HOLA SIBIA', 'QUE PUEDES HACER', 'COMO FUNCIONAS', 'QUE ERES',
            'AYUDA', 'QUE HACES', 'PARA QUE SIRVES', 'COMO TE LLAMAS',
            'GRACIAS', 'ADIOS', 'HASTA LUEGO', 'NOS VEMOS',
            'COMO ESTAS', 'QUE TAL', 'TODO BIEN', 'COMO VA',
            'EXPLICAME', 'ENSEÑAME', 'AYUDAME', 'INSTRUYEME',
            'QUE SABES', 'QUE CONOCES', 'QUE INFORMACION TIENES',
            'COMO PUEDO USARTE', 'QUE COMANDOS TIENES', 'QUE FUNCIONES TIENES'
        ]
        
        for conversacion in conversaciones:
            dataset.append({
                'pregunta': conversacion,
                'tipo': 'conversacion',
                'respuesta_esperada': 'Conversación general'
            })
        
        # KPIs Y SISTEMA (20 preguntas)
        kpis = ['GENERACION', 'INYECTADA', 'SPOT', 'EFICIENCIA', 'CONSUMO', 'METANO']
        variaciones_kpi = [
            'COMO ESTA LA {}', 'COMO ESTA EL {}', 'VALOR DE LA {}', 'VALOR DEL {}',
            'ESTADO DE LA {}', 'ESTADO DEL {}', 'COMO VA LA {}', 'COMO VA EL {}'
        ]
        
        for kpi in kpis:
            for variacion in variaciones_kpi:
                pregunta = variacion.format(kpi)
                dataset.append({
                    'pregunta': pregunta,
                    'tipo': 'kpis_sistema',
                    'kpi': kpi.lower(),
                    'respuesta_esperada': f'Estado de {kpi}'
                })
        
        logger.info(f"✅ Dataset creado: {len(dataset)} preguntas")
        return dataset
    
    def entrenar_modelos(self):
        """Entrena los modelos ML reales"""
        logger.info("🚀 Iniciando entrenamiento de modelos ML reales...")
        
        # Preparar datos
        preguntas = [item['pregunta'] for item in self.dataset]
        tipos = [item['tipo'] for item in self.dataset]
        
        # Vectorizar preguntas
        X = self.vectorizer.fit_transform(preguntas)
        y = self.label_encoder.fit_transform(tipos)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"📊 Datos de entrenamiento: {X_train.shape[0]} muestras")
        logger.info(f"📊 Datos de prueba: {X_test.shape[0]} muestras")
        
        # 1. ENTRENAR XGBOOST
        logger.info("🧠 Entrenando XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        xgb_model.fit(X_train, y_train)
        
        # Evaluar XGBoost
        y_pred_xgb = xgb_model.predict(X_test)
        accuracy_xgb = accuracy_score(y_test, y_pred_xgb)
        logger.info(f"✅ XGBoost - Precisión: {accuracy_xgb:.3f}")
        
        # 2. ENTRENAR RANDOM FOREST
        logger.info("🌲 Entrenando Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        
        # Evaluar Random Forest
        y_pred_rf = rf_model.predict(X_test)
        accuracy_rf = accuracy_score(y_test, y_pred_rf)
        logger.info(f"✅ Random Forest - Precisión: {accuracy_rf:.3f}")
        
        # Guardar modelos
        self.modelos_entrenados = {
            'xgboost': xgb_model,
            'random_forest': rf_model,
            'vectorizer': self.vectorizer
        }
        
        # Guardar modelos en archivos
        joblib.dump(xgb_model, 'modelo_xgboost_sibia_entrenado.pkl')
        joblib.dump(rf_model, 'modelo_random_forest_sibia_entrenado.pkl')
        joblib.dump(self.vectorizer, 'vectorizer_sibia_entrenado.pkl')
        joblib.dump(self.label_encoder, 'label_encoder_sibia_entrenado.pkl')
        
        logger.info("💾 Modelos guardados exitosamente")
        
        # Reporte detallado
        logger.info("\n📊 REPORTE DE CLASIFICACIÓN:")
        logger.info("XGBoost:")
        logger.info(classification_report(y_test, y_pred_xgb))
        logger.info("Random Forest:")
        logger.info(classification_report(y_test, y_pred_rf))
        
        return {
            'xgboost_accuracy': accuracy_xgb,
            'random_forest_accuracy': accuracy_rf,
            'modelos': self.modelos_entrenados
        }
    
    def probar_modelos(self, preguntas_prueba):
        """Prueba los modelos entrenados"""
        logger.info("🧪 Probando modelos entrenados...")
        
        resultados = []
        for pregunta in preguntas_prueba:
            # Vectorizar pregunta
            X_pregunta = self.vectorizer.transform([pregunta])
            
            # Predecir con ambos modelos
            pred_xgb_num = self.modelos_entrenados['xgboost'].predict(X_pregunta)[0]
            pred_xgb = self.label_encoder.inverse_transform([pred_xgb_num])[0]
            prob_xgb = self.modelos_entrenados['xgboost'].predict_proba(X_pregunta)[0].max()
            
            pred_rf_num = self.modelos_entrenados['random_forest'].predict(X_pregunta)[0]
            pred_rf = self.label_encoder.inverse_transform([pred_rf_num])[0]
            prob_rf = self.modelos_entrenados['random_forest'].predict_proba(X_pregunta)[0].max()
            
            resultados.append({
                'pregunta': pregunta,
                'xgboost': {'prediccion': pred_xgb, 'confianza': prob_xgb},
                'random_forest': {'prediccion': pred_rf, 'confianza': prob_rf}
            })
            
            logger.info(f"❓ '{pregunta}'")
            logger.info(f"   XGBoost: {pred_xgb} (confianza: {prob_xgb:.3f})")
            logger.info(f"   Random Forest: {pred_rf} (confianza: {prob_rf:.3f})")
        
        return resultados

def main():
    """Función principal de entrenamiento"""
    logger.info("🚀 INICIANDO ENTRENAMIENTO DE MODELOS ML REALES PARA SIBIA")
    logger.info("=" * 60)
    
    # Crear entrenador
    entrenador = EntrenadorSIBIA()
    
    # Entrenar modelos
    resultados = entrenador.entrenar_modelos()
    
    # Probar con preguntas específicas
    preguntas_prueba = [
        'STOCK DE RUMEN',
        'CUANTO LACTOSA HAY',
        'CUANTOS KW GENERAN 2TN DE LACTOSA',
        'COMO ESTA LA TEMPERATURA',
        'HOLA SIBIA'
    ]
    
    logger.info("\n🧪 PRUEBAS CON MODELOS ENTRENADOS:")
    logger.info("=" * 60)
    entrenador.probar_modelos(preguntas_prueba)
    
    logger.info("\n🎉 ENTRENAMIENTO COMPLETADO")
    logger.info(f"✅ XGBoost - Precisión: {resultados['xgboost_accuracy']:.3f}")
    logger.info(f"✅ Random Forest - Precisión: {resultados['random_forest_accuracy']:.3f}")
    logger.info("💾 Modelos guardados para uso en SIBIA")

if __name__ == "__main__":
    main()
