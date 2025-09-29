// ===== MATERIALES REALES PARA KPIs - SIBIA =====
console.log("📦 Cargando módulo de materiales reales para KPIs...");

/**
 * Obtiene los materiales realmente utilizados en la aplicación
 */
function obtenerMaterialesReales() {
    console.log("📦 Obteniendo materiales realmente utilizados...");
    
    return fetch('/obtener_materiales_reales')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error obteniendo materiales reales:', data.error);
                return obtenerMaterialesPorDefecto();
            }
            return data.materiales;
        })
        .catch(error => {
            console.error('Error de conexión obteniendo materiales reales:', error);
            return obtenerMaterialesPorDefecto();
        });
}

/**
 * Obtiene materiales por defecto basados en el stock actual
 */
function obtenerMaterialesPorDefecto() {
    console.log("📦 Obteniendo materiales por defecto desde stock...");
    
    return fetch('/obtener_stock_actual_json')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error obteniendo stock:', data.error);
                return [];
            }
            
            // Filtrar solo materiales con stock significativo
            const materialesConStock = Object.entries(data.materiales || {})
                .filter(([nombre, info]) => {
                    const stock = info.total_tn || 0;
                    return stock > 1.0; // Solo materiales con más de 1 TN
                })
                .map(([nombre, info]) => ({
                    nombre: nombre,
                    stock_actual: info.total_tn || 0,
                    st_porcentaje: info.total_solido || 0,
                    tipo: determinarTipoMaterial(nombre)
                }))
                .sort((a, b) => b.stock_actual - a.stock_actual); // Ordenar por stock descendente
            
            console.log("📦 Materiales con stock encontrados:", materialesConStock);
            return materialesConStock;
        })
        .catch(error => {
            console.error('Error obteniendo stock:', error);
            return [];
        });
}

/**
 * Determina el tipo de material basado en su nombre
 */
function determinarTipoMaterial(nombre) {
    const nombreLower = nombre.toLowerCase();
    
    // Materiales sólidos
    if (nombreLower.includes('silaje') || 
        nombreLower.includes('maiz') || 
        nombreLower.includes('sa') ||
        nombreLower.includes('expeller') ||
        nombreLower.includes('rumen') ||
        nombreLower.includes('descarte') ||
        nombreLower.includes('barrido') ||
        nombreLower.includes('decomiso') ||
        nombreLower.includes('fondo')) {
        return 'solido';
    }
    
    // Materiales líquidos
    if (nombreLower.includes('purin') || 
        nombreLower.includes('lactosa') || 
        nombreLower.includes('suero') ||
        nombreLower.includes('gomas')) {
        return 'liquido';
    }
    
    // Por defecto
    return 'solido';
}

/**
 * Actualiza los KPIs con materiales reales
 */
function actualizarKPIsConMaterialesReales() {
    console.log("📊 Actualizando KPIs con materiales reales...");
    
    obtenerMaterialesReales().then(materiales => {
        if (!materiales || materiales.length === 0) {
            console.warn("⚠️ No se encontraron materiales reales");
            return;
        }
        
        // Actualizar gráfico de consumo de materiales
        actualizarGraficoConsumoMateriales(materiales);
        
        // Actualizar tabla de materiales utilizados
        actualizarTablaMaterialesUtilizados(materiales);
        
        // Actualizar resumen de materiales
        actualizarResumenMateriales(materiales);
        
        console.log("✅ KPIs actualizados con materiales reales");
    });
}

/**
 * Actualiza el gráfico de consumo de materiales
 */
function actualizarGraficoConsumoMateriales(materiales) {
    const ctx = document.getElementById('kpiConsumoChart');
    if (!ctx) {
        console.warn("⚠️ No se encontró canvas para gráfico de consumo");
        return;
    }
    
    // Destruir gráfico existente si existe
    if (window.graficoConsumo) {
        window.graficoConsumo.destroy();
    }
    
    const labels = materiales.map(m => m.nombre);
    const data = materiales.map(m => m.stock_actual);
    const colors = materiales.map(m => {
        switch(m.tipo) {
            case 'solido': return 'rgba(255, 99, 132, 0.8)';
            case 'liquido': return 'rgba(54, 162, 235, 0.8)';
            default: return 'rgba(75, 192, 192, 0.8)';
        }
    });
    
    window.graficoConsumo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Stock Actual (TN)',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Stock de Materiales Utilizados'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Toneladas'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Materiales'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

/**
 * Actualiza la tabla de materiales utilizados
 */
function actualizarTablaMaterialesUtilizados(materiales) {
    const tabla = document.getElementById('tabla-materiales-kpi');
    if (!tabla) {
        console.warn("⚠️ No se encontró tabla de materiales KPI");
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Material</th>
                        <th>Tipo</th>
                        <th>Stock Actual</th>
                        <th>ST (%)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    materiales.forEach(material => {
        const estado = obtenerEstadoMaterial(material.stock_actual);
        const estadoClass = obtenerClaseEstado(estado);
        
        html += `
            <tr>
                <td><strong>${material.nombre}</strong></td>
                <td>
                    <span class="badge ${material.tipo === 'solido' ? 'bg-warning' : 'bg-info'}">
                        ${material.tipo.toUpperCase()}
                    </span>
                </td>
                <td>${material.stock_actual.toFixed(2)} TN</td>
                <td>${material.st_porcentaje.toFixed(1)}%</td>
                <td>
                    <span class="badge ${estadoClass}">${estado}</span>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    tabla.innerHTML = html;
}

/**
 * Actualiza el resumen de materiales
 */
function actualizarResumenMateriales(materiales) {
    const resumen = {
        total_materiales: materiales.length,
        solidos: materiales.filter(m => m.tipo === 'solido').length,
        liquidos: materiales.filter(m => m.tipo === 'liquido').length,
        stock_total: materiales.reduce((sum, m) => sum + m.stock_actual, 0),
        stock_solidos: materiales.filter(m => m.tipo === 'solido').reduce((sum, m) => sum + m.stock_actual, 0),
        stock_liquidos: materiales.filter(m => m.tipo === 'liquido').reduce((sum, m) => sum + m.stock_actual, 0)
    };
    
    // Actualizar elementos del resumen
    const elementos = {
        'total-materiales-kpi': resumen.total_materiales,
        'materiales-solidos-kpi': resumen.solidos,
        'materiales-liquidos-kpi': resumen.liquidos,
        'stock-total-kpi': resumen.stock_total.toFixed(2) + ' TN',
        'stock-solidos-kpi': resumen.stock_solidos.toFixed(2) + ' TN',
        'stock-liquidos-kpi': resumen.stock_liquidos.toFixed(2) + ' TN'
    };
    
    Object.entries(elementos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.textContent = valor;
        }
    });
}

/**
 * Determina el estado de un material basado en su stock
 */
function obtenerEstadoMaterial(stock) {
    if (stock > 1000) return 'EXCELENTE';
    if (stock > 500) return 'BUENO';
    if (stock > 100) return 'REGULAR';
    if (stock > 10) return 'BAJO';
    return 'CRÍTICO';
}

/**
 * Obtiene la clase CSS para el estado
 */
function obtenerClaseEstado(estado) {
    switch(estado) {
        case 'EXCELENTE': return 'bg-success';
        case 'BUENO': return 'bg-primary';
        case 'REGULAR': return 'bg-warning';
        case 'BAJO': return 'bg-orange';
        case 'CRÍTICO': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que otros scripts se carguen
    setTimeout(() => {
        // Si estamos en la pestaña de KPIs, actualizar materiales
        if (document.querySelector('#kpis')?.classList.contains('show')) {
            actualizarKPIsConMaterialesReales();
        }
    }, 1000);
});

// Exportar funciones para uso global
window.obtenerMaterialesReales = obtenerMaterialesReales;
window.actualizarKPIsConMaterialesReales = actualizarKPIsConMaterialesReales; 