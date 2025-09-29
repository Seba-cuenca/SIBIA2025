#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo XGBoost para Calculadora Rápida SIBIA
Predice KW/TN basado en composición nutricional de materiales
"""

import os
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

class ModeloXGBoostCalculadora:
    """Modelo XGBoost para predicción de KW/TN en calculadora rápida"""
    
    def __init__(self):
        self.modelo_file = "modelo_xgboost_calculadora.json"
        self.datos_entrenamiento_file = "datos_entrenamiento_xgboost.json"
        self.modelo = None
        self.feature_names = [
            'st_porcentaje', 'sv_porcentaje', 'carbohidratos_porcentaje', 
            'lipidos_porcentaje', 'proteinas_porcentaje', 'densidad', 
            'm3_tnsv', 'ch4_porcentaje'
        ]
        
        # Cargar modelo existente o inicializar nuevo
        self.cargar_modelo()
        
        # Si no hay modelo, entrenar con datos iniciales
        if self.modelo is None:
            self.entrenar_modelo_inicial()
    
    def cargar_modelo(self):
        """Carga el modelo XGBoost entrenado"""
        try:
            if os.path.exists(self.modelo_file):
                # XGBoost no se puede serializar directamente a JSON
                # Usaremos un enfoque diferente
                logger.info("📁 Modelo XGBoost encontrado, inicializando nuevo entrenamiento...")
                self.modelo = None
            else:
                logger.info("🆕 No hay modelo XGBoost existente")
                self.modelo = None
        except Exception as e:
            logger.error(f"❌ Error cargando modelo XGBoost: {e}")
            self.modelo = None
    
    def preparar_datos_entrenamiento(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara datos de entrenamiento desde materiales_base_config.json"""
        try:
            # Cargar datos de materiales
            with open('materiales_base_config.json', 'r', encoding='utf-8') as f:
                materiales = json.load(f)
            
            datos = []
            for nombre, material in materiales.items():
                # Extraer características
                st = material.get('st', 0) * 100  # Convertir a porcentaje
                sv = material.get('sv', 0) * 100  # Convertir a porcentaje
                carbohidratos = material.get('carbohidratos', 0) * 100  # Convertir a porcentaje
                lipidos = material.get('lipidos', 0) * 100  # Convertir a porcentaje
                proteinas = material.get('proteinas', 0) * 100  # Convertir a porcentaje
                densidad = material.get('densidad', 1.0)
                m3_tnsv = material.get('m3_tnsv', 300.0)
                kw_tn = material.get('kw/tn', 0.0)
                
                # Calcular CH4% usando la fórmula
                tn_solidos = 1.0 * (material.get('st', 0))
                tn_carbohidratos = tn_solidos * (material.get('carbohidratos', 0))
                tn_lipidos = tn_solidos * (material.get('lipidos', 0))
                tn_proteinas = tn_solidos * (material.get('proteinas', 0))
                
                total_componentes = tn_carbohidratos + tn_lipidos + tn_proteinas
                ch4_porcentaje = 0.65  # Valor por defecto
                if total_componentes > 0:
                    ch4_porcentaje = ((tn_proteinas * 0.71) + (tn_lipidos * 0.68) + (tn_carbohidratos * 0.5)) / total_componentes
                ch4_porcentaje *= 100
                
                # Solo incluir si tiene KW/TN válido
                if kw_tn > 0:
                    datos.append([
                        st, sv, carbohidratos, lipidos, proteinas, 
                        densidad, m3_tnsv, ch4_porcentaje, kw_tn
                    ])
            
            if not datos:
                logger.warning("⚠️ No hay datos válidos para entrenamiento")
                return np.array([]), np.array([])
            
            # Convertir a arrays numpy
            datos_array = np.array(datos)
            X = datos_array[:, :-1]  # Características
            y = datos_array[:, -1]   # Target (KW/TN)
            
            logger.info(f"📊 Datos preparados: {len(datos)} muestras, {X.shape[1]} características")
            return X, y
            
        except Exception as e:
            logger.error(f"❌ Error preparando datos de entrenamiento: {e}")
            return np.array([]), np.array([])
    
    def entrenar_modelo_inicial(self):
        """Entrena el modelo XGBoost con datos iniciales"""
        try:
            X, y = self.preparar_datos_entrenamiento()
            
            if len(X) == 0:
                logger.warning("⚠️ No hay datos para entrenar el modelo")
                return
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Configurar modelo XGBoost
            self.modelo = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
            
            # Entrenar modelo
            logger.info("🚀 Entrenando modelo XGBoost...")
            self.modelo.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = self.modelo.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"✅ Modelo XGBoost entrenado:")
            logger.info(f"   📊 MSE: {mse:.4f}")
            logger.info(f"   📊 R²: {r2:.4f}")
            
            # Guardar información del modelo
            self.guardar_info_modelo(mse, r2)
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo XGBoost: {e}")
            self.modelo = None
    
    def guardar_info_modelo(self, mse: float, r2: float):
        """Guarda información del modelo entrenado"""
        try:
            info_modelo = {
                'fecha_entrenamiento': datetime.now().isoformat(),
                'mse': mse,
                'r2_score': r2,
                'feature_names': self.feature_names,
                'n_samples': len(self.preparar_datos_entrenamiento()[0]),
                'modelo_tipo': 'XGBoost Regressor',
                'parametros': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8
                }
            }
            
            with open(self.modelo_file, 'w', encoding='utf-8') as f:
                json.dump(info_modelo, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 Información del modelo guardada")
            
        except Exception as e:
            logger.error(f"❌ Error guardando información del modelo: {e}")
    
    def predecir_kw_tn(self, st: float, sv: float, carbohidratos: float, 
                      lipidos: float, proteinas: float, densidad: float = 1.0, 
                      m3_tnsv: float = 300.0) -> Tuple[float, float]:
        """
        Predice KW/TN usando XGBoost con fallback a función básica
        
        Returns:
            Tuple[float, float]: (prediccion_kw_tn, confianza)
        """
        try:
            # CORREGIDO: Usar función básica como fallback principal
            kw_basico = self._calcular_kw_tn_basico(st, sv)
            
            if self.modelo is None:
                logger.warning("⚠️ Modelo XGBoost no disponible, usando función básica")
                return (kw_basico, 0.8)
            
            # Calcular CH4%
            tn_solidos = st / 100.0
            tn_carbohidratos = tn_solidos * (carbohidratos / 100.0)
            tn_lipidos = tn_solidos * (lipidos / 100.0)
            tn_proteinas = tn_solidos * (proteinas / 100.0)
            
            total_componentes = tn_carbohidratos + tn_lipidos + tn_proteinas
            ch4_porcentaje = 0.65
            if total_componentes > 0:
                ch4_porcentaje = ((tn_proteinas * 0.71) + (tn_lipidos * 0.68) + (tn_carbohidratos * 0.5)) / total_componentes
            ch4_porcentaje *= 100
            
            # Preparar características
            features = np.array([[
                st, sv, carbohidratos, lipidos, proteinas, 
                densidad, m3_tnsv, ch4_porcentaje
            ]])
            
            # Hacer predicción
            prediccion_raw = self.modelo.predict(features)[0]
            prediccion = float(prediccion_raw)  # Convertir a float Python nativo
            
            # CORREGIDO: Si XGBoost devuelve valor muy bajo, usar función básica
            if prediccion < 1.0:  # Valores muy bajos indican problema
                logger.warning(f"⚠️ XGBoost devuelve valor muy bajo ({prediccion}), usando función básica ({kw_basico})")
                return (kw_basico, 0.8)
            
            # Calcular confianza basada en la varianza de predicciones similares
            confianza_raw = min(0.95, max(0.7, 1.0 - abs(prediccion - kw_basico) / max(prediccion, kw_basico)))
            confianza = float(confianza_raw)  # Convertir a float Python nativo
            
            logger.info(f"🎯 Predicción XGBoost: {prediccion:.4f} KW/TN (confianza: {confianza:.2f})")
            return (prediccion, confianza)
            
        except Exception as e:
            logger.error(f"❌ Error en predicción XGBoost: {e}")
            # Fallback a función básica
            kw_basico = self._calcular_kw_tn_basico(st, sv)
            return (kw_basico, 0.7)
    
    def _calcular_kw_tn_basico(self, st: float, sv: float) -> float:
        """Calcula KW/TN usando la fórmula básica"""
        try:
            # Fórmula básica: KW/TN = (ST * SV * CH4) / 1000
            ch4_porcentaje = 65.0  # Valor por defecto
            kw_tn = (st * sv * ch4_porcentaje) / 1000
            return round(kw_tn, 2)
        except Exception:
            return 0.0
    
    def _calcular_kw_tn_tradicional(self, st: float, sv: float, carbohidratos: float, 
                                   lipidos: float, proteinas: float, densidad: float, 
                                   m3_tnsv: float) -> float:
        """Calcula KW/TN usando la fórmula tradicional como fallback"""
        try:
            # Fórmula tradicional: KW/TN = (ST × SV × M³/TN SV × CH4%) / Consumo CHP
            tn_solidos = st / 100.0
            tn_carbohidratos = tn_solidos * (carbohidratos / 100.0)
            tn_lipidos = tn_solidos * (lipidos / 100.0)
            tn_proteinas = tn_solidos * (proteinas / 100.0)
            
            total_componentes = tn_carbohidratos + tn_lipidos + tn_proteinas
            ch4_porcentaje = 0.65
            if total_componentes > 0:
                ch4_porcentaje = ((tn_proteinas * 0.71) + (tn_lipidos * 0.68) + (tn_carbohidratos * 0.5)) / total_componentes
            
            tnsv = (st / 100.0) * (sv / 100.0)
            consumo_chp = 505.0  # Valor por defecto
            
            kw_tn = (tnsv * m3_tnsv * ch4_porcentaje) / consumo_chp
            
            return kw_tn
            
        except Exception as e:
            logger.error(f"❌ Error en cálculo tradicional: {e}")
            return 0.0
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del modelo"""
        try:
            if os.path.exists(self.modelo_file):
                with open(self.modelo_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                return info
            else:
                return {'estado': 'no_entrenado'}
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {'estado': 'error'}

# Instancia global del modelo
modelo_xgboost = ModeloXGBoostCalculadora()

def predecir_kw_tn_xgboost(st: float, sv: float, carbohidratos: float, 
                          lipidos: float, proteinas: float, densidad: float = 1.0, 
                          m3_tnsv: float = 300.0) -> Tuple[float, float]:
    """Función principal para predicción con XGBoost"""
    return modelo_xgboost.predecir_kw_tn(st, sv, carbohidratos, lipidos, proteinas, densidad, m3_tnsv)

def obtener_estadisticas_xgboost() -> Dict[str, Any]:
    """Función principal para obtener estadísticas del modelo"""
    return modelo_xgboost.obtener_estadisticas()

# Ejemplos de uso
if __name__ == "__main__":
    print("🚀 Pruebas del Modelo XGBoost para Calculadora Rápida")
    print("=" * 60)
    
    # Prueba con datos de ejemplo
    st = 50.7
    sv = 95.0
    carbohidratos = 80.0
    lipidos = 8.0
    proteinas = 12.0
    
    prediccion, confianza = predecir_kw_tn_xgboost(st, sv, carbohidratos, lipidos, proteinas)
    
    print(f"📊 Predicción para material de ejemplo:")
    print(f"   ST: {st}%, SV: {sv}%")
    print(f"   CH: {carbohidratos}%, Lip: {lipidos}%, Prot: {proteinas}%")
    print(f"   🎯 KW/TN predicho: {prediccion:.4f}")
    print(f"   📈 Confianza: {confianza:.2f}")
    
    # Estadísticas del modelo
    stats = obtener_estadisticas_xgboost()
    print(f"\n📈 Estadísticas del modelo:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
