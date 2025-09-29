#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug del endpoint /calcular_mezcla
Verifica exactamente que esta devolviendo
"""

import requests
import json
import time

def debug_endpoint():
    print("DEBUG DEL ENDPOINT /calcular_mezcla")
    print("=" * 50)
    
    # Esperar que la aplicacion este lista
    print("\n1. ESPERANDO QUE LA APLICACION ESTE LISTA...")
    time.sleep(3)
    
    # URL base
    base_url = "http://127.0.0.1:5000"
    
    # Datos de prueba
    datos_prueba = {
        "kw_objetivo": 28800,
        "porcentaje_solidos": 50,
        "porcentaje_liquidos": 40,
        "porcentaje_purin": 10,
        "modo_energetico": False,  # Modo volumetrico
        "incluir_purin": True,
        "num_biodigestores": 2
    }
    
    print("\n2. LLAMANDO AL ENDPOINT...")
    print(f"   URL: {base_url}/calcular_mezcla")
    print(f"   Datos: {json.dumps(datos_prueba, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/calcular_mezcla", 
                               json=datos_prueba, 
                               timeout=30)
        
        print(f"\n3. RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"\n4. RESULTADO JSON:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            
            # Verificar estructura
            print(f"\n5. VERIFICACION DE ESTRUCTURA:")
            
            # Verificar totales
            totales = resultado.get('totales', {})
            print(f"   Total KW Generado: {totales.get('kw_total_generado', 'NO ENCONTRADO')}")
            print(f"   KW Solidos: {totales.get('kw_solidos', 'NO ENCONTRADO')}")
            print(f"   KW Liquidos: {totales.get('kw_liquidos', 'NO ENCONTRADO')}")
            print(f"   KW Purin: {totales.get('kw_purin', 'NO ENCONTRADO')}")
            print(f"   Metano: {totales.get('porcentaje_metano', 'NO ENCONTRADO')}")
            
            # Verificar materiales
            materiales = resultado.get('materiales', {})
            print(f"\n6. MATERIALES:")
            print(f"   Solidos: {len(materiales.get('solidos', {}))}")
            print(f"   Liquidos: {len(materiales.get('liquidos', {}))}")
            print(f"   Purin: {len(materiales.get('purin', {}))}")
            
            # Verificar materiales detalle
            materiales_detalle = resultado.get('materiales_detalle', [])
            print(f"   Materiales Detalle: {len(materiales_detalle)}")
            
            if materiales_detalle:
                print(f"\n7. PRIMEROS MATERIALES DETALLE:")
                for i, mat in enumerate(materiales_detalle[:3]):
                    print(f"   {i+1}. {mat.get('nombre', 'N/A')}:")
                    print(f"      - Cantidad TN: {mat.get('cantidad_tn', 0)}")
                    print(f"      - KW Aportados: {mat.get('kw_aportados', 0)}")
                    print(f"      - Tipo: {mat.get('tipo', 'N/A')}")
            
        else:
            print(f"   ERROR: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ERROR DE CONEXION: {e}")

if __name__ == "__main__":
    debug_endpoint()
