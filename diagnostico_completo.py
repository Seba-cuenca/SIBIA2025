#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico completo del sistema SIBIA
"""
import requests
import json
import time

def test_endpoints():
    """Prueba todos los endpoints críticos"""
    print("="*70)
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA SIBIA")
    print("="*70)
    
    # Detectar la URL correcta del servidor
    urls_posibles = [
        "http://127.0.0.1:5000",
        "http://localhost:5000",
        "http://192.168.1.8:5000",
    ]
    
    base_url = None
    for url in urls_posibles:
        try:
            r = requests.get(f"{url}/health", timeout=2)
            if r.status_code == 200:
                base_url = url
                print(f"✅ Servidor encontrado en: {base_url}")
                break
        except:
            continue
    
    if not base_url:
        print("❌ ERROR: No se pudo encontrar el servidor Flask")
        print("   Verifica que Flask esté corriendo")
        return
    
    print("\n" + "="*70)
    print("1️⃣ PROBANDO /asistente_ia_v2")
    print("="*70)
    
    tests = [
        {
            "nombre": "Saludo inicial",
            "pregunta": "Hola, soy SIBIA",
            "sintetizar": True,
            "esperado": "respuesta_presente"
        },
        {
            "nombre": "Stock de Rumen",
            "pregunta": "¿Cuál es el stock de rumen?",
            "sintetizar": True,
            "esperado": "stock_rumen"
        },
        {
            "nombre": "Stock general",
            "pregunta": "stock general",
            "sintetizar": False,
            "esperado": "stock_total"
        },
        {
            "nombre": "Temperatura Bio 2",
            "pregunta": "temperatura del bio 2",
            "sintetizar": False,
            "esperado": "sensores"
        }
    ]
    
    resultados = {"exitosos": 0, "fallidos": 0}
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'─'*70}")
        print(f"TEST {i}: {test['nombre']}")
        print(f"Pregunta: '{test['pregunta']}'")
        print(f"{'─'*70}")
        
        try:
            start = time.time()
            response = requests.post(
                f"{base_url}/asistente_ia_v2",
                json={
                    "pregunta": test['pregunta'],
                    "sintetizar": test['sintetizar']
                },
                timeout=15
            )
            latencia = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {response.status_code}")
                print(f"⏱️  Latencia: {latencia}ms")
                print(f"📝 Respuesta: {data.get('respuesta', 'N/A')[:100]}...")
                print(f"🎤 TTS disponible: {data.get('tts_disponible', False)}")
                print(f"🔊 Audio presente: {'Sí' if data.get('audio_base64') else 'No'}")
                
                if data.get('audio_base64'):
                    print(f"   └─ Tamaño audio: {len(data['audio_base64'])} chars")
                
                if data.get('datos'):
                    print(f"📊 Datos retornados: {json.dumps(data['datos'], indent=2)[:200]}...")
                
                if data.get('debug'):
                    print(f"🐛 Debug: {data['debug']}")
                
                # Validaciones
                validaciones = []
                if test['esperado'] == 'respuesta_presente':
                    validaciones.append(("Respuesta no vacía", bool(data.get('respuesta'))))
                elif test['esperado'] == 'stock_rumen':
                    validaciones.append(("Datos de stock", 'material' in data.get('datos', {})))
                    validaciones.append(("Total TN > 0", data.get('datos', {}).get('total_tn', 0) > 0))
                elif test['esperado'] == 'stock_total':
                    validaciones.append(("Stock total presente", 'stock_total_tn' in data.get('datos', {})))
                elif test['esperado'] == 'sensores':
                    validaciones.append(("Datos sensores", 'bio1' in data.get('datos', {}) or 'bio2' in data.get('datos', {})))
                
                print(f"\n🔬 Validaciones:")
                for nombre, resultado in validaciones:
                    icono = "✅" if resultado else "❌"
                    print(f"   {icono} {nombre}")
                
                if all(v[1] for v in validaciones):
                    resultados['exitosos'] += 1
                else:
                    resultados['fallidos'] += 1
                    
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                resultados['fallidos'] += 1
                
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT después de 15 segundos")
            resultados['fallidos'] += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            resultados['fallidos'] += 1
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*70)
    print(f"✅ Exitosas: {resultados['exitosos']}")
    print(f"❌ Fallidas: {resultados['fallidos']}")
    print(f"📈 Tasa de éxito: {resultados['exitosos']/(resultados['exitosos']+resultados['fallidos'])*100:.1f}%")
    
    # Probar otros endpoints críticos
    print("\n" + "="*70)
    print("2️⃣ PROBANDO OTROS ENDPOINTS CRÍTICOS")
    print("="*70)
    
    otros_endpoints = [
        ("/stock_actual", "GET"),
        ("/health", "GET"),
        ("/obtener_configuracion_voz", "GET"),
    ]
    
    for endpoint, method in otros_endpoints:
        try:
            if method == "GET":
                r = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                r = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
            
            if r.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"⚠️  {endpoint}: Status {r.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {str(e)[:50]}")
    
    print("\n" + "="*70)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("="*70)

if __name__ == '__main__':
    test_endpoints()
