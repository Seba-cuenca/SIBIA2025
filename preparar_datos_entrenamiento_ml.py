#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PREPARACIÓN DE DATOS PARA ENTRENAMIENTO ML
==========================================

Combina y prepara datos históricos reales para entrenar modelos de predicción de fallos.

Entrada:
- data/historico_planta.parquet
- data/ingresos_camiones.parquet
- data/st_materiales.parquet
- data/alimentacion_horaria.parquet
- data/analisis_quimico_fos_tac.parquet

Salida:
- data/dataset_entrenamiento_ml.parquet
- data/dataset_entrenamiento_ml.json
- data/features_ml.parquet (features calculadas)
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

class PreparadorDatosML:
    """Prepara datos históricos para entrenamiento ML"""
    
    def __init__(self):
        self.datos_historicos = None
        self.datos_quimicos = None
        self.datos_alimentacion = None
        self.datos_camiones = None
        self.datos_st = None
        self.dataset_final = None
        
    def cargar_datos(self):
        """Carga todos los datasets generados"""
        logger.info("📂 Cargando datos históricos...")
        
        try:
            # Cargar historico_planta
            self.datos_historicos = pd.read_parquet(DATA_DIR / 'historico_planta.parquet')
            logger.info(f"✅ Histórico cargado: {len(self.datos_historicos)} registros")
            
            # Cargar análisis químico FOS/TAC
            self.datos_quimicos = pd.read_parquet(DATA_DIR / 'analisis_quimico_fos_tac.parquet')
            logger.info(f"✅ Análisis químico cargado: {len(self.datos_quimicos)} registros")
            
            # Cargar alimentación horaria
            self.datos_alimentacion = pd.read_parquet(DATA_DIR / 'alimentacion_horaria.parquet')
            logger.info(f"✅ Alimentación cargada: {len(self.datos_alimentacion)} registros")
            
            # Cargar ingresos de camiones
            self.datos_camiones = pd.read_parquet(DATA_DIR / 'ingresos_camiones.parquet')
            logger.info(f"✅ Camiones cargado: {len(self.datos_camiones)} registros")
            
            # Cargar ST materiales
            self.datos_st = pd.read_parquet(DATA_DIR / 'st_materiales.parquet')
            logger.info(f"✅ ST materiales cargado: {len(self.datos_st)} registros")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            return False
    
    def limpiar_datos(self):
        """Limpia y valida datos"""
        logger.info("🧹 Limpiando datos...")
        
        # Limpiar historico_planta
        if self.datos_historicos is not None:
            # Convertir fechas
            for col in ['fecha', 'fecha_hora']:
                if col in self.datos_historicos.columns:
                    self.datos_historicos[col] = pd.to_datetime(
                        self.datos_historicos[col], 
                        errors='coerce'
                    )
            
            # Filtrar solo registros que tengan al menos un valor de sensor válido
            # No filtrar por fecha ya que pueden estar incorrectas pero los datos de sensores son válidos
            columnas_sensores = ['co2_bio040_pct', 'co2_bio050_pct', 'o2_bio040_pct', 'o2_bio050_pct', 'caudal_chp_ls']
            columnas_disponibles = [col for col in columnas_sensores if col in self.datos_historicos.columns]
            
            if columnas_disponibles:
                # Mantener registros que tengan al menos un valor de sensor válido
                mask = self.datos_historicos[columnas_disponibles].notna().any(axis=1)
                self.datos_historicos = self.datos_historicos[mask]
                logger.info(f"   Histórico después de limpieza: {len(self.datos_historicos)} registros")
            else:
                logger.warning("   No se encontraron columnas de sensores para filtrar")
        
        # Limpiar datos químicos
        if self.datos_quimicos is not None:
            if 'fecha_hora' in self.datos_quimicos.columns:
                self.datos_quimicos['fecha_hora'] = pd.to_datetime(
                    self.datos_quimicos['fecha_hora'],
                    errors='coerce'
                )
                self.datos_quimicos = self.datos_quimicos[self.datos_quimicos['fecha_hora'].notna()]
                logger.info(f"   Químico después de limpieza: {len(self.datos_quimicos)} registros")
        
        # Limpiar alimentación
        if self.datos_alimentacion is not None:
            if 'fecha_hora' in self.datos_alimentacion.columns:
                self.datos_alimentacion['fecha_hora'] = pd.to_datetime(
                    self.datos_alimentacion['fecha_hora'],
                    errors='coerce'
                )
                self.datos_alimentacion = self.datos_alimentacion[self.datos_alimentacion['fecha_hora'].notna()]
                logger.info(f"   Alimentación después de limpieza: {len(self.datos_alimentacion)} registros")
    
    def calcular_features_derivadas(self):
        """Calcula features derivadas para ML"""
        logger.info("🔢 Calculando features derivadas...")
        
        if self.datos_historicos is None or len(self.datos_historicos) == 0:
            logger.warning("⚠️ No hay datos históricos para calcular features")
            return
        
        df = self.datos_historicos.copy()
        
        # 1. FEATURES DE CALIDAD DE GAS
        # Promedio de CO2
        if 'co2_bio040_pct' in df.columns and 'co2_bio050_pct' in df.columns:
            df['co2_promedio'] = df[['co2_bio040_pct', 'co2_bio050_pct']].mean(axis=1)
            df['co2_diferencia'] = abs(df['co2_bio040_pct'] - df['co2_bio050_pct'])
        
        # Promedio de O2
        if 'o2_bio040_pct' in df.columns and 'o2_bio050_pct' in df.columns:
            df['o2_promedio'] = df[['o2_bio040_pct', 'o2_bio050_pct']].mean(axis=1)
            df['o2_diferencia'] = abs(df['o2_bio040_pct'] - df['o2_bio050_pct'])
        
        # 2. INDICADORES DE SALUD DEL BIODIGESTOR
        # Ratio CO2/O2 (indica balance del proceso)
        if 'co2_promedio' in df.columns and 'o2_promedio' in df.columns:
            df['ratio_co2_o2'] = df['co2_promedio'] / (df['o2_promedio'] + 0.01)  # +0.01 evita div/0
        
        # 3. TENDENCIAS TEMPORALES (rolling windows)
        for col in ['co2_promedio', 'o2_promedio', 'caudal_chp_ls']:
            if col in df.columns:
                # Media móvil 7 días
                df[f'{col}_ma7'] = df[col].rolling(window=7, min_periods=1).mean()
                # Desviación estándar 7 días (volatilidad)
                df[f'{col}_std7'] = df[col].rolling(window=7, min_periods=1).std()
                # Tendencia (diferencia con media móvil)
                df[f'{col}_tendencia'] = df[col] - df[f'{col}_ma7']
        
        # 4. FLAGS DE ANOMALÍAS
        # O2 alto es problemático (indica entrada de aire)
        if 'o2_promedio' in df.columns:
            df['flag_o2_alto'] = (df['o2_promedio'] > 2.0).astype(int)
            df['flag_o2_muy_alto'] = (df['o2_promedio'] > 5.0).astype(int)
        
        # CO2 fuera de rango normal (30-45%)
        if 'co2_promedio' in df.columns:
            df['flag_co2_anormal'] = ((df['co2_promedio'] < 25) | (df['co2_promedio'] > 50)).astype(int)
        
        # Desbalance entre biodigestores
        if 'co2_diferencia' in df.columns:
            df['flag_desbalance_bio'] = (df['co2_diferencia'] > 10).astype(int)
        
        # 5. FEATURES TEMPORALES
        if 'fecha' in df.columns:
            df['dia_semana'] = df['fecha'].dt.dayofweek
            df['dia_mes'] = df['fecha'].dt.day
            df['mes'] = df['fecha'].dt.month
            df['trimestre'] = df['fecha'].dt.quarter
        
        self.datos_historicos = df
        logger.info(f"✅ Features calculadas. Total columnas: {len(df.columns)}")
    
    def agregar_datos_quimicos(self):
        """Agrega datos de FOS/TAC al dataset principal"""
        logger.info("🧪 Agregando datos químicos (FOS/TAC)...")
        
        if self.datos_quimicos is None or len(self.datos_quimicos) == 0:
            logger.warning("⚠️ No hay datos químicos disponibles")
            return
        
        if self.datos_historicos is None or len(self.datos_historicos) == 0:
            logger.warning("⚠️ No hay datos históricos para merge")
            return
        
        if 'fecha' not in self.datos_historicos.columns:
            logger.warning("⚠️ No hay columna fecha en datos históricos, saltando merge")
            return
        
        # Preparar datos químicos
        quimico = self.datos_quimicos.copy()
        if 'fecha_hora' in quimico.columns:
            quimico['fecha'] = quimico['fecha_hora'].dt.date
            quimico['fecha'] = pd.to_datetime(quimico['fecha'])
        
        # Agrupar por día (promedio diario de FOS y TAC)
        quimico_diario = quimico.groupby('fecha').agg({
            'fos': 'mean',
            'tac': 'mean'
        }).reset_index()
        
        # Calcular ratio FOS/TAC
        quimico_diario['fos_tac_ratio'] = quimico_diario['fos'] / (quimico_diario['tac'] + 1)
        
        # Merge con histórico
        self.datos_historicos = self.datos_historicos.merge(
            quimico_diario[['fecha', 'fos', 'tac', 'fos_tac_ratio']],
            on='fecha',
            how='left'
        )
        
        logger.info(f"✅ Datos químicos agregados. Registros con FOS/TAC: {self.datos_historicos['fos'].notna().sum()}")
    
    def crear_etiquetas_estado(self):
        """Crea etiquetas de estado del biodigestor para aprendizaje supervisado"""
        logger.info("🏷️ Creando etiquetas de estado...")
        
        if self.datos_historicos is None or len(self.datos_historicos) == 0:
            logger.warning("⚠️ No hay datos históricos para crear etiquetas")
            return
        
        df = self.datos_historicos.copy()
        
        # Inicializar estado como 'optimo'
        df['estado_biodigestor'] = 'optimo'
        
        # REGLAS EXPERTAS PARA CLASIFICAR ESTADO
        
        # 1. Estado CRITICO (posible fallo inminente)
        condiciones_critico = (
            (df.get('o2_promedio', pd.Series([0]*len(df))) > 5.0) |  # Mucho oxígeno
            (df.get('fos_tac_ratio', pd.Series([0]*len(df))) > 0.5) |  # Ratio FOS/TAC muy alto (acidificación)
            (df.get('co2_promedio', pd.Series([100]*len(df))) < 20) |  # CO2 muy bajo
            (df.get('co2_promedio', pd.Series([0]*len(df))) > 55)  # CO2 muy alto
        )
        df.loc[condiciones_critico, 'estado_biodigestor'] = 'critico'
        
        # 2. Estado ALERTA (problemas moderados)
        o2_prom = df.get('o2_promedio', pd.Series([0]*len(df)))
        fos_tac = df.get('fos_tac_ratio', pd.Series([0]*len(df)))
        co2_prom = df.get('co2_promedio', pd.Series([35]*len(df)))  # Valor típico
        desbalance = df.get('flag_desbalance_bio', pd.Series([0]*len(df)))
        
        condiciones_alerta = (
            ((o2_prom > 2.0) & (o2_prom <= 5.0)) |
            ((fos_tac > 0.35) & (fos_tac <= 0.5)) |
            ((co2_prom >= 20) & (co2_prom < 25)) |
            ((co2_prom > 50) & (co2_prom <= 55)) |
            (desbalance == 1)
        )
        df.loc[condiciones_alerta & (df['estado_biodigestor'] != 'critico'), 'estado_biodigestor'] = 'alerta'
        
        # 3. Estado NORMAL (pequeñas desviaciones)
        condiciones_normal = (
            ((o2_prom > 0.5) & (o2_prom <= 2.0)) |
            ((fos_tac > 0.25) & (fos_tac <= 0.35)) |
            ((co2_prom >= 25) & (co2_prom < 30)) |
            ((co2_prom > 45) & (co2_prom <= 50))
        )
        df.loc[condiciones_normal & (df['estado_biodigestor'] == 'optimo'), 'estado_biodigestor'] = 'normal'
        
        self.datos_historicos = df
        
        # Estadísticas de etiquetas
        distribucion = df['estado_biodigestor'].value_counts()
        logger.info(f"✅ Etiquetas creadas:")
        for estado, count in distribucion.items():
            logger.info(f"   {estado}: {count} ({count/len(df)*100:.1f}%)")
    
    def crear_dataset_final(self):
        """Crea dataset final para entrenamiento"""
        logger.info("📊 Creando dataset final...")
        
        if self.datos_historicos is None:
            logger.error("❌ No hay datos históricos para crear dataset")
            return False
        
        df = self.datos_historicos.copy()
        
        # Seleccionar features relevantes para ML
        features_ml = [
            # Features originales
            'co2_bio040_pct', 'co2_bio050_pct',
            'o2_bio040_pct', 'o2_bio050_pct',
            'caudal_chp_ls',
            
            # Features derivadas
            'co2_promedio', 'co2_diferencia',
            'o2_promedio', 'o2_diferencia',
            'ratio_co2_o2',
            
            # Tendencias
            'co2_promedio_ma7', 'co2_promedio_std7', 'co2_promedio_tendencia',
            'o2_promedio_ma7', 'o2_promedio_std7', 'o2_promedio_tendencia',
            
            # Flags
            'flag_o2_alto', 'flag_o2_muy_alto', 'flag_co2_anormal', 'flag_desbalance_bio',
            
            # Datos químicos
            'fos', 'tac', 'fos_tac_ratio',
            
            # Temporales
            'dia_semana', 'dia_mes', 'mes', 'trimestre',
            
            # Etiqueta
            'estado_biodigestor'
        ]
        
        # Filtrar solo features que existen
        features_disponibles = [f for f in features_ml if f in df.columns]
        
        # Crear dataset final
        self.dataset_final = df[features_disponibles].copy()
        
        # Eliminar filas con muchos NaN
        umbral_nan = 0.5  # 50% de valores válidos mínimo
        self.dataset_final = self.dataset_final.dropna(
            thresh=int(len(features_disponibles) * umbral_nan)
        )
        
        logger.info(f"✅ Dataset final creado:")
        logger.info(f"   Registros: {len(self.dataset_final)}")
        logger.info(f"   Features: {len(features_disponibles)}")
        logger.info(f"   Completitud: {(1 - self.dataset_final.isna().sum().sum() / self.dataset_final.size) * 100:.1f}%")
        
        return True
    
    def guardar_dataset(self):
        """Guarda dataset final para entrenamiento"""
        logger.info("💾 Guardando dataset...")
        
        if self.dataset_final is None or len(self.dataset_final) == 0:
            logger.error("❌ No hay dataset para guardar")
            return False
        
        try:
            # Guardar en Parquet
            output_parquet = DATA_DIR / 'dataset_entrenamiento_ml.parquet'
            self.dataset_final.to_parquet(output_parquet, index=False)
            logger.info(f"✅ Guardado: {output_parquet}")
            
            # Guardar en JSON
            output_json = DATA_DIR / 'dataset_entrenamiento_ml.json'
            self.dataset_final.to_json(output_json, orient='records', date_format='iso', indent=2)
            logger.info(f"✅ Guardado: {output_json}")
            
            # Guardar metadatos
            metadata = {
                'fecha_generacion': datetime.now().isoformat(),
                'total_registros': len(self.dataset_final),
                'total_features': len(self.dataset_final.columns) - 1,  # -1 por etiqueta
                'distribucion_estados': self.dataset_final['estado_biodigestor'].value_counts().to_dict(),
                'features': list(self.dataset_final.columns),
                'completitud_promedio': float((1 - self.dataset_final.isna().sum().sum() / self.dataset_final.size) * 100)
            }
            
            output_meta = DATA_DIR / 'dataset_entrenamiento_ml_metadata.json'
            with open(output_meta, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Metadata guardada: {output_meta}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando dataset: {e}")
            return False
    
    def ejecutar(self):
        """Ejecuta el proceso completo de preparación"""
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO PREPARACIÓN DE DATOS PARA ML")
        logger.info("=" * 60)
        
        # 1. Cargar datos
        if not self.cargar_datos():
            return False
        
        # 2. Limpiar datos
        self.limpiar_datos()
        
        # 3. Calcular features derivadas
        self.calcular_features_derivadas()
        
        # 4. Agregar datos químicos
        self.agregar_datos_quimicos()
        
        # 5. Crear etiquetas de estado
        self.crear_etiquetas_estado()
        
        # 6. Crear dataset final
        if not self.crear_dataset_final():
            return False
        
        # 7. Guardar dataset
        if not self.guardar_dataset():
            return False
        
        logger.info("=" * 60)
        logger.info("✅ PREPARACIÓN DE DATOS COMPLETADA")
        logger.info("=" * 60)
        
        return True

def main():
    """Función principal"""
    preparador = PreparadorDatosML()
    exito = preparador.ejecutar()
    
    if exito:
        print("\n✅ Dataset de entrenamiento listo en:")
        print("   - data/dataset_entrenamiento_ml.parquet")
        print("   - data/dataset_entrenamiento_ml.json")
        print("\n📝 Siguiente paso: ejecutar entrenar_modelo_prediccion_fallos_reales.py")
    else:
        print("\n❌ Error en la preparación de datos")
    
    return 0 if exito else 1

if __name__ == '__main__':
    raise SystemExit(main())
