// JavaScript para Análisis Económico
let chartCostos = null;
let chartFlujo = null;

// Cargar análisis al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarAnalisis();
});

async function cargarAnalisis() {
    try {
        document.getElementById('loading').classList.add('active');
        document.getElementById('content').style.display = 'none';

        const response = await fetch('/api/analisis-economico/calcular');
        const data = await response.json();

        if (data.status === 'success') {
            mostrarDatos(data);
            document.getElementById('content').style.display = 'block';
        } else {
            alert('Error al cargar análisis: ' + (data.error || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión: ' + error.message);
    } finally {
        document.getElementById('loading').classList.remove('active');
    }
}

function mostrarDatos(data) {
    // Métricas principales
    document.getElementById('ingresos-dia').textContent = '$' + formatNumber(data.ingresos.ingresos_dia_usd);
    document.getElementById('ingresos-mes').textContent = '$' + formatNumber(data.ingresos.ingresos_mes_usd);
    document.getElementById('ingresos-ano').textContent = '$' + formatNumber(data.ingresos.ingresos_ano_usd);

    document.getElementById('costos-dia').textContent = '$' + formatNumber(data.resumen.costos_totales_dia_usd);
    document.getElementById('costos-mes').textContent = '$' + formatNumber(data.resumen.costos_totales_dia_usd * 30);
    document.getElementById('costos-ano').textContent = '$' + formatNumber(data.resumen.costos_totales_dia_usd * 365);

    document.getElementById('utilidad-dia').textContent = '$' + formatNumber(data.resumen.utilidad_dia_usd);
    document.getElementById('utilidad-mes').textContent = '$' + formatNumber(data.resumen.utilidad_mes_usd);
    document.getElementById('utilidad-ano').textContent = '$' + formatNumber(data.resumen.utilidad_ano_usd);

    document.getElementById('margen-utilidad').textContent = data.resumen.margen_utilidad_porcentaje.toFixed(1) + '%';
    document.getElementById('roi-anos').textContent = data.capex_opex.roi_anos.toFixed(1);

    // Ahorro SA7
    document.getElementById('tn-sa7-dia').textContent = formatNumber(data.ahorro_sa7.tn_sa7_ahorradas_dia);
    document.getElementById('tn-sa7-mes').textContent = formatNumber(data.ahorro_sa7.tn_sa7_ahorradas_mes);
    document.getElementById('tn-sa7-ano').textContent = formatNumber(data.ahorro_sa7.tn_sa7_ahorradas_ano);
    document.getElementById('ahorro-usd-dia').textContent = '$' + formatNumber(data.ahorro_sa7.ahorro_usd_dia);
    document.getElementById('ahorro-usd-mes').textContent = '$' + formatNumber(data.ahorro_sa7.ahorro_usd_mes);
    document.getElementById('ahorro-usd-ano').textContent = '$' + formatNumber(data.ahorro_sa7.ahorro_usd_ano);
    document.getElementById('precio-sa7').textContent = '$' + data.ahorro_sa7.precio_sa7_tn_usd;

    // Costos operativos
    document.getElementById('elec-dia').textContent = '$' + formatNumber(data.costos_operativos.electricidad_dia_usd);
    document.getElementById('elec-mes').textContent = '$' + formatNumber(data.costos_operativos.electricidad_dia_usd * 30);
    document.getElementById('elec-ano').textContent = '$' + formatNumber(data.costos_operativos.electricidad_dia_usd * 365);

    document.getElementById('mano-dia').textContent = '$' + formatNumber(data.costos_operativos.mano_obra_dia_usd);
    document.getElementById('mano-mes').textContent = '$' + formatNumber(data.costos_operativos.mano_obra_dia_usd * 30);
    document.getElementById('mano-ano').textContent = '$' + formatNumber(data.costos_operativos.mano_obra_dia_usd * 365);

    document.getElementById('mant-dia').textContent = '$' + formatNumber(data.costos_operativos.mantenimiento_dia_usd);
    document.getElementById('mant-mes').textContent = '$' + formatNumber(data.costos_operativos.mantenimiento_dia_usd * 30);
    document.getElementById('mant-ano').textContent = '$' + formatNumber(data.costos_operativos.mantenimiento_dia_usd * 365);

    document.getElementById('seg-dia').textContent = '$' + formatNumber(data.costos_operativos.seguros_dia_usd);
    document.getElementById('seg-mes').textContent = '$' + formatNumber(data.costos_operativos.seguros_dia_usd * 30);
    document.getElementById('seg-ano').textContent = '$' + formatNumber(data.costos_operativos.seguros_dia_usd * 365);

    document.getElementById('admin-dia').textContent = '$' + formatNumber(data.costos_operativos.administrativos_dia_usd);
    document.getElementById('admin-mes').textContent = '$' + formatNumber(data.costos_operativos.administrativos_dia_usd * 30);
    document.getElementById('admin-ano').textContent = '$' + formatNumber(data.costos_operativos.administrativos_dia_usd * 365);

    document.getElementById('opex-dia').textContent = '$' + formatNumber(data.costos_operativos.total_dia_usd);
    document.getElementById('opex-mes').textContent = '$' + formatNumber(data.costos_operativos.total_mes_usd);
    document.getElementById('opex-ano').textContent = '$' + formatNumber(data.costos_operativos.total_ano_usd);

    // CAPEX
    document.getElementById('inversion-inicial').textContent = '$' + formatNumber(data.capex_opex.inversion_inicial_usd);
    document.getElementById('vida-util').textContent = data.capex_opex.vida_util_anos;
    document.getElementById('van').textContent = '$' + formatNumber(data.capex_opex.van_usd);
    document.getElementById('tir').textContent = data.capex_opex.tir_porcentaje.toFixed(1) + '%';

    // Tabla de sustratos
    const tablaSustratos = document.getElementById('tablaSustratos');
    tablaSustratos.innerHTML = '';
    
    if (data.costos_sustratos.detalle && data.costos_sustratos.detalle.length > 0) {
        data.costos_sustratos.detalle.forEach(sustrato => {
            const tr = document.createElement('tr');
            const ahorroClass = sustrato.ahorro_vs_sa7 >= 0 ? 'text-success' : 'text-danger';
            tr.innerHTML = `
                <td><strong>${sustrato.material}</strong></td>
                <td>${sustrato.tn}</td>
                <td>$${sustrato.precio_tn_usd}</td>
                <td>$${formatNumber(sustrato.costo_usd)}</td>
                <td>${formatNumber(sustrato.kw_generados)} KW</td>
                <td>${sustrato.tn_sa7_equivalente}</td>
                <td class="${ahorroClass}">$${formatNumber(sustrato.ahorro_vs_sa7)}</td>
            `;
            tablaSustratos.appendChild(tr);
        });
        
        // Fila de totales
        const trTotal = document.createElement('tr');
        trTotal.className = 'table-primary fw-bold';
        trTotal.innerHTML = `
            <td>TOTAL</td>
            <td>${formatNumber(data.costos_sustratos.detalle.reduce((sum, s) => sum + s.tn, 0))}</td>
            <td>-</td>
            <td>$${formatNumber(data.costos_sustratos.costo_total_dia_usd)}</td>
            <td>${formatNumber(data.costos_sustratos.detalle.reduce((sum, s) => sum + s.kw_generados, 0))} KW</td>
            <td>${formatNumber(data.ahorro_sa7.tn_sa7_ahorradas_dia)}</td>
            <td class="text-success">$${formatNumber(data.ahorro_sa7.ahorro_usd_dia)}</td>
        `;
        tablaSustratos.appendChild(trTotal);
    } else {
        tablaSustratos.innerHTML = '<tr><td colspan="7" class="text-center">No hay datos de mezcla disponibles</td></tr>';
    }

    // Gráficos
    crearGraficoCostos(data);
    crearGraficoFlujo(data);
}

function crearGraficoCostos(data) {
    const ctx = document.getElementById('chartCostos');
    
    if (chartCostos) {
        chartCostos.destroy();
    }

    chartCostos = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Sustratos', 'Electricidad', 'Mano de Obra', 'Mantenimiento', 'Seguros', 'Administrativos'],
            datasets: [{
                data: [
                    data.costos_sustratos.costo_total_dia_usd,
                    data.costos_operativos.electricidad_dia_usd,
                    data.costos_operativos.mano_obra_dia_usd,
                    data.costos_operativos.mantenimiento_dia_usd,
                    data.costos_operativos.seguros_dia_usd,
                    data.costos_operativos.administrativos_dia_usd
                ],
                backgroundColor: [
                    '#27ae60',
                    '#3498db',
                    '#9b59b6',
                    '#e74c3c',
                    '#f39c12',
                    '#95a5a6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': $' + formatNumber(context.parsed);
                        }
                    }
                }
            }
        }
    });
}

function crearGraficoFlujo(data) {
    const ctx = document.getElementById('chartFlujo');
    
    if (chartFlujo) {
        chartFlujo.destroy();
    }

    // Proyección mensual
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    const ingresosMes = Array(12).fill(data.ingresos.ingresos_mes_usd);
    const costosMes = Array(12).fill(data.resumen.costos_totales_dia_usd * 30);
    const utilidadMes = Array(12).fill(data.resumen.utilidad_mes_usd);

    chartFlujo = new Chart(ctx, {
        type: 'line',
        data: {
            labels: meses,
            datasets: [
                {
                    label: 'Ingresos',
                    data: ingresosMes,
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Costos',
                    data: costosMes,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Utilidad',
                    data: utilidadMes,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

function formatNumber(num) {
    if (typeof num !== 'number') {
        num = parseFloat(num) || 0;
    }
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
