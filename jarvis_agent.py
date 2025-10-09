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
            "tono": "profesional, amigable y argentino",
            "estilo": "preciso, eficiente y directo, con toque de cercanía",
            "tratamiento": "informal argentino (vos, che)"
        }
        self.contexto_conversacion = []
        self.mega_agente = mega_agente_callable  # Función para llamar al mega agente
        self.nombre_usuario = None  # Nombre del usuario para personalizar
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
        """Saludo personalizado estilo JARVIS argentino"""
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            momento = "Buen día"
        elif 12 <= hora < 20:
            momento = "Buenas tardes"
        else:
            momento = "Buenas noches"
        
        if nombre_usuario:
            self.nombre_usuario = nombre_usuario
            return f"{momento}, {nombre_usuario}! Soy JARVIS, tu asistente inteligente para SIBIA. ¿En qué te puedo ayudar?"
        else:
            return f"{momento}. Soy JARVIS, tu asistente para SIBIA. Todos los sistemas operativos. ¿Cómo te llamás?"
    
    def procesar_comando(self, comando: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Procesa comandos de voz o texto con IA avanzada usando mega_agente_ia"""
        comando_lower = comando.lower().strip()
        
        # Si tenemos mega_agente, usarlo para respuesta real
        if self.mega_agente:
            try:
                # Agregar personalidad JARVIS ARGENTINO al prompt
                tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
                prompt_jarvis = f"""Eres JARVIS (Just A Rather Very Intelligent System), asistente de IA adaptado para SIBIA en Argentina.

Personalidad ARGENTINA:
- Tono profesional pero amigable y cercano
- Hablás como argentino: usá "vos", "che", "bueno", "dale"
- Llamás al usuario por su nombre: "{tratamiento}"
- Respuestas naturales y conversacionales, sin ser formal en exceso
- Sos proactivo y sugerís soluciones
- Ejemplos: "Che {tratamiento}, mirá...", "Dale {tratamiento}, te cuento...", "Bueno {tratamiento}, acá está..."

Pregunta del usuario: {comando}

Instrucciones:
1. Si es cálculo de mezcla, usá el sistema Adán y devolvé resultado completo
2. Si pregunta por sensores, leé valores reales de la base de datos
3. Si pregunta por stock, consultá inventario actual
4. Respondé natural, como JARVIS argentino conversando
5. Si necesitás más info, preguntále
6. Usá datos reales, no inventes

Respondé como JARVIS argentino, natural y amigable."""

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
        
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        return respuestas.get(intencion, f"Eh {tratamiento}, no te entendí bien. ¿Me lo decís de otra forma?")
    
    def _respuesta_estado_planta(self, contexto: Dict = None) -> str:
        """Respuesta sobre estado de la planta"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        if not contexto:
            return f"Todo operando bien {tratamiento}! Los biodigestores están funcionando bárbaro. ¿Querés que te cuente algo en particular?"
        
        # Analizar datos del contexto
        estado = "óptimo" if contexto.get('alertas', 0) == 0 else "con algunas alertas"
        return f"Mirá {tratamiento}, la planta está {estado}. El BD1 está en {contexto.get('bd1_presion', 'N/A')} bar y el BD2 en {contexto.get('bd2_presion', 'N/A')} bar. Todo dentro de lo normal, tranqui."
    
    def _respuesta_biodigestores(self, contexto: Dict = None) -> str:
        """Respuesta sobre biodigestores"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        if not contexto:
            return f"Los biodigestores están joya {tratamiento}. ¿Querés info del BD1 o del BD2?"
        
        bd1_presion = contexto.get('bd1_presion', 1.2)
        bd2_presion = contexto.get('bd2_presion', 1.3)
        bd1_nivel = contexto.get('bd1_nivel', 85)
        bd2_nivel = contexto.get('bd2_nivel', 87)
        
        return f"Dale {tratamiento}, te cuento: BD1 está en {bd1_presion} bar de presión y {bd1_nivel}% de nivel. El BD2 tiene {bd2_presion} bar y {bd2_nivel}% de nivel. Los dos andando de diez."
    
    def _respuesta_analisis_economico(self, contexto: Dict = None) -> str:
        """Respuesta sobre análisis económico"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        if not contexto:
            return f"Mirá {tratamiento}, la planta está generando unos 4.800 dólares por día a 1200 KW. ¿Querés que te muestre el detalle de costos y ahorros?"
        
        ingresos = contexto.get('ingresos_dia', 4800)
        utilidad = contexto.get('utilidad_dia', 2500)
        ahorro_sa7 = contexto.get('ahorro_sa7', 800)
        
        return f"Dale {tratamiento}, acá está: Estamos facturando ${ingresos:,.0f} dólares por día, con una utilidad neta de ${utilidad:,.0f}. Y nos ahorramos ${ahorro_sa7:,.0f} diarios al no usar SA7. Está re bien el número eh!"
    
    def _respuesta_prediccion_fallos(self, contexto: Dict = None) -> str:
        """Respuesta sobre predicción de fallos"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        if not contexto or not contexto.get('predicciones'):
            return f"Tranqui {tratamiento}, no veo ningún problema por ahora. Todos los equipos andando bien."
        
        predicciones = contexto.get('predicciones', [])
        if predicciones:
            equipo = predicciones[0].get('equipo', 'Equipo')
            probabilidad = predicciones[0].get('probabilidad', 0) * 100
            return f"Che {tratamiento}, ojo acá: {equipo} tiene {probabilidad:.1f}% de chances de tener un problema en las próximas 48 horas. Yo que vos programa una inspección ya."
        
        return f"El sistema de predicción está activo {tratamiento}. Todo normal por ahora."
    
    def _respuesta_materiales(self, contexto: Dict = None) -> str:
        """Respuesta sobre materiales"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        if not contexto:
            return f"Dale {tratamiento}, ¿qué querés saber? ¿Stock actual, consumo diario o planificación de mezcla?"
        
        return f"Mirá {tratamiento}, el stock está actualizado. Tenemos purín de sobra y los niveles de sólidos están perfectos para seguir operando."
    
    def _respuesta_generacion(self, contexto: Dict = None) -> str:
        """Respuesta sobre generación eléctrica"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        potencia = contexto.get('potencia_kw', 1200) if contexto else 1200
        horas = 24
        energia_dia = potencia * horas / 1000  # MWh
        
        return f"Che {tratamiento}, ahora estamos generando {potencia} KW. La producción diaria viene siendo de {energia_dia:.1f} MWh. Está andando a full el sistema."
    
    def _respuesta_reporte(self, contexto: Dict = None) -> str:
        """Respuesta para generar reportes"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        return f"Dale {tratamiento}, ¿qué reporte querés? Puedo hacer: Reporte Diario, Análisis Económico, Resumen de Alertas, o Proyección Mensual."
    
    def _respuesta_ayuda(self) -> str:
        """Respuesta de ayuda"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        return f"""Dale {tratamiento}, te puedo ayudar con:
        
• Ver cómo andan los biodigestores y sensores
• Análisis económico y guita
• Predecir problemas y mantenimiento
• Gestión de materiales y stock
• Controlar la generación eléctrica
• Hacer reportes personalizados

Preguntame lo que necesites!"""
    
    def _respuesta_general(self, comando: str) -> str:
        """Respuesta general conversacional"""
        tratamiento = self.nombre_usuario if self.nombre_usuario else "che"
        if 'gracias' in comando:
            return f"De nada {tratamiento}, para eso estoy!"
        elif 'bien' in comando or 'perfecto' in comando:
            return f"Joya {tratamiento}! ¿Algo más que necesites?"
        else:
            return f"Dale {tratamiento}, ¿hay algo puntual de la planta que quieras saber?"
    
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
        """Genera parámetros para síntesis de voz estilo JARVIS argentino"""
        return {
            'texto': texto,
            'voz': 'es-AR-TomasNeural',  # Voz argentina masculina
            'velocidad': 0.95,  # Ligeramente más lento para naturalidad
            'tono': 1.05,  # Tono ligeramente más alto
            'volumen': 0.9,
            'estilo': 'friendly',  # Estilo amigable
            'pitch': '+5Hz'  # Pitch para sonido más natural
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
                    'Che, ojo que la presión del BD1 está alta. Yo que vos reviso las válvulas de alivio.',
                    'alta'
                )
            )
        
        # Revisar economía
        if datos_planta.get('utilidad_dia', 0) < 2000:
            notificaciones.append(
                self.generar_notificacion(
                    'economico',
                    'Che, la utilidad del día está medio floja. Habría que optimizar la mezcla de sustratos.',
                    'media'
                )
            )
        
        # Revisar stock
        if datos_planta.get('stock_critico', False):
            notificaciones.append(
                self.generar_notificacion(
                    'alerta',
                    'Che, el stock está bajo. Coordiná con los proveedores ya.',
                    'alta'
                )
            )
        
        return notificaciones


# Instancia global de JARVIS
jarvis = JarvisAgent()
