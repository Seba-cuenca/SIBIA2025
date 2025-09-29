// =============================================================================
// SISTEMA DE RECONEXIÓN AUTOMÁTICA A LA BASE DE DATOS
// =============================================================================

(function() {
    'use strict';
    
    // Configuración
    const CONFIG = {
        checkInterval: 30000,      // Verificar conexión cada 30 segundos
        retryInterval: 5000,       // Reintentar cada 5 segundos si falla
        maxRetries: 3,             // Máximo de reintentos antes de mostrar error
        endpoints: [               // Endpoints para verificar conexión
            '/generacion_actual',
            '/sensores_criticos_resumen',
            '/gases_biodigestor_040'
        ]
    };
    
    // Estado
    let isConnected = true;
    let retryCount = 0;
    let checkTimer = null;
    let retryTimer = null;
    
    // Función para verificar la conexión
    async function checkConnection() {
        try {
            // Intentar con el primer endpoint disponible
            const response = await fetch(CONFIG.endpoints[0] + '?t=' + Date.now(), {
                method: 'GET',
                cache: 'no-cache',
                signal: AbortSignal.timeout(5000) // Timeout de 5 segundos
            });
            
            if (response.ok) {
                if (!isConnected) {
                    // La conexión se ha restaurado
                    onConnectionRestored();
                }
                isConnected = true;
                retryCount = 0;
            } else {
                throw new Error('Response not OK');
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            if (isConnected) {
                // Se perdió la conexión
                onConnectionLost();
            }
            isConnected = false;
            scheduleRetry();
        }
    }
    
    // Cuando se pierde la conexión
    function onConnectionLost() {
        console.warn('⚠️ Conexión perdida con la base de datos');
        
        // Mostrar notificación
        mostrarNotificacion('warning', '⚠️ Conexión perdida', 'Se perdió la conexión con la base de datos. Reintentando...');
        
        // Actualizar indicadores en la interfaz
        actualizarIndicadoresConexion(false);
        
        // Detener actualizaciones automáticas
        if (window.stopAllUpdates) {
            window.stopAllUpdates();
        }
    }
    
    // Cuando se restaura la conexión
    function onConnectionRestored() {
        console.log('✅ Conexión restaurada');
        
        // Mostrar notificación
        mostrarNotificacion('success', '✅ Conexión restaurada', 'La conexión con la base de datos ha sido restaurada');
        
        // Actualizar indicadores en la interfaz
        actualizarIndicadoresConexion(true);
        
        // Recargar datos actuales
        recargarDatosActuales();
        
        // Reiniciar actualizaciones automáticas
        if (window.startAllUpdates) {
            window.startAllUpdates();
        }
    }
    
    // Programar reintento
    function scheduleRetry() {
        if (retryCount < CONFIG.maxRetries) {
            retryCount++;
            console.log(`Reintento ${retryCount} de ${CONFIG.maxRetries} en ${CONFIG.retryInterval/1000} segundos...`);
            
            if (retryTimer) clearTimeout(retryTimer);
            retryTimer = setTimeout(() => {
                checkConnection();
            }, CONFIG.retryInterval);
        } else {
            // Mostrar error después de todos los reintentos
            mostrarNotificacion('error', '❌ Error de conexión', 'No se puede conectar con la base de datos. Por favor, verifique su conexión.');
            
            // Agregar botón de reconexión manual
            agregarBotonReconexion();
        }
    }
    
    // Actualizar indicadores de conexión en la interfaz
    function actualizarIndicadoresConexion(conectado) {
        // Cambiar color del header
        const header = document.querySelector('.navbar');
        if (header) {
            if (conectado) {
                header.classList.remove('bg-danger');
                header.classList.add('bg-primary');
            } else {
                header.classList.remove('bg-primary');
                header.classList.add('bg-danger');
            }
        }
        
        // Actualizar badges de conexión
        document.querySelectorAll('.sensor-conectado').forEach(badge => {
            if (conectado) {
                badge.textContent = 'Conectado';
                badge.className = 'badge sensor-conectado ms-1 bg-success text-white';
            } else {
                badge.textContent = 'Desconectado';
                badge.className = 'badge sensor-conectado ms-1 bg-danger text-white';
            }
            badge.style.display = 'inline-block';
        });
        
        // Actualizar estado en el título
        const estadoConexion = document.getElementById('estado-conexion');
        if (estadoConexion) {
            estadoConexion.textContent = conectado ? '🟢 Conectado' : '🔴 Desconectado';
        } else {
            // Crear indicador si no existe
            const navbar = document.querySelector('.navbar-brand');
            if (navbar) {
                const span = document.createElement('span');
                span.id = 'estado-conexion';
                span.className = 'ms-2';
                span.textContent = conectado ? '🟢 Conectado' : '🔴 Desconectado';
                navbar.appendChild(span);
            }
        }
    }
    
    // Recargar datos actuales
    function recargarDatosActuales() {
        console.log('Recargando datos...');
        
        // Recargar según la pestaña activa
        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab) {
            const tabId = activeTab.getAttribute('data-bs-target');
            
            switch(tabId) {
                case '#gases-biodigestores':
                    if (window.actualizarSistemaGasesCompleto) {
                        window.actualizarSistemaGasesCompleto();
                    }
                    break;
                case '#planificacion-diaria':
                    if (window.actualizarGeneracionActual) {
                        window.actualizarGeneracionActual();
                    }
                    if (window.actualizarSensoresCriticos) {
                        window.actualizarSensoresCriticos();
                    }
                    break;
                case '#registros-15min':
                    if (window.actualizarRegistros15min) {
                        window.actualizarRegistros15min();
                    }
                    break;
                // Agregar más casos según sea necesario
            }
        }
    }
    
    // Mostrar notificación
    function mostrarNotificacion(tipo, titulo, mensaje) {
        if (window.toastr) {
            toastr[tipo](mensaje, titulo, {
                timeOut: tipo === 'error' ? 0 : 5000,
                closeButton: true,
                progressBar: true
            });
        } else {
            // Fallback si toastr no está disponible
            console.log(`[${tipo.toUpperCase()}] ${titulo}: ${mensaje}`);
        }
    }
    
    // Agregar botón de reconexión manual
    function agregarBotonReconexion() {
        if (!document.getElementById('btn-reconectar-manual')) {
            const container = document.querySelector('.navbar');
            if (container) {
                const btn = document.createElement('button');
                btn.id = 'btn-reconectar-manual';
                btn.className = 'btn btn-warning btn-sm ms-2';
                btn.innerHTML = '<i class="fas fa-plug"></i> Reconectar';
                btn.onclick = () => {
                    retryCount = 0;
                    checkConnection();
                    btn.remove();
                };
                container.appendChild(btn);
            }
        }
    }
    
    // Inicializar el sistema
    function init() {
        console.log('🔌 Sistema de reconexión automática iniciado');
        
        // Verificar conexión inicial
        checkConnection();
        
        // Programar verificaciones periódicas
        if (checkTimer) clearInterval(checkTimer);
        checkTimer = setInterval(checkConnection, CONFIG.checkInterval);
        
        // Escuchar eventos de red
        window.addEventListener('online', () => {
            console.log('📡 Conexión a Internet restaurada');
            checkConnection();
        });
        
        window.addEventListener('offline', () => {
            console.log('📡 Sin conexión a Internet');
            onConnectionLost();
        });
        
        // Interceptar errores de fetch globalmente
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            return originalFetch.apply(this, args).catch(error => {
                // Si es un error de red, activar el sistema de reconexión
                if (error.name === 'NetworkError' || error.message.includes('Failed to fetch')) {
                    if (isConnected) {
                        onConnectionLost();
                    }
                }
                throw error;
            });
        };
    }
    
    // Exponer funciones útiles
    window.reconexionAutomatica = {
        checkConnection: checkConnection,
        isConnected: () => isConnected,
        forceReconnect: () => {
            retryCount = 0;
            checkConnection();
        }
    };
    
    // Iniciar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})(); 