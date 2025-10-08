#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENTRENAMIENTO DE MODELO ML PARA PREDICCIÓN DE FALLOS CON DATOS REALES
======================================================================

Entrena modelos de Machine Learning con datos históricos reales de la planta
para predecir posibles fallos en biodigestores.

Entrada:
- data/dataset_entrenamiento_ml.parquet

Salida:
- models/modelo_prediccion_fallos.pkl (modelo entrenado)
- models/scaler_prediccion_fallos.pkl (scaler)
- models/metadata_modelo.json (metadata)
- models/reporte_entrenamiento.json (métricas)
"""

import pandas as pd
import numpy as np
import json
import joblib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'
MODELS_DIR.mkdir(exist_ok=True)

class EntrenadorPrediccionFallos:
    """Entrena modelos ML para predicción de fallos en biodigestores"""
    
    def __init__(self):
        self.dataset = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.modelos = {}
        self.mejor_modelo = None
        self.mejor_modelo_nombre = None
        self.resultados = {}
        
    def cargar_dataset(self) -> bool:
        """Carga el dataset preparado"""
        logger.info("📂 Cargando dataset de entrenamiento...")
        
        try:
            dataset_path = DATA_DIR / 'dataset_entrenamiento_ml.parquet'
            if not dataset_path.exists():
                logger.error(f"❌ No existe: {dataset_path}")
                logger.error("   Ejecuta primero: preparar_datos_entrenamiento_ml.py")
                return False
            
            self.dataset = pd.read_parquet(dataset_path)
            logger.info(f"✅ Dataset cargado: {len(self.dataset)} registros")
            
            # Verificar que tenga la columna de etiqueta
            if 'estado_biodigestor' not in self.dataset.columns:
                logger.error("❌ Falta columna 'estado_biodigestor' en el dataset")
                return False
            
            # Mostrar distribución de clases
            distribucion = self.dataset['estado_biodigestor'].value_counts()
            logger.info("📊 Distribución de estados:")
            for estado, count in distribucion.items():
                logger.info(f"   {estado}: {count} ({count/len(self.dataset)*100:.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando dataset: {e}")
            return False
    
    def preparar_datos(self) -> bool:
        """Prepara datos para entrenamiento"""
        logger.info("🔧 Preparando datos para entrenamiento...")
        
        try:
            # Separar features y etiquetas
            X = self.dataset.drop('estado_biodigestor', axis=1)
            y = self.dataset['estado_biodigestor']
            
            # Guardar nombres de features
            self.feature_names = list(X.columns)
            logger.info(f"   Features: {len(self.feature_names)}")
            
            # Eliminar columnas con muchos NaN
            umbral_nan = 0.7  # Eliminar si >70% son NaN
            columnas_validas = X.columns[X.isna().mean() < umbral_nan]
            X = X[columnas_validas]
            self.feature_names = list(X.columns)
            logger.info(f"   Features después de filtrar NaN: {len(self.feature_names)}")
            
            # Rellenar NaN restantes con la mediana
            X = X.fillna(X.median())
            
            # Codificar etiquetas
            y_encoded = self.label_encoder.fit_transform(y)
            logger.info(f"   Clases: {list(self.label_encoder.classes_)}")
            
            # Dividir en train/test
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y_encoded, 
                test_size=0.2, 
                random_state=42, 
                stratify=y_encoded
            )
            
            logger.info(f"   Train: {len(self.X_train)} registros")
            logger.info(f"   Test: {len(self.X_test)} registros")
            
            # Escalar features
            self.X_train_scaled = self.scaler.fit_transform(self.X_train)
            self.X_test_scaled = self.scaler.transform(self.X_test)
            
            logger.info("✅ Datos preparados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error preparando datos: {e}")
            return False
    
    def entrenar_random_forest(self) -> Dict[str, Any]:
        """Entrena Random Forest Classifier"""
        logger.info("🌲 Entrenando Random Forest...")
        
        try:
            modelo = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'  # Importante para clases desbalanceadas
            )
            
            modelo.fit(self.X_train_scaled, self.y_train)
            
            # Predicciones
            y_pred_train = modelo.predict(self.X_train_scaled)
            y_pred_test = modelo.predict(self.X_test_scaled)
            
            # Métricas
            resultados = {
                'nombre': 'Random Forest',
                'accuracy_train': accuracy_score(self.y_train, y_pred_train),
                'accuracy_test': accuracy_score(self.y_test, y_pred_test),
                'precision_test': precision_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'recall_test': recall_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'f1_test': f1_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'feature_importance': dict(zip(self.feature_names, modelo.feature_importances_))
            }
            
            # Cross-validation
            cv_scores = cross_val_score(modelo, self.X_train_scaled, self.y_train, cv=5)
            resultados['cv_mean'] = cv_scores.mean()
            resultados['cv_std'] = cv_scores.std()
            
            self.modelos['random_forest'] = modelo
            
            logger.info(f"   Accuracy Test: {resultados['accuracy_test']:.3f}")
            logger.info(f"   F1 Score: {resultados['f1_test']:.3f}")
            logger.info(f"   CV Mean: {resultados['cv_mean']:.3f} (+/- {resultados['cv_std']:.3f})")
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error entrenando Random Forest: {e}")
            return {}
    
    def entrenar_xgboost(self) -> Dict[str, Any]:
        """Entrena XGBoost Classifier"""
        logger.info("⚡ Entrenando XGBoost...")
        
        try:
            modelo = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=10,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                eval_metric='mlogloss'
            )
            
            modelo.fit(self.X_train_scaled, self.y_train)
            
            # Predicciones
            y_pred_train = modelo.predict(self.X_train_scaled)
            y_pred_test = modelo.predict(self.X_test_scaled)
            
            # Métricas
            resultados = {
                'nombre': 'XGBoost',
                'accuracy_train': accuracy_score(self.y_train, y_pred_train),
                'accuracy_test': accuracy_score(self.y_test, y_pred_test),
                'precision_test': precision_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'recall_test': recall_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'f1_test': f1_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'feature_importance': dict(zip(self.feature_names, modelo.feature_importances_))
            }
            
            # Cross-validation
            cv_scores = cross_val_score(modelo, self.X_train_scaled, self.y_train, cv=5)
            resultados['cv_mean'] = cv_scores.mean()
            resultados['cv_std'] = cv_scores.std()
            
            self.modelos['xgboost'] = modelo
            
            logger.info(f"   Accuracy Test: {resultados['accuracy_test']:.3f}")
            logger.info(f"   F1 Score: {resultados['f1_test']:.3f}")
            logger.info(f"   CV Mean: {resultados['cv_mean']:.3f} (+/- {resultados['cv_std']:.3f})")
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error entrenando XGBoost: {e}")
            return {}
    
    def entrenar_gradient_boosting(self) -> Dict[str, Any]:
        """Entrena Gradient Boosting Classifier"""
        logger.info("📈 Entrenando Gradient Boosting...")
        
        try:
            modelo = GradientBoostingClassifier(
                n_estimators=150,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            )
            
            modelo.fit(self.X_train_scaled, self.y_train)
            
            # Predicciones
            y_pred_train = modelo.predict(self.X_train_scaled)
            y_pred_test = modelo.predict(self.X_test_scaled)
            
            # Métricas
            resultados = {
                'nombre': 'Gradient Boosting',
                'accuracy_train': accuracy_score(self.y_train, y_pred_train),
                'accuracy_test': accuracy_score(self.y_test, y_pred_test),
                'precision_test': precision_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'recall_test': recall_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'f1_test': f1_score(self.y_test, y_pred_test, average='weighted', zero_division=0),
                'feature_importance': dict(zip(self.feature_names, modelo.feature_importances_))
            }
            
            # Cross-validation
            cv_scores = cross_val_score(modelo, self.X_train_scaled, self.y_train, cv=5)
            resultados['cv_mean'] = cv_scores.mean()
            resultados['cv_std'] = cv_scores.std()
            
            self.modelos['gradient_boosting'] = modelo
            
            logger.info(f"   Accuracy Test: {resultados['accuracy_test']:.3f}")
            logger.info(f"   F1 Score: {resultados['f1_test']:.3f}")
            logger.info(f"   CV Mean: {resultados['cv_mean']:.3f} (+/- {resultados['cv_std']:.3f})")
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error entrenando Gradient Boosting: {e}")
            return {}
    
    def seleccionar_mejor_modelo(self):
        """Selecciona el mejor modelo basado en F1 Score"""
        logger.info("🏆 Seleccionando mejor modelo...")
        
        mejor_f1 = 0
        mejor_nombre = None
        
        for nombre, resultado in self.resultados.items():
            f1 = resultado.get('f1_test', 0)
            if f1 > mejor_f1:
                mejor_f1 = f1
                mejor_nombre = nombre
        
        if mejor_nombre:
            self.mejor_modelo = self.modelos[mejor_nombre]
            self.mejor_modelo_nombre = mejor_nombre
            logger.info(f"✅ Mejor modelo: {mejor_nombre} (F1: {mejor_f1:.3f})")
        else:
            logger.error("❌ No se pudo seleccionar mejor modelo")
    
    def generar_reporte_detallado(self):
        """Genera reporte detallado del mejor modelo"""
        logger.info("📝 Generando reporte detallado...")
        
        if self.mejor_modelo is None:
            logger.error("❌ No hay modelo seleccionado")
            return
        
        # Predicciones del mejor modelo
        y_pred = self.mejor_modelo.predict(self.X_test_scaled)
        
        # Classification report
        report = classification_report(
            self.y_test, 
            y_pred, 
            target_names=self.label_encoder.classes_,
            output_dict=True,
            zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        
        # Top features importantes
        if hasattr(self.mejor_modelo, 'feature_importances_'):
            importancias = self.mejor_modelo.feature_importances_
            indices_top = np.argsort(importancias)[-10:][::-1]
            top_features = [
                {
                    'feature': self.feature_names[i],
                    'importance': float(importancias[i])
                }
                for i in indices_top
            ]
        else:
            top_features = []
        
        reporte = {
            'modelo': self.mejor_modelo_nombre,
            'fecha_entrenamiento': datetime.now().isoformat(),
            'metricas_generales': self.resultados[self.mejor_modelo_nombre],
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'clases': list(self.label_encoder.classes_),
            'top_features': top_features,
            'total_features': len(self.feature_names),
            'total_train': len(self.X_train),
            'total_test': len(self.X_test)
        }
        
        # Guardar reporte
        reporte_path = MODELS_DIR / 'reporte_entrenamiento.json'
        with open(reporte_path, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Reporte guardado: {reporte_path}")
        
        # Mostrar reporte en consola
        logger.info("\n" + "=" * 60)
        logger.info("📊 REPORTE DE ENTRENAMIENTO")
        logger.info("=" * 60)
        logger.info(f"Modelo: {self.mejor_modelo_nombre}")
        logger.info(f"Accuracy: {self.resultados[self.mejor_modelo_nombre]['accuracy_test']:.3f}")
        logger.info(f"Precision: {self.resultados[self.mejor_modelo_nombre]['precision_test']:.3f}")
        logger.info(f"Recall: {self.resultados[self.mejor_modelo_nombre]['recall_test']:.3f}")
        logger.info(f"F1 Score: {self.resultados[self.mejor_modelo_nombre]['f1_test']:.3f}")
        logger.info("\nTop 10 Features Más Importantes:")
        for i, feat in enumerate(top_features[:10], 1):
            logger.info(f"  {i}. {feat['feature']}: {feat['importance']:.4f}")
        logger.info("=" * 60)
    
    def guardar_modelo(self):
        """Guarda el mejor modelo y sus componentes"""
        logger.info("💾 Guardando modelo...")
        
        if self.mejor_modelo is None:
            logger.error("❌ No hay modelo para guardar")
            return False
        
        try:
            # Guardar modelo
            modelo_path = MODELS_DIR / 'modelo_prediccion_fallos.pkl'
            joblib.dump(self.mejor_modelo, modelo_path)
            logger.info(f"✅ Modelo guardado: {modelo_path}")
            
            # Guardar scaler
            scaler_path = MODELS_DIR / 'scaler_prediccion_fallos.pkl'
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"✅ Scaler guardado: {scaler_path}")
            
            # Guardar label encoder
            encoder_path = MODELS_DIR / 'label_encoder_prediccion_fallos.pkl'
            joblib.dump(self.label_encoder, encoder_path)
            logger.info(f"✅ Label encoder guardado: {encoder_path}")
            
            # Guardar metadata
            metadata = {
                'modelo_tipo': self.mejor_modelo_nombre,
                'fecha_entrenamiento': datetime.now().isoformat(),
                'feature_names': self.feature_names,
                'clases': list(self.label_encoder.classes_),
                'metricas': self.resultados[self.mejor_modelo_nombre],
                'archivos': {
                    'modelo': str(modelo_path),
                    'scaler': str(scaler_path),
                    'label_encoder': str(encoder_path)
                }
            }
            
            metadata_path = MODELS_DIR / 'metadata_modelo.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Metadata guardada: {metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {e}")
            return False
    
    def ejecutar(self):
        """Ejecuta el proceso completo de entrenamiento"""
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO ENTRENAMIENTO DE MODELO DE PREDICCIÓN DE FALLOS")
        logger.info("=" * 60)
        
        # 1. Cargar dataset
        if not self.cargar_dataset():
            return False
        
        # 2. Preparar datos
        if not self.preparar_datos():
            return False
        
        # 3. Entrenar modelos
        logger.info("\n🎯 Entrenando modelos...")
        self.resultados['random_forest'] = self.entrenar_random_forest()
        self.resultados['xgboost'] = self.entrenar_xgboost()
        self.resultados['gradient_boosting'] = self.entrenar_gradient_boosting()
        
        # 4. Seleccionar mejor modelo
        self.seleccionar_mejor_modelo()
        
        # 5. Generar reporte
        self.generar_reporte_detallado()
        
        # 6. Guardar modelo
        if not self.guardar_modelo():
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 60)
        
        return True

def main():
    """Función principal"""
    entrenador = EntrenadorPrediccionFallos()
    exito = entrenador.ejecutar()
    
    if exito:
        print("\n✅ Modelo de predicción de fallos entrenado exitosamente")
        print("\n📁 Archivos generados:")
        print("   - models/modelo_prediccion_fallos.pkl")
        print("   - models/scaler_prediccion_fallos.pkl")
        print("   - models/label_encoder_prediccion_fallos.pkl")
        print("   - models/metadata_modelo.json")
        print("   - models/reporte_entrenamiento.json")
        print("\n📝 Siguiente paso: Integrar el modelo en la aplicación")
    else:
        print("\n❌ Error en el entrenamiento del modelo")
    
    return 0 if exito else 1

if __name__ == '__main__':
    raise SystemExit(main())
