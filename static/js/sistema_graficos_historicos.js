// Sistema de gráficos históricos SIBIA - Versión limpia UTF-8

// ===== CONFIGURACIÓN DE GRÁFICOS HISTÓRICOS =====

let sistemaGraficosHistoricos = {
    configuracion: {
        colores: {
            objetivo: 'rgba(255, 99, 132, 1)',
            planificado: 'rgba(54, 162, 235, 1)', 
            real: 'rgba(75, 192, 192, 1)',
            inyectado: 'rgba(153, 102, 255, 1)',
            grafana: 'rgba(255, 159, 64, 1)',
            metano: 'rgba(46, 204, 113, 1)',
            h2s: 'rgba(231, 76, 60, 1)',
            eficiencia: 'rgba(52, 152, 219, 1)',
            diferencia_positiva: 'rgba(39, 174, 96, 1)',
            diferencia_negativa: 'rgba(231, 76, 60, 1)'
        },
        opciones: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    },
    
    graficos: {},
    
    // Función para inicializar todos los gráficos
    inicializar: function() {
        console.log('Inicializando sistema de gráficos históricos...');
        
        // Configurar Chart.js por defecto
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = 'Arial, sans-serif';
            Chart.defaults.font.size = 12;
            
            this.crearGraficoProduccion();
            this.crearGraficoEficiencia();
            this.crearGraficoMetano();
        } else {
            console.warn('Chart.js no está disponible');
        }
    },
    
    // Crear gráfico de producción
    crearGraficoProduccion: function() {
        const ctx = document.getElementById('graficoProduccionDiaria');
        if (!ctx) return;
        
        this.graficos.produccion = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Objetivo KW',
                    data: [],
                    borderColor: this.configuracion.colores.objetivo,
                    backgroundColor: this.configuracion.colores.objetivo + '20',
                    tension: 0.1
                }, {
                    label: 'Producción Real KW',
                    data: [],
                    borderColor: this.configuracion.colores.real,
                    backgroundColor: this.configuracion.colores.real + '20',
                    tension: 0.1
                }]
            },
            options: {
                ...this.configuracion.opciones,
                plugins: {
                    ...this.configuracion.opciones.plugins,
                    title: {
                        display: true,
                        text: 'Producción Diaria de Energía'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'KW'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    }
                }
            }
        });
    },
    
    // Crear gráfico de eficiencia
    crearGraficoEficiencia: function() {
        const ctx = document.getElementById('graficoEficiencia');
        if (!ctx) return;
        
        this.graficos.eficiencia = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Eficiencia %',
                    data: [],
                    backgroundColor: this.configuracion.colores.eficiencia,
                    borderColor: this.configuracion.colores.eficiencia,
                    borderWidth: 1
                }]
            },
            options: {
                ...this.configuracion.opciones,
                plugins: {
                    ...this.configuracion.opciones.plugins,
                    title: {
                        display: true,
                        text: 'Eficiencia del Sistema'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Eficiencia (%)'
                        }
                    }
                }
            }
        });
    },
    
    // Crear gráfico de metano
    crearGraficoMetano: function() {
        const ctx = document.getElementById('graficoMetano');
        if (!ctx) return;
        
        this.graficos.metano = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Metano', 'Otros gases'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [
                        this.configuracion.colores.metano,
                        'rgba(200, 200, 200, 0.5)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                ...this.configuracion.opciones,
                plugins: {
                    ...this.configuracion.opciones.plugins,
                    title: {
                        display: true,
                        text: 'Composición de Gases'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    },
    
    // Actualizar datos de los gráficos
    actualizarDatos: function(datos) {
        if (!datos) return;
        
        // Actualizar gráfico de producción
        if (this.graficos.produccion && datos.produccion) {
            const chart = this.graficos.produccion;
            chart.data.labels = datos.produccion.fechas || [];
            chart.data.datasets[0].data = datos.produccion.objetivos || [];
            chart.data.datasets[1].data = datos.produccion.reales || [];
            chart.update();
        }
        
        // Actualizar gráfico de eficiencia
        if (this.graficos.eficiencia && datos.eficiencia) {
            const chart = this.graficos.eficiencia;
            chart.data.labels = datos.eficiencia.fechas || [];
            chart.data.datasets[0].data = datos.eficiencia.valores || [];
            chart.update();
        }
        
        // Actualizar gráfico de metano
        if (this.graficos.metano && datos.metano) {
            const chart = this.graficos.metano;
            chart.data.datasets[0].data = [
                datos.metano.porcentaje || 0,
                100 - (datos.metano.porcentaje || 0)
            ];
            chart.update();
        }
    },
    
    // Limpiar todos los gráficos
    limpiar: function() {
        Object.values(this.graficos).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.graficos = {};
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    sistemaGraficosHistoricos.inicializar();
});

// Exportar para uso global
window.sistemaGraficosHistoricos = sistemaGraficosHistoricos;
