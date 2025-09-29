// SCRIPT CORREGIDO PARA REGISTROS DE 15 MINUTOS

console.log("🔧 Cargando script corregido para registros 15min...");

function actualizarRegistros15minCorregido() {
    console.log("🔄 Actualizando registros de 15 minutos (CORREGIDO)...");
    
    fetch('/registros_15min')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📊 Datos registros 15min recibidos:", data);
            
            if (data.status !== 'success') {
                console.error("❌ Error en registros 15min:", data.message);
                mostrarErrorRegistros15min();
                return;
            }
            
            // 1. Actualizar elementos específicos por ID
            actualizarElementosRegistros15min(data);
            
            // 2. Actualizar tabla específica
            actualizarTablaRegistros15min(data.registros);
            
            console.log("✅ Registros 15min actualizados correctamente");
        })
        .catch(error => {
            console.error('❌ Error actualizando registros 15min:', error);
            mostrarErrorRegistros15min();
        });
}

function actualizarElementosRegistros15min(data) {
    const resumen = data.resumen || {};
    
    // Actualizar elementos específicos
    const elementos = {
        'total-kw-generado-15min': (resumen.total_kw_generado || 0).toFixed(2),
        'total-kw-inyectado-15min': (resumen.total_kw_inyectado || 0).toFixed(2),
        'total-consumo-planta-15min': (resumen.total_consumo_planta || 0).toFixed(2),
        'total-registros-15min': resumen.total_registros || 0,
        'fecha-actual-15min': data.fecha_actual || 'N/A',
        'primer-registro-15min': resumen.primer_registro || 'N/A',
        'ultimo-registro-15min': resumen.ultimo_registro || 'N/A'
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
    
    // Actualizar barra de progreso
    const totalRegistros = resumen.total_registros || 0;
    const progreso = Math.min((totalRegistros / 96) * 100, 100);
    
    const barraProgreso = document.getElementById('progreso-registros-15min');
    if (barraProgreso) {
        barraProgreso.style.width = `${progreso}%`;
        barraProgreso.textContent = `${totalRegistros}/96 (${progreso.toFixed(1)}%)`;
        
        // Cambiar color según progreso
        barraProgreso.className = 'progress-bar';
        if (progreso < 30) {
            barraProgreso.classList.add('bg-danger');
        } else if (progreso < 70) {
            barraProgreso.classList.add('bg-warning');
        } else {
            barraProgreso.classList.add('bg-success');
        }
    }
}

function actualizarTablaRegistros15min(registros) {
    console.log(`📋 Actualizando tabla con ${registros ? registros.length : 0} registros...`);
    
    // Buscar la tabla por su ID correcto
    const tbody = document.getElementById('registros-15min-tbody');
    
    if (!tbody) {
        console.error("❌ No se encontró tbody 'registros-15min-tbody'");
        // Buscar tabla alternativa
        const tablaAlternativa = document.querySelector('#registros-15min table tbody');
        if (tablaAlternativa) {
            console.log("✅ Encontrada tabla alternativa");
            actualizarTablaGenericaRegistros15min(tablaAlternativa, registros);
        }
        return;
    }
    
    // Limpiar tabla
    tbody.innerHTML = '';
    
    if (!registros || registros.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-clock"></i> No hay registros disponibles
                    <br><small>Los registros se generan automáticamente cada 15 minutos</small>
                </td>
            </tr>
        `;
        return;
    }
    
    // Mostrar los últimos 15 registros (más recientes primero)
    const registrosMostrar = registros.slice(-15).reverse();
    
    registrosMostrar.forEach((registro, index) => {
        const fila = document.createElement('tr');
        
        // Formatear hora
        let hora = registro.hora || registro.timestamp || '-';
        if (hora.includes(' ')) {
            hora = hora.split(' ')[1]; // Tomar solo la parte de la hora
        }
        
        // Determinar estado y colores
        const esReciente = index === 0;
        const filaClass = esReciente ? 'table-success' : '';
        
        fila.className = filaClass;
        fila.innerHTML = `
            <td><strong>${hora}</strong></td>
            <td>${(registro.kw_generado || 0).toFixed(2)}</td>
            <td>${(registro.kw_spot || 0).toFixed(2)}</td>
            <td>${(registro.consumo_planta || 0).toFixed(2)}</td>
            <td><strong>${(registro.kw_inyectado || 0).toFixed(2)}</strong></td>
            <td>${registro.numero_registro || (registros.length - index)}</td>
            <td><span class="badge bg-success">AUTO</span></td>
        `;
        
        tbody.appendChild(fila);
    });
    
    console.log(`✅ Tabla actualizada con ${registrosMostrar.length} registros`);
}

function actualizarTablaGenericaRegistros15min(tbody, registros) {
    tbody.innerHTML = '';
    
    if (!registros || registros.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-clock"></i> No hay registros disponibles
                </td>
            </tr>
        `;
        return;
    }
    
    const ultimosRegistros = registros.slice(-10).reverse();
    ultimosRegistros.forEach(registro => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>${registro.hora || '-'}</td>
            <td>${(registro.kw_generado || 0).toFixed(2)}</td>
            <td>${(registro.kw_spot || 0).toFixed(2)}</td>
            <td>${(registro.consumo_planta || 0).toFixed(2)}</td>
            <td>${(registro.kw_inyectado || 0).toFixed(2)}</td>
            <td>${registro.numero_registro || '-'}</td>
            <td><span class="badge bg-success">AUTO</span></td>
        `;
        tbody.appendChild(fila);
    });
}

function mostrarErrorRegistros15min() {
    const tbody = document.getElementById('registros-15min-tbody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error cargando registros
                    <br><small>Verifique la conexión e intente nuevamente</small>
                </td>
            </tr>
        `;
    }
}

// Función para test directo
function testRegistros15minCorregido() {
    console.log("🧪 Test directo registros 15min...");
    actualizarRegistros15minCorregido();
}

// Exportar funciones globalmente
window.actualizarRegistros15minCorregido = actualizarRegistros15minCorregido;
window.testRegistros15minCorregido = testRegistros15minCorregido;

// Inicialización automática cuando se carga la pestaña
document.addEventListener('DOMContentLoaded', function() {
    // Detectar cuando se hace clic en la pestaña de registros 15min
    const tabRegistros15min = document.getElementById('registros-15min-tab');
    if (tabRegistros15min) {
        tabRegistros15min.addEventListener('click', function() {
            console.log("👆 Pestaña registros 15min clickeada - cargando datos...");
            setTimeout(actualizarRegistros15minCorregido, 500); // Esperar 500ms para que se active la pestaña
        });
    }
    
    // También ejecutar si la pestaña ya está activa
    setTimeout(() => {
        const pestanaActiva = document.getElementById('registros-15min');
        if (pestanaActiva && pestanaActiva.classList.contains('active')) {
            console.log("📊 Pestaña registros 15min ya activa - cargando datos...");
            actualizarRegistros15minCorregido();
        }
    }, 1000);
});

console.log("✅ Script corregido para registros 15min cargado correctamente"); 