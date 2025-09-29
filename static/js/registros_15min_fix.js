/**
 * Funciones corregidas para manejar los registros de 15 minutos
 */

// Función para actualizar los registros de 15 minutos con manejo correcto de elementos
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
            
            // 1. Actualizar los totales en las tarjetas
            actualizarTotalesRegistros15min(data.resumen);
            
            // 2. Actualizar la tabla de registros
            actualizarTablaRegistros15min(data.registros);
            
            // 3. Actualizar la barra de progreso
            actualizarProgresoRegistros15min(data.resumen);
            
            console.log("✅ Registros 15min actualizados correctamente");
        })
        .catch(error => {
            console.error('❌ Error actualizando registros 15min:', error);
            mostrarErrorRegistros15min();
        });
}

// Función para actualizar los totales en las tarjetas
function actualizarTotalesRegistros15min(resumen) {
    if (!resumen) {
        console.warn("⚠️ No hay resumen de registros 15min");
        return;
    }
    
    // IDs correctos según el HTML
    const elementos = {
        'resumen-total-kw-generado': resumen.total_kw_generado || 0,
        'resumen-total-kw-spot': resumen.total_kw_spot || 0,
        'resumen-total-consumo-planta': resumen.total_consumo_planta || 0,
        'resumen-total-kw-inyectado': resumen.total_kw_inyectado || 0,
        'resumen-registros-total': `${resumen.total_registros || 0} de 96 registros`,
        'resumen-progreso-dia': ((resumen.total_registros || 0) / 96 * 100).toFixed(1) + '%'
    };
    
    // Actualizar cada elemento
    Object.entries(elementos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            if (id.includes('kw') && typeof valor === 'number') {
                elemento.textContent = valor.toFixed(2) + ' KW';
            } else {
                elemento.textContent = valor;
            }
            console.log(`✅ Actualizado ${id}: ${elemento.textContent}`);
        } else {
            console.warn(`⚠️ Elemento no encontrado: ${id}`);
        }
    });
    
    // Actualizar barra de progreso
    const barraProgreso = document.getElementById('progreso-dia-barra');
    if (barraProgreso) {
        const porcentaje = ((resumen.total_registros || 0) / 96 * 100);
        barraProgreso.style.width = porcentaje + '%';
        barraProgreso.setAttribute('aria-valuenow', porcentaje);
    }
    
    // Actualizar información de configuración
    const configElements = {
        'config-intervalo': '15 minutos',
        'config-registros-dia': '96 registros',
        'config-hora-inicio': resumen.primer_registro || '00:15 hs',
        'config-hora-fin': resumen.ultimo_registro || '00:00 hs'
    };
    
    Object.entries(configElements).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.textContent = valor;
        }
    });
}

// Función para actualizar la tabla de registros
function actualizarTablaRegistros15min(registros) {
    // Buscar la tabla por su ID correcto
    const tabla = document.getElementById('tabla-registros-15min');
    
    if (!tabla) {
        console.error("❌ No se encontró la tabla de registros 15min");
        return;
    }
    
    // Limpiar tabla
    tabla.innerHTML = '';
    
    if (!registros || registros.length === 0) {
        tabla.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-clock"></i> No hay registros disponibles
                </td>
            </tr>
        `;
        return;
    }
    
    // Mostrar los últimos 10 registros (más recientes primero)
    const registrosMostrar = registros.slice(-10).reverse();
    
    registrosMostrar.forEach((registro, index) => {
        const fila = document.createElement('tr');
        
        // Formatear hora
        let hora = registro.hora || registro.timestamp || '-';
        if (hora.includes(' ')) {
            hora = hora.split(' ')[1]; // Tomar solo la parte de la hora
        }
        
        // Determinar estado
        const estado = registro.estado || 'AUTO';
        const badgeClass = estado === 'AUTO' ? 'bg-success' : 'bg-info';
        
        fila.innerHTML = `
            <td>${hora}</td>
            <td>${(registro.kw_generado || 0).toFixed(2)}</td>
            <td>${(registro.kw_spot || 0).toFixed(2)}</td>
            <td>${(registro.consumo_planta || 0).toFixed(2)}</td>
            <td>${(registro.kw_inyectado || 0).toFixed(2)}</td>
            <td>${registro.timestamp || '-'}</td>
            <td><span class="badge ${badgeClass}">${estado}</span></td>
        `;
        
        // Resaltar fila más reciente
        if (index === 0) {
            fila.classList.add('table-active');
        }
        
        tabla.appendChild(fila);
    });
    
    console.log(`✅ Tabla actualizada con ${registrosMostrar.length} registros`);
}

// Función para actualizar la barra de progreso
function actualizarProgresoRegistros15min(resumen) {
    if (!resumen) return;
    
    const totalRegistros = resumen.total_registros || 0;
    const porcentaje = (totalRegistros / 96) * 100;
    
    // Buscar barra de progreso
    const barraProgreso = document.getElementById('progreso-dia-barra');
    
    if (barraProgreso) {
        barraProgreso.style.width = porcentaje + '%';
        barraProgreso.setAttribute('aria-valuenow', porcentaje);
        
        // Cambiar color según progreso
        barraProgreso.className = 'progress-bar';
        if (porcentaje < 50) {
            barraProgreso.classList.add('bg-danger');
        } else if (porcentaje < 80) {
            barraProgreso.classList.add('bg-warning');
        } else {
            barraProgreso.classList.add('bg-info');
        }
    }
}

// Función para mostrar error
function mostrarErrorRegistros15min() {
    // Actualizar totales con ceros
    const elementosError = [
        'resumen-total-kw-generado',
        'resumen-total-kw-spot', 
        'resumen-total-consumo-planta',
        'resumen-total-kw-inyectado'
    ];
    
    elementosError.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.textContent = '0 KW';
            elemento.classList.add('text-danger');
        }
    });
    
    // Mostrar mensaje en la tabla
    const tabla = document.getElementById('tabla-registros-15min');
    if (tabla) {
        tabla.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error al cargar registros
                </td>
            </tr>
        `;
    }
}

// Función para test manual
function testRegistros15min() {
    console.log("🧪 Probando endpoint registros 15min...");
    fetch('/registros_15min')
        .then(response => response.json())
        .then(data => {
            console.log("✅ Respuesta del servidor:", data);
            console.log("📊 Resumen:", data.resumen);
            console.log("📝 Total registros:", data.registros?.length || 0);
            window.datosRegistros15min = data; // Guardar para debug
        })
        .catch(error => {
            console.error("❌ Error:", error);
        });
}

// Reemplazar la función original cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Iniciando fix para registros 15min...");
    
    // Reemplazar función global
    if (window.actualizarRegistros15min) {
        window.actualizarRegistros15minOriginal = window.actualizarRegistros15min;
        window.actualizarRegistros15min = actualizarRegistros15minCorregido;
        console.log("✅ Función actualizarRegistros15min reemplazada");
    }
    
    // Ejecutar actualización inicial después de 2 segundos
    setTimeout(() => {
        console.log("⏱️ Ejecutando actualización inicial de registros 15min...");
        actualizarRegistros15minCorregido();
    }, 2000);
    
    // Actualizar cada 30 segundos
    setInterval(actualizarRegistros15minCorregido, 30000);
});

// Exportar funciones para debug
window.testRegistros15min = testRegistros15min;
window.actualizarRegistros15minCorregido = actualizarRegistros15minCorregido;

console.log("✅ Fix de registros 15min cargado. Funciones disponibles:");
console.log("  - actualizarRegistros15minCorregido()");
console.log("  - testRegistros15min()"); 