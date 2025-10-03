import requests
import json
import random
import time
from datetime import datetime

print("=== SCRIPT DE ENTRENAMIENTO MASIVO DE MODELOS ML ===")
print("Generando 300 calculos diferentes para entrenar los modelos...")

url = "http://192.168.1.8:5000/adan/calcular_mezcla"

# Configuraciones base para generar variaciones
configuraciones_base = [
    {"kwh_objetivo": 100, "porcentaje_ch4": 60, "modo": "energetico"},
    {"kwh_objetivo": 200, "porcentaje_ch4": 65, "modo": "energetico"},
    {"kwh_objetivo": 500, "porcentaje_ch4": 70, "modo": "energetico"},
    {"kwh_objetivo": 1000, "porcentaje_ch4": 60, "modo": "volumetrico"},
    {"kwh_objetivo": 2000, "porcentaje_ch4": 65, "modo": "volumetrico"},
    {"kwh_objetivo": 5000, "porcentaje_ch4": 70, "modo": "volumetrico"},
]

modelos_disponibles = [
    ["xgboost"],
    ["random_forest"],
    ["optimizacion_bayesiana"],
    ["xgboost", "random_forest"],
    ["random_forest", "optimizacion_bayesiana"],
    ["xgboost", "optimizacion_bayesiana"],
    ["xgboost", "random_forest", "optimizacion_bayesiana"]
]

resultados_entrenamiento = []
calculos_exitosos = 0
calculos_fallidos = 0

print(f"Iniciando entrenamiento con {len(configuraciones_base)} configuraciones base...")

for i in range(300):
    try:
        # Seleccionar configuraciÃ³n base aleatoria
        config_base = random.choice(configuraciones_base)
        
        # Generar variaciones aleatorias
        datos_calculo = {
            "kwh_objetivo": config_base["kwh_objetivo"] + random.randint(-50, 200),
            "porcentaje_ch4": config_base["porcentaje_ch4"] + random.randint(-5, 10),
            "m3_purin": random.randint(0, 100),
            "incluir_purin": random.choice([True, False]),
            "num_materiales": random.randint(3, 8),
            "consumo_motor": round(random.uniform(0.1, 1.0), 2),
            "potencia_motor": random.randint(20, 200),
            "modo": config_base["modo"],
            "modelos_seleccionados": random.choice(modelos_disponibles)
        }
        
        # Asegurar valores mÃ­nimos
        datos_calculo["kwh_objetivo"] = max(50, datos_calculo["kwh_objetivo"])
        datos_calculo["porcentaje_ch4"] = max(50, min(80, datos_calculo["porcentaje_ch4"]))
        
        print(f"Calculo {i+1}/300: KW={datos_calculo['kwh_objetivo']}, CH4={datos_calculo['porcentaje_ch4']}, Modelos={datos_calculo['modelos_seleccionados']}")
        
        # Realizar cÃ¡lculo
        response = requests.post(url, json=datos_calculo, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            
            if 'resumen' in resultado and 'receta' in resultado:
                resumen = resultado['resumen']
                receta = resultado['receta']
                
                # Guardar resultado de entrenamiento
                resultado_entrenamiento = {
                    "timestamp": datetime.now().isoformat(),
                    "configuracion": datos_calculo,
                    "resultado": {
                        "kwh_generado": resumen.get('kwh_generado', 0),
                        "total_toneladas": resumen.get('total_toneladas', 0),
                        "porcentaje_ch4_real": resumen.get('porcentaje_ch4_real', 0),
                        "num_materiales_usados": len(receta)
                    },
                    "materiales_usados": [mat.get('material', 'N/A') for mat in receta],
                    "metricas_ml": resultado.get('metricas_ml', {})
                }
                
                resultados_entrenamiento.append(resultado_entrenamiento)
                calculos_exitosos += 1
                
                print(f"  âœ… Exitoso: {resumen.get('kwh_generado', 0):.2f} KW, {len(receta)} materiales")
            else:
                print(f"  âŒ Error: Sin resumen o receta")
                calculos_fallidos += 1
        else:
            print(f"  âŒ Error HTTP: {response.status_code}")
            calculos_fallidos += 1
            
    except Exception as e:
        print(f"  âŒ Error: {e}")
        calculos_fallidos += 1
    
    # Pausa pequeÃ±a para no sobrecargar el servidor
    time.sleep(0.1)

print(f"\n=== RESUMEN DEL ENTRENAMIENTO ===")
print(f"Calculos exitosos: {calculos_exitosos}")
print(f"Calculos fallidos: {calculos_fallidos}")
print(f"Total calculos: {calculos_exitosos + calculos_fallidos}")

# Guardar resultados de entrenamiento
if resultados_entrenamiento:
    with open('entrenamiento_masivo_modelos.json', 'w', encoding='utf-8') as f:
        json.dump(resultados_entrenamiento, f, indent=2, ensure_ascii=False)
    
    print(f"\nâœ… Resultados guardados en 'entrenamiento_masivo_modelos.json'")
    
    # AnÃ¡lisis rÃ¡pido
    modelos_usados = {}
    for resultado in resultados_entrenamiento:
        modelos_key = str(resultado['configuracion']['modelos_seleccionados'])
        if modelos_key not in modelos_usados:
            modelos_usados[modelos_key] = []
        modelos_usados[modelos_key].append(resultado['resultado']['kwh_generado'])
    
    print(f"\n=== ANALISIS POR MODELOS ===")
    for modelos, kwh_values in modelos_usados.items():
        if kwh_values:
            promedio = sum(kwh_values) / len(kwh_values)
            print(f"{modelos}: Promedio {promedio:.2f} KW ({len(kwh_values)} calculos)")
else:
    print("âŒ No se obtuvieron resultados de entrenamiento")

print("\n=== FIN DEL ENTRENAMIENTO ===")
