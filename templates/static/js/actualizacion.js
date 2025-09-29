// Variables globales
let actualizacionAutomatica = false;
let intervaloActualizacion = null;
const INTERVALO_MS = 60000; // Actualizar cada minuto

// Variables para KPIs de energía
let intervaloKPIs = null;
const INTERVALO_KPIS_MS = 3000; // Actualizar KPIs cada 3 segundos

// Función para mostrar/ocultar el spinner de carga
function toggleSpinner(mostrar) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) spinner.style.display = mostrar ? 'block' : 'none';
}

// Función para mostrar mensajes de estado
function mostrarMensaje(mensaje, tipo = 'info') {
    const contenedor = document.getElementById('estadoActualizacion');
    if (!contenedor) return;
    contenedor.textContent = mensaje;
    contenedor.className = `alert alert-${tipo}`;
    contenedor.style.display = 'block';
    setTimeout(() => {
        contenedor.style.display = 'none';
    }, 3000);
}

// Función para actualizar los datos
async function actualizarDatos() {
    try {
        toggleSpinner(true);

        // Actualizar tabla de stock actual
        const respStock = await fetch('/obtener_stock_actual');
        const dataStock = await respStock.json();
        actualizarTablaStock(dataStock);

        // Si tienes endpoints para planificación y resumen, puedes descomentar y adaptar:
        // const respPlan = await fetch('/obtener_planificacion');
        // const dataPlan = await respPlan.json();
        // actualizarPlanificacion(dataPlan);

        // const respResumen = await fetch('/obtener_resumen');
        // const dataResumen = await respResumen.json();
        // actualizarResumen(dataResumen);

        mostrarMensaje('Datos actualizados correctamente', 'success');
    } catch (error) {
        console.error('Error al actualizar datos:', error);
        mostrarMensaje('Error al actualizar los datos', 'danger');
    } finally {
        toggleSpinner(false);
    }
}

// Función para actualizar los KPIs de energía cada 3 segundos
async function actualizarKPIsEnergia() {
    try {
        // Obtener datos de energía desde el endpoint
        const response = await fetch('/datos_kpi');
        const data = await response.json();
        
        if (data.estado === 'ok') {
            // Actualizar tarjeta de Generación
            const generacionValor = document.getElementById('energia-generacion-valor');
            const generacionEstado = document.getElementById('energia-generacion-estado');
            const generacionFecha = document.getElementById('energia-generacion-fecha');
            
            if (generacionValor) generacionValor.textContent = data.kwGen.toFixed(1);
            if (generacionEstado) generacionEstado.textContent = 'Conectado';
            if (generacionFecha) {
                // Convertir fecha a hora argentina
                const fecha = new Date(data.fecha);
                const horaArgentina = fecha.toLocaleString('es-AR', {
                    timeZone: 'America/Argentina/Buenos_Aires',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                generacionFecha.textContent = horaArgentina;
            }
            
            // Actualizar tarjeta de Energía Inyectada
            const inyectadaValor = document.getElementById('energia-inyectada-valor');
            const inyectadaEstado = document.getElementById('energia-inyectada-estado');
            const inyectadaFecha = document.getElementById('energia-inyectada-fecha');
            
            if (inyectadaValor) inyectadaValor.textContent = data.kwDesp.toFixed(1);
            if (inyectadaEstado) inyectadaEstado.textContent = 'Conectado';
            if (inyectadaFecha) {
                // Usar la misma fecha pero con variación para simular actualización
                const fecha = new Date(data.fecha);
                const horaArgentina = fecha.toLocaleString('es-AR', {
                    timeZone: 'America/Argentina/Buenos_Aires',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                inyectadaFecha.textContent = horaArgentina;
            }
            
            // Actualizar tarjeta de Consumo Planta
            const consumoValor = document.getElementById('energia-consumo-valor');
            const consumoEstado = document.getElementById('energia-consumo-estado');
            
            if (consumoValor) consumoValor.textContent = data.kwPta.toFixed(1);
            if (consumoEstado) consumoEstado.textContent = 'Conectado';
            
            // Actualizar tarjeta de % Producción
            const porcentajeValor = document.getElementById('energia-porcentaje-valor');
            const porcentajeBarra = document.getElementById('energia-porcentaje-barra');
            const porcentajeColor = document.getElementById('energia-porcentaje-color');
            
            if (porcentajeValor && porcentajeBarra) {
                const porcentaje = Math.min(100, (data.kwGen / 1000) * 100);
                porcentajeValor.textContent = porcentaje.toFixed(1);
                porcentajeBarra.style.width = porcentaje + '%';
                porcentajeBarra.setAttribute('aria-valuenow', porcentaje);
                
                // Cambiar color según el porcentaje
                if (porcentajeColor) {
                    if (porcentaje >= 80) {
                        porcentajeColor.textContent = 'Excelente';
                        porcentajeColor.className = 'small text-success';
                        porcentajeBarra.className = 'progress-bar bg-success';
                    } else if (porcentaje >= 60) {
                        porcentajeColor.textContent = 'Bueno';
                        porcentajeColor.className = 'small text-warning';
                        porcentajeBarra.className = 'progress-bar bg-warning';
                    } else {
                        porcentajeColor.textContent = 'Bajo';
                        porcentajeColor.className = 'small text-danger';
                        porcentajeBarra.className = 'progress-bar bg-danger';
                    }
                }
            }
            
        } else if (data.estado === 'fallback') {
            // Usar datos de fallback
            const generacionValor = document.getElementById('energia-generacion-valor');
            const generacionEstado = document.getElementById('energia-generacion-estado');
            const generacionFecha = document.getElementById('energia-generacion-fecha');
            
            if (generacionValor) generacionValor.textContent = data.kwGen.toFixed(1);
            if (generacionEstado) generacionEstado.textContent = 'Modo Fallback';
            if (generacionFecha) {
                const ahora = new Date();
                const horaArgentina = ahora.toLocaleString('es-AR', {
                    timeZone: 'America/Argentina/Buenos_Aires',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                generacionFecha.textContent = horaArgentina;
            }
            
            // Actualizar otras tarjetas con datos de fallback
            const inyectadaValor = document.getElementById('energia-inyectada-valor');
            const consumoValor = document.getElementById('energia-consumo-valor');
            
            if (inyectadaValor) inyectadaValor.textContent = '0.0';
            if (consumoValor) consumoValor.textContent = '0.0';
            
        } else {
            // Estado desconectado o error
            const generacionEstado = document.getElementById('energia-generacion-estado');
            const inyectadaEstado = document.getElementById('energia-inyectada-estado');
            const consumoEstado = document.getElementById('energia-consumo-estado');
            
            if (generacionEstado) generacionEstado.textContent = 'Desconectado';
            if (inyectadaEstado) inyectadaEstado.textContent = 'Desconectado';
            if (consumoEstado) consumoEstado.textContent = 'Desconectado';
        }
        
    } catch (error) {
        console.error('Error al actualizar KPIs de energía:', error);
        // En caso de error, mostrar estado desconectado
        const generacionEstado = document.getElementById('energia-generacion-estado');
        const inyectadaEstado = document.getElementById('energia-inyectada-estado');
        const consumoEstado = document.getElementById('energia-consumo-estado');
        
        if (generacionEstado) generacionEstado.textContent = 'Error';
        if (inyectadaEstado) inyectadaEstado.textContent = 'Error';
        if (consumoEstado) consumoEstado.textContent = 'Error';
    }
}

// Función para actualizar la tabla de stock actual
function actualizarTablaStock(data) {
    const tabla = document.querySelector('#stock-actual-table tbody');
    if (!tabla) return;
    tabla.innerHTML = '';

    // data es un objeto tipo { material: {total_tn, ...}, ... }
    Object.entries(data).forEach(([material, datos]) => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>${material}</td>
            <td>${Number(datos.total_tn).toFixed(2)}</td>
        `;
        tabla.appendChild(fila);
    });
}

// Si tienes funciones para planificación y resumen, adáptalas aquí
function actualizarPlanificacion(data) {
    // Implementa según tu estructura de HTML y datos
}

function actualizarResumen(data) {
    // Implementa según tu estructura de HTML y datos
}

// Event listener para el switch de actualización automática
document.addEventListener('DOMContentLoaded', () => {
    // Iniciar actualización automática de KPIs de energía cada 3 segundos
    console.log('Iniciando actualización automática de KPIs de energía...');
    actualizarKPIsEnergia(); // Primera actualización inmediata
    intervaloKPIs = setInterval(actualizarKPIsEnergia, INTERVALO_KPIS_MS);
    
    // Si tienes un switch para activar/desactivar la actualización automática, usa su id aquí
    const switchActualizacion = document.getElementById('controlActualizacion');
    if (switchActualizacion) {
        switchActualizacion.addEventListener('change', (e) => {
            actualizacionAutomatica = e.target.checked;
            if (actualizacionAutomatica) {
                mostrarMensaje('Actualización automática activada', 'info');
                actualizarDatos(); // Primera actualización inmediata
                intervaloActualizacion = setInterval(actualizarDatos, INTERVALO_MS);
            } else {
                mostrarMensaje('Actualización automática desactivada', 'warning');
                if (intervaloActualizacion) {
                    clearInterval(intervaloActualizacion);
                    intervaloActualizacion = null;
                }
            }
        });
        // Si el switch está activado al cargar, inicia la actualización automática
        if (switchActualizacion.checked) {
            actualizarDatos();
            intervaloActualizacion = setInterval(actualizarDatos, INTERVALO_MS);
        }
    } else {
        // Si no hay switch, puedes iniciar la actualización automática por defecto si lo deseas
        // actualizarDatos();
        // intervaloActualizacion = setInterval(actualizarDatos, INTERVALO_MS);
    }
});