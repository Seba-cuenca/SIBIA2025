#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODELO ML PARA PREDECIR INHIBICIÓN DE BIODIGESTORES
===================================================

Modelo de Machine Learning especializado en predecir inhibición bacteriana
en biodigestores usando datos químicos y de sensores.

Autor: SIBIA - Sistema Inteligente de Biogás Avanzado
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import json
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class ModeloMLInhibicionBiodigestores:
    """
    Modelo ML para predecir inhibición de biodigestores
    """
    
    def __init__(self):
        self.modelo = None
        self.scaler = None
        self.label_encoder = None
        self.caracteristicas = []
        self.entrenado = False
        
    def crear_dataset_sintetico(self, n_muestras: int = 1000) -> pd.DataFrame:
        """
        Crea dataset sintético basado en conocimiento experto
        """
        np.random.seed(42)
        
        datos = []
        
        for _ in range(n_muestras):
            # Generar datos sintéticos realistas
            ph = np.random.normal(7.0, 0.5)
            temperatura = np.random.normal(37.5, 2.0)
            h2s = np.random.exponential(30)
            co2 = np.random.normal(35, 5)
            o2 = np.random.exponential(0.5)
            ta = np.random.normal(2500, 500)
            vfa_total = np.random.exponential(400)
            acetato = vfa_total * np.random.uniform(0.4, 0.6)
            propionato = vfa_total * np.random.uniform(0.2, 0.3)
            nitrogeno = np.random.normal(150, 30)
            fosforo = np.random.normal(30, 10)
            produccion_ch4 = np.random.normal(120, 20)
            contenido_ch4 = np.random.normal(62, 5)
            
            # Calcular OLR y FOS/TAC
            carga_organica = np.random.normal(150, 30)
            volumen_digestor = 50
            olr = carga_organica / volumen_digestor
            
            fos_tac = vfa_total / ta if ta > 0 else 0
            
            # Determinar nivel de inhibición basado en reglas expertas
            nivel_inhibicion = self._determinar_inhibicion_sintetica(
                ph, temperatura, h2s, co2, o2, ta, vfa_total, 
                acetato, propionato, olr, fos_tac, produccion_ch4, contenido_ch4
            )
            
            datos.append({
                'ph': ph,
                'temperatura': temperatura,
                'h2s': h2s,
                'co2': co2,
                'o2': o2,
                'ta': ta,
                'vfa_total': vfa_total,
                'acetato': acetato,
                'propionato': propionato,
                'nitrogeno_total': nitrogeno,
                'fosforo_total': fosforo,
                'produccion_ch4': produccion_ch4,
                'contenido_ch4': contenido_ch4,
                'olr': olr,
                'fos_tac': fos_tac,
                'nivel_inhibicion': nivel_inhibicion
            })
        
        return pd.DataFrame(datos)
    
    def _determinar_inhibicion_sintetica(self, ph, temperatura, h2s, co2, o2, ta, 
                                       vfa_total, acetato, propionato, olr, fos_tac, 
                                       produccion_ch4, contenido_ch4) -> str:
        """
        Determina nivel de inhibición basado en reglas expertas
        """
        puntuacion = 0
        
        # Evaluar pH
        if ph < 6.5 or ph > 7.8:
            puntuacion += 3
        elif ph < 6.8 or ph > 7.5:
            puntuacion += 2
        
        # Evaluar temperatura
        if temperatura < 32 or temperatura > 42:
            puntuacion += 3
        elif temperatura < 35 or temperatura > 40:
            puntuacion += 1
        
        # Evaluar H2S
        if h2s > 100:
            puntuacion += 3
        elif h2s > 50:
            puntuacion += 2
        
        # Evaluar O2
        if o2 > 1.0:
            puntuacion += 3
        elif o2 > 0.5:
            puntuacion += 2
        
        # Evaluar VFA
        if vfa_total > 1000:
            puntuacion += 3
        elif vfa_total > 800:
            puntuacion += 2
        
        # Evaluar FOS/TAC
        if fos_tac > 0.4:
            puntuacion += 3
        elif fos_tac > 0.3:
            puntuacion += 2
        
        # Evaluar OLR
        if olr > 5.0:
            puntuacion += 3
        elif olr > 4.0:
            puntuacion += 2
        
        # Evaluar producción CH4
        if produccion_ch4 < 50:
            puntuacion += 2
        elif produccion_ch4 < 80:
            puntuacion += 1
        
        # Evaluar contenido CH4
        if contenido_ch4 < 45:
            puntuacion += 2
        elif contenido_ch4 < 55:
            puntuacion += 1
        
        # Determinar nivel final
        if puntuacion >= 12:
            return 'inhibicion_severa'
        elif puntuacion >= 8:
            return 'inhibicion_moderada'
        elif puntuacion >= 4:
            return 'inhibicion_leve'
        else:
            return 'optimo'
    
    def entrenar_modelo(self, datos: pd.DataFrame = None) -> Dict:
        """
        Entrena el modelo ML
        """
        try:
            if datos is None:
                datos = self.crear_dataset_sintetico()
            
            # Preparar datos
            caracteristicas = [col for col in datos.columns if col != 'nivel_inhibicion']
            X = datos[caracteristicas]
            y = datos['nivel_inhibicion']
            
            # Codificar etiquetas
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
            
            # Escalar características
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entrenar modelo
            self.modelo = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.modelo.fit(X_train_scaled, y_train)
            
            # Evaluar modelo
            y_pred = self.modelo.predict(X_test_scaled)
            accuracy = self.modelo.score(X_test_scaled, y_test)
            
            # Validación cruzada
            cv_scores = cross_val_score(self.modelo, X_train_scaled, y_train, cv=5)
            
            self.caracteristicas = caracteristicas
            self.entrenado = True
            
            return {
                'status': 'success',
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'feature_importance': dict(zip(caracteristicas, self.modelo.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def predecir(self, datos: Dict) -> Dict:
        """
        Realiza predicción de inhibición
        """
        if not self.entrenado:
            return {'error': 'Modelo no entrenado'}
        
        try:
            # Preparar datos
            df = pd.DataFrame([datos])
            
            # Verificar que todas las características estén presentes
            for feature in self.caracteristicas:
                if feature not in df.columns:
                    df[feature] = 0  # Valor por defecto
            
            # Reordenar columnas
            df = df[self.caracteristicas]
            
            # Escalar datos
            datos_escalados = self.scaler.transform(df)
            
            # Predecir
            prediccion_encoded = self.modelo.predict(datos_escalados)[0]
            probabilidades = self.modelo.predict_proba(datos_escalados)[0]
            
            # Decodificar predicción
            prediccion = self.label_encoder.inverse_transform([prediccion_encoded])[0]
            
            # Obtener probabilidades por clase
            clases = self.label_encoder.classes_
            probabilidades_dict = {clase: float(prob) for clase, prob in zip(clases, probabilidades)}
            
            return {
                'prediccion': prediccion,
                'probabilidades': probabilidades_dict,
                'confianza': float(max(probabilidades)),
                'caracteristicas_importantes': self._obtener_caracteristicas_importantes(datos)
            }
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {'error': str(e)}
    
    def _obtener_caracteristicas_importantes(self, datos: Dict) -> List[Dict]:
        """
        Obtiene las características más importantes para la predicción
        """
        if not self.entrenado:
            return []
        
        importancia = self.modelo.feature_importances_
        caracteristicas_importantes = []
        
        for i, feature in enumerate(self.caracteristicas):
            if feature in datos:
                caracteristicas_importantes.append({
                    'caracteristica': feature,
                    'importancia': float(importancia[i]),
                    'valor': datos[feature]
                })
        
        # Ordenar por importancia
        caracteristicas_importantes.sort(key=lambda x: x['importancia'], reverse=True)
        
        return caracteristicas_importantes[:5]  # Top 5
    
    def guardar_modelo(self, ruta: str):
        """
        Guarda el modelo entrenado
        """
        if not self.entrenado:
            raise ValueError("Modelo no entrenado")
        
        modelo_data = {
            'modelo': self.modelo,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'caracteristicas': self.caracteristicas
        }
        
        joblib.dump(modelo_data, ruta)
        logger.info(f"Modelo guardado en {ruta}")
    
    def cargar_modelo(self, ruta: str):
        """
        Carga un modelo previamente entrenado
        """
        try:
            modelo_data = joblib.load(ruta)
            
            self.modelo = modelo_data['modelo']
            self.scaler = modelo_data['scaler']
            self.label_encoder = modelo_data['label_encoder']
            self.caracteristicas = modelo_data['caracteristicas']
            self.entrenado = True
            
            logger.info(f"Modelo cargado desde {ruta}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise

# Función para crear y entrenar modelo
def crear_modelo_inhibicion():
    """
    Crea y entrena el modelo de inhibición
    """
    modelo = ModeloMLInhibicionBiodigestores()
    resultado = modelo.entrenar_modelo()
    
    if resultado['status'] == 'success':
        logger.info(f"Modelo entrenado con accuracy: {resultado['accuracy']:.3f}")
        return modelo
    else:
        logger.error(f"Error entrenando modelo: {resultado['error']}")
        return None

if __name__ == "__main__":
    # Crear y entrenar modelo
    modelo = crear_modelo_inhibicion()
    
    if modelo:
        # Ejemplo de predicción
        datos_ejemplo = {
            'ph': 7.2,
            'temperatura': 37.5,
            'h2s': 25,
            'co2': 35,
            'o2': 0.2,
            'ta': 2500,
            'vfa_total': 400,
            'acetato': 200,
            'propionato': 100,
            'nitrogeno_total': 150,
            'fosforo_total': 30,
            'produccion_ch4': 120,
            'contenido_ch4': 62,
            'olr': 3.0,
            'fos_tac': 0.16
        }
        
        prediccion = modelo.predecir(datos_ejemplo)
        print("Predicción de Inhibición:")
        print(json.dumps(prediccion, indent=2, ensure_ascii=False))
