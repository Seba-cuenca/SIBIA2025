// ===== HISTÓRICO DIARIO MEJORADO - SIBIA =====
console.log("📊 Cargando módulo de histórico diario mejorado...");

let graficoHistoricoDiario = null;
let datosHistoricoDiario = null;

/**
 * Inicializa el sistema de histórico diario
 */
function inicializarHistoricoDiario() {
    console.log("🚀 Inicializando histórico diario mejorado...");
    cargarHistoricoDiario();
    
    // Auto-actualización cada 2 minutos
    setInterval(() => {
        const historicoTab = document.querySelector('#historico-tab');
        const historicoContent = document.querySelector('#historico');
        if (historicoTab && historicoContent && 
            (historicoTab.classList.contains('active') || historicoContent.classList.contains('show'))) {
            cargarHistoricoDiario();
        }
    }, 120000);
}

/**
 * Carga los datos del histórico diario desde el servidor
 */
function cargarHistoricoDiario(dias = 7) {
    console.log(`📊 Cargando histórico diario (últimos ${dias} días)...`);
    
    // Mostrar indicador de carga
    mostrarCargandoHistorico();
    
    fetch(`/historico_diario?dias=${dias}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ Datos histórico diario recibidos:", data);
            datosHistoricoDiario = data;
            
            if (data.error) {
                mostrarErrorHistorico(data.error);
                return;
            }
            
            // Actualizar todas las secciones
            actualizarResumenHistorico(data);
            actualizarGraficoHistorico(data);
            actualizarTablaHistorico(data);
            actualizarEstadisticasHistorico(data);
            
        })
        .catch(error => {
            console.error('❌ Error cargando histórico diario:', error);
            mostrarErrorHistorico(`Error de conexión: ${error.message}`);
        });
}

/**
 * Actualiza el resumen del histórico diario
 */
function actualizarResumenHistorico(data) {
    if (!data.resumen) return;
    
    const elementos = {
        'total-dias-historico': data.resumen.total_dias || 0,
        'promedio-kw-generado-historico': formatearNumero(data.resumen.promedio_kw_generado || 0, 0) + ' kW',
        'promedio-eficiencia-historico': formatearNumero(data.resumen.promedio_eficiencia || 0, 1) + '%',
        'promedio-metano-historico': formatearNumero(data.resumen.promedio_metano || 0, 1) + '%',
        'mejor-dia-kw-historico': formatearNumero(data.resumen.mejor_dia_kw || 0, 0) + ' kW',
        'peor-dia-kw-historico': formatearNumero(data.resumen.peor_dia_kw || 0, 0) + ' kW'
    };
    
    Object.entries(elementos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.textContent = valor;
        }
    });
}

/**
 * Actualiza el gráfico del histórico diario
 */
function actualizarGraficoHistorico(data) {
    const canvas = document.getElementById('grafico-historico-diario');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destruir gráfico anterior si existe
    if (graficoHistoricoDiario) {
        graficoHistoricoDiario.destroy();
    }
    
    // Crear nuevo gráfico
    graficoHistoricoDiario = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.fechas || [],
            datasets: [
                {
                    label: 'KW Objetivo',
                    data: data.produccion_energetica?.kw_objetivo || [],
                    borderColor: '#6c757d',
                    backgroundColor: 'rgba(108, 117, 125, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: 'KW Planificado',
                    data: data.produccion_energetica?.kw_planificado || [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: 'KW Generado Real',
                    data: data.produccion_energetica?.kw_generado_real || [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: false
                },
                {
                    label: 'KW Inyectado Real',
                    data: data.produccion_energetica?.kw_inyectado_real || [],
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: 'Generación Grafana',
                    data: data.produccion_energetica?.generacion_actual_grafana || [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Evolución Energética Diaria'
                },
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
                    },
                    ticks: {
                        callback: function(value) {
                            return formatearNumero(value, 0) + ' kW';
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Fecha'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Actualiza la tabla del histórico diario
 */
function actualizarTablaHistorico(data) {
    const tabla = document.getElementById('tabla-historico-diario');
    if (!tabla) return;
    
    let html = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Fecha</th>
                        <th>KW Objetivo</th>
                        <th>KW Planificado</th>
                        <th>KW Generado</th>
                        <th>KW Inyectado</th>
                        <th>Eficiencia</th>
                        <th>Metano %</th>
                        <th>H₂S ppm</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    if (data.fechas && data.fechas.length > 0) {
        for (let i = 0; i < data.fechas.length; i++) {
            const eficiencia = data.rendimiento?.eficiencia_energetica?.[i] || 0;
            
            // Determinar clase de estado basada en eficiencia
            let estadoClass = 'text-success';
            let estadoTexto = 'Excelente';
            if (eficiencia < 70) {
                estadoClass = 'text-danger';
                estadoTexto = 'Bajo';
            } else if (eficiencia < 85) {
                estadoClass = 'text-warning';
                estadoTexto = 'Regular';
            } else if (eficiencia < 95) {
                estadoClass = 'text-info';
                estadoTexto = 'Bueno';
            }
            
            html += `
                <tr>
                    <td><strong>${data.fechas[i]}</strong></td>
                    <td>${formatearNumero(data.produccion_energetica?.kw_objetivo?.[i] || 0, 0)}</td>
                    <td>${formatearNumero(data.produccion_energetica?.kw_planificado?.[i] || 0, 0)}</td>
                    <td><strong class="text-success">${formatearNumero(data.produccion_energetica?.kw_generado_real?.[i] || 0, 0)}</strong></td>
                    <td><strong class="text-primary">${formatearNumero(data.produccion_energetica?.kw_inyectado_real?.[i] || 0, 0)}</strong></td>
                    <td><span class="${estadoClass}">${formatearNumero(eficiencia, 1)}%</span></td>
                    <td>${formatearNumero(data.calidad_biogas?.metano_actual_grafana?.[i] || 0, 1)}%</td>
                    <td>${formatearNumero(data.calidad_biogas?.h2s_actual_grafana?.[i] || 0, 0)}</td>
                    <td><span class="${estadoClass}">${estadoTexto}</span></td>
                </tr>
            `;
        }
    } else {
        html += `
            <tr>
                <td colspan="9" class="text-center text-muted">
                    <i class="fas fa-info-circle"></i> No hay datos históricos disponibles
                </td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    tabla.innerHTML = html;
}

/**
 * Actualiza las estadísticas del histórico diario
 */
function actualizarEstadisticasHistorico(data) {
    // Actualizar KPIs principales
    const kpis = {
        'kpi-total-dias': data.resumen?.total_dias || 0,
        'kpi-promedio-generacion': formatearNumero(data.resumen?.promedio_kw_generado || 0, 0) + ' kW',
        'kpi-eficiencia-promedio': formatearNumero(data.resumen?.promedio_eficiencia || 0, 1) + '%',
        'kpi-mejor-rendimiento': formatearNumero(data.resumen?.mejor_dia_kw || 0, 0) + ' kW'
    };
    
    Object.entries(kpis).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.textContent = valor;
        }
    });
}

/**
 * Cambia el período del histórico diario
 */
function cambiarPeriodoHistorico() {
    const selector = document.getElementById('selector-periodo');
    if (!selector) return;
    
    const dias = parseInt(selector.value);
    cargarHistoricoDiario(dias);
}

/**
 * Cambia el tipo de vista del histórico
 */
function cambiarTipoVista() {
    const selector = document.getElementById('selector-tipo-vista');
    if (!selector) return;
    
    const tipoVista = selector.value;
    
    // Mostrar/ocultar secciones según el tipo de vista
    const seccionHoraria = document.getElementById('seccion-historico-horario');
    const seccionDiaria = document.getElementById('seccion-historico-diario');
    const seccionSemanal = document.getElementById('seccion-historico-semanal');
    
    // Ocultar todas las secciones
    [seccionHoraria, seccionDiaria, seccionSemanal].forEach(seccion => {
        if (seccion) seccion.style.display = 'none';
    });
    
    // Mostrar la sección correspondiente
    switch (tipoVista) {
        case 'hora':
            if (seccionHoraria) seccionHoraria.style.display = 'block';
            actualizarHistoricoHorario();
            break;
        case 'dia':
            if (seccionDiaria) seccionDiaria.style.display = 'block';
            cargarHistoricoDiario();
            break;
        case 'semana':
            if (seccionSemanal) seccionSemanal.style.display = 'block';
            actualizarHistoricoSemanal();
            break;
    }
}

/**
 * Agrega un nuevo registro al histórico diario
 */
function agregarRegistroHistorico() {
    console.log("➕ Agregando nuevo registro histórico...");
    
    fetch('/agregar_registro_historico', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            fecha: new Date().toISOString().split('T')[0]
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("✅ Registro agregado exitosamente");
            mostrarAlerta('Registro agregado exitosamente', 'success');
            // Recargar datos
            setTimeout(() => cargarHistoricoDiario(), 1000);
        } else {
            console.error("❌ Error agregando registro:", data.mensaje);
            mostrarAlerta(`Error: ${data.mensaje}`, 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Error en solicitud:', error);
        mostrarAlerta(`Error de conexión: ${error.message}`, 'danger');
    });
}

/**
 * Exporta los datos del histórico diario
 */
function exportarHistoricoDiario() {
    if (!datosHistoricoDiario || !datosHistoricoDiario.fechas) {
        mostrarAlerta('No hay datos para exportar', 'warning');
        return;
    }
    
    console.log("📤 Exportando histórico diario...");
    
    // Crear CSV
    let csv = 'Fecha,KW Objetivo,KW Planificado,KW Generado,KW Inyectado,Eficiencia %,Metano %,H2S ppm\n';
    
    for (let i = 0; i < datosHistoricoDiario.fechas.length; i++) {
        csv += [
            datosHistoricoDiario.fechas[i],
            datosHistoricoDiario.produccion_energetica?.kw_objetivo?.[i] || 0,
            datosHistoricoDiario.produccion_energetica?.kw_planificado?.[i] || 0,
            datosHistoricoDiario.produccion_energetica?.kw_generado_real?.[i] || 0,
            datosHistoricoDiario.produccion_energetica?.kw_inyectado_real?.[i] || 0,
            datosHistoricoDiario.rendimiento?.eficiencia_energetica?.[i] || 0,
            datosHistoricoDiario.calidad_biogas?.metano_actual_grafana?.[i] || 0,
            datosHistoricoDiario.calidad_biogas?.h2s_actual_grafana?.[i] || 0
        ].join(',') + '\n';
    }
    
    // Descargar archivo
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `historico_diario_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    mostrarAlerta('Histórico exportado exitosamente', 'success');
}

/**
 * Muestra indicador de carga
 */
function mostrarCargandoHistorico() {
    const contenedores = ['tabla-historico-diario'];
    contenedores.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.innerHTML = `
                <div class="text-center p-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2 text-muted">Cargando datos históricos...</p>
                </div>
            `;
        }
    });
}

/**
 * Muestra error en el histórico
 */
function mostrarErrorHistorico(mensaje) {
    const contenedores = ['tabla-historico-diario'];
    contenedores.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.innerHTML = `
                <div class="alert alert-danger text-center">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Error:</strong> ${mensaje}
                    <br>
                    <button class="btn btn-sm btn-outline-danger mt-2" onclick="cargarHistoricoDiario()">
                        <i class="fas fa-redo"></i> Reintentar
                    </button>
                </div>
            `;
        }
    });
}

/**
 * Muestra una alerta temporal
 */
function mostrarAlerta(mensaje, tipo = 'info') {
    const alertaId = 'alerta-historico-' + Date.now();
    const alerta = document.createElement('div');
    alerta.id = alertaId;
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alerta.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alerta);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        const alertaElement = document.getElementById(alertaId);
        if (alertaElement) {
            alertaElement.remove();
        }
    }, 5000);
}

/**
 * Formatea números para mostrar
 */
function formatearNumero(numero, decimales = 2) {
    if (isNaN(numero)) return '0';
    return Number(numero).toLocaleString('es-ES', {
        minimumFractionDigits: decimales,
        maximumFractionDigits: decimales
    });
}

// Inicializar cuando se carga el documento
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔄 DOM cargado, verificando histórico diario...");
    // Verificar si estamos en la página con histórico diario
    if (document.getElementById('tabla-historico-diario')) {
        console.log("✅ Elemento histórico diario encontrado, inicializando...");
        inicializarHistoricoDiario();
    } else {
        console.log("⚠️ Elemento histórico diario no encontrado");
    }
});

// Exportar funciones para uso global
window.cargarHistoricoDiario = cargarHistoricoDiario;
window.cambiarPeriodoHistorico = cambiarPeriodoHistorico;
window.cambiarTipoVista = cambiarTipoVista;
window.agregarRegistroHistorico = agregarRegistroHistorico;
window.exportarHistoricoDiario = exportarHistoricoDiario; 