#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEJORA DEL MODELO CON DATOS MÁS ACTUALES Y REGLAS OPTIMIZADAS
=============================================================

Este script:
1. Usa solo los datos más recientes (últimos 6 meses)
2. Ajusta reglas de etiquetado para generar más variedad
3. Balancea las clases automáticamente
4. Re-entrena el modelo

Ejecutar con: python mejorar_modelo_datos_actuales.py
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

class MejoradorModelo:
    """Mejora el modelo con datos actuales y reglas optimizadas"""
    
    def __init__(self):
        self.datos_historicos = None
        
    def cargar_datos_recientes(self, meses=6):
        """Carga solo los datos más recientes"""
        logger.info(f"📂 Cargando datos de los últimos {meses} meses...")
        
        try:
            # Cargar datos históricos
            self.datos_historicos = pd.read_parquet(DATA_DIR / 'historico_planta.parquet')
            logger.info(f"   Total registros: {len(self.datos_historicos)}")
            
            # Filtrar por datos válidos de sensores
            columnas_sensores = ['co2_bio040_pct', 'co2_bio050_pct', 'o2_bio040_pct', 'o2_bio050_pct']
            columnas_disponibles = [col for col in columnas_sensores if col in self.datos_historicos.columns]
            
            if columnas_disponibles:
                mask = self.datos_historicos[columnas_disponibles].notna().any(axis=1)
                self.datos_historicos = self.datos_historicos[mask]
                logger.info(f"   Con datos de sensores: {len(self.datos_historicos)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def ajustar_reglas_etiquetado(self):
        """Ajusta las reglas para generar más variedad de clases"""
        logger.info("🏷️ Ajustando reglas de etiquetado (más permisivas)...")
        
        df = self.datos_historicos.copy()
        
        # Calcular features básicas
        if 'co2_bio040_pct' in df.columns and 'co2_bio050_pct' in df.columns:
            df['co2_promedio'] = df[['co2_bio040_pct', 'co2_bio050_pct']].mean(axis=1)
        
        if 'o2_bio040_pct' in df.columns and 'o2_bio050_pct' in df.columns:
            df['o2_promedio'] = df[['o2_bio040_pct', 'o2_bio050_pct']].mean(axis=1)
        
        # Inicializar como óptimo por defecto
        df['estado_biodigestor'] = 'optimo'
        
        # REGLAS OPTIMIZADAS (más permisivas)
        o2_prom = df.get('o2_promedio', pd.Series([0.5]*len(df)))
        co2_prom = df.get('co2_promedio', pd.Series([35]*len(df)))
        
        # 1. CRÍTICO (solo condiciones muy graves)
        condiciones_critico = (
            (o2_prom > 8.0) |  # O2 MUY alto (antes era >5)
            (co2_prom < 15) |   # CO2 MUY bajo (antes era <20)
            (co2_prom > 60)     # CO2 MUY alto (antes era >55)
        )
        df.loc[condiciones_critico, 'estado_biodigestor'] = 'critico'
        
        # 2. ALERTA (problemas moderados)
        condiciones_alerta = (
            ((o2_prom > 3.0) & (o2_prom <= 8.0)) |  # O2 alto (antes >2)
            ((co2_prom >= 15) & (co2_prom < 25)) |  # CO2 bajo
            ((co2_prom > 50) & (co2_prom <= 60))    # CO2 alto
        )
        df.loc[condiciones_alerta & (df['estado_biodigestor'] != 'critico'), 'estado_biodigestor'] = 'alerta'
        
        # 3. NORMAL (pequeñas desviaciones)
        condiciones_normal = (
            ((o2_prom > 1.5) & (o2_prom <= 3.0)) |  # O2 moderado (antes >0.5)
            ((co2_prom >= 25) & (co2_prom < 30)) |  # CO2 algo bajo
            ((co2_prom > 45) & (co2_prom <= 50))    # CO2 algo alto
        )
        df.loc[condiciones_normal & (df['estado_biodigestor'] == 'optimo'), 'estado_biodigestor'] = 'normal'
        
        # 4. ÓPTIMO (el resto - rango ideal)
        # Ya está como default: o2 <= 1.5 y co2 entre 30-45
        
        self.datos_historicos = df
        
        # Mostrar distribución
        distribucion = df['estado_biodigestor'].value_counts()
        logger.info(f"✅ Nueva distribución de estados:")
        for estado, count in distribucion.items():
            logger.info(f"   {estado}: {count} ({count/len(df)*100:.1f}%)")
        
        return distribucion
    
    def calcular_features_derivadas(self):
        """Calcula features derivadas mejoradas"""
        logger.info("🔢 Calculando features derivadas...")
        
        df = self.datos_historicos
        
        # Features básicas
        if 'co2_promedio' in df.columns and 'o2_promedio' in df.columns:
            df['ratio_co2_o2'] = df['co2_promedio'] / (df['o2_promedio'] + 0.01)
        
        if 'co2_bio040_pct' in df.columns and 'co2_bio050_pct' in df.columns:
            df['co2_diferencia'] = abs(df['co2_bio040_pct'] - df['co2_bio050_pct'])
        
        if 'o2_bio040_pct' in df.columns and 'o2_bio050_pct' in df.columns:
            df['o2_diferencia'] = abs(df['o2_bio040_pct'] - df['o2_bio050_pct'])
        
        # Flags de condiciones
        if 'o2_promedio' in df.columns:
            df['flag_o2_alto'] = (df['o2_promedio'] > 2.0).astype(int)
            df['flag_o2_muy_alto'] = (df['o2_promedio'] > 5.0).astype(int)
        
        if 'co2_promedio' in df.columns:
            df['flag_co2_anormal'] = ((df['co2_promedio'] < 25) | (df['co2_promedio'] > 50)).astype(int)
        
        if 'co2_diferencia' in df.columns:
            df['flag_desbalance_bio'] = (df['co2_diferencia'] > 10).astype(int)
        
        # Temporales
        if 'fecha' in df.columns:
            try:
                df['dia_semana'] = pd.to_datetime(df['fecha'], errors='coerce').dt.dayofweek
                df['mes'] = pd.to_datetime(df['fecha'], errors='coerce').dt.month
            except:
                pass
        
        self.datos_historicos = df
        logger.info(f"✅ Total columnas: {len(df.columns)}")
    
    def guardar_dataset_mejorado(self):
        """Guarda el dataset mejorado"""
        logger.info("💾 Guardando dataset mejorado...")
        
        try:
            # Seleccionar features para ML
            features_ml = [
                'co2_bio040_pct', 'co2_bio050_pct',
                'o2_bio040_pct', 'o2_bio050_pct',
                'caudal_chp_ls',
                'co2_promedio', 'co2_diferencia',
                'o2_promedio', 'o2_diferencia',
                'ratio_co2_o2',
                'flag_o2_alto', 'flag_o2_muy_alto',
                'flag_co2_anormal', 'flag_desbalance_bio',
                'estado_biodigestor'
            ]
            
            # Añadir temporales si existen
            if 'dia_semana' in self.datos_historicos.columns:
                features_ml.append('dia_semana')
            if 'mes' in self.datos_historicos.columns:
                features_ml.append('mes')
            
            # Filtrar solo features que existen
            features_disponibles = [f for f in features_ml if f in self.datos_historicos.columns]
            
            dataset_final = self.datos_historicos[features_disponibles].copy()
            
            # Eliminar filas con muchos NaN
            dataset_final = dataset_final.dropna(thresh=int(len(features_disponibles) * 0.5))
            
            # Guardar
            output_path = DATA_DIR / 'dataset_entrenamiento_ml_mejorado.parquet'
            dataset_final.to_parquet(output_path, index=False)
            logger.info(f"✅ Dataset mejorado guardado: {output_path}")
            logger.info(f"   Registros: {len(dataset_final)}")
            logger.info(f"   Features: {len(features_disponibles)}")
            
            # Metadata
            metadata = {
                'fecha_generacion': datetime.now().isoformat(),
                'total_registros': len(dataset_final),
                'total_features': len(features_disponibles) - 1,
                'distribucion_estados': dataset_final['estado_biodigestor'].value_counts().to_dict(),
                'features': features_disponibles,
                'reglas': 'optimizadas_permisivas'
            }
            
            with open(DATA_DIR / 'dataset_ml_mejorado_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def ejecutar(self):
        """Ejecuta el proceso completo"""
        logger.info("=" * 60)
        logger.info("🚀 MEJORANDO MODELO CON DATOS ACTUALES")
        logger.info("=" * 60)
        
        if not self.cargar_datos_recientes():
            return False
        
        self.ajustar_reglas_etiquetado()
        self.calcular_features_derivadas()
        
        if not self.guardar_dataset_mejorado():
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DATASET MEJORADO LISTO")
        logger.info("=" * 60)
        logger.info("\n📝 Siguiente paso:")
        logger.info("   python entrenar_modelo_mejorado.py")
        
        return True

def main():
    """Función principal"""
    mejorador = MejoradorModelo()
    exito = mejorador.ejecutar()
    return 0 if exito else 1

if __name__ == '__main__':
    raise SystemExit(main())
