#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrenamiento Completo de SIBIA
Entrena el agente con muchas preguntas, respuestas, cálculos y datos de internet
"""

import json
import time
from datetime import datetime
import requests
import random

def entrenar_sibia_completo():
    """Entrena SIBIA con datos completos"""
    try:
        print("🚀 ENTRENAMIENTO COMPLETO DE SIBIA")
        print("=" * 50)
        
        # Importar SIBIA
        from mega_agente_ia import obtener_mega_agente, ContextoSistema
        
        sibia = obtener_mega_agente()
        
        # Crear contexto de entrenamiento
        contexto_entrenamiento = ContextoSistema(
            stock_materiales={
                'Maíz': {'cantidad': 25.5, 'tipo': 'solido'},
                'Purín': {'cantidad': 18.0, 'tipo': 'liquido'},
                'Rumen': {'cantidad': 22.0, 'tipo': 'solido'},
                'Expeller': {'cantidad': 15.0, 'tipo': 'solido'},
                'Lactosa': {'cantidad': 8.0, 'tipo': 'solido'},
                'Grasa': {'cantidad': 12.5, 'tipo': 'liquido'},
                'Silaje de Maíz': {'cantidad': 30.0, 'tipo': 'solido'},
                'Descarte de Grano': {'cantidad': 10.0, 'tipo': 'solido'}
            },
            sensores_datos={
                'temperatura_digestor': 38.5,
                'presion_sistema': 1.2,
                'nivel_tanque': 75.0,
                'flujo_biogas': 45.0,
                'temperatura_bio_1': 37.8,
                'temperatura_bio_2': 39.2,
                'presion_bio_1': 1.1,
                'presion_bio_2': 1.3,
                'nivel_tanque_1': 80.0,
                'nivel_tanque_2': 70.0,
                'flujo_entrada': 2.5,
                'flujo_salida': 2.3
            },
            kpis_actuales={
                'generacion': 28500,
                'inyectada': 26000,
                'spot': 2500,
                'calidad_ch4': 62.5,
                'consumo': 120,
                'eficiencia': 89
            },
            mezcla_actual={},
            configuracion_sistema={},
            historial_calculos=[],
            materiales_base={
                'Maíz': {'carbohidratos': 11.0, 'lipidos': 2.0, 'proteinas': 1.0},
                'Purín': {'carbohidratos': 34.0, 'lipidos': 0.3, 'proteinas': 1.05},
                'Rumen': {'carbohidratos': 14.1, 'lipidos': 1.2, 'proteinas': 1.0},
                'Expeller': {'carbohidratos': 34.0, 'lipidos': 3.2, 'proteinas': 1.0}
            },
            objetivos_usuario={
                'kw_objetivo': 28000,
                'metano_objetivo': 65
            }
        )
        
        # DATASET DE ENTRENAMIENTO COMPLETO
        dataset_entrenamiento = [
            # === CONSULTAS DE STOCK ===
            {
                'consulta': '¿Cuánto maíz tengo en stock?',
                'tipo_esperado': 'stock_materiales',
                'respuesta_esperada': 'Tienes 25.5 toneladas de Maíz en stock'
            },
            {
                'consulta': 'STOCK DE RUMEN',
                'tipo_esperado': 'stock_materiales',
                'respuesta_esperada': 'Tienes 22.0 toneladas de Rumen en stock'
            },
            {
                'consulta': '¿Cuánto purín hay disponible?',
                'tipo_esperado': 'stock_materiales',
                'respuesta_esperada': 'Tienes 18.0 toneladas de Purín disponible'
            },
            {
                'consulta': '¿Cuánto expeller tenemos en planta?',
                'tipo_esperado': 'stock_materiales',
                'respuesta_esperada': 'Tienes 15.0 toneladas de Expeller en planta'
            },
            {
                'consulta': '¿Cómo está el inventario de lactosa?',
                'tipo_esperado': 'stock_materiales',
                'respuesta_esperada': 'Tienes 8.0 toneladas de Lactosa en inventario'
            },
            {
                'consulta': '¿Cuánta grasa tengo disponible?',
                'tipo_esperado': 'stock_materiales',
                'respuesta_esperada': 'Tienes 12.5 toneladas de Grasa disponible'
            },
            
            # === CONSULTAS DE SENSORES ===
            {
                'consulta': '¿Cómo está la temperatura del digestor?',
                'tipo_esperado': 'sensores_datos',
                'respuesta_esperada': 'La temperatura del digestor está en 38.5°C'
            },
            {
                'consulta': 'TEMPERATURA DE BIO 2',
                'tipo_esperado': 'sensores_datos',
                'respuesta_esperada': 'La temperatura de BIO 2 está en 39.2°C'
            },
            {
                'consulta': '¿Cuál es la presión del sistema?',
                'tipo_esperado': 'sensores_datos',
                'respuesta_esperada': 'La presión del sistema está en 1.2 bar'
            },
            {
                'consulta': '¿Cómo está el nivel del tanque?',
                'tipo_esperado': 'sensores_datos',
                'respuesta_esperada': 'El nivel del tanque está en 75.0%'
            },
            {
                'consulta': '¿Cuál es el flujo de biogás?',
                'tipo_esperado': 'sensores_datos',
                'respuesta_esperada': 'El flujo de biogás está en 45.0 m³/h'
            },
            
            # === CONSULTAS DE CÁLCULOS ===
            {
                'consulta': '¿Qué mezcla necesito para 30000 kW?',
                'tipo_esperado': 'calculo_mezcla',
                'respuesta_esperada': 'Para 30000 kW necesitarás una mezcla optimizada'
            },
            {
                'consulta': 'CALCULO PARA 25000 KW',
                'tipo_esperado': 'calculo_mezcla',
                'respuesta_esperada': 'Para 25000 kW calculando mezcla optimizada'
            },
            {
                'consulta': '¿Cuál es la mejor receta para 28000 kW?',
                'tipo_esperado': 'calculo_mezcla',
                'respuesta_esperada': 'La mejor receta para 28000 kW usando Adán'
            },
            {
                'consulta': '¿Qué fórmula necesito para optimizar la producción?',
                'tipo_esperado': 'calculo_mezcla',
                'respuesta_esperada': 'Fórmula optimizada calculada con Adán'
            },
            
            # === CONSULTAS DE KPIs ===
            {
                'consulta': '¿Cómo está la generación actual?',
                'tipo_esperado': 'kpis_sistema',
                'respuesta_esperada': 'La generación actual es de 28500 kW'
            },
            {
                'consulta': '¿Cuál es la eficiencia del sistema?',
                'tipo_esperado': 'kpis_sistema',
                'respuesta_esperada': 'La eficiencia del sistema es del 89%'
            },
            {
                'consulta': '¿Cómo está el consumo de CHP?',
                'tipo_esperado': 'kpis_sistema',
                'respuesta_esperada': 'El consumo de CHP es de 120 L/s'
            },
            {
                'consulta': '¿Cuál es la calidad del metano?',
                'tipo_esperado': 'kpis_sistema',
                'respuesta_esperada': 'La calidad del metano es del 62.5%'
            },
            
            # === CONSULTAS DE DIAGNÓSTICO ===
            {
                'consulta': '¿Hay algún problema en el sistema?',
                'tipo_esperado': 'diagnostico',
                'respuesta_esperada': 'Revisando el sistema para detectar problemas'
            },
            {
                'consulta': '¿Por qué está baja la eficiencia?',
                'tipo_esperado': 'diagnostico',
                'respuesta_esperada': 'Analizando causas de baja eficiencia'
            },
            {
                'consulta': '¿Hay algún error en los sensores?',
                'tipo_esperado': 'diagnostico',
                'respuesta_esperada': 'Verificando estado de todos los sensores'
            },
            
            # === CONSULTAS DE PREDICCIÓN ===
            {
                'consulta': '¿Qué va a pasar mañana con la producción?',
                'tipo_esperado': 'prediccion',
                'respuesta_esperada': 'Prediciendo producción para mañana'
            },
            {
                'consulta': '¿Cuál es la tendencia de eficiencia?',
                'tipo_esperado': 'prediccion',
                'respuesta_esperada': 'Analizando tendencias de eficiencia'
            },
            
            # === CONSULTAS DE CONVERSACIÓN ===
            {
                'consulta': 'HOLA',
                'tipo_esperado': 'conversacion',
                'respuesta_esperada': '¡Hola! Soy SIBIA, tu asistente experto en biogás'
            },
            {
                'consulta': '¿Cómo estás?',
                'tipo_esperado': 'conversacion',
                'respuesta_esperada': '¡Muy bien! Estoy listo para ayudarte'
            },
            {
                'consulta': '¿Qué puedes hacer?',
                'tipo_esperado': 'conversacion',
                'respuesta_esperada': 'Puedo ayudarte con análisis, cálculos y diagnósticos'
            },
            {
                'consulta': 'Gracias',
                'tipo_esperado': 'conversacion',
                'respuesta_esperada': '¡De nada! Estoy aquí para ayudarte'
            }
        ]
        
        print(f"📚 Entrenando con {len(dataset_entrenamiento)} ejemplos...")
        print()
        
        resultados_entrenamiento = []
        aciertos = 0
        errores = 0
        
        for i, ejemplo in enumerate(dataset_entrenamiento, 1):
            consulta = ejemplo['consulta']
            tipo_esperado = ejemplo['tipo_esperado']
            respuesta_esperada = ejemplo['respuesta_esperada']
            
            print(f"{i:2d}. Consulta: '{consulta}'")
            
            inicio = time.time()
            resultado = sibia.procesar_consulta(consulta, contexto_entrenamiento)
            tiempo = time.time() - inicio
            
            tipo_obtenido = resultado['tipo']
            respuesta_obtenida = resultado['respuesta']
            confianza = resultado['confianza']
            
            # Verificar si acertó el tipo
            if tipo_obtenido == tipo_esperado:
                aciertos += 1
                estado = "✅ CORRECTO"
            else:
                errores += 1
                estado = "❌ ERROR"
            
            print(f"    Tipo esperado: {tipo_esperado}")
            print(f"    Tipo obtenido: {tipo_obtenido}")
            print(f"    Confianza: {confianza:.2f}")
            print(f"    Tiempo: {tiempo:.2f}s")
            print(f"    Estado: {estado}")
            print(f"    Respuesta: {respuesta_obtenida[:100]}...")
            print()
            
            resultados_entrenamiento.append({
                'consulta': consulta,
                'tipo_esperado': tipo_esperado,
                'tipo_obtenido': tipo_obtenido,
                'confianza': confianza,
                'tiempo': tiempo,
                'acierto': tipo_obtenido == tipo_esperado,
                'respuesta_esperada': respuesta_esperada,
                'respuesta_obtenida': respuesta_obtenida
            })
        
        # === ENTRENAMIENTO CON DATOS DE INTERNET ===
        print("🌐 ENTRENANDO CON DATOS DE INTERNET...")
        print("-" * 40)
        
        consultas_internet = [
            '¿Cuáles son las últimas noticias sobre biogás?',
            '¿Qué es la digestión anaeróbica?',
            '¿Cuáles son los beneficios del biogás?',
            '¿Cómo funciona un biodigestor?',
            '¿Qué materiales son mejores para biogás?'
        ]
        
        for consulta in consultas_internet:
            print(f"🔍 Consulta web: '{consulta}'")
            resultado = sibia.procesar_consulta(consulta, contexto_entrenamiento)
            print(f"   Respuesta: {resultado['respuesta'][:150]}...")
            print()
        
        # === ESTADÍSTICAS FINALES ===
        print("📊 ESTADÍSTICAS DE ENTRENAMIENTO:")
        print("=" * 40)
        
        total_consultas = len(dataset_entrenamiento)
        precision = (aciertos / total_consultas) * 100
        
        print(f"Total de consultas: {total_consultas}")
        print(f"Aciertos: {aciertos}")
        print(f"Errores: {errores}")
        print(f"Precisión: {precision:.1f}%")
        
        # Análisis por tipo
        tipos_analisis = {}
        for resultado in resultados_entrenamiento:
            tipo = resultado['tipo_esperado']
            if tipo not in tipos_analisis:
                tipos_analisis[tipo] = {'total': 0, 'aciertos': 0}
            tipos_analisis[tipo]['total'] += 1
            if resultado['acierto']:
                tipos_analisis[tipo]['aciertos'] += 1
        
        print("\n📈 ANÁLISIS POR TIPO:")
        for tipo, datos in tipos_analisis.items():
            precision_tipo = (datos['aciertos'] / datos['total']) * 100
            print(f"  {tipo}: {datos['aciertos']}/{datos['total']} ({precision_tipo:.1f}%)")
        
        # Guardar resultados
        resultados_completos = {
            'timestamp': datetime.now().isoformat(),
            'estadisticas': {
                'total_consultas': total_consultas,
                'aciertos': aciertos,
                'errores': errores,
                'precision': precision,
                'tipos_analisis': tipos_analisis
            },
            'resultados': resultados_entrenamiento
        }
        
        with open('entrenamiento_sibia_completo.json', 'w', encoding='utf-8') as f:
            json.dump(resultados_completos, f, indent=4, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: entrenamiento_sibia_completo.json")
        print("\n🎉 ¡ENTRENAMIENTO COMPLETO FINALIZADO!")
        
        return resultados_completos
        
    except Exception as e:
        print(f"❌ Error en entrenamiento: {e}")
        return None

if __name__ == "__main__":
    entrenar_sibia_completo()
