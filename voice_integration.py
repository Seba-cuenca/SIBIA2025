#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración de Voz para Calculadora y Asistente SIBIA - Version Corregida
Módulo que integra el sistema de voz con la calculadora rápida y el asistente IA
"""

import logging
import json
from typing import Dict, Any, Optional
from web_voice_system import web_voice_system, generate_voice_audio, VoiceEngine

logger = logging.getLogger(__name__)

class VoiceIntegration:
    """Integración de voz para SIBIA"""
    
    def __init__(self):
        self.enabled = True
        self.calculator_voice = True
        self.assistant_voice = True
        self.load_config()
    
    def load_config(self):
        """Cargar configuración de integración de voz"""
        try:
            with open('voice_integration_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.enabled = config.get('enabled', True)
                self.calculator_voice = config.get('calculator_voice', True)
                self.assistant_voice = config.get('assistant_voice', True)
        except FileNotFoundError:
            # Crear configuración por defecto
            self.save_config()
        except Exception as e:
            logger.error(f"Error cargando configuracion de voz: {e}")
    
    def save_config(self):
        """Guardar configuración de integración de voz"""
        try:
            config = {
                'enabled': self.enabled,
                'calculator_voice': self.calculator_voice,
                'assistant_voice': self.assistant_voice
            }
            with open('voice_integration_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuracion de voz: {e}")
    
    def speak_calculator_result(self, result: Dict[str, Any]) -> bool:
        """Hablar resultado de la calculadora"""
        if not self.enabled or not self.calculator_voice:
            return False

        try:
            # Preferir Edge-TTS por naturalidad
            web_voice_system.set_engine(VoiceEngine.EDGE_TTS)

            # Construir mensaje detallado del resultado
            totales = result.get('totales', {})
            kw_total = totales.get('kw_total_generado', 0)
            metano = totales.get('metano_total', 0)
            tn_total = totales.get('tn_total', 0)
            tn_solidos = totales.get('tn_solidos', 0)
            tn_liquidos = totales.get('tn_liquidos', 0)
            tn_purin = totales.get('tn_purin', 0)

            message = f"Calculo completado exitosamente. "
            if kw_total > 0:
                message += f"Se generaran {kw_total:.0f} kilovatios. "
            if metano > 0:
                message += f"El contenido de metano sera del {metano:.1f} por ciento. "
            if tn_total > 0:
                message += f"Se utilizaran {tn_total:.1f} toneladas de material: "
                if tn_solidos > 0:
                    pct_solidos = (tn_solidos / tn_total) * 100
                    message += f"{pct_solidos:.1f} por ciento solidos, "
                if tn_liquidos > 0:
                    pct_liquidos = (tn_liquidos / tn_total) * 100
                    message += f"{pct_liquidos:.1f} por ciento liquidos, "
                if tn_purin > 0:
                    pct_purin = (tn_purin / tn_total) * 100
                    message += f"{pct_purin:.1f} por ciento purin. "
            advertencias = result.get('advertencias', [])
            if advertencias:
                message += "Advertencias: " + ". ".join(advertencias[:2]) + ". "

            logger.info(f"Generando audio para resultado de calculadora")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando resultado de calculadora: {e}")
            return False
    
    def speak_calculator_error(self, error_message: str) -> bool:
        """Hablar error de la calculadora"""
        if not self.enabled or not self.calculator_voice:
            return False
        
        try:
            message = f"Error en el calculo: {error_message}"
            logger.info(f"Generando audio de error de calculadora")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando error de calculadora: {e}")
            return False
    
    def speak_assistant_response(self, response: str, response_type: str = "normal") -> bool:
        """Hablar respuesta del asistente"""
        if not self.enabled or not self.assistant_voice:
            return False
        
        try:
            # Prefijo según tipo de respuesta
            if response_type == "error":
                prefix = "Error: "
            elif response_type == "warning":
                prefix = "Advertencia: "
            elif response_type == "success":
                prefix = "Exito: "
            else:
                prefix = ""
            
            message = f"{prefix}{response}"
            
            # Limitar longitud del mensaje para evitar mensajes muy largos
            if len(message) > 500:
                message = message[:500] + "..."
            
            logger.info(f"Generando audio para respuesta del asistente")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
            
        except Exception as e:
            logger.error(f"Error hablando respuesta del asistente: {e}")
            return False
    
    def speak_system_notification(self, notification: str) -> bool:
        """Hablar notificación del sistema"""
        if not self.enabled:
            return False
        
        try:
            message = f"Notificacion: {notification}"
            logger.info(f"Generando audio de notificacion")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando notificacion: {e}")
            return False
    
    def speak_calculation_progress(self, step: str, progress: int = 0) -> bool:
        """Hablar progreso del cálculo"""
        if not self.enabled or not self.calculator_voice:
            return False
        
        try:
            if progress > 0:
                message = f"Progreso del calculo: {progress} por ciento. {step}"
            else:
                message = f"Calculando: {step}"
            
            logger.info(f"Generando audio de progreso")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando progreso: {e}")
            return False
    
    def speak_material_recommendation(self, recommendation: str) -> bool:
        """Hablar recomendación de materiales"""
        if not self.enabled or not self.assistant_voice:
            return False
        
        try:
            message = f"Recomendacion: {recommendation}"
            logger.info(f"Generando audio de recomendacion")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando recomendacion: {e}")
            return False
    
    def speak_welcome_message(self) -> bool:
        """Hablar mensaje de bienvenida"""
        if not self.enabled:
            return False
        
        try:
            message = "Bienvenido a SIBIA, tu asistente inteligente de biodigestores. Estoy listo para ayudarte con calculos y consultas."
            logger.info("Generando audio de bienvenida")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando mensaje de bienvenida: {e}")
            return False
    
    def speak_goodbye_message(self) -> bool:
        """Hablar mensaje de despedida"""
        if not self.enabled:
            return False
        
        try:
            message = "Gracias por usar SIBIA. Hasta la proxima!"
            logger.info("Generando audio de despedida")
            audio_b64 = generate_voice_audio(message)
            return bool(audio_b64)
        except Exception as e:
            logger.error(f"Error hablando mensaje de despedida: {e}")
            return False
    
    def enable_calculator_voice(self, enabled: bool = True):
        """Habilitar/deshabilitar voz para calculadora"""
        self.calculator_voice = enabled
        self.save_config()
        logger.info(f"Voz de calculadora {'habilitada' if enabled else 'deshabilitada'}")
    
    def enable_assistant_voice(self, enabled: bool = True):
        """Habilitar/deshabilitar voz para asistente"""
        self.assistant_voice = enabled
        self.save_config()
        logger.info(f"Voz de asistente {'habilitada' if enabled else 'deshabilitada'}")
    
    def enable_all_voice(self, enabled: bool = True):
        """Habilitar/deshabilitar todo el sistema de voz"""
        self.enabled = enabled
        self.save_config()
        logger.info(f"Sistema de voz {'habilitado' if enabled else 'deshabilitado'}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado de la integración de voz"""
        status = {
            'enabled': self.enabled,
            'calculator_voice': self.calculator_voice,
            'assistant_voice': self.assistant_voice,
            'voice_system_status': web_voice_system.get_status()
        }
        return status

# Instancia global de integración de voz
voice_integration = VoiceIntegration()

# Funciones de conveniencia
def speak_calculator_result(result: Dict[str, Any]) -> bool:
    """Hablar resultado de calculadora"""
    return voice_integration.speak_calculator_result(result)

def speak_calculator_error(error_message: str) -> bool:
    """Hablar error de calculadora"""
    return voice_integration.speak_calculator_error(error_message)

def speak_assistant_response(response: str, response_type: str = "normal") -> bool:
    """Hablar respuesta del asistente"""
    return voice_integration.speak_assistant_response(response, response_type)

def speak_system_notification(notification: str) -> bool:
    """Hablar notificación del sistema"""
    return voice_integration.speak_system_notification(notification)

def speak_calculation_progress(step: str, progress: int = 0) -> bool:
    """Hablar progreso del cálculo"""
    return voice_integration.speak_calculation_progress(step, progress)

def speak_material_recommendation(recommendation: str) -> bool:
    """Hablar recomendación de materiales"""
    return voice_integration.speak_material_recommendation(recommendation)

def speak_welcome_message() -> bool:
    """Hablar mensaje de bienvenida"""
    return voice_integration.speak_welcome_message()

def speak_goodbye_message() -> bool:
    """Hablar mensaje de despedida"""
    return voice_integration.speak_goodbye_message()

if __name__ == "__main__":
    # Prueba de integración de voz
    print("Probando Integracion de Voz SIBIA")
    print("=" * 40)
    
    # Mostrar estado
    status = voice_integration.get_status()
    print(f"Sistema habilitado: {status['enabled']}")
    print(f"Voz calculadora: {status['calculator_voice']}")
    print(f"Voz asistente: {status['assistant_voice']}")
    print()
    
    # Probar diferentes funciones
    print("Probando mensaje de bienvenida...")
    voice_integration.speak_welcome_message()
    
    print("Probando resultado de calculadora...")
    resultado_prueba = {
        'totales': {
            'kw_total_generado': 28800,
            'metano_total': 65.5,
            'tn_total': 1000.0,
            'tn_solidos': 400.0,
            'tn_liquidos': 400.0,
            'tn_purin': 200.0
        },
        'advertencias': ['Stock bajo en algunos materiales']
    }
    voice_integration.speak_calculator_result(resultado_prueba)
    
    print("Probando respuesta del asistente...")
    voice_integration.speak_assistant_response("El calculo se completo exitosamente. Se recomienda verificar el stock de materiales.", "success")
    
    print("Probando progreso...")
    voice_integration.speak_calculation_progress("Procesando materiales solidos", 50)
    
    print("Probando recomendacion...")
    voice_integration.speak_material_recommendation("Se recomienda aumentar el porcentaje de solidos para mejorar la eficiencia.")
    
    print("Probando mensaje de despedida...")
    voice_integration.speak_goodbye_message()
    
    print("Pruebas de integracion completadas")
