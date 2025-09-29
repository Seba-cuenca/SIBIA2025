/**
 * Script de inicialización para el histórico y registros 15min
 * Este script se asegura de que todo se inicialice correctamente al cargar la página
 */

console.log("🚀 Iniciando script de inicialización del histórico...");

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM cargado, iniciando inicialización...");
    
    // Función para inicializar el histórico cuando se muestra la pestaña
    function inicializarHistorico() {
        console.log("📊 Inicializando histórico diario...");
        
        // Verificar si las funciones están disponibles (nombres corregidos)
        if (typeof inicializarHistoricoDiario === 'function') {
            console.log("✅ Función inicializarHistoricoDiario disponible, ejecutando...");
            inicializarHistoricoDiario();
        } else {
            console.error("❌ Función inicializarHistoricoDiario no está disponible");
        }
        
        if (typeof cargarHistoricoDiario === 'function') {
            console.log("✅ Función cargarHistoricoDiario disponible, ejecutando...");
            cargarHistoricoDiario();
        } else {
            console.error("❌ Función cargarHistoricoDiario no está disponible");
        }
        
        // También actualizar el histórico horario automático
        if (typeof actualizarHistoricoHorarioAutomatico === 'function') {
            console.log("✅ Función actualizarHistoricoHorarioAutomatico disponible, ejecutando...");
            actualizarHistoricoHorarioAutomatico();
        } else {
            console.error("❌ Función actualizarHistoricoHorarioAutomatico no está disponible");
        }
    }
    
    // Función para inicializar los registros 15min
    function inicializarRegistros15min() {
        console.log("📊 Inicializando registros 15min...");
        
        if (typeof actualizarRegistros15minCorregido === 'function') {
            console.log("✅ Función actualizarRegistros15minCorregido disponible, ejecutando...");
            actualizarRegistros15minCorregido();
        } else {
            console.error("❌ Función actualizarRegistros15minCorregido no está disponible");
        }
    }
    
    // Listener para cuando se muestra la pestaña de histórico
    const historicoTabLink = document.querySelector('[data-bs-target="#historico"]');
    if (historicoTabLink) {
        historicoTabLink.addEventListener('shown.bs.tab', function (event) {
            console.log("📊 Pestaña Histórico mostrada");
            inicializarHistorico();
        });
        
        // También agregar listener para el click
        historicoTabLink.addEventListener('click', function (event) {
            console.log("🖱️ Click en pestaña Histórico");
            setTimeout(() => {
                inicializarHistorico();
            }, 100);
        });
    }
    
    // **AGREGAR: Listener para la pestaña de KPIs**
    const kpiTabLink = document.querySelector('[data-bs-target="#kpis"]');
    if (kpiTabLink) {
        kpiTabLink.addEventListener('shown.bs.tab', function (event) {
            console.log("📊 Pestaña KPIs mostrada");
            if (typeof inicializarGraficosKPI === 'function') {
                console.log("✅ Función inicializarGraficosKPI disponible, ejecutando...");
                inicializarGraficosKPI();
            } else {
                console.error("❌ Función inicializarGraficosKPI no está disponible");
            }
        });
        
        kpiTabLink.addEventListener('click', function (event) {
            console.log("🖱️ Click en pestaña KPIs");
            setTimeout(() => {
                if (typeof inicializarGraficosKPI === 'function') {
                    inicializarGraficosKPI();
                }
            }, 100);
        });
    }
    
    // Verificar si la pestaña ya está activa al cargar
    const pestanaHistoricoActiva = document.querySelector('#historico.active');
    if (pestanaHistoricoActiva) {
        console.log("📊 Pestaña Histórico ya está activa, inicializando...");
        setTimeout(() => {
            inicializarHistorico();
        }, 500);
    }
    
    // **NUEVO: Verificar si la pestaña de KPIs está activa**
    const pestanaKpiActiva = document.querySelector('#kpis.active');
    if (pestanaKpiActiva) {
        console.log("📊 Pestaña KPIs ya está activa, inicializando...");
        setTimeout(() => {
            if (typeof inicializarGraficosKPI === 'function') {
                inicializarGraficosKPI();
            }
        }, 500);
    }
    
    // Listener para la pestaña de registros 15min
    const registrosTabLink = document.querySelector('[data-bs-target="#registros-15min"]');
    if (registrosTabLink) {
        registrosTabLink.addEventListener('shown.bs.tab', function (event) {
            console.log("📊 Pestaña Registros 15min mostrada");
            inicializarRegistros15min();
        });
        
        registrosTabLink.addEventListener('click', function (event) {
            console.log("🖱️ Click en pestaña Registros 15min");
            setTimeout(() => {
                inicializarRegistros15min();
            }, 100);
        });
    }
    
    // Verificar qué pestaña está activa actualmente
    const pestanaActiva = document.querySelector('.tab-pane.active');
    if (pestanaActiva) {
        console.log("🎯 Pestaña activa:", pestanaActiva.id);
        
        if (pestanaActiva.id === 'historico') {
            console.log("📊 Inicializando histórico automáticamente...");
            setTimeout(() => {
                inicializarHistorico();
            }, 1000);
        } else if (pestanaActiva.id === 'registros-15min') {
            console.log("📊 Inicializando registros 15min automáticamente...");
            setTimeout(() => {
                inicializarRegistros15min();
            }, 1000);
        } else if (pestanaActiva.id === 'kpis') {
            console.log("📊 Inicializando KPIs automáticamente...");
            setTimeout(() => {
                if (typeof inicializarGraficosKPI === 'function') {
                    inicializarGraficosKPI();
                }
            }, 1000);
        }
    }
    
    // Actualización automática cada 5 minutos
    setInterval(() => {
        const pestanaActiva = document.querySelector('.tab-pane.active');
        if (pestanaActiva && pestanaActiva.id === 'historico') {
            console.log("🔄 Actualización automática del histórico...");
            inicializarHistorico();
        } else if (pestanaActiva && pestanaActiva.id === 'registros-15min') {
            console.log("🔄 Actualización automática de registros 15min...");
            inicializarRegistros15min();
        } else if (pestanaActiva && pestanaActiva.id === 'kpis') {
            console.log("🔄 Actualización automática de KPIs...");
            if (typeof inicializarGraficosKPI === 'function') {
                inicializarGraficosKPI();
            }
        }
    }, 300000); // 5 minutos
});

// Funciones de utilidad para forzar actualizaciones
window.forzarActualizacionHistorico = function() {
    console.log("🔧 Forzando actualización del histórico...");
    
    if (typeof inicializarHistoricoDiario === 'function') {
        inicializarHistoricoDiario();
    }
    
    if (typeof cargarHistoricoDiario === 'function') {
        cargarHistoricoDiario();
    }
    
    if (typeof actualizarHistoricoHorarioAutomatico === 'function') {
        actualizarHistoricoHorarioAutomatico();
    }
    
    console.log("✅ Actualización forzada completada");
};

window.forzarActualizacionRegistros15min = function() {
    console.log("🔧 Forzando actualización de registros 15min...");
    
    if (typeof actualizarRegistros15minCorregido === 'function') {
        actualizarRegistros15minCorregido();
    }
    
    console.log("✅ Actualización forzada completada");
};

// **NUEVA: Función para forzar actualización de KPIs**
window.forzarActualizacionKPIs = function() {
    console.log("🔧 Forzando actualización de KPIs...");
    
    if (typeof inicializarGraficosKPI === 'function') {
        inicializarGraficosKPI();
    }
    
    console.log("✅ Actualización forzada de KPIs completada");
};

console.log("✅ Script de inicialización cargado");
console.log("📌 Funciones disponibles:");
console.log("  - forzarActualizacionHistorico()");
console.log("  - forzarActualizacionRegistros15min()");
console.log("  - forzarActualizacionKPIs()"); 