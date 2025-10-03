/**
 * OPTIMIZACIONES AGRESIVAS PARA PROBLEMAS REALES - SIBIA
 * Soluciona específicamente los problemas de "redondel calculando" y "asistente colgado"
 */

class OptimizacionesAgressivasSIBIA {
    constructor() {
        this.timeoutsCalculadora = new Map();
        this.timeoutsAsistente = new Map();
        this.cacheCalculadora = new Map();
        this.cacheAsistente = new Map();
        this.estadoCalculadora = 'libre';
        this.estadoAsistente = 'libre';
        
        this.inicializar();
    }

    inicializar() {
        console.log('🚀 Inicializando optimizaciones agresivas...');
        
        // Interceptar funciones críticas
        this.interceptarCalculadora();
        this.interceptarAsistente();
        
        // Implementar sistema de timeout agresivo
        this.implementarTimeoutsAgresivos();
        
        // Pre-cargar recursos críticos
        this.preCargarRecursosCriticos();
        
        console.log('✅ Optimizaciones agresivas activadas');
    }

    interceptarCalculadora() {
        // Interceptar la función calcularMezcla del dashboard híbrido
        const self = this;
        
        // Guardar función original si existe
        if (typeof window.calcularMezcla === 'function') {
            window.calcularMezclaOriginal = window.calcularMezcla;
        }
        
        // Reemplazar con versión optimizada
        window.calcularMezcla = async function() {
            return await self.calcularMezclaOptimizada();
        };
        
        // Interceptar también la función de cálculo automático
        if (typeof window.calcularMezclaAutomatica === 'function') {
            window.calcularMezclaAutomaticaOriginal = window.calcularMezclaAutomatica;
            window.calcularMezclaAutomatica = async function() {
                return await self.calcularMezclaAutomaticaOptimizada();
            };
        }
    }

    interceptarAsistente() {
        // Interceptar funciones del asistente
        const self = this;
        
        // Interceptar envío de mensajes
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (url.includes('/asistente') || url.includes('/chat')) {
                return self.procesarMensajeAsistente(url, options, originalFetch);
            }
            return originalFetch.call(this, url, options);
        };
    }

    async calcularMezclaOptimizada() {
        // Verificar si ya hay un cálculo en progreso
        if (this.estadoCalculadora !== 'libre') {
            console.log('⚠️ Cálculo ya en progreso, cancelando...');
            return;
        }
        
        this.estadoCalculadora = 'calculando';
        
        try {
            // Obtener datos del formulario
            const datos = this.obtenerDatosCalculadora();
            
            // Verificar caché primero
            const cacheKey = this.generarClaveCacheCalculadora(datos);
            if (this.cacheCalculadora.has(cacheKey)) {
                const cached = this.cacheCalculadora.get(cacheKey);
                if (Date.now() - cached.timestamp < 60000) { // 1 minuto TTL
                    console.log('📦 Usando resultado desde caché');
                    this.mostrarResultadoCalculadora(cached.resultado);
                    this.estadoCalculadora = 'libre';
                    return;
                }
            }
            
            // Mostrar spinner optimizado
            this.mostrarSpinnerCalculadora();
            
            // Configurar timeout agresivo
            const timeoutId = setTimeout(() => {
                console.log('⏰ Timeout calculadora - cancelando cálculo');
                this.cancelarCalculoCalculadora();
            }, 5000); // 5 segundos máximo
            
            this.timeoutsCalculadora.set('actual', timeoutId);
            
            // Hacer la llamada con timeout más corto
            const controller = new AbortController();
            const timeoutSignal = setTimeout(() => controller.abort(), 3000); // 3 segundos
            
            const response = await fetch('/calcular_mezcla', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos),
                signal: controller.signal
            });
            
            clearTimeout(timeoutSignal);
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const resultado = await response.json();
                
                // Guardar en caché
                this.cacheCalculadora.set(cacheKey, {
                    resultado: resultado,
                    timestamp: Date.now()
                });
                
                // Limitar tamaño del caché
                if (this.cacheCalculadora.size > 20) {
                    const firstKey = this.cacheCalculadora.keys().next().value;
                    this.cacheCalculadora.delete(firstKey);
                }
                
                this.mostrarResultadoCalculadora(resultado);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Error en cálculo optimizado:', error);
            this.mostrarErrorCalculadora(error.message);
        } finally {
            this.estadoCalculadora = 'libre';
            this.timeoutsCalculadora.delete('actual');
        }
    }

    async calcularMezclaAutomaticaOptimizada() {
        // Similar a calcularMezclaOptimizada pero para cálculo automático
        if (this.estadoCalculadora !== 'libre') {
            console.log('⚠️ Cálculo automático ya en progreso');
            return;
        }
        
        this.estadoCalculadora = 'calculando';
        
        try {
            const datos = this.obtenerDatosCalculadoraAutomatica();
            const cacheKey = this.generarClaveCacheCalculadora(datos);
            
            if (this.cacheCalculadora.has(cacheKey)) {
                const cached = this.cacheCalculadora.get(cacheKey);
                if (Date.now() - cached.timestamp < 30000) { // 30 segundos TTL
                    this.mostrarResultadoCalculadora(cached.resultado);
                    this.estadoCalculadora = 'libre';
                    return;
                }
            }
            
            this.mostrarSpinnerCalculadora();
            
            const timeoutId = setTimeout(() => {
                this.cancelarCalculoCalculadora();
            }, 4000);
            
            this.timeoutsCalculadora.set('automatico', timeoutId);
            
            const controller = new AbortController();
            setTimeout(() => controller.abort(), 2500);
            
            const response = await fetch('/calcular_mezcla', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const resultado = await response.json();
                this.cacheCalculadora.set(cacheKey, {
                    resultado: resultado,
                    timestamp: Date.now()
                });
                this.mostrarResultadoCalculadora(resultado);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Error en cálculo automático:', error);
            this.mostrarErrorCalculadora(error.message);
        } finally {
            this.estadoCalculadora = 'libre';
            this.timeoutsCalculadora.delete('automatico');
        }
    }

    async procesarMensajeAsistente(url, options, originalFetch) {
        if (this.estadoAsistente !== 'libre') {
            console.log('⚠️ Asistente ocupado, cancelando mensaje');
            return Promise.reject(new Error('Asistente ocupado'));
        }
        
        this.estadoAsistente = 'procesando';
        
        try {
            const datos = JSON.parse(options.body);
            const cacheKey = `asistente_${datos.pregunta}`;
            
            // Verificar caché
            if (this.cacheAsistente.has(cacheKey)) {
                const cached = this.cacheAsistente.get(cacheKey);
                if (Date.now() - cached.timestamp < 300000) { // 5 minutos TTL
                    console.log('📦 Respuesta del asistente desde caché');
                    this.estadoAsistente = 'libre';
                    return new Response(JSON.stringify(cached.resultado));
                }
            }
            
            // Configurar timeout agresivo
            const timeoutId = setTimeout(() => {
                console.log('⏰ Timeout asistente - cancelando');
                this.cancelarProcesamientoAsistente();
            }, 8000); // 8 segundos máximo
            
            this.timeoutsAsistente.set('actual', timeoutId);
            
            const controller = new AbortController();
            setTimeout(() => controller.abort(), 6000); // 6 segundos
            
            const response = await originalFetch.call(this, url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const resultado = await response.json();
                
                // Guardar en caché
                this.cacheAsistente.set(cacheKey, {
                    resultado: resultado,
                    timestamp: Date.now()
                });
                
                // Limitar tamaño del caché
                if (this.cacheAsistente.size > 50) {
                    const firstKey = this.cacheAsistente.keys().next().value;
                    this.cacheAsistente.delete(firstKey);
                }
                
                this.estadoAsistente = 'libre';
                return response;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Error en asistente optimizado:', error);
            this.estadoAsistente = 'libre';
            this.timeoutsAsistente.delete('actual');
            throw error;
        }
    }

    obtenerDatosCalculadora() {
        // Obtener modo de cálculo
        const modoEnergetico = document.getElementById('adan-modo-energetico')?.checked;
        const modoCalculo = modoEnergetico ? 'energetico' : 'volumetrico';
        
        // Obtener modelos ML seleccionados
        const modelosSeleccionados = [];
        if (document.getElementById('adan-ml-xgboost')?.checked) modelosSeleccionados.push('xgboost');
        if (document.getElementById('adan-ml-redes')?.checked) modelosSeleccionados.push('redes_neuronales');
        if (document.getElementById('adan-ml-random')?.checked) modelosSeleccionados.push('random_forest');
        if (document.getElementById('adan-ml-bayesiana')?.checked) modelosSeleccionados.push('optimizacion_bayesiana');
        if (document.getElementById('adan-ml-genetico')?.checked) modelosSeleccionados.push('algoritmo_genetico');
        if (document.getElementById('adan-ml-cain')?.checked) modelosSeleccionados.push('cain');
        
        return {
            kw_objetivo: parseFloat(document.getElementById('adan-kw-objetivo')?.value || 28800),
            porcentaje_solidos: parseFloat(document.getElementById('adan-pct-solidos-kw')?.value || 60),
            porcentaje_liquidos: parseFloat(document.getElementById('adan-pct-liquidos-kw')?.value || 30),
            porcentaje_purin: parseFloat(document.getElementById('adan-pct-purin-kw')?.value || 10),
            objetivo_metano: parseFloat(document.getElementById('adan-metano-objetivo')?.value || 65),
            cantidad_materiales: document.getElementById('adan-num-materiales')?.value || '5',
            modo_calculo: modoCalculo,
            incluir_purin: document.getElementById('adan-incluir-purin')?.checked || true,
            modelos_seleccionados: modelosSeleccionados.length > 0 ? modelosSeleccionados : ['xgboost']
        };
    }

    obtenerDatosCalculadoraAutomatica() {
        return {
            solidos: parseFloat(document.getElementById('materiales-solidos')?.value || 0),
            liquidos: parseFloat(document.getElementById('materiales-liquidos')?.value || 0)
        };
    }

    generarClaveCacheCalculadora(datos) {
        return `calc_${JSON.stringify(datos)}`;
    }

    mostrarSpinnerCalculadora() {
        const resultado = document.getElementById('adan-resultado-calc');
        if (resultado) {
            resultado.style.display = 'block';
            resultado.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Calculando...</span>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">Calculando mezcla...</small>
                        <div class="progress mt-1" style="height: 3px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 style="width: 100%"></div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    mostrarResultadoCalculadora(resultado) {
        const resultadoElement = document.getElementById('adan-resultado-calc');
        if (resultadoElement && resultado.datos) {
            // Usar la función original para mostrar el resultado
            if (typeof window.mostrarResultadoCalculadoraOriginal === 'function') {
                window.mostrarResultadoCalculadoraOriginal(resultado);
            } else {
                resultadoElement.innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Cálculo Completado</h6>
                        <p>KW Objetivo: ${resultado.datos.totales?.kw_total_generado || 'N/A'}</p>
                        <p>Materiales Sólidos: ${resultado.datos.totales?.tn_solidos || 'N/A'} TN</p>
                        <p>Materiales Líquidos: ${resultado.datos.totales?.tn_liquidos || 'N/A'} TN</p>
                    </div>
                `;
            }
        }
    }

    mostrarErrorCalculadora(mensaje) {
        const resultado = document.getElementById('adan-resultado-calc');
        if (resultado) {
            resultado.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Error en el Cálculo</h6>
                    <p><strong>Error:</strong> ${mensaje}</p>
                    <small class="text-muted">Intenta nuevamente o verifica los datos ingresados.</small>
                </div>
            `;
        }
    }

    cancelarCalculoCalculadora() {
        console.log('🛑 Cancelando cálculo de calculadora');
        this.estadoCalculadora = 'libre';
        
        const resultado = document.getElementById('adan-resultado-calc');
        if (resultado) {
            resultado.innerHTML = `
                <div class="alert alert-warning">
                    <h6>⏰ Cálculo Cancelado</h6>
                    <p>El cálculo tardó demasiado tiempo. Intenta con datos más simples.</p>
                    <button class="btn btn-sm btn-primary" onclick="window.calcularMezcla()">
                        Reintentar
                    </button>
                </div>
            `;
        }
        
        // Limpiar timeouts
        this.timeoutsCalculadora.forEach(timeout => clearTimeout(timeout));
        this.timeoutsCalculadora.clear();
    }

    cancelarProcesamientoAsistente() {
        console.log('🛑 Cancelando procesamiento del asistente');
        this.estadoAsistente = 'libre';
        
        // Limpiar timeouts
        this.timeoutsAsistente.forEach(timeout => clearTimeout(timeout));
        this.timeoutsAsistente.clear();
    }

    implementarTimeoutsAgresivos() {
        // Timeout global para prevenir colgadas
        setInterval(() => {
            // Verificar calculadora
            if (this.estadoCalculadora === 'calculando') {
                const tiempoInicio = this.timeoutsCalculadora.get('tiempo_inicio');
                if (tiempoInicio && Date.now() - tiempoInicio > 10000) { // 10 segundos
                    console.log('🛑 Forzando cancelación de calculadora');
                    this.cancelarCalculoCalculadora();
                }
            }
            
            // Verificar asistente
            if (this.estadoAsistente === 'procesando') {
                const tiempoInicio = this.timeoutsAsistente.get('tiempo_inicio');
                if (tiempoInicio && Date.now() - tiempoInicio > 15000) { // 15 segundos
                    console.log('🛑 Forzando cancelación de asistente');
                    this.cancelarProcesamientoAsistente();
                }
            }
        }, 1000);
    }

    async preCargarRecursosCriticos() {
        console.log('📦 Pre-cargando recursos críticos...');
        
        try {
            // Pre-cargar materiales base
            const response = await fetch('/obtener_materiales_base_json');
            if (response.ok) {
                const materiales = await response.json();
                this.cacheCalculadora.set('materiales_base', {
                    resultado: materiales,
                    timestamp: Date.now()
                });
                console.log('✅ Materiales base pre-cargados');
            }
        } catch (error) {
            console.log('⚠️ Error pre-cargando materiales:', error);
        }
        
        try {
            // Pre-cargar configuración
            const response = await fetch('/parametros_globales');
            if (response.ok) {
                const config = await response.json();
                this.cacheCalculadora.set('configuracion', {
                    resultado: config,
                    timestamp: Date.now()
                });
                console.log('✅ Configuración pre-cargada');
            }
        } catch (error) {
            console.log('⚠️ Error pre-cargando configuración:', error);
        }
    }

    // Función para limpiar cachés
    limpiarCaches() {
        this.cacheCalculadora.clear();
        this.cacheAsistente.clear();
        console.log('🧹 Cachés agresivos limpiados');
    }

    // Función para obtener estadísticas
    obtenerEstadisticas() {
        return {
            calculadora: {
                estado: this.estadoCalculadora,
                cacheSize: this.cacheCalculadora.size,
                timeoutsActivos: this.timeoutsCalculadora.size
            },
            asistente: {
                estado: this.estadoAsistente,
                cacheSize: this.cacheAsistente.size,
                timeoutsActivos: this.timeoutsAsistente.size
            }
        };
    }
}

// Función para aplicar optimizaciones agresivas
function aplicarOptimizacionesAgressivas() {
    if (!window.optimizacionesAgressivas) {
        window.optimizacionesAgressivas = new OptimizacionesAgressivasSIBIA();
    }
    return window.optimizacionesAgressivas;
}

// Auto-aplicar optimizaciones
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(aplicarOptimizacionesAgressivas, 500);
});

// Exportar para uso global
window.aplicarOptimizacionesAgressivas = aplicarOptimizacionesAgressivas;

console.log('🔧 Optimizaciones agresivas para problemas reales cargadas');
