// SCRIPT DE INICIALIZACIÓN SIBIA
console.log("🚀 === INICIALIZANDO SIBIA ===");

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM Cargado - Iniciando SIBIA");
    
    // Inicializar sistemas en orden
    setTimeout(() => {
        console.log("🔄 Inicializando sistemas...");
        
        // 1. Sistema de Gases Biodigestores
        if (typeof window.actualizarGasesBiodigestores === 'function') {
            console.log("🌬️ Iniciando sistema de gases...");
            window.actualizarGasesBiodigestores();
        }
        
        // 2. Sistema de Flujo Volumétrico
        if (typeof window.actualizarSistemaVolumetrico === 'function') {
            console.log("💧 Iniciando sistema volumétrico...");
            window.actualizarSistemaVolumetrico();
        }
        
        // 3. Sistema de Reconexión Automática
        if (typeof window.iniciarSistemaReconexion === 'function') {
            console.log("🔌 Iniciando sistema de reconexión...");
            window.iniciarSistemaReconexion();
        }
        
        // 4. Actualizar KPIs
        if (typeof window.actualizarKPIs === 'function') {
            console.log("📊 Actualizando KPIs...");
            window.actualizarKPIs();
        }
        
        // 5. Sistema de Energía
        if (typeof window.actualizarSistemaEnergiaCompleto === 'function') {
            console.log("⚡ Actualizando sistema de energía...");
            window.actualizarSistemaEnergiaCompleto();
        }
        
        console.log("✅ Todos los sistemas iniciados");
        
        // Configurar actualizaciones periódicas
        configurarActualizacionesPeriodicas();
        
    }, 2000); // Esperar 2 segundos para asegurar que todos los scripts estén cargados
});

// Configurar actualizaciones periódicas
function configurarActualizacionesPeriodicas() {
    console.log("⏰ Configurando actualizaciones periódicas...");
    
    // Actualizar gases cada 30 segundos
    setInterval(() => {
        if (typeof window.actualizarGasesBiodigestores === 'function') {
            window.actualizarGasesBiodigestores();
        }
    }, 30000);
    
    // Actualizar flujo volumétrico cada 30 segundos
    setInterval(() => {
        if (typeof window.actualizarSistemaVolumetrico === 'function') {
            window.actualizarSistemaVolumetrico();
        }
    }, 30000);
    
    // Actualizar KPIs cada 60 segundos
    setInterval(() => {
        if (typeof window.actualizarKPIs === 'function') {
            window.actualizarKPIs();
        }
    }, 60000);
    
    console.log("✅ Actualizaciones periódicas configuradas");
}

// Manejar errores globales
window.addEventListener('error', function(event) {
    console.error('❌ Error global:', event.error);
    console.error('   Archivo:', event.filename);
    console.error('   Línea:', event.lineno);
    console.error('   Columna:', event.colno);
});

// Verificar que las pestañas estén funcionando
document.addEventListener('shown.bs.tab', function (event) {
    const tabId = event.target.getAttribute('id');
    console.log(`📑 Pestaña activada: ${tabId}`);
    
    // Actualizar contenido según la pestaña
    switch(tabId) {
        case 'gases-biodigestores-tab':
            if (typeof window.actualizarGasesBiodigestores === 'function') {
                window.actualizarGasesBiodigestores();
            }
            break;
        case 'flujo-volumetrico-tab':
            if (typeof window.actualizarSistemaVolumetrico === 'function') {
                window.actualizarSistemaVolumetrico();
            }
            break;
        case 'kpis-tab':
            if (typeof window.actualizarKPIs === 'function') {
                window.actualizarKPIs();
            }
            break;
    }
});

console.log("✅ Script de inicialización cargado"); 