#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENTRENAMIENTO CON REGLAS BASADAS EN DATOS REALES
================================================
Usa percentiles de los datos reales en lugar de valores teóricos
"""

import pandas as pd
import numpy as np
import json
import joblib
import logging
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'

class EntrenadorDatosReales:
    """Entrena modelo usando percentiles de datos reales"""
    
    def __init__(self):
        self.dataset = None
        self.modelo = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def preparar_datos_con_percentiles(self):
        """Prepara datos usando percentiles reales"""
        logger.info("📂 Cargando y preparando datos...")
        
        # Cargar datos históricos
        df = pd.read_parquet(DATA_DIR / 'historico_planta.parquet')
        
        # Filtrar datos válidos
        columnas_sensores = ['co2_bio040_pct', 'co2_bio050_pct', 'o2_bio040_pct', 'o2_bio050_pct']
        mask = df[columnas_sensores].notna().any(axis=1)
        df = df[mask]
        
        logger.info(f"   Registros: {len(df)}")
        
        # Calcular promedios
        df['co2_promedio'] = df[['co2_bio040_pct', 'co2_bio050_pct']].mean(axis=1)
        df['o2_promedio'] = df[['o2_bio040_pct', 'o2_bio050_pct']].mean(axis=1)
        df['co2_diferencia'] = abs(df['co2_bio040_pct'] - df['co2_bio050_pct'])
        df['o2_diferencia'] = abs(df['o2_bio040_pct'] - df['o2_bio050_pct'])
        df['ratio_co2_o2'] = df['co2_promedio'] / (df['o2_promedio'] + 0.01)
        
        # Calcular percentiles para reglas dinámicas
        co2_p25 = df['co2_promedio'].quantile(0.25)
        co2_p50 = df['co2_promedio'].quantile(0.50)
        co2_p75 = df['co2_promedio'].quantile(0.75)
        co2_p90 = df['co2_promedio'].quantile(0.90)
        
        o2_p50 = df['o2_promedio'].quantile(0.50)
        o2_p75 = df['o2_promedio'].quantile(0.75)
        o2_p90 = df['o2_promedio'].quantile(0.90)
        o2_p95 = df['o2_promedio'].quantile(0.95)
        
        logger.info(f"\n📊 Percentiles calculados:")
        logger.info(f"   CO2: P25={co2_p25:.2f}, P50={co2_p50:.2f}, P75={co2_p75:.2f}, P90={co2_p90:.2f}")
        logger.info(f"   O2: P50={o2_p50:.2f}, P75={o2_p75:.2f}, P90={o2_p90:.2f}, P95={o2_p95:.2f}")
        
        # CLASIFICAR BASADO EN PERCENTILES
        df['estado_biodigestor'] = 'optimo'  # Default
        
        # Crítico: valores en el 5% superior de O2 o extremos de CO2
        critico_mask = (
            (df['o2_promedio'] > o2_p95) |
            (df['co2_promedio'] > co2_p90) |
            (df['co2_promedio'] < co2_p25 * 0.5)
        )
        df.loc[critico_mask, 'estado_biodigestor'] = 'critico'
        
        # Alerta: valores entre P75-P90
        alerta_mask = (
            ((df['o2_promedio'] > o2_p75) & (df['o2_promedio'] <= o2_p95)) |
            ((df['co2_promedio'] > co2_p75) & (df['co2_promedio'] <= co2_p90)) |
            ((df['co2_promedio'] < co2_p25) & (df['co2_promedio'] >= co2_p25 * 0.5))
        )
        df.loc[alerta_mask & (df['estado_biodigestor'] != 'critico'), 'estado_biodigestor'] = 'alerta'
        
        # Normal: valores entre P50-P75
        normal_mask = (
            ((df['o2_promedio'] > o2_p50) & (df['o2_promedio'] <= o2_p75)) |
            ((df['co2_promedio'] > co2_p50) & (df['co2_promedio'] <= co2_p75)) |
            ((df['co2_promedio'] < co2_p50) & (df['co2_promedio'] >= co2_p25))
        )
        df.loc[normal_mask & (df['estado_biodigestor'] == 'optimo'), 'estado_biodigestor'] = 'normal'
        
        # Óptimo: el resto (entre P25-P50)
        
        # Mostrar distribución
        distribucion = df['estado_biodigestor'].value_counts()
        logger.info(f"\n✅ Distribución de estados:")
        for estado, count in distribucion.items():
            logger.info(f"   {estado}: {count} ({count/len(df)*100:.1f}%)")
        
        # Features para ML
        features = [
            'co2_bio040_pct', 'co2_bio050_pct',
            'o2_bio040_pct', 'o2_bio050_pct',
            'co2_promedio', 'o2_promedio',
            'co2_diferencia', 'o2_diferencia',
            'ratio_co2_o2'
        ]
        
        # Agregar caudal si existe
        if 'caudal_chp_ls' in df.columns:
            features.append('caudal_chp_ls')
        
        self.dataset = df[features + ['estado_biodigestor']].dropna()
        logger.info(f"\n📊 Dataset final: {len(self.dataset)} registros")
        
        return distribucion
    
    def entrenar_modelo(self):
        """Entrena el modelo Random Forest"""
        logger.info("\n🌲 Entrenando Random Forest...")
        
        # Preparar datos
        X = self.dataset.drop('estado_biodigestor', axis=1)
        y = self.dataset['estado_biodigestor']
        
        self.feature_names = list(X.columns)
        
        # Codificar etiquetas
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Escalar
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar
        self.modelo = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1
        )
        
        self.modelo.fit(X_train_scaled, y_train)
        
        # Evaluar
        y_pred = self.modelo.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Cross-validation
        cv_scores = cross_val_score(self.modelo, X_train_scaled, y_train, cv=5)
        
        logger.info(f"   ✅ Accuracy: {accuracy:.3f}")
        logger.info(f"   ✅ F1 Score: {f1:.3f}")
        logger.info(f"   ✅ CV Mean: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
        
        # Classification report
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            output_dict=True,
            zero_division=0
        )
        
        return {
            'accuracy': accuracy,
            'f1_score': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': report
        }
    
    def guardar_modelo(self, metricas):
        """Guarda el modelo entrenado"""
        logger.info("\n💾 Guardando modelo...")
        
        # Guardar componentes
        joblib.dump(self.modelo, MODELS_DIR / 'modelo_prediccion_fallos.pkl')
        joblib.dump(self.scaler, MODELS_DIR / 'scaler_prediccion_fallos.pkl')
        joblib.dump(self.label_encoder, MODELS_DIR / 'label_encoder_prediccion_fallos.pkl')
        
        # Metadata
        metadata = {
            'modelo_tipo': 'random_forest',
            'fecha_entrenamiento': datetime.now().isoformat(),
            'feature_names': self.feature_names,
            'clases': list(self.label_encoder.classes_),
            'metricas': metricas,
            'reglas': 'percentiles_datos_reales',
            'nota': 'Entrenado con reglas basadas en percentiles de datos reales'
        }
        
        with open(MODELS_DIR / 'metadata_modelo.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"   ✅ Modelo guardado en: {MODELS_DIR}")
    
    def ejecutar(self):
        """Ejecuta el proceso completo"""
        logger.info("=" * 60)
        logger.info("🚀 ENTRENAMIENTO CON DATOS REALES (PERCENTILES)")
        logger.info("=" * 60)
        
        self.preparar_datos_con_percentiles()
        metricas = self.entrenar_modelo()
        self.guardar_modelo(metricas)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ MODELO ENTRENADO Y GUARDADO")
        logger.info("=" * 60)
        logger.info("\n📝 Siguiente paso:")
        logger.info("   1. Recarga la app: Ctrl+C en Flask y python app_CORREGIDO_OK_FINAL.py")
        logger.info("   2. Prueba: python test_prediccion_fallos_api.py")
        logger.info("   3. Recarga navegador: Ctrl+F5")
        
        return True

def main():
    entrenador = EntrenadorDatosReales()
    exito = entrenador.ejecutar()
    return 0 if exito else 1

if __name__ == '__main__':
    raise SystemExit(main())
