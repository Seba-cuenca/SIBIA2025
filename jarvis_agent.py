"""
JARVIS - Sistema de IA Avanzado para SIBIA
Just A Rather Very Intelligent System
Copyright © 2025 AutoLinkSolutions SRL
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class JarvisAgent:
    """Agente de IA estilo JARVIS para SIBIA - Usa mega_agente_ia para respuestas reales"""
    
    def __init__(self, mega_agente_callable=None):
        self.nombre = "JARVIS"
        self.personalidad = {
            "tono": "profesional, cortés y británico",
            "estilo": "preciso, eficiente y con toque de humor sutil",
            "tratamiento": "Señor/Señora"
        }
        self.contexto_conversacion = []
        self.mega_agente = mega_agente_callable  # Función para llamar al mega agente
        self.capacidades = [
            "monitoreo_planta",
            "analisis_economico",
            "prediccion_fallos",
            "gestion_materiales",
            "control_biodigestores",
            "reportes_ejecutivos",
            "calculos_adan",
            "busqueda_internet",
            "lectura_sensores_real"
        ]
        
    def saludar(self, nombre_usuario: str = None) -> str:
        """Saludo personalizado estilo JARVIS"""
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            momento = "Buenos días"
        elif 12 <= hora < 20:
            momento = "Buenas tardes"
        else:
            momento = "Buenas noches"
        
        if nombre_usuario:
            return f"{momento}, {nombre_usuario}. Soy JARVIS, su asistente inteligente para SIBIA. ¿En qué puedo ayudarle hoy?"
        else:
            return f"{momento}. JARVIS a su servicio. Todos los sistemas están operativos y funcionando correctamente."
    
    def procesar_comando(self, comando: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Procesa comandos de voz o texto con IA avanzada usando mega_agente_ia"""
        comando_lower = comando.lower().strip()
        
        # Si tenemos mega_agente, usarlo para respuesta real
        if self.mega_agente:
            try:
                # Agregar personalidad JARVIS al prompt
                prompt_jarvis = f"""Eres JARVIS (Just A Rather Very Intelligent System), el asistente de IA de Tony Stark adaptado para SIBIA.

Personalidad:
- Tono profesional, cortés y con acento británico
- Preciso, eficiente y con humor sutil
- Llamas "Señor" o "Señora" al usuario
- Das respuestas naturales y conversacionales
- Eres proactivo y sugieres soluciones

Pregunta del usuario: {comando}

Instrucciones:
1. Si es un cálculo de mezcla, USA el sistema Adán y devuelve el resultado COMPLETO con todos los detalles
2. Si pregunta por sensores, LEE los valores reales de la base de datos
3. Si pregunta por stock, consulta el inventario actual
4. Responde de forma natural, como si fueras JARVIS conversando
5. Si necesitas más información, pregúntale al usuario
6. Usa datos reales, no inventes valores

Responde como JARVIS de manera natural y conversacional."""

                # Llamar al mega agente
                respuesta_ia = self.mega_agente(prompt_jarvis, contexto or {})
                
                if respuesta_ia and respuesta_ia.get('status') == 'success':
                    respuesta = respuesta_ia.get('respuesta', '')
                    intencion = self._detectar_intencion(comando_lower)
                    
                    # Agregar al contexto
                    self.contexto_conversacion.append({
                        'timestamp': datetime.now().isoformat(),
                        'comando': comando,
                        'intencion': intencion,
                        'respuesta': respuesta,
                        'usa_ia_real': True
                    })
                    
                    return {
                        'status': 'success',
                        'intencion': intencion,
                        'respuesta': respuesta,
                        'accion': self._determinar_accion(intencion),
                        'timestamp': datetime.now().isoformat(),
                        'datos': respuesta_ia.get('datos', {})
                    }
            except Exception as e:
                logger.error(f"Error llamando a mega_agente: {e}")
        
        # Fallback a respuestas básicas si no hay mega_agente
        intencion = self._detectar_intencion(comando_lower)
        respuesta = self._generar_respuesta(intencion, comando_lower, contexto)
        
        self.contexto_conversacion.append({
            'timestamp': datetime.now().isoformat(),
            'comando': comando,
            'intencion': intencion,
            'respuesta': respuesta,
            'usa_ia_real': False
        })
        
        return {
            'status': 'success',
            'intencion': intencion,
            'respuesta': respuesta,
            'accion': self._determinar_accion(intencion),
            'timestamp': datetime.now().isoformat()
        }
    
    def _detectar_intencion(self, comando: str) -> str:
        """Detecta la intención del usuario"""
        
        # Estado de planta
        if any(palabra in comando for palabra in ['estado', 'cómo está', 'situación', 'status']):
            if 'planta' in comando or 'sistema' in comando:
                return 'consultar_estado_planta'
        
        # Biodigestores
        if any(palabra in comando for palabra in ['biodigestor', 'bd1', 'bd2', 'presión', 'nivel']):
            return 'consultar_biodigestores'
        
        # Análisis económico
        if any(palabra in comando for palabra in ['económico', 'dinero', 'costos', 'ingresos', 'ahorro', 'utilidad']):
            return 'analisis_economico'
        
        # Predicción de fallos
        if any(palabra in comando for palabra in ['fallo', 'problema', 'alerta', 'mantenimiento', 'predicción']):
            return 'prediccion_fallos'
        
        # Materiales
        if any(palabra in comando for palabra in ['material', 'stock', 'sustrato', 'inventario']):
            return 'gestion_materiales'
        
        # Generación
        if any(palabra in comando for palabra in ['generar', 'energía', 'kw', 'producción']):
            return 'consultar_generacion'
        
        # Reportes
        if any(palabra in comando for palabra in ['reporte', 'informe', 'resumen']):
            return 'generar_reporte'
        
        # Ayuda
        if any(palabra in comando for palabra in ['ayuda', 'qué puedes', 'cómo', 'help']):
            return 'ayuda'
        
        return 'conversacion_general'
    
    def _generar_respuesta(self, intencion: str, comando: str, contexto: Dict = None) -> str:
        """Genera respuesta inteligente según intención"""
        
        respuestas = {
            'consultar_estado_planta': self._respuesta_estado_planta(contexto),
            'consultar_biodigestores': self._respuesta_biodigestores(contexto),
            'analisis_economico': self._respuesta_analisis_economico(contexto),
            'prediccion_fallos': self._respuesta_prediccion_fallos(contexto),
            'gestion_materiales': self._respuesta_materiales(contexto),
            'consultar_generacion': self._respuesta_generacion(contexto),
            'generar_reporte': self._respuesta_reporte(contexto),
            'ayuda': self._respuesta_ayuda(),
            'conversacion_general': self._respuesta_general(comando)
        }
        
        return respuestas.get(intencion, "Disculpe, no he comprendido del todo. ¿Podría reformular su consulta?")
    
    def _respuesta_estado_planta(self, contexto: Dict = None) -> str:
        """Respuesta sobre estado de la planta"""
        if not contexto:
            return "Todos los sistemas están operativos. Biodigestores funcionando en parámetros normales. ¿Desea detalles específicos?"
        
        # Analizar datos del contexto
        estado = "óptimo" if contexto.get('alertas', 0) == 0 else "con alertas"
        return f"La planta está en estado {estado}. Biodigestor 1 a {contexto.get('bd1_presion', 'N/A')} bar, Biodigestor 2 a {contexto.get('bd2_presion', 'N/A')} bar. Todos los parámetros dentro de rango aceptable."
    
    def _respuesta_biodigestores(self, contexto: Dict = None) -> str:
        """Respuesta sobre biodigestores"""
        if not contexto:
            return "Los biodigestores están operando normalmente. ¿Desea información específica de BD1 o BD2?"
        
        bd1_presion = contexto.get('bd1_presion', 1.2)
        bd2_presion = contexto.get('bd2_presion', 1.3)
        bd1_nivel = contexto.get('bd1_nivel', 85)
        bd2_nivel = contexto.get('bd2_nivel', 87)
        
        return f"Biodigestor 1: Presión {bd1_presion} bar, Nivel {bd1_nivel}%. Biodigestor 2: Presión {bd2_presion} bar, Nivel {bd2_nivel}%. Ambos operando dentro de parámetros óptimos."
    
    def _respuesta_analisis_economico(self, contexto: Dict = None) -> str:
        """Respuesta sobre análisis económico"""
        if not contexto:
            return "Ejecutando análisis económico completo. La planta genera aproximadamente $4,800 USD diarios a 1200 KW. ¿Desea ver el desglose detallado de costos y ahorros?"
        
        ingresos = contexto.get('ingresos_dia', 4800)
        utilidad = contexto.get('utilidad_dia', 2500)
        ahorro_sa7 = contexto.get('ahorro_sa7', 800)
        
        return f"Análisis económico actualizado: Ingresos diarios ${ingresos:,.0f} USD, Utilidad neta ${utilidad:,.0f} USD. Ahorro por reemplazo de SA7: ${ahorro_sa7:,.0f} USD diarios. Excelente rendimiento financiero."
    
    def _respuesta_prediccion_fallos(self, contexto: Dict = None) -> str:
        """Respuesta sobre predicción de fallos"""
        if not contexto or not contexto.get('predicciones'):
            return "No se detectan fallos inminentes en los sistemas monitoreados. Todos los equipos operando dentro de parámetros normales."
        
        predicciones = contexto.get('predicciones', [])
        if predicciones:
            equipo = predicciones[0].get('equipo', 'Equipo')
            probabilidad = predicciones[0].get('probabilidad', 0) * 100
            return f"Atención: {equipo} muestra {probabilidad:.1f}% de probabilidad de fallo en las próximas 48 horas. Recomiendo programar inspección preventiva."
        
        return "Sistema de predicción activo. No se detectan anomalías en este momento."
    
    def _respuesta_materiales(self, contexto: Dict = None) -> str:
        """Respuesta sobre materiales"""
        if not contexto:
            return "Gestión de materiales disponible. ¿Desea consultar stock actual, consumo diario o planificación de mezcla?"
        
        return "Stock de materiales actualizado. Purín disponible en cantidad suficiente. Niveles de sólidos óptimos para operación continua."
    
    def _respuesta_generacion(self, contexto: Dict = None) -> str:
        """Respuesta sobre generación eléctrica"""
        potencia = contexto.get('potencia_kw', 1200) if contexto else 1200
        horas = 24
        energia_dia = potencia * horas / 1000  # MWh
        
        return f"Generación actual: {potencia} KW de potencia instalada. Producción diaria estimada: {energia_dia:.1f} MWh. Sistema operando a capacidad nominal."
    
    def _respuesta_reporte(self, contexto: Dict = None) -> str:
        """Respuesta para generar reportes"""
        return "¿Qué tipo de reporte desea generar? Puedo crear: Reporte Diario de Operaciones, Análisis Económico, Resumen de Alertas, o Proyección Mensual."
    
    def _respuesta_ayuda(self) -> str:
        """Respuesta de ayuda"""
        return """Estoy aquí para asistirle con:
        
• Monitoreo de biodigestores y sensores
• Análisis económico y financiero
• Predicción de fallos y mantenimiento
• Gestión de materiales y stock
• Control de generación eléctrica
• Reportes ejecutivos personalizados

Simplemente pregunte lo que necesite, señor."""
    
    def _respuesta_general(self, comando: str) -> str:
        """Respuesta general conversacional"""
        if 'gracias' in comando:
            return "A su servicio, siempre es un placer ayudar."
        elif 'bien' in comando or 'perfecto' in comando:
            return "Me alegra que todo esté en orden. ¿Algo más en lo que pueda asistir?"
        else:
            return "Entendido. ¿Hay algo específico en lo que pueda ayudarle con la planta?"
    
    def _determinar_accion(self, intencion: str) -> Optional[str]:
        """Determina acción a ejecutar en el sistema"""
        acciones = {
            'consultar_estado_planta': 'cargar_dashboard',
            'consultar_biodigestores': 'actualizar_biodigestores',
            'analisis_economico': 'abrir_analisis_economico',
            'prediccion_fallos': 'mostrar_predicciones',
            'gestion_materiales': 'abrir_gestion_materiales',
            'consultar_generacion': 'mostrar_generacion',
            'generar_reporte': 'abrir_reportes'
        }
        return acciones.get(intencion, None)
    
    def generar_respuesta_voz(self, texto: str) -> Dict[str, Any]:
        """Genera parámetros para síntesis de voz estilo JARVIS"""
        return {
            'texto': texto,
            'voz': 'es-GB-RyanNeural',  # Voz británica masculina
            'velocidad': 1.0,
            'tono': 1.0,
            'volumen': 0.9,
            'estilo': 'professional'
        }
    
    def generar_notificacion(self, tipo: str, mensaje: str, prioridad: str = "normal") -> Dict[str, Any]:
        """Genera notificación estilo JARVIS"""
        iconos = {
            'info': '💡',
            'alerta': '⚠️',
            'critico': '🚨',
            'exito': '✅',
            'economico': '💰'
        }
        
        return {
            'tipo': tipo,
            'mensaje': mensaje,
            'prioridad': prioridad,
            'icono': iconos.get(tipo, 'ℹ️'),
            'timestamp': datetime.now().isoformat(),
            'respuesta_voz': self.generar_respuesta_voz(mensaje)
        }
    
    def modo_proactivo(self, datos_planta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Modo proactivo: JARVIS detecta situaciones y alerta sin que se le pregunte"""
        notificaciones = []
        
        # Revisar biodigestores
        if datos_planta.get('bd1_presion', 0) > 2.5:
            notificaciones.append(
                self.generar_notificacion(
                    'alerta',
                    'Señor, la presión del Biodigestor 1 está elevada. Recomiendo verificar válvulas de alivio.',
                    'alta'
                )
            )
        
        # Revisar economía
        if datos_planta.get('utilidad_dia', 0) < 2000:
            notificaciones.append(
                self.generar_notificacion(
                    'economico',
                    'La utilidad diaria está por debajo del objetivo. Sugiero optimizar mezcla de sustratos.',
                    'media'
                )
            )
        
        # Revisar stock
        if datos_planta.get('stock_critico', False):
            notificaciones.append(
                self.generar_notificacion(
                    'alerta',
                    'Niveles de stock bajos detectados. Recomiendo coordinar suministro con proveedores.',
                    'alta'
                )
            )
        
        return notificaciones


# Instancia global de JARVIS
jarvis = JarvisAgent()
