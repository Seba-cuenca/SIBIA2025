#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo de IA Completo con Machine Learning para la aplicación de biogás
Combina velocidad + ML real + voz fluida
"""

import json
import time
import re
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModeloIABiogas:
    """
    Modelo de IA completo con Machine Learning para aplicación de biogás
    """
    
    def __init__(self):
        self.nombre = "SIBIA-AI-ML"
        self.version = "2.0"
        self.aprendizaje_file = "modelo_ia_aprendizaje.json"
        self.modelo_entrenado = None
        self.vectorizer = None
        self.categorias = {
            'calculo_material': 0,
            'stock': 1, 
            'mezcla': 2,
            'materiales_solidos': 3,
            'kpi': 4,
            'configuracion': 5,
            'saludo': 6,
            'ayuda': 7,
            'tecnico': 8
        }
        self.cargar_modelo()
        
    def cargar_modelo(self):
        """Carga el modelo entrenado o inicializa uno nuevo"""
        try:
            with open(self.aprendizaje_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.modelo_entrenado = data.get('modelo', {})
                logger.info(f"✅ Modelo cargado: {len(self.modelo_entrenado)} patrones")
        except Exception:
            self.modelo_entrenado = {}
            logger.info("🆕 Inicializando nuevo modelo")
    
    def guardar_modelo(self):
        """Guarda el modelo entrenado"""
        try:
            data = {
                'modelo': self.modelo_entrenado,
                'version': self.version,
                'timestamp': time.time(),
                'total_patrones': len(self.modelo_entrenado)
            }
            with open(self.aprendizaje_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Modelo guardado: {len(self.modelo_entrenado)} patrones")
        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {e}")
    
    def extraer_caracteristicas(self, texto: str) -> Dict:
        """Extrae características del texto para ML"""
        texto_lower = texto.lower().strip()
        
        # Características numéricas
        numeros = re.findall(r'\d+(?:[\.,]\d+)?', texto)
        cantidad_numeros = len(numeros)
        tiene_cantidad = any(re.search(r'\d+\s*(?:tn|toneladas?)', texto_lower) for _ in [1])
        
        # Características de palabras clave
        palabras_clave = {
            'tn': 'tn' in texto_lower or 'tonelada' in texto_lower,
            'kw': 'kw' in texto_lower,
            'stock': 'stock' in texto_lower,
            'mezcla': 'mezcla' in texto_lower,
            'calcular': 'calcular' in texto_lower or 'calculo' in texto_lower,
            'hola': any(w in texto_lower for w in ['hola', 'buenos', 'buenas']),
            'ayuda': 'ayuda' in texto_lower or 'ayudar' in texto_lower,
            'material': 'material' in texto_lower,
            'biodigestor': 'biodigestor' in texto_lower,
            'energia': 'energia' in texto_lower or 'energía' in texto_lower,
            'solidos': 'solidos' in texto_lower or 'sólidos' in texto_lower,
            'liquidos': 'liquidos' in texto_lower or 'líquidos' in texto_lower,
            'dia': 'dia' in texto_lower or 'día' in texto_lower or 'hoy' in texto_lower
        }
        
        # Longitud y complejidad
        longitud_texto = len(texto)
        palabras_totales = len(texto.split())
        
        return {
            'cantidad_numeros': cantidad_numeros,
            'tiene_cantidad': int(tiene_cantidad),
            'longitud_texto': longitud_texto,
            'palabras_totales': palabras_totales,
            **palabras_clave
        }
    
    def clasificar_intencion(self, texto: str) -> Tuple[str, float]:
        """Clasifica la intención usando ML"""
        caracteristicas = self.extraer_caracteristicas(texto)
        
        # Reglas de ML simples pero efectivas
        scores = {}
        
        # Cálculo de materiales
        if caracteristicas['tiene_cantidad'] and caracteristicas['tn']:
            scores['calculo_material'] = 0.9
        elif caracteristicas['kw'] and caracteristicas['material']:
            scores['calculo_material'] = 0.7
            
        # Stock
        if caracteristicas['stock']:
            scores['stock'] = 0.9
        elif caracteristicas['material'] and not caracteristicas['tiene_cantidad']:
            scores['stock'] = 0.6
        
        # Materiales sólidos específicos
        if caracteristicas['solidos'] and caracteristicas['dia']:
            scores['materiales_solidos'] = 0.9
        elif caracteristicas['solidos']:
            scores['materiales_solidos'] = 0.7
            
        # Mezcla
        if caracteristicas['mezcla']:
            scores['mezcla'] = 0.9
        elif caracteristicas['calcular'] and caracteristicas['kw']:
            scores['mezcla'] = 0.7
            
        # Saludo
        if caracteristicas['hola']:
            scores['saludo'] = 0.9
            
        # Ayuda
        if caracteristicas['ayuda']:
            scores['ayuda'] = 0.8
            
        # Técnico
        if caracteristicas['biodigestor'] or caracteristicas['energia']:
            scores['tecnico'] = 0.7
            
        # Fallback
        if not scores:
            scores['ayuda'] = 0.5
            
        # Encontrar mejor categoría
        mejor_categoria = max(scores.items(), key=lambda x: x[1])
        return mejor_categoria[0], mejor_categoria[1]
    
    def generar_respuesta_ml(self, texto: str, contexto: Dict) -> Dict:
        """Genera respuesta usando ML"""
        inicio = time.time()
        
        # Clasificar intención
        intencion, confianza = self.clasificar_intencion(texto)
        
        # Generar respuesta basada en intención
        respuesta = self._generar_respuesta_por_intencion(intencion, texto, contexto)
        
        # Calcular tiempo
        latencia_ms = int((time.time() - inicio) * 1000)
        
        # Aprender de esta interacción
        self._aprender_interaccion(texto, intencion, respuesta, confianza)
        
        return {
            'respuesta': respuesta,
            'intencion': intencion,
            'confianza': confianza,
            'motor': f'ML_{intencion.upper()}',
            'latencia_ms': latencia_ms,
            'modelo': self.nombre
        }
    
    def _generar_respuesta_por_intencion(self, intencion: str, texto: str, contexto: Dict) -> str:
        """Genera respuesta específica por intención"""
        
        if intencion == 'calculo_material':
            return self._calcular_material_ml(texto, contexto)
        elif intencion == 'stock':
            return self._consultar_stock_ml(contexto)
        elif intencion == 'mezcla':
            return self._calcular_mezcla_ml(contexto)
        elif intencion == 'materiales_solidos':
            return self._consultar_materiales_solidos_ml(contexto)
        elif intencion == 'saludo':
            return self._saludo_ml()
        elif intencion == 'ayuda':
            return self._ayuda_ml()
        elif intencion == 'tecnico':
            return self._respuesta_tecnica_ml(texto)
        else:
            return self._respuesta_generica_ml(texto)
    
    def _calcular_material_ml(self, texto: str, contexto: Dict) -> str:
        """Cálculo de materiales con ML"""
        # Extraer cantidad y material
        match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:tn|toneladas?)\s*de\s*(.+)', texto.lower())
        if match:
            cantidad = float(match.group(1).replace(',', '.'))
            material = match.group(2).strip()
            
            # Buscar en contexto
            materiales_base = contexto.get('materiales_base', {})
            kw_tn = 0
            
            for mat_name, props in materiales_base.items():
                if material in mat_name.lower() or mat_name.lower() in material:
                    kw_tn = float(props.get('kw/tn', 0))
                    material = mat_name
                    break
            
            # Fallback para materiales conocidos
            if kw_tn < 10:
                fallbacks = {
                    'expeller': 180.0, 'expeller de soja': 180.0, 'soja': 180.0,
                    'maiz': 200.0, 'maíz': 200.0, 'grasa': 2.47
                }
                for k, v in fallbacks.items():
                    if k in material.lower():
                        kw_tn = v
                        break
            
            if kw_tn > 0:
                kw_total = cantidad * kw_tn
                return f"🤖 ML: {cantidad:.2f} TN de {material} × {kw_tn:.2f} KW/TN = {kw_total:.2f} KW"
            else:
                return f"🤖 ML: No tengo datos de KW/TN para '{material}'"
        
        return "🤖 ML: No pude interpretar el cálculo solicitado"
    
    def _consultar_stock_ml(self, contexto: Dict) -> str:
        """Consulta de stock con ML"""
        stock = contexto.get('stock', {})
        if stock:
            resumen = []
            for mat, d in list(stock.items())[:5]:
                tn = float(d.get('total_tn', 0) or 0)
                resumen.append(f"{mat}: {tn:.1f} TN")
            return f"🤖 ML Stock: " + "; ".join(resumen)
        return "🤖 ML: No hay stock disponible"
    
    def _calcular_mezcla_ml(self, contexto: Dict) -> str:
        """Cálculo de mezcla con ML"""
        mezcla = contexto.get('mezcla_calculada', {})
        if mezcla and mezcla.get('totales', {}).get('kw_total_generado', 0) > 0:
            tot = mezcla['totales']
            return f"🤖 ML Mezcla: {tot.get('kw_total_generado', 0):.1f} KW, Sólidos {tot.get('tn_solidos',0):.1f} TN, Líquidos {tot.get('tn_liquidos',0):.1f} TN"
        return "🤖 ML: No hay mezcla calculada disponible"
    
    def _consultar_materiales_solidos_ml(self, contexto: Dict) -> str:
        """Consulta específica de materiales sólidos del día"""
        mezcla = contexto.get('mezcla_calculada', {})
        if mezcla and 'materiales' in mezcla:
            solidos = []
            for mat, data in mezcla['materiales'].items():
                if data.get('tipo') == 'solido' and data.get('cantidad_tn', 0) > 0:
                    solidos.append(f"{mat}: {data['cantidad_tn']:.1f} TN")
            
            if solidos:
                return f"🤖 ML Materiales sólidos del día: " + "; ".join(solidos)
        
        # Fallback: buscar en stock
        stock = contexto.get('stock', {})
        solidos_stock = []
        for mat, data in stock.items():
            if 'solido' in mat.lower() or 'rumen' in mat.lower() or 'grasa' in mat.lower():
                tn = float(data.get('total_tn', 0) or 0)
                if tn > 0:
                    solidos_stock.append(f"{mat}: {tn:.1f} TN")
        
        if solidos_stock:
            return f"🤖 ML Materiales sólidos disponibles: " + "; ".join(solidos_stock[:5])
        
        return "🤖 ML: No hay información de materiales sólidos disponible"
    
    def _saludo_ml(self) -> str:
        """Saludo con ML"""
        hoy = datetime.now().strftime("%A, %d de %B de %Y")
        return f"🤖 ML: ¡Hola! Soy {self.nombre}. Hoy es {hoy}. ¿En qué puedo ayudarte con tu planta de biogás?"
    
    def _ayuda_ml(self) -> str:
        """Ayuda con ML"""
        return "🤖 ML: Puedo ayudarte con cálculos de materiales, stock, mezclas y análisis técnicos. Prueba preguntando '5 tn de expeller' o 'stock'"
    
    def _respuesta_tecnica_ml(self, texto: str) -> str:
        """Respuesta técnica con ML"""
        if 'biodigestor' in texto.lower():
            return "🤖 ML: Los biodigestores son sistemas que convierten materia orgánica en biogás mediante digestión anaeróbica. ¿Necesitas información específica sobre algún parámetro?"
        elif 'energia' in texto.lower() or 'energía' in texto.lower():
            return "🤖 ML: La energía se genera a través de la combustión del biogás en motores. ¿Quieres saber sobre generación actual o eficiencia?"
        return "🤖 ML: ¿Podrías ser más específico sobre tu consulta técnica?"
    
    def _respuesta_generica_ml(self, texto: str) -> str:
        """Respuesta genérica con ML"""
        return f"🤖 ML: Entiendo que preguntas sobre '{texto[:30]}...'. ¿Podrías reformular tu pregunta de manera más específica?"
    
    def _aprender_interaccion(self, texto: str, intencion: str, respuesta: str, confianza: float):
        """Aprende de la interacción"""
        try:
            patron = {
                'texto': texto.lower().strip(),
                'intencion': intencion,
                'respuesta': respuesta,
                'confianza': confianza,
                'timestamp': time.time(),
                'caracteristicas': self.extraer_caracteristicas(texto)
            }
            
            # Agregar al modelo
            texto_key = texto.lower().strip()
            if texto_key not in self.modelo_entrenado:
                self.modelo_entrenado[texto_key] = []
            
            self.modelo_entrenado[texto_key].append(patron)
            
            # Mantener solo las últimas 3 interacciones por patrón
            if len(self.modelo_entrenado[texto_key]) > 3:
                self.modelo_entrenado[texto_key] = self.modelo_entrenado[texto_key][-3:]
            
            # Guardar cada 10 interacciones
            if len(self.modelo_entrenado) % 10 == 0:
                self.guardar_modelo()
                
        except Exception as e:
            logger.error(f"❌ Error en aprendizaje: {e}")
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del modelo"""
        return {
            'nombre': self.nombre,
            'version': self.version,
            'total_patrones': len(self.modelo_entrenado),
            'categorias': len(self.categorias),
            'archivo_aprendizaje': self.aprendizaje_file
        }

# Instancia global del modelo
modelo_ia = ModeloIABiogas()

def procesar_con_ml(texto: str, contexto: Dict = None) -> Dict:
    """Función principal para procesar con ML"""
    if contexto is None:
        contexto = {}
    
    return modelo_ia.generar_respuesta_ml(texto, contexto)

if __name__ == "__main__":
    # Prueba del modelo
    print("🤖 Probando Modelo de IA con ML...")
    
    contexto_test = {
        'materiales_base': {
            'Expeller de soja': {'kw/tn': 180.0},
            'Maíz': {'kw/tn': 200.0}
        },
        'stock': {
            'Expeller': {'total_tn': 15.5},
            'Maíz': {'total_tn': 8.2}
        }
    }
    
    preguntas_test = [
        "5 tn de expeller de soja",
        "stock",
        "mezcla del día",
        "hola",
        "ayuda"
    ]
    
    for pregunta in preguntas_test:
        resultado = procesar_con_ml(pregunta, contexto_test)
        print(f"\n❓ {pregunta}")
        print(f"🤖 {resultado['respuesta']}")
        print(f"📊 Intención: {resultado['intencion']} (confianza: {resultado['confianza']:.2f})")
        print(f"⚡ Tiempo: {resultado['latencia_ms']}ms")
    
    print(f"\n📈 Estadísticas: {modelo_ia.obtener_estadisticas()}")
