/**
 * OPTIMIZACIONES ESPECÍFICAS PARA ASISTENTE Y CALCULADORA SIBIA
 * Mejoras de rendimiento específicas para estas funciones críticas
 */

class OptimizacionesEspecificasSIBIA {
    constructor() {
        this.cacheAsistente = new Map();
        this.cacheCalculadora = new Map();
        this.debounceTimers = new Map();
        this.workerCalculos = null;
        
        this.inicializar();
    }

    inicializar() {
        console.log('🚀 Inicializando optimizaciones específicas...');
        
        // Optimizar asistente
        this.optimizarAsistente();
        
        // Optimizar calculadora
        this.optimizarCalculadora();
        
        // Crear Web Worker para cálculos pesados
        this.crearWebWorker();
        
        console.log('✅ Optimizaciones específicas activadas');
    }

    optimizarAsistente() {
        // Interceptar llamadas del asistente para aplicar caché
        this.interceptarAsistente();
        
        // Optimizar síntesis de voz
        this.optimizarSintesisVoz();
        
        // Implementar debouncing para reconocimiento de voz
        this.optimizarReconocimientoVoz();
    }

    interceptarAsistente() {
        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = function(url, options) {
            // Solo interceptar llamadas del asistente
            if (url.includes('/asistente') || url.includes('/chat')) {
                const cacheKey = `${url}_${JSON.stringify(options)}`;
                
                // Verificar caché
                if (self.cacheAsistente.has(cacheKey)) {
                    const cached = self.cacheAsistente.get(cacheKey);
                    if (Date.now() - cached.timestamp < 30000) { // 30 segundos TTL
                        console.log('📦 Respuesta del asistente desde caché');
                        return Promise.resolve(new Response(JSON.stringify(cached.data)));
                    }
                }
                
                // Hacer la llamada real
                return originalFetch.call(this, url, options)
                    .then(response => response.clone())
                    .then(response => response.json())
                    .then(data => {
                        // Guardar en caché
                        self.cacheAsistente.set(cacheKey, {
                            data: data,
                            timestamp: Date.now()
                        });
                        
                        // Limitar tamaño del caché
                        if (self.cacheAsistente.size > 50) {
                            const firstKey = self.cacheAsistente.keys().next().value;
                            self.cacheAsistente.delete(firstKey);
                        }
                        
                        return new Response(JSON.stringify(data));
                    });
            }
            
            return originalFetch.call(this, url, options);
        };
    }

    optimizarSintesisVoz() {
        if (!window.speechSynthesis) return;
        
        // Crear pool de voces para evitar recreación
        this.poolVoces = new Map();
        
        // Pre-cargar voces disponibles
        const voces = window.speechSynthesis.getVoices();
        voces.forEach(voz => {
            if (voz.lang.startsWith('es')) {
                this.poolVoces.set(voz.name, voz);
            }
        });
        
        // Interceptar SpeechSynthesisUtterance
        const originalUtterance = window.SpeechSynthesisUtterance;
        const self = this;
        
        window.SpeechSynthesisUtterance = function(text) {
            const utterance = new originalUtterance(text);
            
            // Optimizar configuración
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            
            // Usar voz pre-cargada
            if (self.poolVoces.size > 0) {
                const vozEspañol = Array.from(self.poolVoces.values())[0];
                utterance.voice = vozEspañol;
            }
            
            return utterance;
        };
    }

    optimizarReconocimientoVoz() {
        if (!window.SpeechRecognition && !window.webkitSpeechRecognition) return;
        
        // Implementar debouncing para reconocimiento
        const debounceDelay = 500;
        
        const originalStart = window.SpeechRecognition.prototype.start;
        const self = this;
        
        window.SpeechRecognition.prototype.start = function() {
            const recognition = this;
            const timerKey = 'recognition_' + Date.now();
            
            // Cancelar timer anterior si existe
            if (self.debounceTimers.has('recognition')) {
                clearTimeout(self.debounceTimers.get('recognition'));
            }
            
            // Implementar debouncing
            self.debounceTimers.set('recognition', setTimeout(() => {
                originalStart.call(recognition);
            }, debounceDelay));
        };
    }

    optimizarCalculadora() {
        // Interceptar carga de materiales
        this.interceptarCargaMateriales();
        
        // Optimizar cálculos matemáticos
        this.optimizarCalculosMatematicos();
        
        // Optimizar renderizado de gráficos
        this.optimizarGraficos();
    }

    interceptarCargaMateriales() {
        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = function(url, options) {
            if (url.includes('/obtener_materiales_base_json')) {
                const cacheKey = 'materiales_base';
                
                // Verificar caché
                if (self.cacheCalculadora.has(cacheKey)) {
                    const cached = self.cacheCalculadora.get(cacheKey);
                    if (Date.now() - cached.timestamp < 300000) { // 5 minutos TTL
                        console.log('📦 Materiales base desde caché');
                        return Promise.resolve(new Response(JSON.stringify(cached.data)));
                    }
                }
                
                // Hacer la llamada real
                return originalFetch.call(this, url, options)
                    .then(response => response.clone())
                    .then(response => response.json())
                    .then(data => {
                        // Guardar en caché
                        self.cacheCalculadora.set(cacheKey, {
                            data: data,
                            timestamp: Date.now()
                        });
                        
                        return new Response(JSON.stringify(data));
                    });
            }
            
            return originalFetch.call(this, url, options);
        };
    }

    optimizarCalculosMatematicos() {
        // Crear funciones optimizadas para cálculos frecuentes
        this.funcionesCalculo = {
            // Cálculo optimizado de KW/TN
            calcularKwTn: (materialesSolidos, materialesLiquidos, porcentajePurin) => {
                // Usar operaciones bitwise para cálculos simples
                const factorSolidos = materialesSolidos * 0.8;
                const factorLiquidos = materialesLiquidos * 0.6;
                const factorPurin = porcentajePurin * 0.01;
                
                return (factorSolidos + factorLiquidos) * factorPurin;
            },
            
            // Cálculo optimizado de eficiencia
            calcularEficiencia: (kwGenerados, kwObjetivo) => {
                if (kwObjetivo === 0) return 0;
                return Math.min((kwGenerados / kwObjetivo) * 100, 100);
            },
            
            // Cálculo optimizado de mezcla
            calcularMezcla: (datos) => {
                const { materialesSolidos, materialesLiquidos, porcentajePurin } = datos;
                
                // Usar Web Worker si está disponible
                if (self.workerCalculos) {
                    return new Promise((resolve) => {
                        self.workerCalculos.postMessage({
                            tipo: 'calcularMezcla',
                            datos: datos
                        });
                        
                        self.workerCalculos.onmessage = (e) => {
                            resolve(e.data);
                        };
                    });
                }
                
                // Cálculo directo optimizado
                const kwEstimado = self.funcionesCalculo.calcularKwTn(materialesSolidos, materialesLiquidos, porcentajePurin);
                const eficiencia = self.funcionesCalculo.calcularEficiencia(kwEstimado, datos.objetivoKw || 100);
                
                return {
                    kwEstimado,
                    eficiencia,
                    materialesSolidos,
                    materialesLiquidos,
                    porcentajePurin
                };
            }
        };
        
        // Hacer funciones disponibles globalmente
        window.calcularKwTnOptimizado = this.funcionesCalculo.calcularKwTn;
        window.calcularEficienciaOptimizada = this.funcionesCalculo.calcularEficiencia;
        window.calcularMezclaOptimizada = this.funcionesCalculo.calcularMezcla;
    }

    optimizarGraficos() {
        // Optimizar Chart.js
        if (window.Chart) {
            // Configuración optimizada para Chart.js
            Chart.defaults.animation = {
                duration: 200, // Reducir tiempo de animación
                easing: 'easeOutQuart'
            };
            
            Chart.defaults.responsive = true;
            Chart.defaults.maintainAspectRatio = false;
            
            // Interceptar creación de gráficos
            const originalChart = window.Chart;
            const self = this;
            
            window.Chart = function(ctx, config) {
                // Optimizar configuración
                if (config.options && config.options.animation) {
                    config.options.animation.duration = 200;
                }
                
                // Usar requestAnimationFrame para actualizaciones
                const chart = new originalChart(ctx, config);
                
                const originalUpdate = chart.update;
                chart.update = function(mode, animation) {
                    requestAnimationFrame(() => {
                        originalUpdate.call(this, mode, animation);
                    });
                };
                
                return chart;
            };
        }
    }

    crearWebWorker() {
        // Crear Web Worker para cálculos pesados
        const workerCode = `
            self.onmessage = function(e) {
                const { tipo, datos } = e.data;
                
                switch (tipo) {
                    case 'calcularMezcla':
                        const resultado = calcularMezclaWorker(datos);
                        self.postMessage(resultado);
                        break;
                }
            };
            
            function calcularMezclaWorker(datos) {
                const { materialesSolidos, materialesLiquidos, porcentajePurin, objetivoKw } = datos;
                
                // Cálculos intensivos en el worker
                let kwEstimado = 0;
                for (let i = 0; i < 1000; i++) {
                    kwEstimado += (materialesSolidos * 0.8 + materialesLiquidos * 0.6) * (porcentajePurin * 0.01);
                }
                kwEstimado /= 1000;
                
                const eficiencia = Math.min((kwEstimado / objetivoKw) * 100, 100);
                
                return {
                    kwEstimado,
                    eficiencia,
                    materialesSolidos,
                    materialesLiquidos,
                    porcentajePurin,
                    calculadoEnWorker: true
                };
            }
        `;
        
        try {
            const blob = new Blob([workerCode], { type: 'application/javascript' });
            this.workerCalculos = new Worker(URL.createObjectURL(blob));
            console.log('✅ Web Worker para cálculos creado');
        } catch (error) {
            console.log('⚠️ Web Worker no disponible:', error);
        }
    }

    // Función para limpiar cachés
    limpiarCaches() {
        this.cacheAsistente.clear();
        this.cacheCalculadora.clear();
        console.log('🧹 Cachés específicos limpiados');
    }

    // Función para obtener estadísticas
    obtenerEstadisticasEspecificas() {
        return {
            asistente: {
                cacheSize: this.cacheAsistente.size,
                poolVoces: this.poolVoces ? this.poolVoces.size : 0
            },
            calculadora: {
                cacheSize: this.cacheCalculadora.size,
                workerDisponible: !!this.workerCalculos
            },
            debounceTimers: this.debounceTimers.size
        };
    }
}

// Función para aplicar optimizaciones específicas
function aplicarOptimizacionesEspecificas() {
    if (!window.optimizacionesEspecificas) {
        window.optimizacionesEspecificas = new OptimizacionesEspecificasSIBIA();
    }
    return window.optimizacionesEspecificas;
}

// Auto-aplicar optimizaciones
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(aplicarOptimizacionesEspecificas, 1000);
});

// Exportar para uso global
window.aplicarOptimizacionesEspecificas = aplicarOptimizacionesEspecificas;

console.log('🔧 Optimizaciones específicas para asistente y calculadora cargadas');
