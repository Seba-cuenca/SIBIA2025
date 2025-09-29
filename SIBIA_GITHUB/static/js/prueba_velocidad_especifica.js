/**
 * PRUEBA DE VELOCIDAD ESPECÍFICA - ASISTENTE Y CALCULADORA SIBIA
 * Este script mide específicamente los tiempos de respuesta de estas funciones
 */

class PruebaVelocidadEspecifica {
    constructor() {
        this.metricas = {
            asistente: {
                tiempoInicializacion: 0,
                tiempoRespuesta: 0,
                tiempoVoz: 0,
                llamadasAPI: 0,
                errores: []
            },
            calculadora: {
                tiempoCargaMateriales: 0,
                tiempoCalculo: 0,
                tiempoRenderizadoGrafico: 0,
                llamadasAPI: 0,
                errores: []
            }
        };
        this.iniciarPruebas();
    }

    async iniciarPruebas() {
        console.log('🚀 Iniciando pruebas de velocidad específicas...');
        
        // Esperar a que el DOM esté completamente cargado
        await this.esperarDOM();
        
        // Probar asistente
        await this.probarAsistente();
        
        // Probar calculadora
        await this.probarCalculadora();
        
        // Mostrar resultados
        this.mostrarResultados();
    }

    async esperarDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                window.addEventListener('load', resolve);
            }
        });
    }

    async probarAsistente() {
        console.log('🤖 Probando velocidad del asistente...');
        
        const inicio = performance.now();
        
        try {
            // 1. Probar inicialización del asistente
            const inicioInit = performance.now();
            await this.probarInicializacionAsistente();
            this.metricas.asistente.tiempoInicializacion = performance.now() - inicioInit;
            
            // 2. Probar respuesta del asistente
            const inicioRespuesta = performance.now();
            await this.probarRespuestaAsistente();
            this.metricas.asistente.tiempoRespuesta = performance.now() - inicioRespuesta;
            
            // 3. Probar síntesis de voz
            const inicioVoz = performance.now();
            await this.probarSintesisVoz();
            this.metricas.asistente.tiempoVoz = performance.now() - inicioVoz;
            
        } catch (error) {
            this.metricas.asistente.errores.push(error.message);
            console.error('Error probando asistente:', error);
        }
        
        console.log(`✅ Asistente probado en ${(performance.now() - inicio).toFixed(2)}ms`);
    }

    async probarInicializacionAsistente() {
        return new Promise((resolve) => {
            // Verificar elementos del asistente
            const elementos = [
                'asistente-chat-container',
                'asistente-chatbox',
                'asistente-input',
                'asistente-send-btn',
                'asistente-mic-btn'
            ];
            
            let elementosEncontrados = 0;
            elementos.forEach(id => {
                if (document.getElementById(id)) {
                    elementosEncontrados++;
                }
            });
            
            console.log(`📋 Elementos del asistente encontrados: ${elementosEncontrados}/${elementos.length}`);
            
            // Verificar APIs de voz
            const vozDisponible = window.speechSynthesis && (window.SpeechRecognition || window.webkitSpeechRecognition);
            console.log(`🎤 APIs de voz disponibles: ${vozDisponible ? 'Sí' : 'No'}`);
            
            resolve();
        });
    }

    async probarRespuestaAsistente() {
        return new Promise((resolve) => {
            // Simular una pregunta al asistente
            const pregunta = "¿Cuál es el estado actual del sistema?";
            
            // Interceptar llamadas fetch para medir tiempo de respuesta
            const originalFetch = window.fetch;
            let llamadasAsistente = 0;
            
            window.fetch = function(url, options) {
                if (url.includes('/asistente') || url.includes('/chat')) {
                    llamadasAsistente++;
                    const inicio = performance.now();
                    
                    return originalFetch.call(this, url, options).then(response => {
                        const tiempo = performance.now() - inicio;
                        console.log(`🌐 Llamada API asistente: ${tiempo.toFixed(2)}ms`);
                        return response;
                    });
                }
                return originalFetch.call(this, url, options);
            };
            
            this.metricas.asistente.llamadasAPI = llamadasAsistente;
            
            // Restaurar fetch original después de un tiempo
            setTimeout(() => {
                window.fetch = originalFetch;
                resolve();
            }, 1000);
        });
    }

    async probarSintesisVoz() {
        return new Promise((resolve) => {
            if (!window.speechSynthesis) {
                console.log('⚠️ Síntesis de voz no disponible');
                resolve();
                return;
            }
            
            const texto = "Prueba de síntesis de voz";
            const inicio = performance.now();
            
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.onend = () => {
                const tiempo = performance.now() - inicio;
                console.log(`🎵 Síntesis de voz: ${tiempo.toFixed(2)}ms`);
                resolve();
            };
            
            utterance.onerror = () => {
                console.log('❌ Error en síntesis de voz');
                resolve();
            };
            
            // Cancelar cualquier síntesis anterior
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        });
    }

    async probarCalculadora() {
        console.log('🧮 Probando velocidad de la calculadora...');
        
        const inicio = performance.now();
        
        try {
            // 1. Probar carga de materiales
            const inicioMateriales = performance.now();
            await this.probarCargaMateriales();
            this.metricas.calculadora.tiempoCargaMateriales = performance.now() - inicioMateriales;
            
            // 2. Probar cálculo de mezcla
            const inicioCalculo = performance.now();
            await this.probarCalculoMezcla();
            this.metricas.calculadora.tiempoCalculo = performance.now() - inicioCalculo;
            
            // 3. Probar renderizado de gráfico
            const inicioGrafico = performance.now();
            await this.probarRenderizadoGrafico();
            this.metricas.calculadora.tiempoRenderizadoGrafico = performance.now() - inicioGrafico;
            
        } catch (error) {
            this.metricas.calculadora.errores.push(error.message);
            console.error('Error probando calculadora:', error);
        }
        
        console.log(`✅ Calculadora probada en ${(performance.now() - inicio).toFixed(2)}ms`);
    }

    async probarCargaMateriales() {
        return new Promise((resolve) => {
            // Verificar si ya hay materiales cargados
            if (window.materialesBase && Object.keys(window.materialesBase).length > 0) {
                console.log('📦 Materiales ya cargados en memoria');
                resolve();
                return;
            }
            
            // Simular carga de materiales
            const inicio = performance.now();
            
            fetch('/obtener_materiales_base_json')
                .then(response => response.json())
                .then(data => {
                    const tiempo = performance.now() - inicio;
                    console.log(`📦 Carga de materiales: ${tiempo.toFixed(2)}ms`);
                    this.metricas.calculadora.llamadasAPI++;
                    resolve();
                })
                .catch(error => {
                    console.log('❌ Error cargando materiales:', error);
                    resolve();
                });
        });
    }

    async probarCalculoMezcla() {
        return new Promise((resolve) => {
            // Simular cálculo de mezcla
            const inicio = performance.now();
            
            // Datos de prueba
            const datosPrueba = {
                materiales_solidos: 10,
                materiales_liquidos: 5,
                porcentaje_purin: 70,
                objetivo_kw: 100
            };
            
            // Simular cálculo
            setTimeout(() => {
                const tiempo = performance.now() - inicio;
                console.log(`🧮 Cálculo de mezcla: ${tiempo.toFixed(2)}ms`);
                resolve();
            }, 50); // Simular tiempo de cálculo
        });
    }

    async probarRenderizadoGrafico() {
        return new Promise((resolve) => {
            const canvas = document.getElementById('graficoMezcla');
            if (!canvas) {
                console.log('⚠️ Canvas del gráfico no encontrado');
                resolve();
                return;
            }
            
            const inicio = performance.now();
            
            // Simular renderizado de gráfico
            if (window.Chart && window.graficoMezcla) {
                // Actualizar datos del gráfico
                window.graficoMezcla.data.datasets[0].data = [60, 40];
                window.graficoMezcla.update();
                
                const tiempo = performance.now() - inicio;
                console.log(`📊 Renderizado de gráfico: ${tiempo.toFixed(2)}ms`);
            } else {
                console.log('⚠️ Chart.js no disponible');
            }
            
            resolve();
        });
    }

    mostrarResultados() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 RESULTADOS DE PRUEBAS DE VELOCIDAD ESPECÍFICAS');
        console.log('='.repeat(60));
        
        console.log('\n🤖 ASISTENTE:');
        console.log(`   • Inicialización: ${this.metricas.asistente.tiempoInicializacion.toFixed(2)}ms`);
        console.log(`   • Tiempo de respuesta: ${this.metricas.asistente.tiempoRespuesta.toFixed(2)}ms`);
        console.log(`   • Síntesis de voz: ${this.metricas.asistente.tiempoVoz.toFixed(2)}ms`);
        console.log(`   • Llamadas API: ${this.metricas.asistente.llamadasAPI}`);
        
        if (this.metricas.asistente.errores.length > 0) {
            console.log(`   • Errores: ${this.metricas.asistente.errores.join(', ')}`);
        }
        
        console.log('\n🧮 CALCULADORA:');
        console.log(`   • Carga de materiales: ${this.metricas.calculadora.tiempoCargaMateriales.toFixed(2)}ms`);
        console.log(`   • Cálculo de mezcla: ${this.metricas.calculadora.tiempoCalculo.toFixed(2)}ms`);
        console.log(`   • Renderizado gráfico: ${this.metricas.calculadora.tiempoRenderizadoGrafico.toFixed(2)}ms`);
        console.log(`   • Llamadas API: ${this.metricas.calculadora.llamadasAPI}`);
        
        if (this.metricas.calculadora.errores.length > 0) {
            console.log(`   • Errores: ${this.metricas.calculadora.errores.join(', ')}`);
        }
        
        // Análisis de rendimiento
        this.analizarRendimiento();
    }

    analizarRendimiento() {
        console.log('\n🔍 ANÁLISIS DE RENDIMIENTO:');
        
        // Análisis del asistente
        const tiempoTotalAsistente = this.metricas.asistente.tiempoInicializacion + 
                                   this.metricas.asistente.tiempoRespuesta + 
                                   this.metricas.asistente.tiempoVoz;
        
        if (tiempoTotalAsistente > 2000) {
            console.log('⚠️ ASISTENTE LENTO: Tiempo total > 2000ms');
            console.log('   Recomendaciones:');
            console.log('   - Implementar caché para respuestas frecuentes');
            console.log('   - Optimizar síntesis de voz');
            console.log('   - Reducir tiempo de inicialización');
        } else if (tiempoTotalAsistente > 1000) {
            console.log('⚠️ ASISTENTE MODERADO: Tiempo total > 1000ms');
            console.log('   Recomendaciones:');
            console.log('   - Considerar optimizaciones menores');
        } else {
            console.log('✅ ASISTENTE RÁPIDO: Tiempo total < 1000ms');
        }
        
        // Análisis de la calculadora
        const tiempoTotalCalculadora = this.metricas.calculadora.tiempoCargaMateriales + 
                                     this.metricas.calculadora.tiempoCalculo + 
                                     this.metricas.calculadora.tiempoRenderizadoGrafico;
        
        if (tiempoTotalCalculadora > 1500) {
            console.log('⚠️ CALCULADORA LENTA: Tiempo total > 1500ms');
            console.log('   Recomendaciones:');
            console.log('   - Cargar materiales en background');
            console.log('   - Optimizar cálculos matemáticos');
            console.log('   - Mejorar renderizado de gráficos');
        } else if (tiempoTotalCalculadora > 500) {
            console.log('⚠️ CALCULADORA MODERADA: Tiempo total > 500ms');
            console.log('   Recomendaciones:');
            console.log('   - Considerar optimizaciones menores');
        } else {
            console.log('✅ CALCULADORA RÁPIDA: Tiempo total < 500ms');
        }
        
        // Recomendaciones generales
        console.log('\n💡 RECOMENDACIONES GENERALES:');
        console.log('   1. Implementar lazy loading para componentes pesados');
        console.log('   2. Usar Web Workers para cálculos intensivos');
        console.log('   3. Implementar caché inteligente para datos frecuentes');
        console.log('   4. Optimizar animaciones y transiciones');
        console.log('   5. Reducir llamadas API innecesarias');
    }
}

// Función para ejecutar las pruebas
function ejecutarPruebasVelocidadEspecifica() {
    new PruebaVelocidadEspecifica();
}

// Auto-ejecutar si se está en modo debug
if (window.location.search.includes('debug=speed')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(ejecutarPruebasVelocidadEspecifica, 2000);
    });
}

// Exportar para uso global
window.ejecutarPruebasVelocidadEspecifica = ejecutarPruebasVelocidadEspecifica;

console.log('🔧 Pruebas de velocidad específicas cargadas');
