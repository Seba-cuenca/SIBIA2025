#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISIS DE DATOS REALES PARA AJUSTAR REGLAS DE ETIQUETADO
===========================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

def analizar_datos():
    """Analiza los valores reales de los datos"""
    print("=" * 60)
    print("📊 ANÁLISIS DE DATOS REALES")
    print("=" * 60)
    
    # Cargar datos
    df = pd.read_parquet(DATA_DIR / 'historico_planta.parquet')
    
    # Filtrar solo datos con sensores válidos
    columnas_sensores = ['co2_bio040_pct', 'co2_bio050_pct', 'o2_bio040_pct', 'o2_bio050_pct']
    columnas_disponibles = [col for col in columnas_sensores if col in df.columns]
    
    if columnas_disponibles:
        mask = df[columnas_disponibles].notna().any(axis=1)
        df = df[mask]
    
    print(f"\n📈 Total registros con datos: {len(df)}")
    print(f"\n🔍 ESTADÍSTICAS DESCRIPTIVAS:\n")
    
    # Analizar cada columna
    for col in columnas_sensores:
        if col in df.columns:
            datos = df[col].dropna()
            if len(datos) > 0:
                print(f"📊 {col}:")
                print(f"   Registros: {len(datos)}")
                print(f"   Min: {datos.min():.2f}")
                print(f"   25%: {datos.quantile(0.25):.2f}")
                print(f"   50% (mediana): {datos.median():.2f}")
                print(f"   75%: {datos.quantile(0.75):.2f}")
                print(f"   Max: {datos.max():.2f}")
                print(f"   Promedio: {datos.mean():.2f}")
                print(f"   Desv. Std: {datos.std():.2f}")
                print()
    
    # Calcular promedios
    if 'co2_bio040_pct' in df.columns and 'co2_bio050_pct' in df.columns:
        df['co2_promedio'] = df[['co2_bio040_pct', 'co2_bio050_pct']].mean(axis=1)
        print(f"📊 CO2 PROMEDIO:")
        datos = df['co2_promedio'].dropna()
        print(f"   Min: {datos.min():.2f}")
        print(f"   Mediana: {datos.median():.2f}")
        print(f"   Max: {datos.max():.2f}")
        print(f"   Promedio: {datos.mean():.2f}")
        print()
    
    if 'o2_bio040_pct' in df.columns and 'o2_bio050_pct' in df.columns:
        df['o2_promedio'] = df[['o2_bio040_pct', 'o2_bio050_pct']].mean(axis=1)
        print(f"📊 O2 PROMEDIO:")
        datos = df['o2_promedio'].dropna()
        print(f"   Min: {datos.min():.2f}")
        print(f"   Mediana: {datos.median():.2f}")
        print(f"   Max: {datos.max():.2f}")
        print(f"   Promedio: {datos.mean():.2f}")
        print()
    
    # Sugerir reglas basadas en percentiles
    print("=" * 60)
    print("💡 REGLAS SUGERIDAS (basadas en los datos reales):")
    print("=" * 60)
    
    if 'co2_promedio' in df.columns:
        co2 = df['co2_promedio'].dropna()
        p25 = co2.quantile(0.25)
        p75 = co2.quantile(0.75)
        print(f"\n🟢 CO2 Óptimo: {p25:.1f} - {p75:.1f}%")
        print(f"🟡 CO2 Normal: {p25*.8:.1f} - {p25:.1f}% o {p75:.1f} - {p75*1.2:.1f}%")
        print(f"🟠 CO2 Alerta: < {p25*.8:.1f}% o > {p75*1.2:.1f}%")
        print(f"🔴 CO2 Crítico: < {p25*.6:.1f}% o > {p75*1.4:.1f}%")
    
    if 'o2_promedio' in df.columns:
        o2 = df['o2_promedio'].dropna()
        p75 = o2.quantile(0.75)
        p90 = o2.quantile(0.90)
        p95 = o2.quantile(0.95)
        print(f"\n🟢 O2 Óptimo: < {p75:.1f}%")
        print(f"🟡 O2 Normal: {p75:.1f} - {p90:.1f}%")
        print(f"🟠 O2 Alerta: {p90:.1f} - {p95:.1f}%")
        print(f"🔴 O2 Crítico: > {p95:.1f}%")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    analizar_datos()
