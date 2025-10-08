// JARVIS - Sistema de IA Avanzado estilo Iron Man
// Copyright © 2025 AutoLinkSolutions SRL

class JarvisUI {
    constructor() {
        this.reconocimientoActivo = false;
        this.recognition = null;
        this.orbe = null;
        this.chatbox = null;
        this.inputUsuario = null;
        this.btnEnviar = null;
        this.btnVoz = null;
        this.inicializado = false;
    }

    inicializar() {
        if (this.inicializado) return;
        
        console.log('🤖 Inicializando JARVIS...');
        
        // Obtener elementos
        this.orbe = document.getElementById('ai-orb');
        this.chatbox = document.getElementById('asistente-chatbox');
        this.inputUsuario = document.getElementById('input-usuario-asistente');
        this.btnEnviar = document.getElementById('btn-enviar-asistente');
        this.btnVoz = document.getElementById('btn-voz-asistente');
        
        // Configurar eventos
        if (this.btnEnviar) {
            this.btnEnviar.addEventListener('click', () => this.enviarMensaje());
        }
        
        if (this.inputUsuario) {
            this.inputUsuario.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.enviarMensaje();
            });
        }
        
        if (this.btnVoz) {
            this.btnVoz.addEventListener('click', () => this.toggleReconocimientoVoz());
        }
        
        // Inicializar reconocimiento de voz
        this.inicializarReconocimientoVoz();
        
        // Saludo inicial
        this.saludarUsuario();
        
        // Modo proactivo cada 30 segundos
        setInterval(() => this.verificarNotificacionesProactivas(), 30000);
        
        this.inicializado = true;
        console.log('✅ JARVIS inicializado correctamente');
    }

    inicializarReconocimientoVoz() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'es-ES';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;

            this.recognition.onresult = (event) => {
                const texto = event.results[0][0].transcript;
                if (this.inputUsuario) {
                    this.inputUsuario.value = texto;
                }
                this.enviarMensaje();
            };

            this.recognition.onerror = (event) => {
                console.error('Error en reconocimiento:', event.error);
                this.detenerReconocimiento();
            };

            this.recognition.onend = () => {
                this.detenerReconocimiento();
            };
        } else {
            console.warn('Reconocimiento de voz no disponible');
            if (this.btnVoz) {
                this.btnVoz.style.display = 'none';
            }
        }
    }

    toggleReconocimientoVoz() {
        if (this.reconocimientoActivo) {
            this.detenerReconocimiento();
        } else {
            this.iniciarReconocimiento();
        }
    }

    iniciarReconocimiento() {
        if (!this.recognition) return;
        
        try {
            this.recognition.start();
            this.reconocimientoActivo = true;
            this.activarOrbeEscuchando();
            
            if (this.btnVoz) {
                this.btnVoz.classList.add('recording');
                this.btnVoz.innerHTML = '<i class="fas fa-stop"></i>';
            }
        } catch (e) {
            console.error('Error iniciando reconocimiento:', e);
        }
    }

    detenerReconocimiento() {
        if (!this.recognition) return;
        
        try {
            this.recognition.stop();
            this.reconocimientoActivo = false;
            this.desactivarOrbeEscuchando();
            
            if (this.btnVoz) {
                this.btnVoz.classList.remove('recording');
                this.btnVoz.innerHTML = '<i class="fas fa-microphone"></i>';
            }
        } catch (e) {
            console.error('Error deteniendo reconocimiento:', e);
        }
    }

    async saludarUsuario() {
        try {
            const response = await fetch('/api/jarvis/saludo');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.mostrarMensajeAsistente(data.mensaje);
                this.hablar(data.mensaje);
            }
        } catch (error) {
            console.error('Error en saludo:', error);
            this.mostrarMensajeAsistente('Buenas tardes. JARVIS a su servicio.');
        }
    }

    async enviarMensaje() {
        const mensaje = this.inputUsuario ? this.inputUsuario.value.trim() : '';
        
        if (!mensaje) return;
        
        // Limpiar input
        if (this.inputUsuario) {
            this.inputUsuario.value = '';
        }
        
        // Mostrar mensaje del usuario
        this.mostrarMensajeUsuario(mensaje);
        
        // Activar orbe pensando
        this.activarOrbePensando();
        
        try {
            const response = await fetch('/api/jarvis/comando', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    comando: mensaje
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.desactivarOrbePensando();
                this.mostrarMensajeAsistente(data.respuesta);
                this.hablar(data.respuesta);
                
                // Ejecutar acción si hay alguna
                if (data.accion) {
                    this.ejecutarAccion(data.accion);
                }
            } else {
                throw new Error(data.mensaje || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error comunicando con JARVIS:', error);
            this.desactivarOrbePensando();
            this.mostrarMensajeAsistente('Disculpe, he tenido un problema procesando su solicitud.');
        }
    }

    async verificarNotificacionesProactivas() {
        try {
            const response = await fetch('/api/jarvis/proactivo');
            const data = await response.json();
            
            if (data.status === 'success' && data.notificaciones && data.notificaciones.length > 0) {
                data.notificaciones.forEach(notif => {
                    this.mostrarNotificacion(notif);
                    
                    // Solo hablar la primera notificación para no saturar
                    if (data.notificaciones.indexOf(notif) === 0) {
                        this.hablar(notif.mensaje);
                    }
                });
            }
        } catch (error) {
            console.error('Error en modo proactivo:', error);
        }
    }

    mostrarMensajeUsuario(texto) {
        if (!this.chatbox) return;
        
        const div = document.createElement('div');
        div.className = 'mensaje-usuario mb-3';
        div.innerHTML = `
            <div class="d-flex justify-content-end">
                <div class="bg-primary text-white p-2 rounded" style="max-width: 70%;">
                    <p class="mb-0">${this.escapeHtml(texto)}</p>
                </div>
            </div>
        `;
        
        this.chatbox.appendChild(div);
        this.chatbox.scrollTop = this.chatbox.scrollHeight;
        this.chatbox.classList.add('has-messages');
        this.ocultarOrbe();
    }

    mostrarMensajeAsistente(texto) {
        if (!this.chatbox) return;
        
        const div = document.createElement('div');
        div.className = 'mensaje-asistente mb-3';
        div.innerHTML = `
            <div class="d-flex justify-content-start">
                <div class="bg-secondary text-white p-2 rounded" style="max-width: 70%;">
                    <p class="mb-0">${this.escapeHtml(texto)}</p>
                </div>
            </div>
        `;
        
        this.chatbox.appendChild(div);
        this.chatbox.scrollTop = this.chatbox.scrollHeight;
    }

    mostrarNotificacion(notif) {
        const icono = notif.icono || '💡';
        const prioridad = notif.prioridad || 'normal';
        let colorClase = 'bg-info';
        
        if (prioridad === 'alta') colorClase = 'bg-warning';
        if (prioridad === 'critica') colorClase = 'bg-danger';
        
        // Mostrar en chatbox
        this.mostrarMensajeAsistente(`${icono} ${notif.mensaje}`);
        
        // Mostrar toast si existe
        if (typeof mostrarToast === 'function') {
            mostrarToast(notif.mensaje, prioridad === 'alta' ? 'warning' : 'info');
        }
    }

    hablar(texto) {
        // Usar Web Speech API si está disponible
        if ('speechSynthesis' in window) {
            this.activarOrbeHablando();
            
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = 'es-ES';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            
            utterance.onend = () => {
                this.desactivarOrbeHablando();
            };
            
            window.speechSynthesis.speak(utterance);
        }
    }

    ejecutarAccion(accion) {
        const acciones = {
            'cargar_dashboard': () => {
                // Ya estamos en el dashboard, refrescar datos
                if (typeof actualizarDatosSensores === 'function') {
                    actualizarDatosSensores();
                }
            },
            'actualizar_biodigestores': () => {
                if (typeof actualizarDatosBiodigestores === 'function') {
                    actualizarDatosBiodigestores();
                }
            },
            'abrir_analisis_economico': () => {
                window.location.href = '/analisis-economico';
            },
            'mostrar_predicciones': () => {
                // Cambiar a tab de predicciones si existe
                const tabPredicciones = document.querySelector('[data-bs-target="#predicciones-ia"]');
                if (tabPredicciones) {
                    tabPredicciones.click();
                }
            },
            'abrir_gestion_materiales': () => {
                window.location.href = '/gestion_materiales';
            },
            'mostrar_generacion': () => {
                const tabGeneracion = document.querySelector('[data-bs-target="#generacion-tiempo-real"]');
                if (tabGeneracion) {
                    tabGeneracion.click();
                }
            },
            'abrir_reportes': () => {
                // TODO: implementar módulo de reportes
                this.mostrarMensajeAsistente('El módulo de reportes estará disponible próximamente.');
            }
        };
        
        const fn = acciones[accion];
        if (fn) {
            fn();
        }
    }

    // Métodos del orbe
    activarOrbeEscuchando() {
        if (this.orbe) {
            this.orbe.classList.add('listening');
            this.orbe.classList.remove('thinking', 'speaking');
        }
    }

    desactivarOrbeEscuchando() {
        if (this.orbe) {
            this.orbe.classList.remove('listening');
        }
    }

    activarOrbePensando() {
        if (this.orbe) {
            this.orbe.classList.add('thinking');
            this.orbe.classList.remove('listening', 'speaking');
        }
    }

    desactivarOrbePensando() {
        if (this.orbe) {
            this.orbe.classList.remove('thinking');
        }
    }

    activarOrbeHablando() {
        if (this.orbe) {
            this.orbe.classList.add('speaking');
            this.orbe.classList.remove('listening', 'thinking');
        }
    }

    desactivarOrbeHablando() {
        if (this.orbe) {
            this.orbe.classList.remove('speaking');
        }
    }

    ocultarOrbe() {
        if (this.orbe) {
            this.orbe.style.display = 'none';
        }
    }

    mostrarOrbe() {
        if (this.orbe) {
            this.orbe.style.display = 'flex';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Instancia global de JARVIS
const jarvisUI = new JarvisUI();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Esperar un poco para asegurar que el DOM esté completamente cargado
    setTimeout(() => {
        jarvisUI.inicializar();
    }, 500);
});

// Exportar para debugging
window.jarvisUI = jarvisUI;
