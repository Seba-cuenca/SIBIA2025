#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulacion de la Calculadora Rapida
Simula exactamente lo que hace la funcion calcular_mezcla_volumetrica_simple
"""

import json
import os

def simular_calculadora():
    print("SIMULACION DE LA CALCULADORA RAPIDA")
    print("=" * 50)
    
    # Cargar stock
    with open('stock.json', 'r', encoding='utf-8') as f:
        stock_data = json.load(f)
    
    stock_actual = stock_data.get('materiales', {})
    
    print(f"\n1. STOCK ORIGINAL: {len(stock_actual)} materiales")
    
    # Simular el filtro de la funcion calcular_mezcla_volumetrica_simple
    materiales_solidos = {}
    materiales_liquidos = {}
    materiales_purin = {}
    
    total_solidos_stock = 0
    total_liquidos_stock = 0
    total_purin_stock = 0
    
    materiales_filtrados = []
    
    for mat, datos in stock_actual.items():
        # Simular el filtro exacto de la funcion
        tipo = datos.get('tipo', 'solido').lower()
        stock_tn = float(datos.get('total_tn', 0))
        kw_tn = float(datos.get('kw_tn', 0) or 0)
        
        print(f"\n   Material: {mat}")
        print(f"   - Tipo: {tipo}")
        print(f"   - Stock TN: {stock_tn}")
        print(f"   - KW/TN: {kw_tn}")
        
        # Este es el filtro que esta causando el problema
        if stock_tn <= 0 or kw_tn <= 0:
            print(f"   - FILTRADO: stock_tn <= 0 o kw_tn <= 0")
            materiales_filtrados.append(mat)
            continue
        
        print(f"   - PASO EL FILTRO")
        
        if 'purin' in mat.lower():
            total_purin_stock += stock_tn
            materiales_purin[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
            print(f"   - CLASIFICADO COMO PURIN")
        elif tipo == 'liquido':
            total_liquidos_stock += stock_tn
            materiales_liquidos[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
            print(f"   - CLASIFICADO COMO LIQUIDO")
        else:
            total_solidos_stock += stock_tn
            materiales_solidos[mat] = {'cantidad_tn': 0, 'kw_aportados': 0}
            print(f"   - CLASIFICADO COMO SOLIDO")
    
    print(f"\n2. RESULTADO DEL FILTRADO:")
    print(f"   Materiales filtrados: {len(materiales_filtrados)}")
    for mat in materiales_filtrados:
        print(f"      - {mat}")
    
    print(f"\n3. MATERIALES CLASIFICADOS:")
    print(f"   Solidos: {len(materiales_solidos)} materiales, {total_solidos_stock:.2f} TN")
    print(f"   Liquidos: {len(materiales_liquidos)} materiales, {total_liquidos_stock:.2f} TN")
    print(f"   Purin: {len(materiales_purin)} materiales, {total_purin_stock:.2f} TN")
    
    print(f"\n4. PROBLEMA IDENTIFICADO:")
    if len(materiales_solidos) == 0 and len(materiales_liquidos) == 0:
        print("   ERROR: No hay materiales clasificados!")
        print("   Esto explica por que la calculadora muestra 0 KW")
    else:
        print("   Los materiales estan siendo clasificados correctamente")
        print("   El problema debe estar en otra parte del calculo")

if __name__ == "__main__":
    simular_calculadora()
