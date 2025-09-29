#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificacion de kw_tn en materiales_liquidos_ordenados
"""

import json

def verificar_kw_tn():
    print("VERIFICACION DE KW_TN EN MATERIALES LIQUIDOS")
    print("=" * 50)
    
    # Cargar stock
    with open('stock.json', 'r', encoding='utf-8') as f:
        stock_data = json.load(f)
    
    stock_actual = stock_data.get('materiales', {})
    
    # Simular materiales_liquidos como en la funcion
    materiales_liquidos = {}
    
    for mat, datos in stock_actual.items():
        tipo = datos.get('tipo', 'solido').lower()
        stock_tn = float(datos.get('total_tn', 0))
        kw_tn = float(datos.get('kw_tn', 0) or 0)
        
        if stock_tn <= 0 or kw_tn <= 0:
            continue
            
        if tipo == 'liquido':
            materiales_liquidos[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
    
    print(f"\n1. MATERIALES LIQUIDOS CLASIFICADOS: {len(materiales_liquidos)}")
    for mat in materiales_liquidos:
        print(f"   - {mat}")
    
    # Simular materiales_liquidos_ordenados
    materiales_liquidos_ordenados = []
    for mat, datos_mat in materiales_liquidos.items():
        kw_tn = float(stock_actual[mat].get('kw_tn', 0) or 0)
        stock = float(stock_actual[mat]['total_tn'])
        materiales_liquidos_ordenados.append((mat, datos_mat, kw_tn, stock))
    
    materiales_liquidos_ordenados.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n2. MATERIALES LIQUIDOS ORDENADOS:")
    for mat, datos_mat, kw_tn, stock in materiales_liquidos_ordenados:
        print(f"   - {mat}: kw_tn={kw_tn:.6f}, stock={stock:.2f}")
        
        # Simular calculo de usar_kw
        usar_tn = min(1000, stock)  # Simular tn_restante_liquidos = 1000
        usar_kw = usar_tn * kw_tn
        print(f"     usar_tn={usar_tn:.2f}, usar_kw={usar_kw:.6f}")

if __name__ == "__main__":
    verificar_kw_tn()
