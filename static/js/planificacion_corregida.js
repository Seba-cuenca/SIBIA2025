// SCRIPT CORREGIDO PARA PLANIFICACIÓN SEMANAL Y MENSUAL

console.log("🔧 Cargando script corregido para planificación...");

function cargarPlanSemanalCorregido() {
    console.log("📅 Cargando planificación semanal (CORREGIDO)...");
    
    const contenedor = document.getElementById('contenido-plan-semanal');
    if (!contenedor) {
        console.error("❌ No se encontró contenedor de plan semanal");
        return;
    }
    
    // Mostrar indicador de carga
    contenedor.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando planificación semanal...</span>
            </div>
            <p class="mt-2">Cargando datos de planificación semanal...</p>
        </div>
    `;
    
    fetch('/planificacion_semanal')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📅 Datos plan semanal recibidos:", data);
            
            if (data.error) {
                mostrarErrorPlanSemanal(data.error);
                return;
            }
            
            generarContenidoPlanSemanal(data);
            console.log("✅ Plan semanal cargado correctamente");
        })
        .catch(error => {
            console.error('❌ Error cargando plan semanal:', error);
            mostrarErrorPlanSemanal('Error de conexión');
        });
}

function cargarPlanMensualCorregido() {
    console.log("📆 Cargando planificación mensual (CORREGIDO)...");
    
    const contenedor = document.getElementById('contenido-plan-mensual');
    if (!contenedor) {
        console.error("❌ No se encontró contenedor de plan mensual");
        return;
    }
    
    // Mostrar indicador de carga
    contenedor.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando planificación mensual...</span>
            </div>
            <p class="mt-2">Cargando datos de planificación mensual...</p>
        </div>
    `;
    
    fetch('/planificacion_mensual')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📆 Datos plan mensual recibidos:", data);
            
            if (data.error) {
                mostrarErrorPlanMensual(data.error);
                return;
            }
            
            generarContenidoPlanMensual(data);
            console.log("✅ Plan mensual cargado correctamente");
        })
        .catch(error => {
            console.error('❌ Error cargando plan mensual:', error);
            mostrarErrorPlanMensual('Error de conexión');
        });
}

function generarContenidoPlanSemanal(data) {
    const contenedor = document.getElementById('contenido-plan-semanal');
    if (!contenedor) return;
    
    // Actualizar fecha en el header
    const fechaElement = document.getElementById('fecha-plan-semanal');
    if (fechaElement) {
        const fecha = new Date();
        const opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        fechaElement.textContent = fecha.toLocaleDateString('es-ES', opciones);
    }
    
    let html = '<h4>Planificación Semanal</h4>';
    
    if (data && Object.keys(data).length > 0) {
        // Filtrar solo los días de la semana (excluir advertencias_generales)
        const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
        
        html += `
            <div class="table-responsive">
                <table class="table table-bordered table-hover">
                    <thead class="table-primary">
                        <tr>
                            <th>Día</th>
                            <th>Materiales Sólidos</th>
                            <th>Materiales Líquidos</th>
                            <th>KW Objetivo</th>
                            <th>KW Estimados</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        diasSemana.forEach(dia => {
            const diaData = data[dia];
            if (diaData) {
                const estadoBadge = diaData.completado 
                    ? '<span class="badge bg-success">Completado</span>' 
                    : '<span class="badge bg-warning">Pendiente</span>';
                
                let materialesSolidos = '';
                let materialesLiquidos = '';
                
                if (diaData.materiales_solidos) {
                    Object.entries(diaData.materiales_solidos).forEach(([material, info]) => {
                        materialesSolidos += `${material}: ${(info.cantidad || 0).toFixed(2)} TN<br>`;
                    });
                }
                
                if (diaData.materiales_liquidos) {
                    Object.entries(diaData.materiales_liquidos).forEach(([material, info]) => {
                        materialesLiquidos += `${material}: ${(info.cantidad || 0).toFixed(2)} TN<br>`;
                    });
                }
                
                html += `
                    <tr>
                        <td><strong>${dia}</strong><br><small class="text-muted">${diaData.fecha || ''}</small></td>
                        <td>${materialesSolidos || 'Sin datos'}</td>
                        <td>${materialesLiquidos || 'Sin datos'}</td>
                        <td>${(diaData.kw_objetivo || 0).toFixed(2)} KW</td>
                        <td>${(diaData.kw_generados || 0).toFixed(2)} KW</td>
                        <td>${estadoBadge}</td>
                    </tr>
                `;
            } else {
                html += `
                    <tr>
                        <td><strong>${dia}</strong></td>
                        <td colspan="5" class="text-muted">Sin planificación</td>
                    </tr>
                `;
            }
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        // Mostrar advertencias si existen
        if (data.advertencias_generales && data.advertencias_generales.length > 0) {
            html += `
                <div class="alert alert-warning mt-3">
                    <h6><i class="fas fa-exclamation-triangle"></i> Advertencias:</h6>
                    <ul class="mb-0">
                        ${data.advertencias_generales.map(adv => `<li>${adv}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
    } else {
        html += '<div class="alert alert-info">No hay datos de planificación semanal disponibles.</div>';
    }
    
    contenedor.innerHTML = html;
}

function generarContenidoPlanMensual(data) {
    const contenedor = document.getElementById('contenido-plan-mensual');
    if (!contenedor) return;
    
    // Actualizar fecha en el header
    const fechaElement = document.getElementById('fecha-plan-mensual');
    if (fechaElement) {
        const fecha = new Date();
        const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        fechaElement.textContent = `${meses[fecha.getMonth()]} ${fecha.getFullYear()}`;
    }
    
    let html = '<h4>Planificación Mensual</h4>';
    
    if (data.planificacion_mensual && Object.keys(data.planificacion_mensual).length > 0) {
        Object.entries(data.planificacion_mensual).forEach(([semanaKey, semanaData]) => {
            html += `<h5>${semanaKey}</h5>`;
            html += `
                <div class="table-responsive mb-4">
                    <table class="table table-bordered table-sm">
                        <thead class="table-secondary">
                            <tr>
                                <th>Día</th>
                                <th>Materiales Sólidos</th>
                                <th>Materiales Líquidos</th>
                                <th>KW Objetivo</th>
                                <th>KW Estimados</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            if (semanaData && typeof semanaData === 'object') {
                Object.entries(semanaData).forEach(([diaKey, diaData]) => {
                    if (diaData && typeof diaData === 'object') {
                        const estadoBadge = diaData.completado 
                            ? '<span class="badge bg-success">Completado</span>' 
                            : '<span class="badge bg-warning">Pendiente</span>';
                        
                        let materialesSolidos = '';
                        let materialesLiquidos = '';
                        
                        if (diaData.materiales_solidos) {
                            Object.entries(diaData.materiales_solidos).forEach(([material, info]) => {
                                materialesSolidos += `${material}: ${(info.cantidad || 0).toFixed(2)} TN<br>`;
                            });
                        }
                        
                        if (diaData.materiales_liquidos) {
                            Object.entries(diaData.materiales_liquidos).forEach(([material, info]) => {
                                materialesLiquidos += `${material}: ${(info.cantidad || 0).toFixed(2)} TN<br>`;
                            });
                        }
                        
                        html += `
                            <tr>
                                <td><strong>${diaData.dia_nombre || diaKey}</strong><br><small class="text-muted">${diaData.fecha || ''}</small></td>
                                <td>${materialesSolidos || 'Sin datos'}</td>
                                <td>${materialesLiquidos || 'Sin datos'}</td>
                                <td>${(diaData.kw_objetivo || 0).toFixed(2)} KW</td>
                                <td>${(diaData.kw_generados || 0).toFixed(2)} KW</td>
                                <td>${estadoBadge}</td>
                            </tr>
                        `;
                    }
                });
            }
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
        });
    } else {
        html += '<div class="alert alert-info">No hay datos de planificación mensual disponibles.</div>';
    }
    
    contenedor.innerHTML = html;
}

function mostrarErrorPlanSemanal(mensaje) {
    const contenedor = document.getElementById('contenido-plan-semanal');
    if (contenedor) {
        contenedor.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle"></i> Error cargando plan semanal</h5>
                <p>${mensaje}</p>
                <button class="btn btn-primary btn-sm" onclick="cargarPlanSemanalCorregido()">
                    <i class="fas fa-redo"></i> Reintentar
                </button>
            </div>
        `;
    }
}

function mostrarErrorPlanMensual(mensaje) {
    const contenedor = document.getElementById('contenido-plan-mensual');
    if (contenedor) {
        contenedor.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle"></i> Error cargando plan mensual</h5>
                <p>${mensaje}</p>
                <button class="btn btn-primary btn-sm" onclick="cargarPlanMensualCorregido()">
                    <i class="fas fa-redo"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// Exportar funciones globalmente
window.cargarPlanSemanalCorregido = cargarPlanSemanalCorregido;
window.cargarPlanMensualCorregido = cargarPlanMensualCorregido;

// Inicialización automática cuando se cargan las pestañas
document.addEventListener('DOMContentLoaded', function() {
    // Detectar cuando se hace clic en las pestañas
    const tabPlanSemanal = document.getElementById('plan-semanal-tab');
    const tabPlanMensual = document.getElementById('plan-mensual-tab');
    
    if (tabPlanSemanal) {
        tabPlanSemanal.addEventListener('click', function() {
            console.log("👆 Pestaña plan semanal clickeada - cargando datos...");
            setTimeout(cargarPlanSemanalCorregido, 500);
        });
    }
    
    if (tabPlanMensual) {
        tabPlanMensual.addEventListener('click', function() {
            console.log("👆 Pestaña plan mensual clickeada - cargando datos...");
            setTimeout(cargarPlanMensualCorregido, 500);
        });
    }
    
    // También ejecutar si las pestañas ya están activas
    setTimeout(() => {
        const pestanaSemanal = document.getElementById('plan-semanal');
        const pestanaMensual = document.getElementById('plan-mensual');
        
        if (pestanaSemanal && pestanaSemanal.classList.contains('active')) {
            console.log("📅 Pestaña plan semanal ya activa - cargando datos...");
            cargarPlanSemanalCorregido();
        }
        
        if (pestanaMensual && pestanaMensual.classList.contains('active')) {
            console.log("📆 Pestaña plan mensual ya activa - cargando datos...");
            cargarPlanMensualCorregido();
        }
    }, 1000);
});

console.log("✅ Script corregido para planificación cargado correctamente"); 