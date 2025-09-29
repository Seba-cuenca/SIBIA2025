// ===== FILTROS DE TIEMPO PARA HISTÓRICOS - SIBIA =====
console.log("⏰ Cargando módulo de filtros de tiempo...");

/**
 * Inicializa los filtros de tiempo en todos los históricos
 */
function inicializarFiltrosTiempo() {
    console.log("🚀 Inicializando filtros de tiempo...");
    
    // Agregar filtros a histórico diario
    agregarFiltroHistoricoDiario();
    
    // Agregar filtros a histórico de gases
    agregarFiltroHistoricoGases();
    
    // Agregar filtros a registros 15min
    agregarFiltroRegistros15min();
    
    // Agregar filtros a histórico semanal
    agregarFiltroHistoricoSemanal();
}

/**
 * Agrega filtros de tiempo al histórico diario
 */
function agregarFiltroHistoricoDiario() {
    const contenedor = document.querySelector('#historico .card-header');
    if (!contenedor) return;
    
    const filtroHTML = `
        <div class="d-flex align-items-center gap-2 ms-auto">
            <label class="form-label mb-0">Período:</label>
            <select id="filtro-periodo-historico" class="form-select form-select-sm" style="width: auto;">
                <option value="1">Último día</option>
                <option value="7" selected>Última semana</option>
                <option value="30">Último mes</option>
                <option value="90">Últimos 3 meses</option>
                <option value="365">Último año</option>
            </select>
            <button id="btn-aplicar-filtro-historico" class="btn btn-primary btn-sm">
                <i class="fas fa-filter"></i> Aplicar
            </button>
        </div>
    `;
    
    contenedor.insertAdjacentHTML('beforeend', filtroHTML);
    
    // Evento para aplicar filtro
    document.getElementById('btn-aplicar-filtro-historico').addEventListener('click', function() {
        const dias = document.getElementById('filtro-periodo-historico').value;
        cargarHistoricoDiario(parseInt(dias));
    });
}

/**
 * Agrega filtros de tiempo al histórico de gases
 */
function agregarFiltroHistoricoGases() {
    const contenedor = document.querySelector('#gases-biodigestores .card-header');
    if (!contenedor) return;
    
    const filtroHTML = `
        <div class="d-flex align-items-center gap-2 ms-auto">
            <label class="form-label mb-0">Período:</label>
            <select id="filtro-periodo-gases" class="form-select form-select-sm" style="width: auto;">
                <option value="1">Último día</option>
                <option value="7" selected>Última semana</option>
                <option value="30">Último mes</option>
                <option value="90">Últimos 3 meses</option>
            </select>
            <button id="btn-aplicar-filtro-gases" class="btn btn-primary btn-sm">
                <i class="fas fa-filter"></i> Aplicar
            </button>
        </div>
    `;
    
    contenedor.insertAdjacentHTML('beforeend', filtroHTML);
    
    // Evento para aplicar filtro
    document.getElementById('btn-aplicar-filtro-gases').addEventListener('click', function() {
        const dias = document.getElementById('filtro-periodo-gases').value;
        cargarHistoricoGases(parseInt(dias));
    });
}

/**
 * Agrega filtros de tiempo a registros 15min
 */
function agregarFiltroRegistros15min() {
    const contenedor = document.querySelector('#registros-15min .card-header');
    if (!contenedor) return;
    
    const filtroHTML = `
        <div class="d-flex align-items-center gap-2 ms-auto">
            <label class="form-label mb-0">Período:</label>
            <select id="filtro-periodo-15min" class="form-select form-select-sm" style="width: auto;">
                <option value="1">Último día</option>
                <option value="7" selected>Última semana</option>
                <option value="30">Último mes</option>
            </select>
            <button id="btn-aplicar-filtro-15min" class="btn btn-primary btn-sm">
                <i class="fas fa-filter"></i> Aplicar
            </button>
        </div>
    `;
    
    contenedor.insertAdjacentHTML('beforeend', filtroHTML);
    
    // Evento para aplicar filtro
    document.getElementById('btn-aplicar-filtro-15min').addEventListener('click', function() {
        const dias = document.getElementById('filtro-periodo-15min').value;
        cargarRegistros15min(parseInt(dias));
    });
}

/**
 * Agrega filtros de tiempo al histórico semanal
 */
function agregarFiltroHistoricoSemanal() {
    const contenedor = document.querySelector('#historico-semanal .card-header');
    if (!contenedor) return;
    
    const filtroHTML = `
        <div class="d-flex align-items-center gap-2 ms-auto">
            <label class="form-label mb-0">Período:</label>
            <select id="filtro-periodo-semanal" class="form-select form-select-sm" style="width: auto;">
                <option value="4">Últimas 4 semanas</option>
                <option value="8" selected>Últimas 8 semanas</option>
                <option value="12">Últimas 12 semanas</option>
                <option value="26">Último semestre</option>
            </select>
            <button id="btn-aplicar-filtro-semanal" class="btn btn-primary btn-sm">
                <i class="fas fa-filter"></i> Aplicar
            </button>
        </div>
    `;
    
    contenedor.insertAdjacentHTML('beforeend', filtroHTML);
    
    // Evento para aplicar filtro
    document.getElementById('btn-aplicar-filtro-semanal').addEventListener('click', function() {
        const semanas = document.getElementById('filtro-periodo-semanal').value;
        cargarHistoricoSemanal(parseInt(semanas));
    });
}

/**
 * Función para cargar histórico de gases con filtro
 */
function cargarHistoricoGases(dias = 7) {
    console.log(`💨 Cargando histórico de gases (últimos ${dias} días)...`);
    
    fetch(`/historico_gases?dias=${dias}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                mostrarError('Error cargando histórico de gases: ' + data.error);
                return;
            }
            actualizarGraficoGases(data);
        })
        .catch(error => {
            console.error('Error cargando histórico de gases:', error);
            mostrarError('Error de conexión al cargar histórico de gases');
        });
}

/**
 * Función para cargar registros 15min con filtro
 */
function cargarRegistros15min(dias = 7) {
    console.log(`⏰ Cargando registros 15min (últimos ${dias} días)...`);
    
    fetch(`/registros_15min?dias=${dias}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                mostrarError('Error cargando registros 15min: ' + data.error);
                return;
            }
            actualizarRegistros15min(data);
        })
        .catch(error => {
            console.error('Error cargando registros 15min:', error);
            mostrarError('Error de conexión al cargar registros 15min');
        });
}

/**
 * Función para cargar histórico semanal con filtro
 */
function cargarHistoricoSemanal(semanas = 8) {
    console.log(`📅 Cargando histórico semanal (últimas ${semanas} semanas)...`);
    
    fetch(`/historico_semanal?semanas=${semanas}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                mostrarError('Error cargando histórico semanal: ' + data.error);
                return;
            }
            actualizarHistoricoSemanal(data);
        })
        .catch(error => {
            console.error('Error cargando histórico semanal:', error);
            mostrarError('Error de conexión al cargar histórico semanal');
        });
}

/**
 * Función auxiliar para mostrar errores
 */
function mostrarError(mensaje) {
    if (typeof toastr !== 'undefined') {
        toastr.error(mensaje);
    } else {
        alert(mensaje);
    }
}

// Inicializar filtros cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que otros scripts se carguen
    setTimeout(inicializarFiltrosTiempo, 1000);
});

// Exportar funciones para uso global
window.inicializarFiltrosTiempo = inicializarFiltrosTiempo;
window.cargarHistoricoGases = cargarHistoricoGases;
window.cargarRegistros15min = cargarRegistros15min;
window.cargarHistoricoSemanal = cargarHistoricoSemanal; 