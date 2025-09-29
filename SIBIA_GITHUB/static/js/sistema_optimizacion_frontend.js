/**
 * SISTEMA DE OPTIMIZACIÓN FRONTEND - SIBIA
 * Implementa las mejoras críticas de rendimiento
 */

class SistemaOptimizacionSIBIA {
    constructor() {
        this.cache = new Map();
        this.ttl = new Map();
        this.intervalosActivos = new Set();
        this.llamadasAPI = new Map();
        this.DEBUG = window.location.hostname === 'localhost';
        
        this.inicializar();
    }

    inicializar() {
        console.log('🚀 Iniciando sistema de optimización SIBIA...');
        
        // Interceptar fetch para implementar caché
        this.interceptarFetch();
        
        // Consolidar intervalos existentes
        this.consolidarIntervalos();
        
        // Implementar sistema de logging optimizado
        this.configurarLogging();
        
        console.log('✅ Sistema de optimización activado');
    }

    // Sistema de caché inteligente
    async get(endpoint, ttlSeconds = 30) {
        const now = Date.now();
        const cached = this.cache.get(endpoint);
        const expiry = this.ttl.get(endpoint);
        
        if (cached && expiry && now < expiry) {
            this.log(`📦 Cache hit: ${endpoint}`);
            return cached;
        }
        
        this.log(`🌐 Cache miss: ${endpoint}`);
        
        try {
            // Usar fetch original para evitar recursión infinita
            const response = await window.originalFetch(endpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Guardar en caché
            this.cache.set(endpoint, data);
            this.ttl.set(endpoint, now + (ttlSeconds * 1000));
            
            return data;
        } catch (error) {
            this.logError(`Error en ${endpoint}:`, error);
            throw error;
        }
    }

    // Interceptar llamadas fetch para aplicar caché automáticamente
    interceptarFetch() {
        const originalFetch = window.fetch;
        const self = this;
        
        // Guardar fetch original globalmente para evitar recursión
        window.originalFetch = originalFetch;
        
        window.fetch = function(url, options = {}) {
            // Solo aplicar caché a GET requests sin opciones especiales
            if (options.method === 'GET' || !options.method) {
                const endpoint = typeof url === 'string' ? url : url.toString();
                
                // Verificar si es un endpoint que debe ser cacheado
                if (self.debeCachear(endpoint)) {
                    return self.get(endpoint);
                }
            }
            
            return originalFetch.call(this, url, options);
        };
    }

    // Determinar qué endpoints deben ser cacheados
    debeCachear(endpoint) {
        const endpointsCacheables = [
            '/datos_kpi',
            '/registros_15min',
            '/obtener_materiales_base_json',
            '/parametros_globales',
            '/stock',
            '/historico_diario',
            '/plan_mensual',
            '/plan_semanal',
            '/gases_biodigestores',
            '/balance_volumetrico'
        ];
        
        return endpointsCacheables.some(ep => endpoint.includes(ep));
    }

    // Consolidar intervalos múltiples en uno solo
    consolidarIntervalos() {
        // Limpiar intervalos existentes
        this.intervalosActivos.forEach(id => clearInterval(id));
        this.intervalosActivos.clear();
        
        // Crear sistema unificado
        this.crearSistemaUnificado();
    }

    crearSistemaUnificado() {
        const contadores = {
            principal: 0,
            sensores: 0,
            presiones: 0,
            kpis: 0,
            registros: 0
        };
        
        const intervaloId = setInterval(() => {
            contadores.principal++;
            contadores.sensores++;
            contadores.presiones++;
            contadores.kpis++;
            contadores.registros++;
            
            // Actualizar sistema principal cada 5 segundos
            if (contadores.principal >= 1) {
                this.actualizarSistemaPrincipal();
                contadores.principal = 0;
            }
            
            // Actualizar sensores cada 10 segundos
            if (contadores.sensores >= 2) {
                this.actualizarSensores();
                contadores.sensores = 0;
            }
            
            // Actualizar presiones cada 10 segundos
            if (contadores.presiones >= 2) {
                this.actualizarPresiones();
                contadores.presiones = 0;
            }
            
            // Actualizar KPIs cada 15 segundos
            if (contadores.kpis >= 3) {
                this.actualizarKPIs();
                contadores.kpis = 0;
            }
            
            // Actualizar registros cada 20 segundos
            if (contadores.registros >= 4) {
                this.actualizarRegistros();
                contadores.registros = 0;
            }
            
        }, 5000);
        
        this.intervalosActivos.add(intervaloId);
        this.log('🔄 Sistema de intervalos unificado activado');
    }

    // Funciones de actualización optimizadas
    async actualizarSistemaPrincipal() {
        try {
            if (typeof window.actualizarTodosLosSistemas === 'function') {
                await window.actualizarTodosLosSistemas();
            }
        } catch (error) {
            this.logError('Error actualizando sistema principal:', error);
        }
    }

    async actualizarSensores() {
        try {
            if (typeof window.actualizarGasesBiodigestores === 'function') {
                await window.actualizarGasesBiodigestores();
            }
            if (typeof window.actualizarSistemaVolumetrico === 'function') {
                await window.actualizarSistemaVolumetrico();
            }
        } catch (error) {
            this.logError('Error actualizando sensores:', error);
        }
    }

    async actualizarPresiones() {
        try {
            if (typeof window.actualizarPresionesEstabilizadas === 'function') {
                await window.actualizarPresionesEstabilizadas();
            }
        } catch (error) {
            this.logError('Error actualizando presiones:', error);
        }
    }

    async actualizarKPIs() {
        try {
            if (typeof window.actualizarKPIsCorregido === 'function') {
                await window.actualizarKPIsCorregido();
            }
        } catch (error) {
            this.logError('Error actualizando KPIs:', error);
        }
    }

    async actualizarRegistros() {
        try {
            if (typeof window.actualizarRegistros15minCorregido === 'function') {
                await window.actualizarRegistros15minCorregido();
            }
        } catch (error) {
            this.logError('Error actualizando registros:', error);
        }
    }

    // Sistema de logging optimizado
    configurarLogging() {
        // Reemplazar console.log con sistema optimizado
        window.log = this.log.bind(this);
        window.logError = this.logError.bind(this);
    }

    log(message, ...args) {
        if (this.DEBUG) {
            console.log(`[SIBIA-OPT] ${message}`, ...args);
        }
    }

    logError(message, ...args) {
        console.error(`[SIBIA-OPT] ${message}`, ...args);
    }

    // Función de debouncing
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Optimizar actualizaciones de DOM
    actualizarDOMPorLotes(updates) {
        requestAnimationFrame(() => {
            updates.forEach(({ id, valor, tipo = 'textContent' }) => {
                const elemento = document.getElementById(id);
                if (elemento) {
                    elemento[tipo] = valor;
                }
            });
        });
    }

    // Limpiar caché
    limpiarCache() {
        this.cache.clear();
        this.ttl.clear();
        this.log('🧹 Cache limpiado');
    }

    // Obtener estadísticas de rendimiento
    obtenerEstadisticas() {
        return {
            cacheSize: this.cache.size,
            intervalosActivos: this.intervalosActivos.size,
            llamadasAPI: this.llamadasAPI.size,
            memoria: performance.memory ? {
                usado: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limite: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            } : null
        };
    }

    // Destruir sistema
    destruir() {
        this.intervalosActivos.forEach(id => clearInterval(id));
        this.intervalosActivos.clear();
        this.limpiarCache();
        this.log('🛑 Sistema de optimización destruido');
    }
}

// Función para aplicar optimizaciones a funciones existentes
function optimizarFuncionExistente(nombreFuncion, nuevaFuncion) {
    if (typeof window[nombreFuncion] === 'function') {
        const funcionOriginal = window[nombreFuncion];
        window[nombreFuncion] = nuevaFuncion;
        return funcionOriginal;
    }
    return null;
}

// Función para crear versiones optimizadas de funciones comunes
function crearFuncionesOptimizadas() {
    // Optimizar actualizarKPIsCorregido
    if (typeof window.actualizarKPIsCorregido === 'function') {
        const original = window.actualizarKPIsCorregido;
        window.actualizarKPIsCorregido = window.sistemaOptimizacion.debounce(original, 500);
    }

    // Optimizar actualizarRegistros15minCorregido
    if (typeof window.actualizarRegistros15minCorregido === 'function') {
        const original = window.actualizarRegistros15minCorregido;
        window.actualizarRegistros15minCorregido = window.sistemaOptimizacion.debounce(original, 500);
    }
}

// Inicializar sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Crear instancia global del sistema de optimización
    window.sistemaOptimizacion = new SistemaOptimizacionSIBIA();
    
    // Aplicar optimizaciones a funciones existentes
    setTimeout(crearFuncionesOptimizadas, 1000);
    
    // Mostrar estadísticas cada 30 segundos en modo debug
    if (window.sistemaOptimizacion.DEBUG) {
        setInterval(() => {
            const stats = window.sistemaOptimizacion.obtenerEstadisticas();
            console.log('📊 Estadísticas SIBIA:', stats);
        }, 30000);
    }
});

// Exportar para uso global
window.SistemaOptimizacionSIBIA = SistemaOptimizacionSIBIA;

console.log('🔧 Sistema de optimización frontend SIBIA cargado');
