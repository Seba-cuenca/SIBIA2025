#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostico de la Calculadora Rapida
Verifica que datos esta recibiendo la calculadora
"""

import json
import os

def diagnosticar_calculadora():
    print("DIAGNOSTICO DE LA CALCULADORA RAPIDA")
    print("=" * 50)
    
    # 1. Verificar archivo stock.json
    print("\n1. VERIFICANDO ARCHIVO stock.json:")
    if os.path.exists('stock.json'):
        with open('stock.json', 'r', encoding='utf-8') as f:
            stock_data = json.load(f)
        
        materiales = stock_data.get('materiales', {})
        print(f"   Archivo existe")
        print(f"   Total materiales: {len(materiales)}")
        
        # Mostrar primeros 5 materiales con sus datos
        print("\n   PRIMEROS 5 MATERIALES:")
        for i, (mat, datos) in enumerate(list(materiales.items())[:5]):
            total_tn = datos.get('total_tn', 0)
            kw_tn = datos.get('kw_tn', 0)
            tipo = datos.get('tipo', 'N/A')
            print(f"   {i+1}. {mat}:")
            print(f"      - Total TN: {total_tn}")
            print(f"      - KW/TN: {kw_tn}")
            print(f"      - Tipo: {tipo}")
    else:
        print("   Archivo stock.json NO EXISTE")
        return
    
    # 2. Verificar materiales con stock > 0
    print("\n2. MATERIALES CON STOCK > 0:")
    materiales_con_stock = []
    for mat, datos in materiales.items():
        total_tn = float(datos.get('total_tn', 0))
        if total_tn > 0:
            materiales_con_stock.append((mat, total_tn))
    
    if materiales_con_stock:
        print(f"   {len(materiales_con_stock)} materiales con stock:")
        for mat, tn in materiales_con_stock[:10]:  # Mostrar primeros 10
            print(f"      - {mat}: {tn:.2f} TN")
    else:
        print("   NO HAY MATERIALES CON STOCK > 0")
    
    # 3. Verificar materiales con kw_tn > 0
    print("\n3. MATERIALES CON KW/TN > 0:")
    materiales_con_kw = []
    for mat, datos in materiales.items():
        kw_tn = float(datos.get('kw_tn', 0))
        if kw_tn > 0:
            materiales_con_kw.append((mat, kw_tn))
    
    if materiales_con_kw:
        print(f"   {len(materiales_con_kw)} materiales con KW/TN:")
        for mat, kw in materiales_con_kw[:10]:  # Mostrar primeros 10
            print(f"      - {mat}: {kw:.4f} KW/TN")
    else:
        print("   NO HAY MATERIALES CON KW/TN > 0")
    
    # 4. Verificar clasificacion solidos/liquidos
    print("\n4. CLASIFICACION SOLIDOS/LIQUIDOS:")
    solidos = []
    liquidos = []
    
    for mat, datos in materiales.items():
        total_tn = float(datos.get('total_tn', 0))
        tipo = datos.get('tipo', '').lower()
        
        if total_tn > 0:  # Solo materiales con stock
            if tipo == 'solido':
                solidos.append((mat, total_tn))
            elif tipo == 'liquido':
                liquidos.append((mat, total_tn))
    
    print(f"   Solidos con stock: {len(solidos)}")
    for mat, tn in solidos[:5]:
        print(f"      - {mat}: {tn:.2f} TN")
    
    print(f"   Liquidos con stock: {len(liquidos)}")
    for mat, tn in liquidos[:5]:
        print(f"      - {mat}: {tn:.2f} TN")
    
    # 5. Resumen del problema
    print("\n5. RESUMEN DEL PROBLEMA:")
    if not materiales_con_stock:
        print("   PROBLEMA: No hay materiales con stock > 0")
    elif not materiales_con_kw:
        print("   PROBLEMA: No hay materiales con KW/TN > 0")
    elif not solidos and not liquidos:
        print("   PROBLEMA: No hay materiales clasificados como solidos o liquidos")
    else:
        print("   Los datos parecen estar correctos")
        print("   El problema podria estar en la logica de calculo")

if __name__ == "__main__":
    diagnosticar_calculadora()
