#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug de calcular_mezcla_volumetrica_simple
Simula exactamente lo que hace la funcion para encontrar el problema
"""

import json

def debug_calcular_mezcla_volumetrica_simple():
    print("DEBUG DE CALCULAR_MEZCLA_VOLUMETRICA_SIMPLE")
    print("=" * 50)
    
    # Cargar stock
    with open('stock.json', 'r', encoding='utf-8') as f:
        stock_data = json.load(f)
    
    stock_actual = stock_data.get('materiales', {})
    
    # Simular config
    config = {
        'kw_objetivo': 28800,
        'porcentaje_solidos': 0.5,
        'porcentaje_liquidos': 0.4,
        'porcentaje_purin': 0.1,
        'max_materiales_solidos': 12
    }
    
    # Simular clasificacion de materiales
    materiales_solidos = {}
    materiales_liquidos = {}
    materiales_purin = {}
    
    for mat, datos in stock_actual.items():
        tipo = datos.get('tipo', 'solido').lower()
        stock_tn = float(datos.get('total_tn', 0))
        kw_tn = float(datos.get('kw_tn', 0) or 0)
        
        if stock_tn <= 0 or kw_tn <= 0:
            continue
            
        if 'purin' in mat.lower():
            materiales_purin[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
        elif tipo == 'liquido':
            materiales_liquidos[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
        else:
            materiales_solidos[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
    
    print(f"\n1. MATERIALES CLASIFICADOS:")
    print(f"   Solidos: {len(materiales_solidos)}")
    print(f"   Liquidos: {len(materiales_liquidos)}")
    print(f"   Purin: {len(materiales_purin)}")
    
    # Simular calculo de objetivos TN
    kw_objetivo = config['kw_objetivo']
    porcentaje_solidos = config['porcentaje_solidos']
    porcentaje_liquidos = config['porcentaje_liquidos']
    porcentaje_purin = config['porcentaje_purin']
    
    # Calcular eficiencia promedio
    kw_tn_solidos_promedio = 0.0
    kw_tn_liquidos_promedio = 0.0
    kw_tn_purin_promedio = 0.0
    
    if materiales_solidos:
        total_kw_solidos = 0
        count_solidos = 0
        for mat, datos in materiales_solidos.items():
            kw_tn = float(stock_actual[mat].get('kw_tn', 0) or 0)
            if kw_tn > 0:
                total_kw_solidos += kw_tn
                count_solidos += 1
        kw_tn_solidos_promedio = total_kw_solidos / count_solidos if count_solidos > 0 else 0.5
    
    if materiales_liquidos:
        total_kw_liquidos = 0
        count_liquidos = 0
        for mat, datos in materiales_liquidos.items():
            kw_tn = float(stock_actual[mat].get('kw_tn', 0) or 0)
            if kw_tn > 0:
                total_kw_liquidos += kw_tn
                count_liquidos += 1
        kw_tn_liquidos_promedio = total_kw_liquidos / count_liquidos if count_liquidos > 0 else 0.08
    
    if materiales_purin:
        total_kw_purin = 0
        count_purin = 0
        for mat, datos in materiales_purin.items():
            kw_tn = float(stock_actual[mat].get('kw_tn', 0) or 0)
            if kw_tn > 0:
                total_kw_purin += kw_tn
                count_purin += 1
        kw_tn_purin_promedio = total_kw_purin / count_purin if count_purin > 0 else 0.025
    
    print(f"\n2. EFICIENCIAS PROMEDIO:")
    print(f"   Solidos: {kw_tn_solidos_promedio:.6f}")
    print(f"   Liquidos: {kw_tn_liquidos_promedio:.6f}")
    print(f"   Purin: {kw_tn_purin_promedio:.6f}")
    
    # Calcular eficiencia ponderada
    eficiencia_promedio_ponderada = (kw_tn_solidos_promedio * porcentaje_solidos + 
                                   kw_tn_liquidos_promedio * porcentaje_liquidos + 
                                   kw_tn_purin_promedio * porcentaje_purin)
    
    print(f"\n3. EFICIENCIA PONDERADA: {eficiencia_promedio_ponderada:.6f}")
    
    # Calcular TN necesarias
    tn_exactas_para_objetivo = kw_objetivo / eficiencia_promedio_ponderada
    objetivo_solidos_tn = tn_exactas_para_objetivo * porcentaje_solidos
    objetivo_liquidos_tn = tn_exactas_para_objetivo * porcentaje_liquidos
    objetivo_purin_tn = tn_exactas_para_objetivo * porcentaje_purin
    
    print(f"\n4. OBJETIVOS TN:")
    print(f"   Total: {tn_exactas_para_objetivo:.2f}")
    print(f"   Solidos: {objetivo_solidos_tn:.2f}")
    print(f"   Liquidos: {objetivo_liquidos_tn:.2f}")
    print(f"   Purin: {objetivo_purin_tn:.2f}")
    
    # Simular procesamiento de solidos
    print(f"\n5. PROCESANDO SOLIDOS:")
    tn_restante_solidos = objetivo_solidos_tn
    
    solidos_ordenados = sorted(materiales_solidos.items(), 
                             key=lambda x: float(stock_actual[x[0]].get('kw_tn', 0) or 0), 
                             reverse=True)
    
    for mat, datos_mat in solidos_ordenados[:3]:  # Solo primeros 3
        kw_tn = float(stock_actual[mat].get('kw_tn', 0) or 0)
        stock = float(stock_actual[mat]['total_tn'])
        
        usar_tn = min(tn_restante_solidos, stock)
        usar_kw = usar_tn * kw_tn
        
        print(f"   {mat}:")
        print(f"      kw_tn: {kw_tn:.6f}")
        print(f"      stock: {stock:.2f}")
        print(f"      usar_tn: {usar_tn:.2f}")
        print(f"      usar_kw: {usar_kw:.6f}")
        
        tn_restante_solidos -= usar_tn

if __name__ == "__main__":
    debug_calcular_mezcla_volumetrica_simple()
