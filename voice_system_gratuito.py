#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Voz Gratuito con Parler-TTS
Reemplaza Eleven Labs con una solución completamente gratuita
"""

import os
import logging
import base64
import io
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
import requests
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParlerTTSVoiceSystem:
    """Sistema de voz gratuito usando Parler-TTS de Hugging Face"""
    
    def __init__(self):
        self.is_initialized = False
        self.model_name = "parler-tts/parler_tts_mini_v0.1"
        self.api_url = "https://api-inference.huggingface.co/models/parler-tts/parler_tts_mini_v0.1"
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY', '')}",
            "Content-Type": "application/json"
        }
        
        # Configuraciones de voz para español
        self.voice_profiles = {
            'sibia_asistente': {
                'description': 'Voz profesional para asistente técnico SIBIA',
                'language': 'es',
                'speed': 1.0,
                'pitch': 0.0
            },
            'sibia_explicativo': {
                'description': 'Voz clara para explicaciones técnicas',
                'language': 'es',
                'speed': 0.9,
                'pitch': 0.1
            },
            'sibia_alerta': {
                'description': 'Voz firme para alertas del sistema',
                'language': 'es',
                'speed': 1.1,
                'pitch': -0.1
            }
        }
        
        self.initialize_parler_tts()
    
    def initialize_parler_tts(self):
        """Inicializar Parler-TTS"""
        try:
            logger.info("🔄 Inicializando Parler-TTS...")
            
            # Verificar si tenemos API key de Hugging Face
            api_key = os.environ.get('HUGGINGFACE_API_KEY')
            if not api_key:
                logger.warning("⚠️ No hay API key de Hugging Face - usando modo local")
                self.is_initialized = True  # Funcionará con Edge-TTS como fallback
            else:
                logger.info("✅ API key de Hugging Face encontrada")
                self.is_initialized = True
            
            logger.info("✅ Parler-TTS inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Parler-TTS: {e}")
            self.is_initialized = False
    
    def generate_speech_parler_tts(self, text: str, voice_profile: str = 'sibia_asistente') -> Optional[bytes]:
        """
        Generar audio usando Parler-TTS
        
        Args:
            text: Texto a convertir en voz
            voice_profile: Perfil de voz a usar
            
        Returns:
            bytes: Audio en formato bytes o None si falla
        """
        try:
            # Limpiar texto para mejor pronunciación
            clean_text = self._clean_text_for_tts(text)
            
            # Preparar payload para Parler-TTS
            payload = {
                "inputs": clean_text,
                "parameters": {
                    "max_length": 512,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            # Hacer solicitud a Hugging Face
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parler-TTS devuelve audio directamente
                audio_data = response.content
                logger.info(f"🎵 Audio Parler-TTS generado: {len(audio_data)} bytes")
                return audio_data
            else:
                logger.error(f"❌ Error Parler-TTS: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generando audio Parler-TTS: {e}")
            return None
    
    def generate_speech_edge_tts(self, text: str, voice_profile: str = 'sibia_asistente') -> Optional[bytes]:
        """
        Fallback usando Edge-TTS (completamente gratuito)
        """
        try:
            import edge_tts
            import asyncio
            
            # Limpiar texto para Edge-TTS
            clean_text = self._clean_text_for_tts(text)
            
            # Seleccionar voz en español
            voice_map = {
                'sibia_asistente': 'es-ES-LauraNeural',
                'sibia_explicativo': 'es-ES-ElviraNeural',
                'sibia_alerta': 'es-ES-AlvaroNeural'
            }
            
            voice = voice_map.get(voice_profile, 'es-ES-LauraNeural')
            
            async def _generate():
                communicate = edge_tts.Communicate(clean_text, voice)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data
            
            # Ejecutar en loop de eventos
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_bytes = loop.run_until_complete(_generate())
            loop.close()
            
            logger.info("🎵 Audio Edge-TTS generado como fallback")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Error en Edge-TTS fallback: {e}")
            return None
    
    def generate_speech(self, text: str, voice_profile: str = 'sibia_asistente') -> Optional[bytes]:
        """
        Generar audio con fallback automático
        
        Args:
            text: Texto a convertir
            voice_profile: Perfil de voz
            
        Returns:
            bytes: Audio generado
        """
        try:
            # Intentar Parler-TTS primero
            audio_bytes = self.generate_speech_parler_tts(text, voice_profile)
            
            if audio_bytes:
                return audio_bytes
            else:
                # Fallback a Edge-TTS
                logger.info("🔄 Parler-TTS falló, usando Edge-TTS como fallback")
                return self.generate_speech_edge_tts(text, voice_profile)
                
        except Exception as e:
            logger.error(f"❌ Error en generación de voz: {e}")
            return self.generate_speech_edge_tts(text, voice_profile)
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Limpiar texto para mejor pronunciación en TTS"""
        try:
            # Normalizar abreviaciones para mejor pronunciación
            clean_text = text
            # Correcciones específicas de pronunciación
            clean_text = clean_text.replace('más', 'mas')  # Corregir "más"
            clean_text = clean_text.replace('purín', 'purin')  # Corregir "purín"
            clean_text = clean_text.replace('óptimo', 'optimo')  # Corregir "óptimo"
            clean_text = clean_text.replace('energía', 'energia')  # Corregir "energía"
            clean_text = clean_text.replace('qué', 'que')  # Corregir "qué"
            clean_text = clean_text.replace('ñ', 'ni')  # Corregir "ñ"
            clean_text = clean_text.replace('Ñ', 'NI')  # Corregir "Ñ"
            # Abreviaciones principales
            clean_text = clean_text.replace('KW/TN', 'kilovatios por tonelada')
            clean_text = clean_text.replace('KWH', 'kilovatios hora')
            clean_text = clean_text.replace('KW', 'kilovatios')
            clean_text = clean_text.replace('TN', 'toneladas')
            clean_text = clean_text.replace('ST', 'sólidos totales')
            clean_text = clean_text.replace('SV', 'sólidos volátiles')
            clean_text = clean_text.replace('CH4', 'metano')
            clean_text = clean_text.replace('CO2', 'dióxido de carbono')
            clean_text = clean_text.replace('H2S', 'ácido sulfhídrico')
            clean_text = clean_text.replace('PH', 'pe hache')
            clean_text = clean_text.replace('TRH', 'tiempo de retención hidráulica')
            clean_text = clean_text.replace('m³', 'metros cúbicos')
            clean_text = clean_text.replace('kg', 'kilogramos')
            clean_text = clean_text.replace('°C', 'grados centígrados')
            # Limpiar markdown y caracteres especiales
            clean_text = clean_text.replace('**', '')  # Remover markdown bold
            clean_text = clean_text.replace('*', '')     # Remover markdown italic
            clean_text = clean_text.replace('#', '')       # Remover headers markdown
            clean_text = clean_text.replace('•', '')               # Remover bullets
            # Limpiar caracteres especiales
            import re
            clean_text = re.sub(r'[^\w\s.,!?¿¡:;()-]', ' ', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text)            # Normalizar espacios
            clean_text = clean_text.strip()
            
            return clean_text
            
        except Exception as e:
            logger.error(f"Error limpiando texto: {e}")
            return text
    
    def process_ia_response_with_voice(self, texto_respuesta: str, tipo_respuesta: str = 'normal') -> Dict[str, Any]:
        """
        Procesar respuesta del IA y generar audio
        
        Args:
            texto_respuesta: Respuesta del sistema IA
            tipo_respuesta: Tipo de respuesta (normal, alerta, explicacion)
            
        Returns:
            Dict con respuesta y audio
        """
        try:
            # Seleccionar perfil de voz según el tipo
            voice_profiles_map = {
                'normal': 'sibia_asistente',
                'alerta': 'sibia_alerta',
                'explicacion': 'sibia_explicativo',
                'tecnico': 'sibia_explicativo'
            }
            
            voice_profile = voice_profiles_map.get(tipo_respuesta, 'sibia_asistente')
            
            # Generar audio
            audio_bytes = self.generate_speech(texto_respuesta, voice_profile)
            
            audio_base64 = None
            if audio_bytes:
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                audio_base64 = f"data:audio/wav;base64,{audio_base64}"
            
            resultado = {
                'texto': texto_respuesta,
                'audio_disponible': audio_base64 is not None,
                'audio_base64': audio_base64,
                'voice_profile': voice_profile,
                'tts_system': 'parler_tts_edge_fallback',
                'timestamp': datetime.now().isoformat()
            }
            
            if audio_base64:
                logger.info(f"🎵 Audio generado para respuesta tipo '{tipo_respuesta}'")
            else:
                logger.warning(f"⚠️ No se pudo generar audio para: {texto_respuesta[:50]}...")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error procesando respuesta con voz: {e}")
            return {
                'texto': texto_respuesta,
                'audio_disponible': False,
                'audio_base64': None,
                'voice_profile': 'error',
                'tts_system': 'error',
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de voz"""
        return {
            'parler_tts_disponible': self.is_initialized,
            'edge_tts_fallback': True,
            'perfiles_voz': list(self.voice_profiles.keys()),
            'modelo': self.model_name,
            'api_url': self.api_url,
            'gratuito': True,
            'sin_limites': True
        }

# Instancia global del sistema de voz gratuito
voice_system_gratuito = ParlerTTSVoiceSystem()

def generar_audio_gratuito(texto: str, tipo: str = 'normal') -> Dict[str, Any]:
    """
    Función principal para generar respuesta con voz gratuita
    
    Args:
        texto: Texto de la respuesta
        tipo: Tipo de respuesta
        
    Returns:
        Dict con respuesta procesada
    """
    return voice_system_gratuito.process_ia_response_with_voice(texto, tipo)

def get_voice_system_status_gratuito() -> Dict[str, Any]:
    """Obtener estado del sistema de voz gratuito"""
    return voice_system_gratuito.get_system_status()

if __name__ == "__main__":
    # Prueba del sistema
    print("🎵 Probando Sistema de Voz Gratuito...")
    
    status = get_voice_system_status_gratuito()
    print(f"📊 Estado del sistema: {status}")
    
    # Probar diferentes tipos de respuesta
    test_responses = [
        ("Bienvenido al sistema SIBIA. Análisis de biodigestores iniciado.", "normal"),
        ("Alerta: Temperatura del biodigestor 1 fuera del rango óptimo.", "alerta"),
        ("El sistema utiliza redes neuronales y XGBoost para predicciones avanzadas.", "explicacion")
    ]
    
    for texto, tipo in test_responses:
        print(f"\n🧪 Probando respuesta tipo '{tipo}'...")
        resultado = generar_audio_gratuito(texto, tipo)
        print(f"✅ Audio generado: {resultado['audio_disponible']}")
        print(f"🎵 Sistema usado: {resultado['tts_system']}")
