"""
Sistema de Memoria y Aprendizaje para JARVIS
Implementa RAG (Retrieval Augmented Generation) básico
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class JarvisMemory:
    """Sistema de memoria persistente para JARVIS"""
    
    def __init__(self, memory_file: str = "jarvis_memory.json"):
        self.memory_file = memory_file
        self.memoria = self._cargar_memoria()
        
    def _cargar_memoria(self) -> Dict:
        """Carga la memoria desde archivo JSON"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"✅ Memoria JARVIS cargada: {len(data.get('conversaciones', []))} conversaciones")
                    return data
            except Exception as e:
                logger.error(f"Error cargando memoria: {e}")
        
        # Memoria vacía inicial
        return {
            "conversaciones": [],
            "preferencias_usuario": {},
            "patrones_aprendidos": {},
            "contexto_frecuente": {},
            "estadisticas": {
                "total_conversaciones": 0,
                "temas_mas_consultados": {},
                "tiempo_promedio_respuesta": 0
            }
        }
    
    def _guardar_memoria(self):
        """Guarda la memoria en archivo JSON"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memoria, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Memoria JARVIS guardada: {self.memory_file}")
        except Exception as e:
            logger.error(f"Error guardando memoria: {e}")
    
    def agregar_conversacion(
        self, 
        usuario: str,
        pregunta: str, 
        respuesta: str, 
        intencion: str = None,
        contexto: Dict = None,
        feedback: str = None
    ):
        """Registra una conversación completa"""
        conversacion = {
            "timestamp": datetime.now().isoformat(),
            "usuario": usuario,
            "pregunta": pregunta,
            "respuesta": respuesta,
            "intencion": intencion,
            "contexto": contexto or {},
            "feedback": feedback,
            "id": len(self.memoria["conversaciones"]) + 1
        }
        
        self.memoria["conversaciones"].append(conversacion)
        
        # Actualizar estadísticas
        self.memoria["estadisticas"]["total_conversaciones"] += 1
        
        if intencion:
            temas = self.memoria["estadisticas"]["temas_mas_consultados"]
            temas[intencion] = temas.get(intencion, 0) + 1
        
        self._guardar_memoria()
        logger.info(f"📝 Conversación guardada: {pregunta[:50]}...")
    
    def buscar_conversaciones_similares(
        self, 
        pregunta: str, 
        limite: int = 5
    ) -> List[Dict]:
        """
        Busca conversaciones similares en la memoria
        Implementación simple basada en palabras clave
        """
        palabras_clave = set(pregunta.lower().split())
        conversaciones = self.memoria["conversaciones"]
        
        # Calcular relevancia de cada conversación
        resultados = []
        for conv in conversaciones:
            palabras_conv = set(conv["pregunta"].lower().split())
            # Similaridad simple: palabras en común
            coincidencias = len(palabras_clave & palabras_conv)
            
            if coincidencias > 0:
                resultados.append({
                    "conversacion": conv,
                    "relevancia": coincidencias
                })
        
        # Ordenar por relevancia y retornar top N
        resultados.sort(key=lambda x: x["relevancia"], reverse=True)
        return [r["conversacion"] for r in resultados[:limite]]
    
    def obtener_contexto_historico(self, intencion: str = None) -> str:
        """
        Obtiene contexto histórico relevante para mejorar respuestas
        """
        if not self.memoria["conversaciones"]:
            return ""
        
        # Filtrar por intención si se especifica
        conversaciones_relevantes = []
        if intencion:
            conversaciones_relevantes = [
                c for c in self.memoria["conversaciones"][-20:]  # Últimas 20
                if c.get("intencion") == intencion
            ]
        else:
            conversaciones_relevantes = self.memoria["conversaciones"][-10:]
        
        if not conversaciones_relevantes:
            return ""
        
        # Construir resumen de conversaciones previas
        contexto = "\n=== CONTEXTO HISTÓRICO ===\n"
        contexto += f"El usuario ha preguntado {len(conversaciones_relevantes)} veces sobre esto antes.\n"
        
        # Agregar ejemplos de conversaciones previas
        for conv in conversaciones_relevantes[-3:]:  # Últimas 3
            contexto += f"\n- Usuario preguntó: '{conv['pregunta']}'\n"
            contexto += f"  JARVIS respondió: '{conv['respuesta'][:100]}...'\n"
        
        return contexto
    
    def actualizar_preferencias(self, usuario: str, preferencia: str, valor: Any):
        """Guarda preferencias del usuario"""
        if usuario not in self.memoria["preferencias_usuario"]:
            self.memoria["preferencias_usuario"][usuario] = {}
        
        self.memoria["preferencias_usuario"][usuario][preferencia] = {
            "valor": valor,
            "timestamp": datetime.now().isoformat()
        }
        
        self._guardar_memoria()
        logger.info(f"💾 Preferencia guardada para {usuario}: {preferencia} = {valor}")
    
    def obtener_preferencias(self, usuario: str) -> Dict:
        """Obtiene preferencias del usuario"""
        return self.memoria["preferencias_usuario"].get(usuario, {})
    
    def aprender_patron(self, patron_id: str, descripcion: str, datos: Dict):
        """Aprende un patrón nuevo basado en interacciones"""
        self.memoria["patrones_aprendidos"][patron_id] = {
            "descripcion": descripcion,
            "datos": datos,
            "veces_observado": self.memoria["patrones_aprendidos"].get(patron_id, {}).get("veces_observado", 0) + 1,
            "ultima_vez": datetime.now().isoformat()
        }
        
        self._guardar_memoria()
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de uso"""
        stats = self.memoria["estadisticas"].copy()
        
        # Agregar más estadísticas calculadas
        if self.memoria["conversaciones"]:
            stats["ultima_conversacion"] = self.memoria["conversaciones"][-1]["timestamp"]
            stats["usuarios_unicos"] = len(set(c.get("usuario", "desconocido") for c in self.memoria["conversaciones"]))
        
        return stats
    
    def limpiar_memoria_antigua(self, dias: int = 30):
        """Limpia conversaciones más antiguas que X días"""
        from datetime import timedelta
        
        limite = datetime.now() - timedelta(days=dias)
        conversaciones_nuevas = [
            c for c in self.memoria["conversaciones"]
            if datetime.fromisoformat(c["timestamp"]) > limite
        ]
        
        removidas = len(self.memoria["conversaciones"]) - len(conversaciones_nuevas)
        self.memoria["conversaciones"] = conversaciones_nuevas
        
        if removidas > 0:
            self._guardar_memoria()
            logger.info(f"🗑️ Limpiadas {removidas} conversaciones antiguas")
        
        return removidas
    
    def exportar_para_entrenamiento(self, archivo_salida: str = "jarvis_training_data.jsonl"):
        """
        Exporta conversaciones en formato JSONL para fine-tuning
        """
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                for conv in self.memoria["conversaciones"]:
                    # Formato para fine-tuning de modelos
                    training_sample = {
                        "messages": [
                            {"role": "user", "content": conv["pregunta"]},
                            {"role": "assistant", "content": conv["respuesta"]}
                        ],
                        "metadata": {
                            "intencion": conv.get("intencion"),
                            "timestamp": conv.get("timestamp")
                        }
                    }
                    f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')
            
            logger.info(f"📤 Datos de entrenamiento exportados: {archivo_salida}")
            return True
        except Exception as e:
            logger.error(f"Error exportando datos: {e}")
            return False


# Instancia global de memoria
jarvis_memory = JarvisMemory()
