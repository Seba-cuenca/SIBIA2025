#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar que el endpoint /asistente_ia_v2 funciona correctamente
"""
import requests
import json

BASE_URL = "http://192.168.1.8:5000"

def test_asistente_v2():
    """Prueba el endpoint /asistente_ia_v2"""
    print("="*60)
    print("PROBANDO ENDPOINT /asistente_ia_v2")
    print("="*60)
    
    tests = [
        {"pregunta": "Hola, soy SIBIA", "sintetizar": True},
        {"pregunta": "¿Cuál es el stock de rumen?", "sintetizar": True},
        {"pregunta": "stock general", "sintetizar": False},
        {"pregunta": "temperatura del bio 2", "sintetizar": False},
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test['pregunta']}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/asistente_ia_v2",
                json=test,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Respuesta exitosa:")
                print(f"   Status: {data.get('status')}")
                print(f"   Respuesta: {data.get('respuesta')}")
                print(f"   TTS disponible: {data.get('tts_disponible')}")
                print(f"   Audio presente: {'Sí' if data.get('audio_base64') else 'No'}")
                if data.get('audio_base64'):
                    print(f"   Audio length: {len(data['audio_base64'])} chars")
                print(f"   Datos: {json.dumps(data.get('datos'), indent=2)}")
                if data.get('debug'):
                    print(f"   Debug: {data['debug']}")
            else:
                print(f"\n❌ Error {response.status_code}:")
                print(f"   {response.text[:500]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: No se pudo conectar al servidor Flask")
            print("   Asegurate de que Flask esté corriendo en http://127.0.0.1:5000")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*60}")
    print("PRUEBAS COMPLETADAS")
    print("="*60)

if __name__ == '__main__':
    test_asistente_v2()
