// SCRIPT CORREGIDO PARA KPIs

console.log("🔧 Cargando script corregido para KPIs...");

function actualizarKPIsCorregido() {
    console.log("📊 Actualizando KPIs (CORREGIDO)...");
    
    // Mostrar indicador de carga
    const container = document.getElementById('kpis');
    if (container) {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'kpi-loading';
        loadingDiv.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando KPIs...</span>
                </div>
                <p class="mt-2">Cargando datos de KPI...</p>
            </div>
        `;
        container.appendChild(loadingDiv);
    }
    
    fetch('/datos_kpi')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📊 Datos KPI recibidos:", data);
            
            // Remover indicador de carga
            const loadingDiv = document.getElementById('kpi-loading');
            if (loadingDiv) {
                loadingDiv.remove();
            }
            
            if (data.error) {
                mostrarErrorKPIs(data.error);
                return;
            }
            
            // Actualizar elementos básicos de KPI
            actualizarElementosBasicosKPI(data);
            
            // Actualizar gráficos si están disponibles
            if (data.resumen && data.produccion && data.consumo) {
                actualizarGraficosKPI(data);
            }
            
            console.log("✅ KPIs actualizados correctamente");
        })
        .catch(error => {
            console.error('❌ Error actualizando KPIs:', error);
            mostrarErrorKPIs('Error de conexión');
        });
}

function actualizarElementosBasicosKPI(data) {
    // Actualizar elementos específicos por ID
    const elementos = {
        'kw-generados-planificados': (data.kw_generados_planificados || 0).toFixed(2) + ' kW',
        'kw-generados-real': (data.kw_generados_real || 0).toFixed(2) + ' kW',
        'diferencia-vs-planificado': (data.diferencia_vs_planificado_kw || 0).toFixed(2) + ' kW',
        'kw-inyectados-real': (data.kw_inyectados_real || 0).toFixed(2) + ' kW',
        'kw-consumidos-planta': (data.kw_consumidos_planta_real || 0).toFixed(2) + ' kW'
    };
    
    Object.entries(elementos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.textContent = valor;
            console.log(`✅ Actualizado ${id}: ${valor}`);
        } else {
            console.warn(`⚠️ No se encontró elemento: ${id}`);
        }
    });
    
    // Actualizar generación actual
    if (data.generacion_actual && data.generacion_actual.kw_actual) {
        const genElement = document.getElementById('generacion-actual');
        if (genElement) {
            genElement.textContent = data.generacion_actual.kw_actual.toFixed(2) + ' kW';
        }
    }
    
    // Actualizar resumen si está disponible
    if (data.resumen) {
        const resumen = data.resumen;
        const resumenElements = {
            'eficiencia-energetica': resumen.eficiencia_energetica + '%',
            'ahorro-total-mes': '$' + resumen.ahorro_total_mes.toFixed(2),
            'kw-total-mes': resumen.kw_total_mes.toFixed(2) + ' kW'
        };
        
        Object.entries(resumenElements).forEach(([id, valor]) => {
            const elemento = document.getElementById(id);
            if (elemento) {
                elemento.textContent = valor;
            }
        });
    }
}

function actualizarGraficosKPI(data) {
    console.log("📈 Actualizando gráficos KPI...");
    
    // Gráfico de producción energética
    if (data.produccion && data.produccion.labels && data.produccion.real) {
        actualizarGraficoProduccion(data.produccion);
    }
    
    // Gráfico de consumo de materiales
    if (data.consumo && data.consumo.labels && data.consumo.data) {
        actualizarGraficoConsumo(data.consumo);
    }
    
    // Gráfico de cumplimiento
    if (data.cumplimiento) {
        actualizarGraficoCumplimiento(data.cumplimiento);
    }
}

function actualizarGraficoProduccion(datos) {
    const ctx = document.getElementById('kpiProduccionChart');
    if (!ctx) {
        console.warn("⚠️ No se encontró canvas para gráfico de producción");
        return;
    }
    
    // Destruir gráfico existente si existe
    if (window.graficoProduccion) {
        window.graficoProduccion.destroy();
    }
    
    window.graficoProduccion = new Chart(ctx, {
        type: 'line',
        data: {
            labels: datos.labels || [],
            datasets: [{
                label: 'Planificado',
                data: datos.planificado || [],
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }, {
                label: 'Real',
                data: datos.real || [],
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'KW Generados'
                    }
                }
            }
        }
    });
}

function actualizarGraficoConsumo(datos) {
    const ctx = document.getElementById('kpiConsumoChart');
    if (!ctx) {
        console.warn("⚠️ No se encontró canvas para gráfico de consumo");
        return;
    }
    
    // Destruir gráfico existente si existe
    if (window.graficoConsumo) {
        window.graficoConsumo.destroy();
    }
    
    window.graficoConsumo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: datos.labels || [],
            datasets: [{
                label: 'Consumo (TN)',
                data: datos.data || [],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Toneladas'
                    }
                }
            }
        }
    });
}

function actualizarGraficoCumplimiento(datos) {
    const ctx = document.getElementById('kpiCumplimientoDona');
    if (!ctx) {
        console.warn("⚠️ No se encontró canvas para gráfico de cumplimiento");
        return;
    }
    
    // Destruir gráfico existente si existe
    if (window.graficoCumplimiento) {
        window.graficoCumplimiento.destroy();
    }
    
    window.graficoCumplimiento = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Horas Alimentadas', 'Horas Faltantes'],
            datasets: [{
                data: [datos.alimentadas || 0, datos.faltantes || 0],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ]
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

function mostrarErrorKPIs(mensaje) {
    const container = document.getElementById('kpis');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle"></i> Error cargando KPIs</h5>
                <p>${mensaje}</p>
                <button class="btn btn-primary btn-sm" onclick="actualizarKPIsCorregido()">
                    <i class="fas fa-redo"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// Función para test directo
function testKPIsCorregido() {
    console.log("🧪 Test directo KPIs...");
    actualizarKPIsCorregido();
}

// Exportar funciones globalmente
window.actualizarKPIsCorregido = actualizarKPIsCorregido;
window.testKPIsCorregido = testKPIsCorregido;

// Inicialización automática cuando se carga la pestaña
document.addEventListener('DOMContentLoaded', function() {
    // Detectar cuando se hace clic en la pestaña de KPIs
    const tabKPIs = document.getElementById('kpis-tab');
    if (tabKPIs) {
        tabKPIs.addEventListener('click', function() {
            console.log("👆 Pestaña KPIs clickeada - cargando datos...");
            setTimeout(actualizarKPIsCorregido, 500);
        });
    }
    
    // También ejecutar si la pestaña ya está activa
    setTimeout(() => {
        const pestanaActiva = document.getElementById('kpis');
        if (pestanaActiva && pestanaActiva.classList.contains('active')) {
            console.log("📊 Pestaña KPIs ya activa - cargando datos...");
            actualizarKPIsCorregido();
        }
    }, 1000);
});

console.log("✅ Script corregido para KPIs cargado correctamente"); 