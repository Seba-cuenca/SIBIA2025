document.addEventListener('DOMContentLoaded', function() {
    console.log("KPI.js cargado - inicializando sistema de KPIs");
    
    // La pestaña de KPI puede no estar activa al cargar,
    // así que inicializamos los gráficos cuando se hace clic en la pestaña.
    const kpiTab = document.getElementById('kpis-tab');
    if (kpiTab) {
        kpiTab.addEventListener('shown.bs.tab', function () {
            console.log("Pestaña de KPI activada. Inicializando gráficos.");
            setTimeout(() => {
                inicializarGraficosKPI();
            }, 100); // Pequeña pausa para asegurar que el DOM esté listo
        });
    }

    // Si la pestaña ya está activa en la carga (por ejemplo, si el usuario recarga la página en esa pestaña)
    if (kpiTab && kpiTab.classList.contains('active')) {
        console.log("Pestaña KPI ya está activa, inicializando directamente");
        setTimeout(() => {
            inicializarGraficosKPI();
        }, 100);
    }
});

let graficosKPI = {}; // Para gestionar los gráficos creados

function inicializarGraficosKPI() {
    console.log("🔄 Iniciando carga de datos KPI...");
    
    // Mostrar indicador de carga
    const container = document.getElementById('kpi-pane-content');
    if (container) {
        container.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="sr-only">Cargando KPIs...</span></div><p class="mt-2">Cargando datos de KPI...</p></div>';
    }
    
    fetch('/datos_kpi')
        .then(response => {
            console.log("📡 Respuesta KPI recibida:", response.status);
            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(datos => {
            console.log("📊 Datos KPI procesados:", datos);
            
            if (!datos || datos.error) {
                throw new Error(datos.error || "No se recibieron datos válidos para los KPIs");
            }

            // Verificar que tenemos la estructura esperada
            if (!datos.resumen || !datos.produccion || !datos.consumo || !datos.cumplimiento) {
                throw new Error("Estructura de datos KPI incompleta");
            }

            console.log("✅ Estructura de datos válida, renderizando interfaz...");
            renderizarInterfazKPI(datos);
            
        })
        .catch(error => {
            console.error('❌ Error al cargar datos KPI:', error);
            const container = document.getElementById('kpi-pane-content');
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-danger">
                        <h5><i class="fas fa-exclamation-triangle"></i> Error al Cargar KPIs</h5>
                        <p><strong>Detalles:</strong> ${error.message}</p>
                        <hr>
                        <button class="btn btn-warning btn-sm" onclick="retryKPIs()">
                            <i class="fas fa-redo"></i> Reintentar
                        </button>
                        <small class="text-muted d-block mt-2">
                            Revise la consola del navegador (F12) y del servidor para más detalles.
                        </small>
                    </div>`;
            }
        });
}

function renderizarInterfazKPI(datos) {
    console.log("🎨 Renderizando interfaz KPI con datos:", datos);
    
    const container = document.getElementById('kpi-pane-content');
    if (!container) {
        console.error("No se encontró el contenedor kpi-pane-content");
        return;
    }

    // Generar HTML de la interfaz
    container.innerHTML = `
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-chart-line"></i> Resumen de KPIs</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <div class="border-bottom pb-2 mb-2">
                                    <small class="text-muted">Producción Total (7 días)</small>
                                    <h4 class="text-success mb-0">${formatearNumero(datos.resumen.kw_total_mes, 0)} kW</h4>
                                </div>
                                <div>
                                    <small class="text-muted">Eficiencia Energética</small>
                                    <h5 class="text-info mb-0">${formatearNumero(datos.resumen.eficiencia_energetica, 1)}%</h5>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="border-bottom pb-2 mb-2">
                                    <small class="text-muted">Cumplimiento Alimentación</small>
                                    <h4 class="text-warning mb-0">${formatearNumero(datos.resumen.eficiencia_alimentacion, 1)}%</h4>
                                </div>
                                <div>
                                    <small class="text-muted">Ahorro Total</small>
                                    <h5 class="text-success mb-0">$${formatearNumero(datos.resumen.ahorro_total_mes, 2)}</h5>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0"><i class="fas fa-bolt"></i> Producción Energética - Últimos 7 Días</h6>
                    </div>
                    <div class="card-body">
                        <div style="height: 250px;">
                            <canvas id="kpiProduccionChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-info text-white">
                        <h6 class="mb-0"><i class="fas fa-industry"></i> Consumo de Materiales Principales</h6>
                    </div>
                    <div class="card-body">
                        <div style="height: 300px;">
                            <canvas id="kpiConsumoChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-warning text-white">
                        <h6 class="mb-0"><i class="fas fa-clock"></i> Cumplimiento de Alimentación</h6>
                    </div>
                    <div class="card-body">
                        <div style="height: 300px;">
                            <canvas id="kpiCumplimientoDona"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;

    // Pequeña pausa para que el DOM se actualice antes de crear los gráficos
    setTimeout(() => {
        renderizarGraficos(datos);
    }, 100);
}

function renderizarGraficos(datos) {
    console.log("📈 Creando gráficos con datos:", {
        produccion: datos.produccion,
        consumo: datos.consumo,
        cumplimiento: datos.cumplimiento
    });

    // Destruir gráficos existentes si existen
    Object.keys(graficosKPI).forEach(key => {
        if (graficosKPI[key]) {
            graficosKPI[key].destroy();
            delete graficosKPI[key];
        }
    });

    // Gráfico de Producción Energética
    const ctxProduccion = document.getElementById('kpiProduccionChart');
    if (ctxProduccion) {
        console.log("🔹 Creando gráfico de producción");
        graficosKPI.produccion = new Chart(ctxProduccion, {
            type: 'line',
            data: {
                labels: datos.produccion.labels || [],
                datasets: [
                    {
                        label: 'KW Planificados',
                        data: datos.produccion.planificado || [],
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'KW Generados Reales',
                        data: datos.produccion.real || [],
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'KW'
                        }
                    }
                }
            }
        });
    }

    // Gráfico de Consumo de Materiales
    const ctxConsumo = document.getElementById('kpiConsumoChart');
    if (ctxConsumo) {
        console.log("🔹 Creando gráfico de consumo");
        graficosKPI.consumo = new Chart(ctxConsumo, {
            type: 'bar',
            data: {
                labels: datos.consumo.labels || [],
                datasets: [{
                    label: 'Consumo (TN)',
                    data: datos.consumo.data || [],
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(255, 87, 34, 0.8)',
                        'rgba(63, 81, 181, 0.8)',
                        'rgba(156, 39, 176, 0.8)'
                    ],
                    borderColor: [
                        'rgba(76, 175, 80, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(255, 87, 34, 1)',
                        'rgba(63, 81, 181, 1)',
                        'rgba(156, 39, 176, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Toneladas (TN)'
                        }
                    }
                }
            }
        });
    }

    // Gráfico de Cumplimiento de Alimentación
    const ctxCumplimiento = document.getElementById('kpiCumplimientoDona');
    if (ctxCumplimiento) {
        console.log("🔹 Creando gráfico de cumplimiento");
        graficosKPI.cumplimiento = new Chart(ctxCumplimiento, {
            type: 'doughnut',
            data: {
                labels: ['Horas Alimentadas', 'Horas Faltantes'],
                datasets: [{
                    data: [
                        datos.cumplimiento.alimentadas || 0,
                        datos.cumplimiento.faltantes || 0
                    ],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    console.log("✅ Todos los gráficos KPI creados exitosamente");
}

// Función de formato mejorada
function formatearNumero(num, decimales = 2) {
    if (typeof num !== 'number') {
        num = parseFloat(num);
    }
    if (isNaN(num)) {
        return '0';
    }
    return num.toLocaleString('es-ES', { 
        minimumFractionDigits: decimales, 
        maximumFractionDigits: decimales 
    });
}

// Función para reintentar la carga de KPIs
function retryKPIs() {
    console.log("🔄 Reintentando carga de KPIs...");
    inicializarGraficosKPI();
}

// Función global para actualizar KPIs desde otros scripts
window.actualizarKPIs = function() {
    console.log("🔄 Actualización de KPIs solicitada externamente");
    inicializarGraficosKPI();
};

console.log("✅ KPI.js completamente cargado y listo"); 