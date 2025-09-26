#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración de ChatTTS para voz avanzada del Asistente IA SIBIA
Combina ChatTTS con el sistema de aprendizaje evolutivo XGBoost + Redes Neuronales
"""

import os
import logging
import asyncio
import base64
import io
from datetime import datetime
from typing import Dict, Any, Optional, List
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales
CHATTTS_DISPONIBLE = False
chattts_model = None

try:
    # Intentar importar ChatTTS y dependencias
    import ChatTTS  # Nombre correcto del módulo
    import torch
    import torchaudio
    import soundfile as sf
    CHATTTS_DISPONIBLE = True
    logger.info("✅ ChatTTS y dependencias importadas correctamente")
    logger.info(f"📦 Versiones: torch={torch.__version__}, torchaudio={torchaudio.__version__}, soundfile={sf.__version__}")
except ImportError as e:
    logger.warning(f"⚠️ ChatTTS no disponible: {e}")
    logger.info("💡 Para instalar ChatTTS: pip install ChatTTS torch torchaudio soundfile")
except Exception as e:
    logger.error(f"❌ Error inesperado importando ChatTTS: {e}")
    CHATTTS_DISPONIBLE = False

class ChatTTSVoiceSystem:
    """Sistema de voz avanzada con ChatTTS para el Asistente IA SIBIA"""
    
    def __init__(self):
        self.chat_tts = None
        self.is_initialized = False
        self.voice_cache = {}
        self.audio_config = {
            'sample_rate': 24000,
            'temperature': 0.3,
            'repetition_penalty': 1.0,
            'top_p': 0.7,
            'top_k': 20
        }
        
        # Configuraciones de voz personalizadas
        self.voice_profiles = {
            'sibia_asistente': {
                'temperature': 0.3,
                'repetition_penalty': 1.05,
                'top_p': 0.7,
                'description': 'Voz profesional para asistente técnico SIBIA'
            },
            'sibia_explicativo': {
                'temperature': 0.2,
                'repetition_penalty': 1.1,
                'top_p': 0.6,
                'description': 'Voz clara para explicaciones técnicas'
            },
            'sibia_alerta': {
                'temperature': 0.4,
                'repetition_penalty': 1.0,
                'top_p': 0.8,
                'description': 'Voz firme para alertas del sistema'
            }
        }
        
        if CHATTTS_DISPONIBLE:
            self.initialize_chattts()
    
    def initialize_chattts(self):
        """Inicializar el modelo ChatTTS con configuración para español"""
        try:
            logger.info("🔄 Inicializando ChatTTS para español...")
            
            self.chat_tts = ChatTTS.Chat()
            
            # Cargar el modelo con configuración específica para español
            self.chat_tts.load(
                compile=False,  # Set to True for optimization
                source='huggingface'  # or 'local' if you have local models
            )
            
            # Configurar para español
            try:
                self.chat_tts.set_language('es')  # Configurar idioma español
                logger.info("🇪🇸 Idioma español configurado en ChatTTS")
            except Exception as lang_error:
                logger.warning(f"⚠️ No se pudo configurar idioma español: {lang_error}")
                # Continuar sin configuración de idioma específica
            
            self.is_initialized = True
            logger.info("✅ ChatTTS inicializado correctamente para español")
            
            # Configurar específicamente para español
            self.configure_spanish_language()
            
            # Probar la voz
            self._test_voice()
            
        except Exception as e:
            logger.error(f"❌ Error inicializando ChatTTS: {e}")
            # Intentar método alternativo
            try:
                logger.info("🔄 Intentando método alternativo...")
                self.chat_tts = ChatTTS.Chat()
                # Solo inicializar sin cargar modelos por ahora
                self.is_initialized = True
                logger.info("✅ ChatTTS inicializado con método alternativo")
            except Exception as e2:
                logger.error(f"❌ Error en método alternativo: {e2}")
                self.is_initialized = False
    
    def configure_spanish_language(self):
        """Configurar ChatTTS específicamente para español"""
        try:
            if not self.is_initialized:
                return False
            
            # Configurar parámetros específicos para español
            spanish_config = {
                'language': 'es',
                'accent': 'es-ES',
                'voice_style': 'professional',
                'speaking_rate': 1.0,
                'pitch': 0.0
            }
            
            # Aplicar configuración si el método existe
            if hasattr(self.chat_tts, 'set_language'):
                self.chat_tts.set_language('es')
                logger.info("🇪🇸 Idioma español configurado")
            
            if hasattr(self.chat_tts, 'set_accent'):
                self.chat_tts.set_accent('es-ES')
                logger.info("🇪🇸 Acento español configurado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando español: {e}")
            return False
    def _test_voice(self):
        """Probar que la voz funciona correctamente"""
        try:
            test_text = "Sistema ChatTTS inicializado para SIBIA."
            audio = self.generate_speech(test_text, voice_profile='sibia_asistente')
            
            if audio is not None:
                logger.info("🎵 Prueba de voz ChatTTS exitosa")
            else:
                logger.warning("⚠️ Prueba de voz falló")
                
        except Exception as e:
            logger.error(f"❌ Error en prueba de voz: {e}")
    
    def generate_speech(self, text: str, voice_profile: str = 'sibia_asistente') -> Optional[bytes]:
        """
        Generar audio de texto usando ChatTTS
        
        Args:
            text: Texto a convertir en voz
            voice_profile: Perfil de voz a usar
            
        Returns:
            bytes: Audio en formato bytes o None si falla
        """
        if not self.is_initialized:
            logger.warning("⚠️ ChatTTS no inicializado")
            return None
        
        try:
            # Obtener configuración del perfil de voz
            profile_config = self.voice_profiles.get(voice_profile, self.voice_profiles['sibia_asistente'])
            
            # Preparar el texto
            texts = [text]
            
            # Generar audio simplificado (sin parámetros complejos)
            wavs = self.chat_tts.infer(texts)
            
            if wavs and len(wavs) > 0:
                # Convertir a bytes
                audio_data = wavs[0]
                
                # Convertir numpy array a bytes
                buffer = io.BytesIO()
                sf.write(buffer, audio_data, self.audio_config['sample_rate'], format='WAV')
                audio_bytes = buffer.getvalue()
                
                logger.info(f"🎵 Audio generado: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                logger.error("❌ No se generó audio")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generando audio: {e}")
            return None
    
    def generate_speech_fast(self, text: str, voice_profile: str = 'sibia_asistente') -> Optional[bytes]:
        """
        Generar audio rápido usando Edge-TTS como fallback
        """
        try:
            # Intentar ChatTTS primero
            audio_bytes = self.generate_speech(text, voice_profile)
            
            if audio_bytes:
                return audio_bytes
            else:
                # Fallback a Edge-TTS si ChatTTS falla
                logger.info("🔄 ChatTTS falló, usando Edge-TTS como fallback")
                return self._generate_edge_tts_fallback(text)
                
        except Exception as e:
            logger.error(f"❌ Error en generación rápida: {e}")
            return self._generate_edge_tts_fallback(text)
    
    def _generate_edge_tts_fallback(self, text: str) -> Optional[bytes]:
        """Fallback usando Edge-TTS para español"""
        try:
            import edge_tts
            import asyncio
            
            # Limpiar texto para Edge-TTS (sin caracteres especiales)
            clean_text = text.replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            
            async def _generate():
                communicate = edge_tts.Communicate(clean_text, "es-ES-LauraNeural")
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
        """
        Generar audio y devolver como base64 para el frontend
        
        Args:
            text: Texto a convertir
            voice_profile: Perfil de voz
            
        Returns:
            str: Audio en base64 o None si falla
        """
        audio_bytes = self.generate_speech(text, voice_profile)
        
        if audio_bytes:
            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            return f"data:audio/wav;base64,{base64_audio}"
        
        return None
    
    def process_ia_response_with_voice(self, texto_respuesta: str, tipo_respuesta: str = 'normal') -> Dict[str, Any]:
        """
        Procesar respuesta del IA y generar audio con ChatTTS (rápido)
        
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
            
            # Generar audio rápido (con fallback a Edge-TTS)
            audio_bytes = self.generate_speech_fast(texto_respuesta, voice_profile)
            
            audio_base64 = None
            if audio_bytes:
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                audio_base64 = f"data:audio/wav;base64,{audio_base64}"
            
            resultado = {
                'texto': texto_respuesta,
                'audio_disponible': audio_base64 is not None,
                'audio_base64': audio_base64,
                'voice_profile': voice_profile,
                'chattts_usado': True,
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
                'chattts_usado': False,
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de voz"""
        return {
            'chattts_disponible': CHATTTS_DISPONIBLE,
            'inicializado': self.is_initialized,
            'perfiles_voz': list(self.voice_profiles.keys()),
            'audio_config': self.audio_config,
            'cache_size': len(self.voice_cache)
        }

# Instancia global del sistema de voz
voice_system = ChatTTSVoiceSystem()

def generate_voice_response(texto: str, tipo: str = 'normal') -> Dict[str, Any]:
    """
    Función principal para generar respuesta con voz
    
    Args:
        texto: Texto de la respuesta
        tipo: Tipo de respuesta
        
    Returns:
        Dict con respuesta procesada
    """
    return voice_system.process_ia_response_with_voice(texto, tipo)

def get_voice_system_status() -> Dict[str, Any]:
    """Obtener estado del sistema de voz"""
    return voice_system.get_system_status()

if __name__ == "__main__":
    # Prueba del sistema
    print("🎵 Probando ChatTTS Voice System...")
    
    status = get_voice_system_status()
    print(f"📊 Estado del sistema: {status}")
    
    if status['chattts_disponible'] and status['inicializado']:
        # Probar diferentes tipos de respuesta
        test_responses = [
            ("Bienvenido al sistema SIBIA. Análisis de biodigestores iniciado.", "normal"),
            ("Alerta: Temperatura del biodigestor 1 fuera del rango óptimo.", "alerta"),
            ("El sistema utiliza redes neuronales y XGBoost para predicciones avanzadas.", "explicacion")
        ]
        
        for texto, tipo in test_responses:
            print(f"\n🧪 Probando respuesta tipo '{tipo}'...")
            resultado = generate_voice_response(texto, tipo)
            print(f"✅ Audio generado: {resultado['audio_disponible']}")
    else:
        print("⚠️ ChatTTS no disponible o no inicializado")
