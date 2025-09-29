#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug de la funcion llamada desde el endpoint
"""

import json
import sys
import os

# Agregar el directorio actual al path para importar el modulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_funcion_endpoint():
    print("DEBUG DE LA FUNCION LLAMADA DESDE EL ENDPOINT")
    print("=" * 60)
    
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
        
        print(f"\n1. LLAMANDO A LA FUNCION...")
        resultado = calcular_mezcla_volumetrica_simple(
            config_actual, 
            stock_actual, 
            porcentaje_solidos/100, 
            porcentaje_liquidos/100, 
            incluir_purin
        )
        
        print(f"\n2. RESULTADO DE LA FUNCION:")
        print(f"   KW Total Generado: {resultado.get('totales', {}).get('kw_total_generado', 'NO ENCONTRADO')}")
        print(f"   KW Solidos: {resultado.get('totales', {}).get('kw_solidos', 'NO ENCONTRADO')}")
        print(f"   KW Liquidos: {resultado.get('totales', {}).get('kw_liquidos', 'NO ENCONTRADO')}")
        print(f"   KW Purin: {resultado.get('totales', {}).get('kw_purin', 'NO ENCONTRADO')}")
        
        # Verificar materiales
        materiales_solidos = resultado.get('materiales_solidos', {})
        materiales_liquidos = resultado.get('materiales_liquidos', {})
        materiales_purin = resultado.get('materiales_purin', {})
        
        print(f"\n3. MATERIALES DE LA FUNCION:")
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
        
        # Simular la logica del endpoint
        print(f"\n4. SIMULANDO LOGICA DEL ENDPOINT:")
        kw_obj = float(config_actual.get('kw_objetivo', 0))
        kw_act = float(resultado.get('totales', {}).get('kw_total_generado', 0))
        
        print(f"   kw_obj: {kw_obj}")
        print(f"   kw_act: {kw_act}")
        print(f"   kw_act > 0: {kw_act > 0}")
        print(f"   kw_act < kw_obj * 0.999: {kw_act < kw_obj * 0.999}")
        print(f"   Condicion completa: {kw_obj > 0 and kw_act > 0 and kw_act < kw_obj * 0.999}")
        
        if kw_obj > 0 and kw_act > 0 and kw_act < kw_obj * 0.999:
            print(f"   ENTRARIA EN EL BLOQUE DE ESCALADO")
        else:
            print(f"   NO ENTRARIA EN EL BLOQUE DE ESCALADO")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_funcion_endpoint()
