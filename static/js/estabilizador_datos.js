// ESTABILIZADOR DE DATOS PARA SENSORES INTERMITENTES
console.log("🔧 Cargando estabilizador de datos...");

// Cache para mantener los últimos valores válidos
let cacheDatos = {
    presiones: {
        '040PT01': { valor: null, timestamp: null, intentos: 0 },
        '050PT01': { valor: null, timestamp: null, intentos: 0 }
    },
    temperaturas: {
        '040TT01': { valor: null, timestamp: null, intentos: 0 },
        '050TT01': { valor: null, timestamp: null, intentos: 0 }
    },
    niveles: {
        '040LT01': { valor: null, timestamp: null, intentos: 0 },
        '050LT01': { valor: null, timestamp: null, intentos: 0 }
    },
    flujos: {
        '040FT01': { valor: null, timestamp: null, intentos: 0 },
        '050FT01': { valor: null, timestamp: null, intentos: 0 }
    }
};

// Configuración del estabilizador
const CONFIG_ESTABILIZADOR = {
    maxReintentos: 3,
    timeoutValidez: 60000, // 1 minuto
    intervaloPruebaConexion: 5000, // 5 segundos
    variacionMaxima: 20 // % de variación máxima permitida
};

// Función para obtener datos estabilizados
async function obtenerDatosEstabilizados(endpoint, sensor) {
    const cache = obtenerCache(sensor);
    
    try {
        const response = await fetch(endpoint, { timeout: 3000 });
        const data = await response.json();
        
        if (data && data.valor !== undefined && data.valor !== null) {
            // Validar que el valor no sea demasiado diferente del anterior
            if (cache.valor !== null) {
                const variacion = Math.abs((data.valor - cache.valor) / cache.valor * 100);
                if (variacion > CONFIG_ESTABILIZADOR.variacionMaxima) {
                    console.warn(`⚠️ Variación alta en ${sensor}: ${variacion.toFixed(1)}%`);
                }
            }
            
            // Actualizar cache
            cache.valor = data.valor;
            cache.timestamp = Date.now();
            cache.intentos = 0;
            
            return {
                ...data,
                estabilizado: true,
                fuente: 'tiempo_real'
            };
        } else {
            throw new Error('Datos inválidos recibidos');
        }
    } catch (error) {
        console.warn(`⚠️ Error obteniendo ${sensor}:`, error.message);
        cache.intentos++;
        
        // Si tenemos un valor en cache y no es muy viejo, usarlo
        if (cache.valor !== null && (Date.now() - cache.timestamp) < CONFIG_ESTABILIZADOR.timeoutValidez) {
            return {
                valor: cache.valor,
                sensor: sensor,
                fecha_hora: new Date(cache.timestamp).toISOString(),
                estado: 'cache',
                estabilizado: true,
                fuente: 'cache_estabilizado',
                intentos: cache.intentos
            };
        }
        
        // Si no hay cache válido, devolver error
        return {
            valor: '--',
            sensor: sensor,
            fecha_hora: new Date().toISOString(),
            estado: 'error',
            estabilizado: false,
            fuente: 'error',
            intentos: cache.intentos
        };
    }
}

// Función para obtener el cache apropiado
function obtenerCache(sensor) {
    if (sensor.includes('PT')) return cacheDatos.presiones[sensor] || {};
    if (sensor.includes('TT')) return cacheDatos.temperaturas[sensor] || {};
    if (sensor.includes('LT')) return cacheDatos.niveles[sensor] || {};
    if (sensor.includes('FT')) return cacheDatos.flujos[sensor] || {};
    return {};
}

// Función para actualizar presiones con estabilización
async function actualizarPresionesEstabilizadas() {
    console.log("🔧 Actualizando presiones con estabilización...");
    
    try {
        // Obtener datos de ambas presiones en paralelo
        const [datos040, datos050] = await Promise.all([
            obtenerDatosEstabilizados('/040pt01', '040PT01'),
            obtenerDatosEstabilizados('/050pt01', '050PT01')
        ]);
        
        // Actualizar UI con datos estabilizados
        actualizarElementoPresion('presion-bio1-valor', datos040);
        actualizarElementoPresion('presion-bio2-valor', datos050);
        
        // Calcular diferencia
        if (datos040.valor !== '--' && datos050.valor !== '--') {
            const diferencia = Math.abs(datos040.valor - datos050.valor);
            document.getElementById('presion-diferencia').textContent = diferencia.toFixed(3) + ' bar';
            
            // Estado general
            const estadoGeneral = determinarEstadoPresiones(datos040.valor, datos050.valor);
            document.getElementById('presion-estado-general').textContent = estadoGeneral;
            document.getElementById('presion-estado-general').className = `badge bg-${estadoGeneral === 'NORMAL' ? 'success' : estadoGeneral === 'ALERTA' ? 'warning' : 'danger'}`;
        }
        
    } catch (error) {
        console.error('❌ Error actualizando presiones estabilizadas:', error);
    }
}

// Función para actualizar elemento de presión
function actualizarElementoPresion(elementId, datos) {
    const elemento = document.getElementById(elementId);
    if (elemento) {
        if (datos.valor !== '--') {
            elemento.textContent = parseFloat(datos.valor).toFixed(3);
            elemento.parentElement.classList.remove('text-danger');
            elemento.parentElement.classList.add('text-primary');
        } else {
            elemento.textContent = '--';
            elemento.parentElement.classList.add('text-danger');
        }
    }
    
    // Actualizar estado
    const estadoElement = document.getElementById(elementId.replace('-valor', '-estado'));
    if (estadoElement) {
        if (datos.fuente === 'cache_estabilizado') {
            estadoElement.textContent = 'Estabilizado';
            estadoElement.className = 'badge bg-warning';
        } else if (datos.fuente === 'tiempo_real') {
            estadoElement.textContent = 'En línea';
            estadoElement.className = 'badge bg-success';
        } else {
            estadoElement.textContent = 'Error';
            estadoElement.className = 'badge bg-danger';
        }
    }
    
    // Actualizar fecha
    const fechaElement = document.getElementById(elementId.replace('-valor', '-fecha'));
    if (fechaElement && datos.fecha_hora) {
        const fecha = new Date(datos.fecha_hora);
        fechaElement.textContent = `Última actualización: ${fecha.toLocaleTimeString()}`;
    }
}

// Función para determinar estado de presiones
function determinarEstadoPresiones(presion1, presion2) {
    const rango_normal = [0.02, 0.08];
    const rango_alerta = [0.01, 0.10];
    
    const p1_normal = presion1 >= rango_normal[0] && presion1 <= rango_normal[1];
    const p2_normal = presion2 >= rango_normal[0] && presion2 <= rango_normal[1];
    
    const p1_alerta = presion1 >= rango_alerta[0] && presion1 <= rango_alerta[1];
    const p2_alerta = presion2 >= rango_alerta[0] && presion2 <= rango_alerta[1];
    
    if (p1_normal && p2_normal) return 'NORMAL';
    if (p1_alerta && p2_alerta) return 'ALERTA';
    return 'CRÍTICO';
}

// Sistema de monitoreo de conexión
function iniciarMonitoreoConexion() {
    setInterval(async () => {
        try {
            const response = await fetch('/ping', { timeout: 2000 });
            if (response.ok) {
                document.body.classList.remove('conexion-perdida');
            } else {
                document.body.classList.add('conexion-perdida');
            }
        } catch (error) {
            document.body.classList.add('conexion-perdida');
        }
    }, CONFIG_ESTABILIZADOR.intervaloPruebaConexion);
}

// Sobrescribir función de presiones existente
if (typeof window.actualizarPresiones === 'function') {
    window.actualizarPresiones = actualizarPresionesEstabilizadas;
    console.log("✅ Función de presiones reemplazada por versión estabilizada");
}

// Exponer funciones globalmente
window.estabilizadorDatos = {
    obtenerDatosEstabilizados,
    actualizarPresionesEstabilizadas,
    cacheDatos,
    CONFIG_ESTABILIZADOR
};

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 Estabilizador de datos inicializado");
    iniciarMonitoreoConexion();
    
    // Aplicar actualizaciones estabilizadas cada 10 segundos
    setInterval(actualizarPresionesEstabilizadas, 10000);
});

console.log("✅ Estabilizador de datos cargado"); 