#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Voz Web para SIBIA
Implementa voz que funciona correctamente en contexto web
"""

import os
import sys
import json
import logging
import threading
import time
import base64
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logger = logging.getLogger(__name__)

class VoiceEngine(Enum):
    """Motores de voz disponibles"""
    PYTTSX3 = "pyttsx3"      # Motor local multiplataforma
    EDGE_TTS = "edge_tts"    # Microsoft Edge TTS (gratuito)
    GTTS = "gtts"            # Google TTS (requiere internet)

@dataclass
class VoiceConfig:
    """Configuración de voz"""
    engine: VoiceEngine = VoiceEngine.GTTS
    language: str = "es"
    rate: int = 200          # Velocidad de habla
    volume: float = 0.8     # Volumen (0.0 a 1.0)
    voice_id: Optional[str] = None  # ID específico de voz
    enabled: bool = True
    auto_speak: bool = True  # Hablar automáticamente las respuestas

class WebVoiceSystem:
    """Sistema de voz optimizado para web"""
    
    def __init__(self, config_file: str = "voice_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.engines = {}
        self.current_engine = None
        
        # Inicializar motores disponibles
        self._initialize_engines()
        
        logger.info(f"Sistema de voz web inicializado con motor: {self.config.engine.value}")
    
    def _load_config(self) -> VoiceConfig:
        """Cargar configuración de voz"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return VoiceConfig(**data)
        except Exception as e:
            logger.warning(f"Error cargando configuracion de voz: {e}")
        
        # Configuración por defecto - usar gTTS para web
        return VoiceConfig(engine=VoiceEngine.GTTS)
    
    def _save_config(self):
        """Guardar configuración de voz"""
        try:
            config_dict = {
                'engine': self.config.engine.value,
                'language': self.config.language,
                'rate': self.config.rate,
                'volume': self.config.volume,
                'voice_id': self.config.voice_id,
                'enabled': self.config.enabled,
                'auto_speak': self.config.auto_speak
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuracion de voz: {e}")
    
    def _initialize_engines(self):
        """Inicializar motores de voz disponibles"""
        
        # 1. gTTS - Google Text-to-Speech (mejor para web)
        try:
            from gtts import gTTS
            self.engines[VoiceEngine.GTTS] = {
                'engine': gTTS,
                'available': True
            }
            logger.info("gTTS disponible")
        except ImportError:
            logger.warning("gTTS no disponible - instalar con: pip install gtts")
        except Exception as e:
            logger.warning(f"Error inicializando gTTS: {e}")
        
        # 2. Edge-TTS - Microsoft Edge TTS
        try:
            import edge_tts
            self.engines[VoiceEngine.EDGE_TTS] = {
                'engine': edge_tts,
                'available': True
            }
            logger.info("Edge-TTS disponible")
        except ImportError:
            logger.warning("Edge-TTS no disponible - instalar con: pip install edge-tts")
        except Exception as e:
            logger.warning(f"Error inicializando Edge-TTS: {e}")
        
        # 3. pyttsx3 - Motor local (no funciona bien en servidor web)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            self.engines[VoiceEngine.PYTTSX3] = {
                'engine': engine,
                'voices': voices,
                'available': True
            }
            logger.info(f"pyttsx3 disponible - {len(voices)} voces encontradas")
        except ImportError:
            logger.warning("pyttsx3 no disponible - instalar con: pip install pyttsx3")
        except Exception as e:
            logger.warning(f"Error inicializando pyttsx3: {e}")
        
        # Seleccionar motor por defecto
        self._select_default_engine()
    
    def _select_default_engine(self):
        """Seleccionar motor por defecto basado en disponibilidad"""
        preferred_order = [
            VoiceEngine.EDGE_TTS,    # Más natural (Microsoft Edge TTS)
            VoiceEngine.GTTS,        # Alternativa basada en Google
            VoiceEngine.PYTTSX3,     # Local, puede no funcionar en servidor
        ]
        
        for engine in preferred_order:
            if engine in self.engines and self.engines[engine]['available']:
                self.config.engine = engine
                self.current_engine = engine
                logger.info(f"Motor seleccionado: {engine.value}")
                return
        
        logger.error("No hay motores de voz disponibles")
        self.config.enabled = False
    
    def generate_audio_base64(self, text: str) -> Optional[str]:
        """Generar audio en base64 para enviar al navegador"""
        if not self.config.enabled or not text.strip():
            return None
        
        try:
            if self.config.engine == VoiceEngine.GTTS:
                return self._generate_gtts_audio(text)
            elif self.config.engine == VoiceEngine.EDGE_TTS:
                return self._generate_edge_tts_audio(text)
            elif self.config.engine == VoiceEngine.PYTTSX3:
                return self._generate_pyttsx3_audio(text)
            else:
                logger.error(f"Motor no soportado: {self.config.engine}")
                return None
        except Exception as e:
            logger.error(f"Error generando audio: {e}")
            return None
    
    def _generate_gtts_audio(self, text: str) -> Optional[str]:
        """Generar audio con gTTS"""
        try:
            from gtts import gTTS
            import io
            
            # Crear archivo temporal en memoria
            audio_buffer = io.BytesIO()
            
            # Generar audio
            tts = gTTS(text=text, lang=self.config.language, slow=False)
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convertir a base64
            audio_data = audio_buffer.getvalue()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return audio_base64
        except Exception as e:
            logger.error(f"Error con gTTS: {e}")
            return None
    
    def _generate_edge_tts_audio(self, text: str) -> Optional[str]:
        """Generar audio con Edge-TTS"""
        try:
            import asyncio
            import edge_tts
            import io
            
            # Seleccionar voz
            voice = self._get_edge_voice()
            
            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data
            
            # Ejecutar en hilo separado
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(_generate())
            loop.close()
            
            # Convertir a base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            return audio_base64
        except Exception as e:
            logger.error(f"Error con Edge-TTS: {e}")
            return None
    
    def _generate_pyttsx3_audio(self, text: str) -> Optional[str]:
        """Generar audio con pyttsx3 (no recomendado para web)"""
        try:
            import pyttsx3
            import wave
            import io
            
            engine_data = self.engines[VoiceEngine.PYTTSX3]
            engine = engine_data['engine']
            
            # Configurar propiedades
            engine.setProperty('rate', self.config.rate)
            engine.setProperty('volume', self.config.volume)
            
            # pyttsx3 no puede generar archivos directamente
            # Solo puede reproducir, por lo que no es adecuado para web
            logger.warning("pyttsx3 no es adecuado para generar audio web")
            return None
        except Exception as e:
            logger.error(f"Error con pyttsx3: {e}")
            return None
    
    def _get_edge_voice(self) -> str:
        """Obtener voz Edge-TTS apropiada"""
        voices_map = {
            'es': 'es-ES-ElviraNeural',      # Español España
            'es-MX': 'es-MX-DaliaNeural',    # Español México
            'en': 'en-US-AriaNeural',        # Inglés US
            'en-GB': 'en-GB-SoniaNeural'     # Inglés UK
        }
        return voices_map.get(self.config.language, 'es-ES-ElviraNeural')
    
    def set_engine(self, engine: VoiceEngine) -> bool:
        """Cambiar motor de voz"""
        if engine in self.engines and self.engines[engine]['available']:
            self.config.engine = engine
            self.current_engine = engine
            self._save_config()
            logger.info(f"Motor cambiado a: {engine.value}")
            return True
        else:
            logger.error(f"Motor no disponible: {engine.value}")
            return False
    
    def set_language(self, language: str) -> bool:
        """Cambiar idioma"""
        self.config.language = language
        self._save_config()
        logger.info(f"Idioma cambiado a: {language}")
        return True
    
    def set_rate(self, rate: int) -> bool:
        """Cambiar velocidad de habla"""
        if 50 <= rate <= 500:
            self.config.rate = rate
            self._save_config()
            logger.info(f"Velocidad cambiada a: {rate}")
            return True
        return False
    
    def set_volume(self, volume: float) -> bool:
        """Cambiar volumen"""
        if 0.0 <= volume <= 1.0:
            self.config.volume = volume
            self._save_config()
            logger.info(f"Volumen cambiado a: {volume}")
            return True
        return False
    
    def enable(self, enabled: bool = True):
        """Habilitar/deshabilitar sistema de voz"""
        self.config.enabled = enabled
        self._save_config()
        status = "habilitado" if enabled else "deshabilitado"
        logger.info(f"Sistema de voz {status}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de voz"""
        return {
            'enabled': self.config.enabled,
            'current_engine': self.config.engine.value,
            'language': self.config.language,
            'rate': self.config.rate,
            'volume': self.config.volume,
            'voice_id': self.config.voice_id,
            'auto_speak': self.config.auto_speak,
            'available_engines': [engine.value for engine, data in self.engines.items() if data['available']]
        }

# Instancia global del sistema de voz web
web_voice_system = WebVoiceSystem()

def generate_voice_audio(text: str) -> Optional[str]:
    """Función de conveniencia para generar audio"""
    return web_voice_system.generate_audio_base64(text)

if __name__ == "__main__":
    # Prueba del sistema de voz web
    print("Probando Sistema de Voz Web SIBIA")
    print("=" * 40)
    
    # Mostrar estado
    status = web_voice_system.get_status()
    print(f"Motor actual: {status['current_engine']}")
    print(f"Idioma: {status['language']}")
    print(f"Motores disponibles: {', '.join(status['available_engines'])}")
    print()
    
    # Probar generación de audio
    test_text = "Hola, soy SIBIA, tu asistente inteligente de biodigestores."
    print(f"Generando audio para: {test_text}")
    
    audio_base64 = web_voice_system.generate_audio_base64(test_text)
    if audio_base64:
        print(f"Audio generado exitosamente. Tamaño: {len(audio_base64)} caracteres")
        print("El audio se puede reproducir en el navegador usando:")
        print("const audio = new Audio('data:audio/mpeg;base64,' + audioBase64);")
        print("audio.play();")
    else:
        print("Error generando audio")
    
    print("Pruebas completadas")
