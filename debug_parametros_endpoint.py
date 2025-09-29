#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug de la funcion con parametros del endpoint
"""

import json
import sys
import os

# Agregar el directorio actual al path para importar el modulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_con_parametros_endpoint():
    print("DEBUG CON PARAMETROS DEL ENDPOINT")
    print("=" * 50)
    
    try:
        # Importar funciones
        from app_CORREGIDO_OK_FINAL import calcular_mezcla_volumetrica_simple, cargar_json_seguro, cargar_configuracion
        
        # Cargar datos como lo hace el endpoint
        config_actual = cargar_configuracion()
        stock_data = cargar_json_seguro('stock.json') or {"materiales": {}}
        stock_actual = stock_data.get('materiales', {})
        
        # Parametros del endpoint
        kw_objetivo = 28800
        porcentaje_solidos = 50
        porcentaje_liquidos = 40
        incluir_purin = True
        
        # Actualizar configuracion como lo hace el endpoint
        config_actual['kw_objetivo'] = kw_objetivo
        config_actual['porcentaje_solidos'] = porcentaje_solidos
        config_actual['porcentaje_liquidos'] = porcentaje_liquidos
        config_actual['num_biodigestores'] = 2
        config_actual['modo_calculo'] = 'volumetrico'
        
        print(f"\n1. PARAMETROS:")
        print(f"   KW Objetivo: {kw_objetivo}")
        print(f"   Porcentaje Solidos: {porcentaje_solidos}")
        print(f"   Porcentaje Liquidos: {porcentaje_liquidos}")
        print(f"   Incluir Purin: {incluir_purin}")
        print(f"   Stock materiales: {len(stock_actual)}")
        
        # Llamar a la funcion
        print(f"\n2. LLAMANDO A LA FUNCION...")
        resultado = calcular_mezcla_volumetrica_simple(
            config_actual, 
            stock_actual, 
            porcentaje_solidos/100, 
            porcentaje_liquidos/100, 
            incluir_purin
        )
        
        print(f"\n3. RESULTADO:")
        print(f"   Tipo: {type(resultado)}")
        print(f"   Keys: {list(resultado.keys()) if isinstance(resultado, dict) else 'No es dict'}")
        
        # Verificar totales
        totales = resultado.get('totales', {})
        print(f"\n4. TOTALES:")
        print(f"   KW Total Generado: {totales.get('kw_total_generado', 'NO ENCONTRADO')}")
        print(f"   KW Solidos: {totales.get('kw_solidos', 'NO ENCONTRADO')}")
        print(f"   KW Liquidos: {totales.get('kw_liquidos', 'NO ENCONTRADO')}")
        print(f"   KW Purin: {totales.get('kw_purin', 'NO ENCONTRADO')}")
        
        # Verificar materiales
        materiales_solidos = resultado.get('materiales_solidos', {})
        materiales_liquidos = resultado.get('materiales_liquidos', {})
        materiales_purin = resultado.get('materiales_purin', {})
        
        print(f"\n5. MATERIALES:")
        print(f"   Solidos: {len(materiales_solidos)}")
        for mat, datos in materiales_solidos.items():
            cantidad = datos.get('cantidad_tn', 0)
            kw = datos.get('kw_aportados', 0)
            print(f"      - {mat}: {cantidad:.2f} TN -> {kw:.2f} KW")
        
        print(f"   Liquidos: {len(materiales_liquidos)}")
        for mat, datos in materiales_liquidos.items():
            cantidad = datos.get('cantidad_tn', 0)
            kw = datos.get('kw_aportados', 0)
            print(f"      - {mat}: {cantidad:.2f} TN -> {kw:.2f} KW")
        
        print(f"   Purin: {len(materiales_purin)}")
        for mat, datos in materiales_purin.items():
            cantidad = datos.get('cantidad_tn', 0)
            kw = datos.get('kw_aportados', 0)
            print(f"      - {mat}: {cantidad:.2f} TN -> {kw:.2f} KW")
        
        # Mostrar resultado completo si hay problemas
        if totales.get('kw_total_generado', 0) == 0:
            print(f"\n6. RESULTADO COMPLETO (KW=0):")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_con_parametros_endpoint()
