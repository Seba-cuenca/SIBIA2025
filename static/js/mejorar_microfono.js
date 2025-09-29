/**
 * Script para mejorar la funcionalidad del micrófono en el asistente SIBIA
 * 
 * Este script soluciona problemas comunes con el reconocimiento de voz
 * y facilita el uso del micrófono en la aplicación.
 */

// Esperar a que el documento se cargue completamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando mejoras del micrófono...');
    
    // Comprobar la compatibilidad del navegador con el reconocimiento de voz
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.error('Este navegador no soporta reconocimiento de voz. Por favor, usa Chrome, Edge o Safari.');
        // Mostrar un mensaje al usuario
        if (document.getElementById('voice-status')) {
            document.getElementById('voice-status').textContent = 'Tu navegador no soporta reconocimiento de voz.';
            document.getElementById('voice-status').style.color = 'red';
        }
        return;
    }
    
    // Variables globales
    let recognition = null;
    let isListening = false;
    let recognitionAttempts = 0;
    const MAX_ATTEMPTS = 5; // Aumentado para dar más oportunidades
    let autoStartAttempt = 0;
    const MAX_AUTO_START_ATTEMPTS = 3;
    
    // Elementos de la interfaz
    const voiceBtn = document.getElementById('btnVoz') || document.getElementById('voice-assistant-btn');
    const voiceStatus = document.getElementById('voice-status');
    
    if (!voiceBtn) {
        console.error('No se encontró el botón de voz en la página');
        return;
    }
    
    // Verificar si ya teníamos permiso
    const hasStoredPermission = localStorage.getItem('microphonePermissionGranted') === 'true';
    
    // Preparar el reconocimiento de voz
    function setupRecognition() {
        // Crear una nueva instancia si no existe
        if (!recognition) {
            recognition = new SpeechRecognition();
            
            // Configurar opciones
            recognition.lang = 'es-ES';
            recognition.interimResults = true; // Muestra resultados mientras hablas
            recognition.continuous = false; // No continuo para evitar problemas
            recognition.maxAlternatives = 3; // Más alternativas para mejor precisión
            
            // Configurar eventos
            recognition.onstart = handleRecognitionStart;
            recognition.onresult = handleRecognitionResult;
            recognition.onerror = handleRecognitionError;
            recognition.onend = handleRecognitionEnd;
            
            console.log('Reconocimiento de voz configurado correctamente');
        }
    }
    
    // Manejadores de eventos
    function handleRecognitionStart() {
        isListening = true;
        if (voiceStatus) {
            voiceStatus.textContent = '🎤 Escuchando...';
            voiceStatus.style.color = 'green';
        }
        if (voiceBtn) {
            voiceBtn.classList.add('active');
        }
        console.log('Reconocimiento iniciado');
    }
    
    function handleRecognitionResult(event) {
        console.log('Resultado de reconocimiento recibido');
        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript.trim();
        
        // Mostrar transcripción intermedia
        if (voiceStatus) {
            voiceStatus.textContent = `"${transcript}"`;
        }
        
        // Si es un resultado final
        if (event.results[last].isFinal) {
            console.log(`Transcripción final: "${transcript}"`);
            
            // Reiniciar contador de intentos en caso de éxito
            recognitionAttempts = 0;
            
            // Aquí podríamos procesar la transcripción, pero lo dejamos al código existente
        }
    }
    
    function handleRecognitionError(event) {
        console.error('Error de reconocimiento:', event.error);
        isListening = false;
        
        // Manejar diferentes tipos de errores
        let message = '';
        switch(event.error) {
            case 'no-speech':
                message = 'No se detectó voz. Intenta hablar más fuerte.';
                // Estos errores son comunes, no contarlos como intentos
                break;
            case 'audio-capture':
                message = 'Error: No se pudo acceder al micrófono.';
                recognitionAttempts++;
                break;
            case 'not-allowed':
                message = '<strong>Permiso de micrófono denegado</strong>. Sigue estos pasos:<br>1. Haz clic en el icono de candado 🔒 en la barra de direcciones<br>2. Cambia el permiso del micrófono a "Permitir"<br>3. Recarga la página';
                // Eliminar el permiso guardado
                localStorage.removeItem('microphonePermissionGranted');
                recognitionAttempts++;
                break;
            case 'network':
                message = 'Error de red. Verifica tu conexión.';
                recognitionAttempts++;
                break;
            default:
                message = `Error: ${event.error}`;
                recognitionAttempts++;
        }
        
        if (voiceStatus) {
            voiceStatus.innerHTML = message;
            voiceStatus.style.color = 'red';
        }
        
        // Si hay demasiados errores, detener los intentos
        if (recognitionAttempts >= MAX_ATTEMPTS) {
            console.error('Demasiados errores de reconocimiento, deteniendo los intentos');
            if (voiceStatus) {
                voiceStatus.innerHTML = 'Reconocimiento de voz desactivado por errores.<br>Recarga la página o intenta con otro navegador.';
            }
            return;
        }
    }
    
    function handleRecognitionEnd() {
        console.log('Reconocimiento finalizado');
        isListening = false;
        
        if (voiceBtn) {
            voiceBtn.classList.remove('active');
        }
        
        // Actualizar estado solo si no se estableció como error
        if (voiceStatus && !voiceStatus.style.color.includes('red')) {
            voiceStatus.textContent = 'Reconocimiento listo';
            voiceStatus.style.color = '';
        }
    }
    
    // Función para iniciar/detener el reconocimiento
    function toggleRecognition() {
        setupRecognition();
        
        if (isListening) {
            // Detener reconocimiento
            try {
                recognition.stop();
                console.log('Reconocimiento detenido');
            } catch (e) {
                console.error('Error al detener el reconocimiento:', e);
            }
        } else {
            // Iniciar reconocimiento
            try {
                // Verificamos si ya teníamos permiso almacenado
                const hasStoredPermission = localStorage.getItem('microphonePermissionGranted') === 'true';
                
                if (hasStoredPermission) {
                    // Intentar iniciar directamente si ya tenemos permiso
                    try {
                        recognition.start();
                        console.log('Reconocimiento iniciado (permiso previo)');
                        return;
                    } catch (err) {
                        console.warn('No se pudo iniciar con permiso almacenado:', err);
                        // Continuar con el flujo normal si falla
                    }
                }
                
                // Solicitar permisos de micrófono primero
                requestMicrophonePermission()
                    .then(hasPermission => {
                        if (hasPermission) {
                            try {
                                recognition.start();
                                console.log('Reconocimiento iniciado');
                            } catch (err) {
                                console.error('Error al iniciar el reconocimiento después de obtener permiso:', err);
                                if (voiceStatus) {
                                    voiceStatus.innerHTML = `Error al iniciar: ${err.message}<br>Intenta recargar la página.`;
                                    voiceStatus.style.color = 'red';
                                }
                            }
                        } else {
                            if (voiceStatus) {
                                voiceStatus.innerHTML = 'No hay permiso para usar el micrófono.<br>Haz clic en el icono de candado 🔒 en la barra de direcciones y habilita el micrófono.';
                                voiceStatus.style.color = 'red';
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error al solicitar permisos:', error);
                    });
            } catch (e) {
                console.error('Error al iniciar el reconocimiento:', e);
                if (voiceStatus) {
                    voiceStatus.innerHTML = `Error al iniciar: ${e.message}<br>Intenta con otro navegador como Chrome.`;
                    voiceStatus.style.color = 'red';
                }
            }
        }
    }
    
    // Intento automático para iniciar micrófono
    function tryAutoStart() {
        if (autoStartAttempt >= MAX_AUTO_START_ATTEMPTS) {
            console.log('Máximo de intentos automáticos alcanzado');
            return;
        }
        
        autoStartAttempt++;
        
        // Si tenemos permiso guardado, intentar iniciar automáticamente
        if (hasStoredPermission) {
            console.log('Intentando inicio automático (intento ' + autoStartAttempt + ')');
            
            if (voiceStatus) {
                voiceStatus.textContent = 'Iniciando micrófono automáticamente...';
                voiceStatus.style.color = 'blue';
            }
            
            setTimeout(() => {
                toggleRecognition();
            }, 1500);
        }
    }
    
    // Solicitar permiso de micrófono de forma explícita
    async function requestMicrophonePermission() {
        try {
            // Mostrar estado solicitando permiso
            if (voiceStatus) {
                voiceStatus.innerHTML = 'Solicitando permiso de micrófono... <strong>IMPORTANTE: Selecciona "Permitir" y marca "Recordar esta decisión"</strong>';
                voiceStatus.style.color = 'red';
                voiceStatus.style.fontWeight = 'bold';
            }
            
            // Esperar 1 segundo para dar tiempo a la interfaz
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: true,
                    video: false
                });
                
                // Detener el stream inmediatamente (solo necesitamos comprobar permisos)
                stream.getTracks().forEach(track => track.stop());
                
                console.log('Permiso de micrófono concedido');
                
                if (voiceStatus) {
                    voiceStatus.textContent = 'Micrófono listo. Haz clic para hablar.';
                    voiceStatus.style.color = 'green';
                }
                
                // Guardar en localStorage que el permiso fue concedido
                localStorage.setItem('microphonePermissionGranted', 'true');
                
                return true;
            } catch (err) {
                console.error('Error específico al solicitar permiso de micrófono:', err);
                
                if (voiceStatus) {
                    // Instrucciones más específicas según el error
                    if (err.name === 'NotAllowedError') {
                        voiceStatus.innerHTML = '<strong>Permiso denegado</strong>. Para habilitar el micrófono: <br>' +
                                               '1. Haz clic en el icono 🔒 en la barra de direcciones<br>' + 
                                               '2. Selecciona "Permitir" para el micrófono<br>' +
                                               '3. Recarga la página';
                    } else {
                        voiceStatus.textContent = `Error de micrófono: ${err.message}. Intenta con otro navegador como Chrome.`;
                    }
                    voiceStatus.style.color = 'red';
                }
                
                return false;
            }
        } catch (error) {
            console.error('Error general al solicitar permiso de micrófono:', error);
            
            if (voiceStatus) {
                voiceStatus.innerHTML = 'Error al acceder al micrófono. <br>Comprueba que tu navegador tenga permisos y que el micrófono esté conectado.';
                voiceStatus.style.color = 'red';
            }
            
            return false;
        }
    }
    
    // Añadir evento al botón de voz
    if (voiceBtn) {
        voiceBtn.addEventListener('click', function() {
            toggleRecognition();
        });
        
        console.log('Evento click añadido al botón de voz');
    }
    
    // Comprobar permiso de micrófono al cargar
    requestMicrophonePermission()
        .then(hasPermission => {
            if (hasPermission) {
                if (voiceStatus) {
                    voiceStatus.textContent = 'Micrófono listo. Haz clic para hablar.';
                }
                console.log('Micrófono disponible y listo');
                
                // Intentar iniciar automáticamente después de 2 segundos
                setTimeout(tryAutoStart, 2000);
            } else {
                if (voiceStatus) {
                    voiceStatus.innerHTML = 'Sin acceso al micrófono. Haz clic en el botón del micrófono para conceder permiso.<br>Asegúrate de seleccionar "Permitir" y marcar "Recordar"';
                    voiceStatus.style.color = 'orange';
                    voiceStatus.style.fontWeight = 'bold';
                }
                console.warn('No hay permiso para usar el micrófono');
            }
        });
    
    console.log('Mejoras del micrófono cargadas correctamente');
    
    // Exponer funciones globalmente
    window.sibiaMicrophone = {
        toggle: toggleRecognition,
        requestPermission: requestMicrophonePermission
    };
});

// Sobrescribir la función global toggleVoz
function toggleVoz() {
    // Si tenemos nuestra versión mejorada, usarla
    if (window.sibiaMicrophone && window.sibiaMicrophone.toggle) {
        window.sibiaMicrophone.toggle();
    } else {
        // Fallback al código original si está disponible
        if (window.originalToggleVoz) {
            window.originalToggleVoz();
        }
    }
} 