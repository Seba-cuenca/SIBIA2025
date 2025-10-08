#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE REENTRENAMIENTO AUTOMÁTICO DE MODELOS ML
==================================================

Reentrenar modelos automáticamente cuando hay suficientes datos nuevos.

Autor: SIBIA - Sistema Inteligente de Biogás Avanzado
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

from sistema_recoleccion_datos_ml import recolector_ml

logger = logging.getLogger(__name__)

class ReentrenadorML:
    """Sistema automático de reentrenamiento de modelos ML"""
    
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.recolector = recolector_ml
        
        # Umbrales mínimos para reentrenar
        self.min_datos_fallos = 100
        self.min_datos_inhibicion = 50
        self.min_datos_optimizacion = 30
        
        # Historial de reentrenamientos
        self.historial_file = os.path.join(models_dir, 'historial_reentrenamiento.json')
        
    def reentrenar_prediccion_fallos(self, forzar: bool = False) -> Dict[str, Any]:
        """
        Reentrenar modelo de predicción de fallos con datos reales
        
        Args:
            forzar: Si True, reentrenar aunque no haya suficientes datos
            
        Returns:
            Resultado del reentrenamiento
        """
        try:
            logger.info("🔄 Iniciando reentrenamiento de Predicción de Fallos...")
            
            # Obtener datos verificados
            datos_nuevos = self.recolector.obtener_datos_para_reentrenamiento('fallos', solo_verificados=True)
            
            if len(datos_nuevos) < self.min_datos_fallos and not forzar:
                logger.info(f"⏳ Insuficientes datos ({len(datos_nuevos)}/{self.min_datos_fallos}). Esperando más datos...")
                return {
                    'status': 'esperando',
                    'datos_actuales': len(datos_nuevos),
                    'datos_necesarios': self.min_datos_fallos
                }
            
            # Preparar dataset
            registros = []
            for dato in datos_nuevos:
                entrada = dato['datos_entrada']
                entrada['resultado'] = dato['resultado_real']
                registros.append(entrada)
            
            df = pd.DataFrame(registros)
            
            # Separar features y target
            feature_names = [col for col in df.columns if col != 'resultado']
            X = df[feature_names]
            y = df['resultado']
            
            # Codificar labels
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)
            
            # Split datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
            
            # Escalar
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entrenar nuevo modelo
            modelo = RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            modelo.fit(X_train_scaled, y_train)
            
            # Evaluar
            y_pred = modelo.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores = cross_val_score(modelo, X_train_scaled, y_train, cv=5)
            
            # Cargar modelo anterior para comparar
            modelo_anterior_path = os.path.join(self.models_dir, 'modelo_prediccion_fallos.pkl')
            accuracy_anterior = self._obtener_accuracy_anterior('prediccion_fallos')
            
            logger.info(f"📊 Accuracy anterior: {accuracy_anterior:.2%}")
            logger.info(f"📊 Accuracy nuevo: {accuracy:.2%}")
            
            # Guardar solo si mejoró o es primer entrenamiento
            if accuracy >= accuracy_anterior * 0.95:  # Permitir 5% de margen
                # Guardar modelo
                joblib.dump(modelo, modelo_anterior_path)
                joblib.dump(scaler, os.path.join(self.models_dir, 'scaler_prediccion_fallos.pkl'))
                joblib.dump(label_encoder, os.path.join(self.models_dir, 'label_encoder_prediccion_fallos.pkl'))
                
                # Guardar metadata
                metadata = {
                    'feature_names': feature_names,
                    'clases': label_encoder.classes_.tolist(),
                    'metricas': {
                        'accuracy': float(accuracy),
                        'cv_mean': float(cv_scores.mean()),
                        'cv_std': float(cv_scores.std())
                    },
                    'entrenamiento': {
                        'fecha': datetime.now().isoformat(),
                        'n_muestras': len(df),
                        'n_muestras_train': len(X_train),
                        'n_muestras_test': len(X_test),
                        'datos_reales': True
                    }
                }
                
                metadata_path = os.path.join(self.models_dir, 'metadata_modelo.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                self._registrar_reentrenamiento('prediccion_fallos', accuracy, len(df))
                
                logger.info(f"✅ Modelo de Predicción de Fallos reentrenado exitosamente")
                logger.info(f"   Accuracy: {accuracy:.2%} (anterior: {accuracy_anterior:.2%})")
                logger.info(f"   Datos: {len(df)} muestras reales")
                
                return {
                    'status': 'success',
                    'accuracy_nuevo': accuracy,
                    'accuracy_anterior': accuracy_anterior,
                    'mejora': accuracy - accuracy_anterior,
                    'datos_usados': len(df)
                }
            else:
                logger.warning(f"⚠️ Nuevo modelo tiene accuracy inferior ({accuracy:.2%} vs {accuracy_anterior:.2%}). No se guarda.")
                return {
                    'status': 'no_guardado',
                    'razon': 'accuracy_inferior',
                    'accuracy_nuevo': accuracy,
                    'accuracy_anterior': accuracy_anterior
                }
                
        except Exception as e:
            logger.error(f"Error reentrenando Predicción de Fallos: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}
    
    def reentrenar_inhibicion(self, forzar: bool = False) -> Dict[str, Any]:
        """
        Reentrenar modelo de inhibición con datos reales
        """
        try:
            logger.info("🔄 Iniciando reentrenamiento de Inhibición...")
            
            datos_nuevos = self.recolector.obtener_datos_para_reentrenamiento('inhibicion', solo_verificados=True)
            
            if len(datos_nuevos) < self.min_datos_inhibicion and not forzar:
                logger.info(f"⏳ Insuficientes datos ({len(datos_nuevos)}/{self.min_datos_inhibicion}). Esperando más datos...")
                return {
                    'status': 'esperando',
                    'datos_actuales': len(datos_nuevos),
                    'datos_necesarios': self.min_datos_inhibicion
                }
            
            # Preparar dataset
            registros = []
            for dato in datos_nuevos:
                sensores = dato['datos_sensores']
                sensores['nivel_inhibicion'] = dato['estado_real']
                registros.append(sensores)
            
            df = pd.DataFrame(registros)
            
            # Separar features y target
            caracteristicas = [col for col in df.columns if col != 'nivel_inhibicion']
            X = df[caracteristicas]
            y = df['nivel_inhibicion']
            
            # Codificar labels
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)
            
            # Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
            
            # Escalar
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entrenar
            modelo = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            modelo.fit(X_train_scaled, y_train)
            
            # Evaluar
            y_pred = modelo.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores = cross_val_score(modelo, X_train_scaled, y_train, cv=5)
            
            # Comparar con anterior
            accuracy_anterior = self._obtener_accuracy_anterior('inhibicion')
            
            logger.info(f"📊 Accuracy anterior: {accuracy_anterior:.2%}")
            logger.info(f"📊 Accuracy nuevo: {accuracy:.2%}")
            
            if accuracy >= accuracy_anterior * 0.95:
                # Guardar modelo (aquí deberías guardarlo en el objeto ModeloMLInhibicionBiodigestores)
                # Por ahora guardamos como pickle independiente
                inhibicion_model_path = os.path.join(self.models_dir, 'modelo_inhibicion_reentrenado.pkl')
                joblib.dump({
                    'modelo': modelo,
                    'scaler': scaler,
                    'label_encoder': label_encoder,
                    'caracteristicas': caracteristicas
                }, inhibicion_model_path)
                
                self._registrar_reentrenamiento('inhibicion', accuracy, len(df))
                
                logger.info(f"✅ Modelo de Inhibición reentrenado exitosamente")
                logger.info(f"   Accuracy: {accuracy:.2%} (anterior: {accuracy_anterior:.2%})")
                
                return {
                    'status': 'success',
                    'accuracy_nuevo': accuracy,
                    'accuracy_anterior': accuracy_anterior,
                    'mejora': accuracy - accuracy_anterior,
                    'datos_usados': len(df)
                }
            else:
                logger.warning(f"⚠️ Nuevo modelo de inhibición tiene accuracy inferior. No se guarda.")
                return {
                    'status': 'no_guardado',
                    'razon': 'accuracy_inferior'
                }
                
        except Exception as e:
            logger.error(f"Error reentrenando Inhibición: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}
    
    def verificar_estado_reentrenamiento(self) -> Dict[str, Any]:
        """
        Verifica el estado actual del sistema de reentrenamiento
        """
        stats = self.recolector.obtener_estadisticas()
        historial = self._cargar_historial()
        
        return {
            'datos_recolectados': stats,
            'ultimo_reentrenamiento': historial,
            'listo_para_reentrenar': {
                'prediccion_fallos': stats.get('prediccion_fallos', {}).get('listo_reentrenar', False),
                'inhibicion': stats.get('inhibicion', {}).get('listo_reentrenar', False),
                'optimizacion': stats.get('optimizacion', {}).get('listo_reentrenar', False)
            }
        }
    
    def _obtener_accuracy_anterior(self, tipo_modelo: str) -> float:
        """Obtiene accuracy del modelo anterior desde historial"""
        historial = self._cargar_historial()
        
        if tipo_modelo in historial and historial[tipo_modelo]:
            return historial[tipo_modelo][-1].get('accuracy', 0.0)
        
        # Valores por defecto si no hay historial
        defaults = {
            'prediccion_fallos': 1.0,
            'inhibicion': 0.95
        }
        return defaults.get(tipo_modelo, 0.0)
    
    def _registrar_reentrenamiento(self, tipo_modelo: str, accuracy: float, n_datos: int):
        """Registra un reentrenamiento en el historial"""
        historial = self._cargar_historial()
        
        if tipo_modelo not in historial:
            historial[tipo_modelo] = []
        
        historial[tipo_modelo].append({
            'fecha': datetime.now().isoformat(),
            'accuracy': float(accuracy),
            'n_datos': n_datos
        })
        
        self._guardar_historial(historial)
    
    def _cargar_historial(self) -> Dict[str, List]:
        """Carga historial de reentrenamientos"""
        if os.path.exists(self.historial_file):
            try:
                with open(self.historial_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _guardar_historial(self, historial: Dict):
        """Guarda historial de reentrenamientos"""
        with open(self.historial_file, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)


# Instancia global
reentrenador_ml = ReentrenadorML()

if __name__ == "__main__":
    # Test del reentrenador
    print("🧪 Probando sistema de reentrenamiento...")
    
    reentrenador = ReentrenadorML()
    
    # Verificar estado
    estado = reentrenador.verificar_estado_reentrenamiento()
    print("\n📊 Estado del sistema:")
    print(json.dumps(estado, indent=2))
    
    print("\n✅ Sistema de reentrenamiento funcionando correctamente")
