let reconocimientoActivo = false;
let vozActiva = false;
let asistenteInicializado = false; // Flag para controlar la inicialización

// Variables para el control del orbe IA
let aiOrb = null;
let orbContainer = null;
let isOrbListening = false;
let isOrbSpeaking = false;

// Función de prueba del orbe (temporal)
window.probarOrbe = function() {
    console.log('=== PRUEBA DEL ORBE ===');
    console.log('aiOrb:', document.getElementById('ai-orb'));
    console.log('orbContainer:', document.getElementById('ai-orb-container'));
    console.log('chatbox:', document.getElementById('asistente-chatbox'));
    
    const orb = document.getElementById('ai-orb');
    if (orb) {
        console.log('Orbe encontrado, probando rostro...');
        
        // Probar el rostro
        activarOrbeHablando();
        
        setTimeout(() => {
            desactivarOrbeHablando();
        }, 3000);
        
        console.log('Prueba del rostro completada');
    } else {
        console.error('Orbe NO encontrado');
    }
};

// Función para probar todos los estados del orbe
window.probarEstadosOrbe = function() {
    console.log('=== PROBANDO TODOS LOS ESTADOS ===');
    
    setTimeout(() => {
        console.log('Activando estado escuchando...');
        activarOrbeEscuchando();
    }, 1000);
    
    setTimeout(() => {
        console.log('Activando estado pensando...');
        desactivarOrbeEscuchando();
        activarOrbePensando();
    }, 3000);
    
    setTimeout(() => {
        console.log('Activando estado hablando...');
        desactivarOrbePensando();
        activarOrbeHablando();
    }, 5000);
    
    setTimeout(() => {
        console.log('Volviendo a estado normal...');
        desactivarOrbeHablando();
    }, 8000);
};

// Función para limpiar el chat y mostrar el orbe
window.limpiarChat = function() {
    const chatbox = document.getElementById('asistente-chatbox');
    if (chatbox) {
        // Mantener solo el mensaje inicial
        const mensajeInicial = chatbox.querySelector('.mensaje-inicial');
        
        // Limpiar todo el chatbox
        chatbox.innerHTML = '';
        
        // Recrear el mensaje inicial si no existe
        if (!mensajeInicial) {
            chatbox.innerHTML = `
                <div class="mensaje-asistente mb-3 mensaje-inicial">
                    <div class="d-flex justify-content-start">
                        <div class="mensaje-inicial-bg p-2 rounded border" style="max-width: 70%;">
                            <p style="color: rgba(255,255,255,0.9); margin: 0;">¡Hola! Soy tu asistente de SIBIA. Puedo ayudarte con consultas sobre biodigestores, mezclas, cálculos energéticos y más. ¿En qué puedo ayudarte?</p>
                        </div>
                    </div>
                </div>
            `;
        } else {
            chatbox.appendChild(mensajeInicial);
        }
        
        // Quitar la clase has-messages para mostrar el orbe
        chatbox.classList.remove('has-messages');
        mostrarOrbe();
        
        console.log('Chat limpiado, orbe visible');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Escuchar cuando se muestra una pestaña en toda la aplicación
    const tabs = document.querySelectorAll('a[data-bs-toggle="tab"], button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', (event) => {
            // Verificar si la pestaña mostrada es la del asistente
            if (event.target.getAttribute('data-bs-target') === '#asistente-ia') {
                console.log('Pestaña del asistente IA activada');
                inicializarAsistente();
            }
        });
    });

    // En caso de que la página se cargue con la pestaña del asistente ya activa
    const asistenteTabPane = document.querySelector('#asistente-ia');
    if (asistenteTabPane && asistenteTabPane.classList.contains('active')) {
        console.log('Pestaña del asistente IA ya activa al cargar');
        inicializarAsistente();
    }
    
    // Intentar inicializar después de un breve delay para asegurar que el DOM esté completamente cargado
    setTimeout(() => {
        if (document.getElementById('ai-orb') && !asistenteInicializado) {
            console.log('Inicializando asistente por timeout');
            inicializarAsistente();
        }
    }, 1000);
});

function inicializarAsistente() {
    if (asistenteInicializado) {
        return; // No volver a inicializar
    }

    const input = document.getElementById('asistente-input');
    const enviarBtn = document.getElementById('asistente-enviar-btn');
    const microBtn = document.getElementById('asistente-micro-btn');

    // Si los elementos no existen, no hacer nada.
    if (!input || !enviarBtn || !microBtn) {
        console.error("No se encontraron los elementos del chat del asistente para inicializar.");
        return;
    }

    enviarBtn.addEventListener('click', () => consultarAsistente(input));
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Evitar que el formulario se envíe (si lo hubiera)
            consultarAsistente(input);
        }
    });
    
    // Hacer que el orbe reaccione al escribir
    input.addEventListener('input', () => {
        if (input.value.trim().length > 0) {
            // Activar un pulso suave cuando el usuario está escribiendo
            if (aiOrb && !isOrbSpeaking && !isOrbListening) {
                aiOrb.style.animation = 'orbPulse 1s ease-in-out infinite, orbFloat 6s ease-in-out infinite';
            }
        } else {
            // Volver al pulso normal cuando no hay texto
            if (aiOrb && !isOrbSpeaking && !isOrbListening) {
                aiOrb.style.animation = 'orbPulse 3s ease-in-out infinite, orbFloat 6s ease-in-out infinite';
            }
        }
    });

    if ('webkitSpeechRecognition' in window) {
        inicializarReconocimientoVoz(microBtn, input);
    } else {
        const estadoMicro = document.getElementById('asistente-estado-micro');
        if (estadoMicro) {
            estadoMicro.textContent = 'El reconocimiento de voz no es compatible con este navegador.';
        }
        microBtn.disabled = true;
    }
    
    // Inicializar el orbe IA
    inicializarOrbeIA();
    
    asistenteInicializado = true;
    console.log("Asistente de IA inicializado correctamente.");
}

function agregarMensajeChat(texto, tipo) {
    const chatbox = document.getElementById('asistente-chatbox');
    const mensajeDiv = document.createElement('div');
    mensajeDiv.classList.add('mensaje', tipo === 'usuario' ? 'mensaje-usuario' : 'mensaje-asistente', 'mb-3');
    
    // Crear estructura del mensaje
    const flexDiv = document.createElement('div');
    flexDiv.classList.add('d-flex', tipo === 'usuario' ? 'justify-content-end' : 'justify-content-start');
    
    const contenidoDiv = document.createElement('div');
    contenidoDiv.classList.add(tipo === 'usuario' ? 'bg-primary' : 'bg-light', 'p-2', 'rounded', 'border');
    contenidoDiv.style.maxWidth = '70%';
    
    // Usar innerHTML para que formatee saltos de línea y otros HTML
    const parrafo = document.createElement('p');
    parrafo.innerHTML = texto;
    parrafo.style.margin = '0';
    if (tipo === 'usuario') {
        parrafo.style.color = 'white';
    }
    
    contenidoDiv.appendChild(parrafo);
    flexDiv.appendChild(contenidoDiv);
    mensajeDiv.appendChild(flexDiv);
    
    chatbox.appendChild(mensajeDiv);
    chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll hacia abajo
}

async function consultarAsistente(inputElement) {
    const pregunta = inputElement.value.trim();
    if (!pregunta) return;

    agregarMensajeChat(pregunta, 'usuario');
    inputElement.value = '';

    const btnEnviar = document.getElementById('asistente-enviar-btn');
    btnEnviar.disabled = true;
    btnEnviar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    // Activar orbe pensando
    activarOrbePensando();

    try {
        const response = await fetch('/ask_assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pregunta: pregunta })
        });

        const data = await response.json();
        let respuestaTexto = '';

        if (response.ok && data.status === 'success') {
            respuestaTexto = data.respuesta.replace(/\n/g, '<br>');
        } else {
            respuestaTexto = data.respuesta || 'Lo siento, ocurrió un error inesperado.';
        }
        
        // Activar orbe hablando antes de mostrar la respuesta
        activarOrbeHablando();
        agregarMensajeChat(respuestaTexto, 'asistente');
        
        // Simular tiempo de "habla" y luego desactivar
        setTimeout(() => {
            desactivarOrbeHablando();
        }, Math.max(2000, respuestaTexto.length * 50)); // Tiempo basado en longitud del texto

    } catch (error) {
        console.error('Error al consultar al asistente:', error);
        agregarMensajeChat('Error de conexión. No pude contactar al asistente.', 'asistente');
    } finally {
        // Desactivar orbe pensando
        desactivarOrbePensando();
        
        btnEnviar.disabled = false;
        btnEnviar.innerHTML = '<i class="fas fa-paper-plane"></i>';
    }
}

function inicializarReconocimientoVoz(microBtn, input) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';

    let isListening = false;
    let isAlwaysListeningEnabled = false;
    let vocesDisponibles = [];
    let vozSeleccionada = null;
    const WAKE_WORD = "sibia";
    
    let chatHistory = [];
    const MAX_HISTORY_LENGTH = 5;

    const preferredVoiceNames = [
        'Microsoft Sabina - Spanish (Mexico)',
        'Google español', 
        'Microsoft Helena - Spanish (Spain)', 
        'Microsoft Laura - Spanish (Spain)',
        'Google US English',
        'Microsoft Zira Desktop - English (United States)'
    ];

    function cargarVoces() {
        vocesDisponibles = speechSynthesis.getVoices();
        console.log("--- Voces Disponibles ---");
        vocesDisponibles.forEach((voice, index) => {
            if (voice.lang.startsWith('es')) {
                console.log(`${index + 1}. Voz en Español: ${voice.name} (${voice.lang})`);
            }
        });

        for (const preferredName of preferredVoiceNames) {
            const foundVoice = vocesDisponibles.find(voice => 
                voice.name.includes(preferredName) && voice.lang.startsWith('es'));
            if (foundVoice) {
                vozSeleccionada = foundVoice;
                console.log(`Voz preferida encontrada: ${foundVoice.name} (${foundVoice.lang})`);
                break;
            }
        }
        
        if (!vozSeleccionada) {
            vozSeleccionada = vocesDisponibles.find(voice => voice.lang.startsWith('es'));
        }
        
        console.log("Voz seleccionada para usar:", vozSeleccionada ? vozSeleccionada.name : "(Default)");
    }

    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = cargarVoces;
    }
    cargarVoces();

    function logMessage(sender, message, preguntaOriginal = null) {
        if (!conversationLog) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender.toLowerCase() === 'tú' ? 'user' : 'assistant'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${message}</p>`;
        
        messageDiv.appendChild(messageContent);
        conversationLog.appendChild(messageDiv);
        
        conversationLog.scrollTop = conversationLog.scrollHeight;

        if (sender.toLowerCase() === 'asistente' && preguntaOriginal) {
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                const assistantMessages = chatMessages.getElementsByClassName('message assistant');
                if (assistantMessages.length > 0) {
                    const lastMsg = assistantMessages[assistantMessages.length - 1];
                    addLearnButtonToAssistantMessage(lastMsg, preguntaOriginal, message);
                }
            }
        }
    }

    function addLearnButtonToAssistantMessage(messageDiv, pregunta, respuesta) {
        const learnBtn = document.createElement('button');
        learnBtn.className = 'btn btn-sm btn-outline-success ms-2';
        learnBtn.textContent = 'Aprender';
        learnBtn.title = 'Haz clic para que el asistente aprenda esta respuesta';
        learnBtn.onclick = function() {
            fetch('/asistente_aprender', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta, respuesta })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.mensaje || '¡Gracias! El asistente ha aprendido esta respuesta.');
            })
            .catch(() => {
                alert('Error al guardar el aprendizaje.');
            });
        };
        messageDiv.appendChild(learnBtn);
    }

    function hablar(texto) {
        if (!speechSynthesis || !vozSeleccionada || !texto) {
            console.warn("Síntesis de voz no disponible, voz no seleccionada o texto vacío.");
            return;
        }

        speechSynthesis.cancel();

        const fragmentos = texto.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [texto];
        let indiceFragmento = 0;

        const hablarSiguienteFragmento = () => {
            if (indiceFragmento < fragmentos.length) {
                const utterance = new SpeechSynthesisUtterance(fragmentos[indiceFragmento]);
                utterance.voice = vozSeleccionada;
                utterance.lang = vozSeleccionada.lang;
                utterance.volume = 1;
                utterance.rate = 1.0;
                utterance.pitch = 1.1;

                utterance.onstart = () => {
                    if (voiceStatus) voiceStatus.textContent = "Hablando...";
                    // Activar orbe hablando
                    activarOrbeHablando();
                };

                utterance.onend = () => {
                    indiceFragmento++;
                    if (indiceFragmento >= fragmentos.length) {
                        if (voiceStatus) voiceStatus.textContent = "Esperando activación...";
                        // Desactivar orbe hablando al terminar todos los fragmentos
                        desactivarOrbeHablando();
                    }
                    hablarSiguienteFragmento();
                };

                utterance.onerror = (event) => {
                    console.error("Error en la síntesis de voz:", event);
                    if (voiceStatus) voiceStatus.textContent = "Error al reproducir voz. Por favor, intenta de nuevo más tarde.";
                    indiceFragmento++;
                    hablarSiguienteFragmento();
                };

                speechSynthesis.speak(utterance);
            }
        };

        hablarSiguienteFragmento();
    }

    if (!recognition && microBtn) {
        if (voiceStatus) voiceStatus.textContent = "Reconocimiento de voz no soportado por este navegador.";
        microBtn.disabled = true;
        return;
    }

    if (recognition) {
        recognition.onstart = () => {
            isListening = true;
            microBtn.classList.add('active');
            voiceStatus.textContent = "Escuchando...";
            // Activar orbe escuchando
            activarOrbeEscuchando();
        };

        recognition.onend = () => {
            isListening = false;
            microBtn.classList.remove('active');
            voiceStatus.textContent = "Esperando activación...";
            // Desactivar orbe escuchando
            desactivarOrbeEscuchando();
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.trim();
            console.log("Transcripción:", transcript);
            
            const transcriptLower = transcript.toLowerCase();
            
            if (transcriptLower.includes(WAKE_WORD) || isAlwaysListeningEnabled) {
                let pregunta = transcript;
                if (transcriptLower.includes(WAKE_WORD)) {
                    const wakeWordIndex = transcriptLower.indexOf(WAKE_WORD);
                    if (wakeWordIndex === 0) {
                        pregunta = transcript.substring(WAKE_WORD.length).trim();
                    }
                }
                
                if (pregunta && pregunta !== WAKE_WORD) {
                    enviarPregunta(pregunta);
                } else if (transcriptLower === WAKE_WORD || transcriptLower.trim() === WAKE_WORD) {
                    logMessage("Tú", WAKE_WORD);
                    const respuesta = "Sí, dime en qué puedo ayudarte.";
                    logMessage("SIBIA", respuesta);
                    hablar(respuesta);
                    
                    isAlwaysListeningEnabled = true;
                    setTimeout(() => {
                        if (isAlwaysListeningEnabled) {
                            isAlwaysListeningEnabled = false;
                            if (voiceStatus) voiceStatus.textContent = "Esperando activación...";
                            hablar("Volviendo al modo de espera. Di 'SIBIA' para activarme nuevamente.");
                        }
                    }, 30000);
                }
            }
        };

        recognition.onerror = (event) => {
            isListening = false;
            let errorMsg = `Error: ${event.error}`;
            
            if (event.error === 'no-speech') {
                errorMsg = "No se detectó voz.";
            } else if (event.error === 'audio-capture') {
                errorMsg = "Error de micrófono. Verifica que esté conectado y activado.";
                isAlwaysListeningEnabled = false;
            } else if (event.error === 'not-allowed') {
                errorMsg = "Permiso de micrófono denegado. Por favor, activa los permisos.";
                isAlwaysListeningEnabled = false;
            } else if (event.error === 'aborted') {
                errorMsg = "Reconocimiento cancelado.";
            }
            
            console.error("Error de reconocimiento:", event);
            if (voiceStatus) voiceStatus.textContent = errorMsg;
            
            if (event.error !== 'no-speech' && event.error !== 'aborted') {
                logMessage("Error", errorMsg);
            }
        };

        microBtn.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        function enviarPregunta(pregunta) {
            if (!pregunta) return;
            logMessage('Tú', pregunta);
            mostrarRespuestaAsistente('Pensando...', '...');
            fetch('/ask_assistant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta })
            })
            .then(res => res.json())
            .then(data => {
                if (chatMessages && chatMessages.lastChild && chatMessages.lastChild.textContent.includes('Pensando...')) {
                    chatMessages.removeChild(chatMessages.lastChild);
                }
                mostrarRespuestaAsistente(data.respuesta, data.motor, pregunta);
            })
            .catch(err => {
                mostrarRespuestaAsistente('Error al contactar al asistente.', 'Error');
            });
        }
    }
}

function mostrarRespuestaAsistente(respuesta, motor, preguntaOriginal = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    let badgeColor = 'secondary';
    if (motor === 'APP') badgeColor = 'success';
    else if (motor === 'Gemini') badgeColor = 'primary';
    else if (motor === 'OpenAI') badgeColor = 'dark';
    else if (motor === 'Error') badgeColor = 'danger';
    const badge = `<span class="badge bg-${badgeColor} ms-2">${motor}</span>`;
    messageDiv.innerHTML = `<div class="message-content"><p>${respuesta}</p> ${badge}</div>`;
    if (preguntaOriginal && motor !== 'Error') {
        const learnBtn = document.createElement('button');
        learnBtn.className = 'btn btn-sm btn-outline-success ms-2';
        learnBtn.textContent = 'Aprender';
        learnBtn.title = 'Haz clic para que el asistente aprenda esta respuesta';
        learnBtn.onclick = function() {
            fetch('/asistente_aprender', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta: preguntaOriginal, respuesta })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.mensaje || '¡Gracias! El asistente ha aprendido esta respuesta.');
            })
            .catch(() => {
                alert('Error al guardar el aprendizaje.');
            });
        };
        messageDiv.querySelector('.message-content').appendChild(learnBtn);
    }
    document.getElementById('chat-messages').appendChild(messageDiv);
    document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
}

// ===== FUNCIONES DEL ORBE IA =====

function inicializarOrbeIA() {
    console.log('Iniciando inicialización del orbe IA...');
    
    aiOrb = document.getElementById('ai-orb');
    orbContainer = document.getElementById('ai-orb-container');
    
    console.log('aiOrb:', aiOrb);
    console.log('orbContainer:', orbContainer);
    
    if (!aiOrb || !orbContainer) {
        console.warn('Elementos del orbe IA no encontrados');
        console.log('Elementos disponibles con ID ai-orb:', document.querySelectorAll('#ai-orb'));
        console.log('Elementos disponibles con ID ai-orb-container:', document.querySelectorAll('#ai-orb-container'));
        return;
    }
    
    console.log('Orbe IA inicializado correctamente');
    
    // Mostrar el orbe al inicializar
    mostrarOrbe();
    
    // Ocultar el orbe cuando hay mensajes y cambiar fondo del chatbox
    const chatbox = document.getElementById('asistente-chatbox');
    if (chatbox) {
        console.log('Chatbox encontrado, configurando observer');
        // Observar cambios en el chatbox
        const observer = new MutationObserver((mutations) => {
            const mensajes = chatbox.querySelectorAll('.mensaje-asistente:not(.mensaje-inicial), .mensaje-usuario');
            console.log('Mensajes de conversación encontrados:', mensajes.length);
            if (mensajes.length > 0) { // Si hay mensajes además del inicial
                ocultarOrbe();
                chatbox.classList.add('has-messages');
            } else {
                mostrarOrbe();
                chatbox.classList.remove('has-messages');
            }
        });
        
        observer.observe(chatbox, { childList: true, subtree: true });
        
        // Verificar estado inicial
        const mensajesConversacion = chatbox.querySelectorAll('.mensaje-asistente:not(.mensaje-inicial), .mensaje-usuario');
        if (mensajesConversacion.length === 0) {
            chatbox.classList.remove('has-messages');
            mostrarOrbe();
        }
    } else {
        console.warn('Chatbox no encontrado');
    }
}

function mostrarOrbe() {
    console.log('Intentando mostrar orbe...');
    if (orbContainer) {
        orbContainer.style.opacity = '1';
        orbContainer.style.visibility = 'visible';
        console.log('Orbe mostrado');
    } else {
        console.warn('orbContainer no disponible para mostrar');
    }
}

function ocultarOrbe() {
    console.log('Intentando ocultar orbe...');
    if (orbContainer) {
        orbContainer.style.opacity = '0';
        orbContainer.style.visibility = 'hidden';
        console.log('Orbe ocultado');
    } else {
        console.warn('orbContainer no disponible para ocultar');
    }
}

function activarOrbeEscuchando() {
    if (aiOrb && !isOrbListening) {
        isOrbListening = true;
        aiOrb.classList.add('listening');
        
        // Cambiar colores cuando está escuchando
        aiOrb.style.background = `radial-gradient(circle at 30% 30%, 
            rgba(0, 255, 127, 0.9) 0%, 
            rgba(30, 144, 255, 0.8) 25%, 
            rgba(138, 43, 226, 0.7) 50%, 
            rgba(255, 20, 147, 0.6) 75%, 
            rgba(255, 215, 0, 0.5) 100%)`;
        
        aiOrb.style.boxShadow = `
            0 0 40px rgba(0, 255, 127, 0.8),
            0 0 80px rgba(30, 144, 255, 0.6),
            0 0 120px rgba(138, 43, 226, 0.4)`;
            
        console.log('Orbe activado - Escuchando');
    }
}

function desactivarOrbeEscuchando() {
    if (aiOrb && isOrbListening) {
        isOrbListening = false;
        aiOrb.classList.remove('listening');
        
        // Volver a colores normales
        aiOrb.style.background = `radial-gradient(circle at 30% 30%, 
            rgba(255, 255, 255, 0.8) 0%, 
            rgba(138, 43, 226, 0.8) 25%, 
            rgba(30, 144, 255, 0.7) 50%, 
            rgba(255, 20, 147, 0.6) 75%, 
            rgba(0, 255, 127, 0.5) 100%)`;
        
        aiOrb.style.boxShadow = `
            0 0 30px rgba(138, 43, 226, 0.6),
            0 0 60px rgba(30, 144, 255, 0.4),
            0 0 90px rgba(255, 20, 147, 0.3)`;
            
        console.log('Orbe desactivado - Reposo');
    }
}

function activarOrbeHablando() {
    if (aiOrb && !isOrbSpeaking) {
        isOrbSpeaking = true;
        aiOrb.classList.add('speaking');
        
        // Forzar la visibilidad del rostro
        const face = aiOrb.querySelector('.ai-face');
        if (face) {
            face.style.opacity = '1';
            face.style.transform = 'translate(-50%, -50%) scale(1.1)';
        }
        
        mostrarOrbe(); // Asegurar que sea visible cuando habla
        console.log('Orbe hablando - Rostro visible');
    }
}

function desactivarOrbeHablando() {
    if (aiOrb && isOrbSpeaking) {
        isOrbSpeaking = false;
        aiOrb.classList.remove('speaking');
        
        // Ocultar el rostro gradualmente
        const face = aiOrb.querySelector('.ai-face');
        if (face) {
            face.style.opacity = '0';
            face.style.transform = 'translate(-50%, -50%) scale(1)';
        }
        
        console.log('Orbe terminó de hablar - Rostro oculto');
    }
}

// Función para hacer pulsar el orbe cuando está procesando
function activarOrbePensando() {
    if (aiOrb) {
        aiOrb.style.animation = 'orbPulse 0.5s ease-in-out infinite, orbFloat 6s ease-in-out infinite';
        console.log('Orbe pensando - Pulsando rápido');
    }
}

function desactivarOrbePensando() {
    if (aiOrb) {
        aiOrb.style.animation = 'orbPulse 3s ease-in-out infinite, orbFloat 6s ease-in-out infinite';
        console.log('Orbe en reposo - Pulsando normal');
    }
}