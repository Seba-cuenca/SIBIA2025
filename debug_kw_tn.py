#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug de kw_tn en calcular_mezcla_volumetrica_simple
"""

import json
import sys
import os

# Agregar el directorio actual al path para importar el modulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_kw_tn():
    print("DEBUG DE KW_TN EN CALCULAR_MEZCLA_VOLUMETRICA_SIMPLE")
    print("=" * 60)
    
    try:
        # Importar funciones
        from app_CORREGIDO_OK_FINAL import cargar_json_seguro, cargar_configuracion
        
        # Cargar datos
        config_actual = cargar_configuracion()
        stock_data = cargar_json_seguro('stock.json') or {"materiales": {}}
        stock_actual = stock_data.get('materiales', {})
        
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
        
        # Simular procesamiento de solidos
        print(f"\n2. PROCESANDO SOLIDOS:")
        solidos_ordenados = sorted(materiales_solidos.items(), 
                                 key=lambda x: float(stock_actual[x[0]].get('kw_tn', 0) or 0), 
                                 reverse=True)
        
        for i, (mat, datos_mat) in enumerate(solidos_ordenados[:3]):
            # CORREGIDO: Usar kw_tn del stock_actual
            kw_tn = float(stock_actual[mat].get('kw_tn', 0) or 0)
            stock = float(stock_actual[mat]['total_tn'])
            
            print(f"\n   {i+1}. {mat}:")
            print(f"      kw_tn del stock: {kw_tn:.6f}")
            print(f"      stock: {stock:.2f}")
            
            # Simular calculo de usar_tn y usar_kw
            usar_tn = min(1000, stock)  # Simular objetivo
            usar_kw = usar_tn * kw_tn
            
            print(f"      usar_tn: {usar_tn:.2f}")
            print(f"      usar_kw: {usar_kw:.6f}")
            
            # Simular guardado
            datos_mat['cantidad_tn'] = usar_tn
            datos_mat['tn_usadas'] = usar_tn
            datos_mat['kw_aportados'] = usar_kw
            
            print(f"      kw_aportados guardado: {datos_mat['kw_aportados']:.6f}")
        
        # Verificar materiales finales
        print(f"\n3. MATERIALES FINALES:")
        for mat, datos in materiales_solidos.items():
            if datos['cantidad_tn'] > 0:
                print(f"   {mat}:")
                print(f"      cantidad_tn: {datos['cantidad_tn']:.2f}")
                print(f"      kw_aportados: {datos['kw_aportados']:.6f}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_kw_tn()
