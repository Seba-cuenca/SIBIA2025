document.addEventListener('DOMContentLoaded', function() {
    // Asegurarse de que el código se ejecute solo si los elementos del asistente existen
    if (!document.getElementById('asistente-chat-container')) {
        return;
    }

    // --- ELEMENTOS DEL DOM ---
    const chatContainer = document.getElementById('asistente-chat-container');
    const chatBox = document.getElementById('asistente-chatbox');
    const aiPlaceholder = document.getElementById('ai-placeholder');
    const aiIconContainer = document.getElementById('ai-icon-container');
    const aiGlowCircle = document.getElementById('ai-glow-circle');
    const aiStatusText = document.getElementById('ai-status-text');
    const userInput = document.getElementById('asistente-input');
    const sendButton = document.getElementById('asistente-send-btn');
    const micButton = document.getElementById('asistente-mic-btn');

    // --- ESTADO DEL ASISTENTE ---
    let isActivated = false;
    let isListening = false;
    let isSpeaking = false;
    let isProcessing = false;

    // --- API DE VOZ ---
    const synth = window.speechSynthesis;
    let recognition;
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'es-AR';
        recognition.continuous = false;
        recognition.interimResults = false;
    } else {
        if (aiStatusText) aiStatusText.textContent = "Reconocimiento de voz no soportado.";
        if (aiIconContainer) aiIconContainer.style.display = 'none';
        if (micButton) micButton.disabled = true;
    }

    // --- FUNCIONES PRINCIPALES ---

    function setAiStatus(status, text) {
        if (aiStatusText) aiStatusText.textContent = text;
        if (!aiGlowCircle) return;
        
        aiGlowCircle.style.transform = 'scale(1)';
        aiGlowCircle.style.opacity = '1';
        
        switch (status) {
            case 'listening':
                aiGlowCircle.style.transform = 'scale(1.2)';
                break;
            case 'processing':
                aiGlowCircle.style.transform = 'scale(0.9)';
                aiGlowCircle.style.opacity = '0.8';
                break;
            case 'speaking':
                aiGlowCircle.style.transform = 'scale(1.1)';
                break;
        }
    }
    
    function hablar(texto) {
        return new Promise((resolve, reject) => {
            if (isSpeaking) synth.cancel();
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = 'es-AR';
            
            utterance.onstart = () => { isSpeaking = true; setAiStatus('speaking', "Hablando..."); };
            utterance.onend = () => { isSpeaking = false; setAiStatus('idle', "Pregúntame algo..."); resolve(); };
            utterance.onerror = (e) => {
                isSpeaking = false;
                console.error('Error en síntesis de voz:', e.error);
                setAiStatus('idle', "Error de voz.");
                reject(e.error);
            };
            synth.speak(utterance);
        });
    }

    function startListening() {
        if (!recognition || isListening || isSpeaking || isProcessing) return;
        try {
            recognition.start();
        } catch (e) {
            console.error("Error al iniciar reconocimiento:", e);
            setAiStatus('idle', "Error de micrófono.");
        }
    }

    function agregarMensaje(texto, tipo) {
        if (aiPlaceholder && aiPlaceholder.style.opacity !== '0') {
            aiPlaceholder.style.opacity = '0';
            setTimeout(() => {
                if (aiPlaceholder) aiPlaceholder.style.display = 'none';
                if (chatBox) chatBox.style.display = 'flex';
            }, 500);
        }

        const msgDiv = document.createElement('div');
        msgDiv.classList.add('d-flex', 'mb-3', tipo === 'usuario' ? 'justify-content-end' : 'justify-content-start');
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('p-2', 'rounded', 'mw-75', 'shadow-sm');
        contentDiv.classList.add(tipo === 'usuario' ? 'bg-primary' : 'bg-light', tipo === 'usuario' ? 'text-white' : 'text-dark');
        contentDiv.textContent = texto;

        msgDiv.appendChild(contentDiv);
        if (chatBox) {
            chatBox.appendChild(msgDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    async function enviarPregunta(pregunta) {
        if (!pregunta) return;
        agregarMensaje(pregunta, 'usuario');
        isProcessing = true;
        setAiStatus('processing', "Pensando...");

        try {
            const response = await fetch('/ask_assistant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta, return_full_response: true })
            });
            const data = await response.json();
            isProcessing = false;
            
            const respuesta = data.respuesta_texto || "No pude procesar esa pregunta.";
            agregarMensaje(respuesta, 'asistente');
            
            await hablar(respuesta);
        } catch (error) {
            isProcessing = false;
            console.error('Error al contactar al asistente:', error);
            const errorMsg = "Lo siento, hay un problema de conexión.";
            agregarMensaje(errorMsg, 'asistente');
            await hablar(errorMsg);
        }
    }

    // --- EVENT HANDLERS ---
    
    function activarAsistente() {
        if (isActivated) {
            if (isListening) {
                recognition.stop();
            } else {
                startListening();
            }
        } else {
            isActivated = true;
            setAiStatus('idle', "¡Hola! ¿En qué puedo ayudarte?");
            hablar("Bienvenido a SIBIA. Estoy lista para escuchar.").finally(() => {
                startListening();
            });
        }
    }

    if (aiIconContainer) aiIconContainer.addEventListener('click', activarAsistente);
    if (micButton) micButton.addEventListener('click', activarAsistente);
    
    if (recognition) {
        recognition.onstart = () => { isListening = true; setAiStatus('listening', "Escuchando..."); };
        recognition.onresult = (e) => {
            const transcripcion = e.results[0][0].transcript;
            enviarPregunta(transcripcion);
        };
        recognition.onerror = (e) => {
            let msg = "No te escuché. Inténtalo de nuevo.";
            if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
                msg = "Necesito permiso para usar el micrófono.";
            }
            setAiStatus('idle', msg);
        };
        recognition.onend = () => {
            isListening = false;
            if (!isProcessing && !isSpeaking) {
                 setAiStatus('idle', "Toca el ícono para hablar.");
            }
        };
    }

    if (sendButton) {
        sendButton.addEventListener('click', () => enviarPregunta(userInput.value.trim()));
    }
    if (userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') enviarPregunta(userInput.value.trim());
        });
    }
}); 