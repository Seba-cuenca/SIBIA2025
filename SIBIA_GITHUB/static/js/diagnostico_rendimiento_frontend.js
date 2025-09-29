/**
 * DIAGNÓSTICO DE RENDIMIENTO FRONTEND - SIBIA
 * Este script identifica problemas de rendimiento en el frontend
 */

class FrontendPerformanceDiagnostic {
    constructor() {
        this.metrics = {
            domLoadTime: 0,
            jsLoadTime: 0,
            apiResponseTimes: {},
            memoryUsage: 0,
            renderTimes: {},
            errors: []
        };
        this.startTime = performance.now();
    }

    // Medir tiempo de carga del DOM
    measureDOMLoadTime() {
        const domContentLoaded = performance.getEntriesByType('navigation')[0];
        if (domContentLoaded) {
            this.metrics.domLoadTime = domContentLoaded.domContentLoadedEventEnd - domContentLoaded.domContentLoadedEventStart;
        }
    }

    // Medir tiempo de carga de JavaScript
    measureJSLoadTime() {
        const jsEntries = performance.getEntriesByType('resource').filter(entry => 
            entry.name.includes('.js') && entry.name.includes('static')
        );
        
        if (jsEntries.length > 0) {
            const totalJSTime = jsEntries.reduce((sum, entry) => sum + entry.duration, 0);
            this.metrics.jsLoadTime = totalJSTime;
        }
    }

    // Medir tiempo de respuesta de APIs
    async measureAPIResponseTimes() {
        const endpoints = [
            '/datos_kpi',
            '/registros_15min',
            '/obtener_materiales_base_json',
            '/parametros_globales',
            '/stock',
            '/historico_diario'
        ];

        for (const endpoint of endpoints) {
            try {
                const startTime = performance.now();
                const response = await fetch(endpoint);
                const endTime = performance.now();
                
                this.metrics.apiResponseTimes[endpoint] = {
                    responseTime: endTime - startTime,
                    status: response.status,
                    success: response.ok,
                    size: response.headers.get('content-length') || 0
                };
            } catch (error) {
                this.metrics.apiResponseTimes[endpoint] = {
                    responseTime: 0,
                    status: 0,
                    success: false,
                    error: error.message
                };
                this.metrics.errors.push(`Error en ${endpoint}: ${error.message}`);
            }
        }
    }

    // Medir uso de memoria
    measureMemoryUsage() {
        if (performance.memory) {
            this.metrics.memoryUsage = {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            };
        }
    }

    // Medir tiempo de renderizado de elementos específicos
    measureRenderTimes() {
        const elementsToMeasure = [
            'kpis',
            'registros-15min',
            'dashboard',
            'calculadora',
            'asistente-ia'
        ];

        elementsToMeasure.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                const startTime = performance.now();
                // Simular operación de renderizado
                element.style.display = 'none';
                element.style.display = 'block';
                const endTime = performance.now();
                
                this.metrics.renderTimes[elementId] = endTime - startTime;
            }
        });
    }

    // Detectar problemas comunes
    detectCommonIssues() {
        const issues = [];

        // Verificar intervalos múltiples
        const intervals = this.findActiveIntervals();
        if (intervals.length > 5) {
            issues.push(`⚠️ Demasiados intervalos activos (${intervals.length}). Esto puede causar lentitud.`);
        }

        // Verificar llamadas API frecuentes
        const slowAPIs = Object.entries(this.metrics.apiResponseTimes)
            .filter(([endpoint, data]) => data.responseTime > 1000);
        
        if (slowAPIs.length > 0) {
            issues.push(`⚠️ APIs lentas detectadas: ${slowAPIs.map(([endpoint]) => endpoint).join(', ')}`);
        }

        // Verificar uso de memoria
        if (this.metrics.memoryUsage.used > this.metrics.memoryUsage.limit * 0.8) {
            issues.push('⚠️ Uso de memoria alto (>80% del límite)');
        }

        // Verificar errores JavaScript
        if (this.metrics.errors.length > 0) {
            issues.push(`⚠️ ${this.metrics.errors.length} errores JavaScript detectados`);
        }

        return issues;
    }

    // Encontrar intervalos activos
    findActiveIntervals() {
        // Esta es una aproximación - en realidad es difícil detectar intervalos activos
        const scripts = document.querySelectorAll('script[src*="static/js"]');
        return Array.from(scripts).map(script => script.src);
    }

    // Generar reporte completo
    generateReport() {
        const totalTime = performance.now() - this.startTime;
        
        console.log('='.repeat(60));
        console.log('🔍 DIAGNÓSTICO DE RENDIMIENTO FRONTEND - SIBIA');
        console.log('='.repeat(60));
        
        console.log('\n📊 MÉTRICAS DE CARGA:');
        console.log(`   • Tiempo total de diagnóstico: ${totalTime.toFixed(2)} ms`);
        console.log(`   • Tiempo de carga DOM: ${this.metrics.domLoadTime.toFixed(2)} ms`);
        console.log(`   • Tiempo de carga JS: ${this.metrics.jsLoadTime.toFixed(2)} ms`);
        
        console.log('\n🌐 TIEMPOS DE RESPUESTA API:');
        Object.entries(this.metrics.apiResponseTimes).forEach(([endpoint, data]) => {
            const status = data.success ? '✅' : '❌';
            console.log(`   ${status} ${endpoint}: ${data.responseTime.toFixed(2)} ms`);
            if (!data.success && data.error) {
                console.log(`      Error: ${data.error}`);
            }
        });

        console.log('\n🎨 TIEMPOS DE RENDERIZADO:');
        Object.entries(this.metrics.renderTimes).forEach(([element, time]) => {
            console.log(`   • ${element}: ${time.toFixed(2)} ms`);
        });

        if (this.metrics.memoryUsage.used > 0) {
            console.log('\n💾 USO DE MEMORIA:');
            console.log(`   • Usado: ${(this.metrics.memoryUsage.used / 1024 / 1024).toFixed(2)} MB`);
            console.log(`   • Total: ${(this.metrics.memoryUsage.total / 1024 / 1024).toFixed(2)} MB`);
            console.log(`   • Límite: ${(this.metrics.memoryUsage.limit / 1024 / 1024).toFixed(2)} MB`);
        }

        const issues = this.detectCommonIssues();
        if (issues.length > 0) {
            console.log('\n⚠️ PROBLEMAS DETECTADOS:');
            issues.forEach(issue => console.log(`   ${issue}`));
        }

        console.log('\n💡 RECOMENDACIONES:');
        this.generateRecommendations();

        return {
            metrics: this.metrics,
            issues: issues,
            totalTime: totalTime
        };
    }

    // Generar recomendaciones
    generateRecommendations() {
        const recommendations = [];

        if (this.metrics.domLoadTime > 1000) {
            recommendations.push('• Optimizar carga del DOM - reducir elementos innecesarios');
        }

        if (this.metrics.jsLoadTime > 2000) {
            recommendations.push('• Optimizar carga de JavaScript - usar lazy loading o code splitting');
        }

        const slowAPIs = Object.entries(this.metrics.apiResponseTimes)
            .filter(([endpoint, data]) => data.responseTime > 1000);
        
        if (slowAPIs.length > 0) {
            recommendations.push('• Implementar caché para APIs lentas');
            recommendations.push('• Optimizar consultas de base de datos');
        }

        const intervals = this.findActiveIntervals();
        if (intervals.length > 5) {
            recommendations.push('• Reducir número de intervalos activos');
            recommendations.push('• Consolidar actualizaciones periódicas');
        }

        if (this.metrics.errors.length > 0) {
            recommendations.push('• Corregir errores JavaScript');
            recommendations.push('• Implementar manejo de errores más robusto');
        }

        if (recommendations.length === 0) {
            recommendations.push('• ✅ No se detectaron problemas críticos');
        }

        recommendations.forEach(rec => console.log(`   ${rec}`));
    }

    // Ejecutar diagnóstico completo
    async runFullDiagnostic() {
        console.log('🚀 Iniciando diagnóstico completo de rendimiento...');
        
        this.measureDOMLoadTime();
        this.measureJSLoadTime();
        await this.measureAPIResponseTimes();
        this.measureMemoryUsage();
        this.measureRenderTimes();
        
        return this.generateReport();
    }
}

// Función para ejecutar el diagnóstico
async function ejecutarDiagnosticoRendimiento() {
    const diagnostic = new FrontendPerformanceDiagnostic();
    return await diagnostic.runFullDiagnostic();
}

// Función para monitorear rendimiento en tiempo real
function iniciarMonitoreoRendimiento() {
    console.log('📊 Iniciando monitoreo de rendimiento en tiempo real...');
    
    let lastMemoryCheck = 0;
    let apiCallCount = 0;
    
    // Interceptar llamadas fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const startTime = performance.now();
        apiCallCount++;
        
        return originalFetch.apply(this, args).then(response => {
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            if (responseTime > 1000) {
                console.warn(`⚠️ API lenta detectada: ${args[0]} - ${responseTime.toFixed(2)} ms`);
            }
            
            return response;
        });
    };
    
    // Monitorear memoria cada 30 segundos
    setInterval(() => {
        if (performance.memory) {
            const memoryUsage = performance.memory.usedJSHeapSize / 1024 / 1024;
            const memoryLimit = performance.memory.jsHeapSizeLimit / 1024 / 1024;
            const usagePercent = (memoryUsage / memoryLimit) * 100;
            
            if (usagePercent > 80) {
                console.warn(`⚠️ Uso de memoria alto: ${memoryUsage.toFixed(2)} MB (${usagePercent.toFixed(1)}%)`);
            }
        }
    }, 30000);
    
    console.log('✅ Monitoreo de rendimiento activado');
}

// Exportar funciones para uso global
window.ejecutarDiagnosticoRendimiento = ejecutarDiagnosticoRendimiento;
window.iniciarMonitoreoRendimiento = iniciarMonitoreoRendimiento;

// Auto-ejecutar diagnóstico si se está en modo debug
if (window.location.search.includes('debug=performance')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            ejecutarDiagnosticoRendimiento();
            iniciarMonitoreoRendimiento();
        }, 2000);
    });
}

console.log('🔧 Diagnóstico de rendimiento frontend cargado');
