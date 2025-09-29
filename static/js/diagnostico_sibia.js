// SCRIPT DE DIAGNÓSTICO SIBIA
console.log("🔍 === DIAGNÓSTICO SIBIA INICIADO ===");

// Verificar pestañas
function verificarPestanas() {
    console.log("📑 Verificando pestañas...");
    
    const pestanas = {
        'parametros-tab': 'Parámetros',
        'registro-material-tab': 'Registro Material',
        'stock-tab': 'Stock',
        'planificacion-diaria-tab': 'Planificación Diaria',
        'registros-15min-tab': 'Registros 15min',
        'historico-diario-tab': 'Histórico Diario',
        'seguimiento-horario-tab': 'Seguimiento Horario',
        'calculadora-tab': 'Calculadora Mezclas',
        'analisis-economico-tab': 'Análisis Económico',
        'kpis-tab': 'KPIs',
        'plan-semanal-tab': 'Plan Semanal',
        'plan-mensual-tab': 'Plan Mensual',
        'asistente-ia-tab': 'Asistente IA',
        'informes-tab': 'Informes',
        'gases-biodigestores-tab': 'Gases Biodigestores',
        'flujo-volumetrico-tab': 'Flujo Volumétrico'
    };
    
    let encontradas = 0;
    let faltantes = [];
    
    Object.entries(pestanas).forEach(([id, nombre]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            encontradas++;
            console.log(`✅ ${nombre}: ENCONTRADA`);
        } else {
            faltantes.push(nombre);
            console.log(`❌ ${nombre}: NO ENCONTRADA`);
        }
    });
    
    console.log(`\n📊 Resumen: ${encontradas}/${Object.keys(pestanas).length} pestañas encontradas`);
    if (faltantes.length > 0) {
        console.log(`❌ Pestañas faltantes: ${faltantes.join(', ')}`);
    }
}

// Verificar funciones JavaScript
function verificarFunciones() {
    console.log("\n🔧 Verificando funciones JavaScript...");
    
    const funciones = {
        // Gases
        'actualizarGasesBiodigestores': 'Actualizar gases biodigestores',
        'actualizarTablaComparacion': 'Actualizar tabla comparación',
        
        // Flujo volumétrico
        'actualizarTemperaturas': 'Actualizar temperaturas',
        'actualizarPresiones': 'Actualizar presiones',
        'actualizarFlujos': 'Actualizar flujos',
        'actualizarNiveles': 'Actualizar niveles',
        'actualizarBalanceVolumetrico': 'Actualizar balance volumétrico',
        'actualizarSistemaVolumetrico': 'Actualizar sistema volumétrico',
        
        // Reconexión
        'iniciarSistemaReconexion': 'Sistema de reconexión automática',
        
        // KPIs y energía
        'actualizarKPIs': 'Actualizar KPIs',
        'actualizarSistemaEnergiaCompleto': 'Actualizar sistema de energía'
    };
    
    let funcionesOk = 0;
    let funcionesFaltantes = [];
    
    Object.entries(funciones).forEach(([nombre, descripcion]) => {
        if (typeof window[nombre] === 'function') {
            funcionesOk++;
            console.log(`✅ ${descripcion}: DISPONIBLE`);
        } else {
            funcionesFaltantes.push(descripcion);
            console.log(`❌ ${descripcion}: NO DISPONIBLE`);
        }
    });
    
    console.log(`\n📊 Resumen: ${funcionesOk}/${Object.keys(funciones).length} funciones disponibles`);
    if (funcionesFaltantes.length > 0) {
        console.log(`❌ Funciones faltantes: ${funcionesFaltantes.join(', ')}`);
    }
}

// Verificar elementos del DOM
function verificarElementosDOM() {
    console.log("\n🎯 Verificando elementos del DOM...");
    
    const elementos = {
        // Gases biodigestores
        'co2-bio1': 'CO2 Biodigestor 1',
        'ch4-bio1': 'CH4 Biodigestor 1',
        'o2-bio1': 'O2 Biodigestor 1',
        'h2s-bio1': 'H2S Biodigestor 1',
        
        // Flujo volumétrico
        'temp-bio1-valor': 'Temperatura Biodigestor 1',
        'temp-bio2-valor': 'Temperatura Biodigestor 2',
        'presion-bio1-valor': 'Presión Biodigestor 1',
        'presion-bio2-valor': 'Presión Biodigestor 2',
        'flujo-bio1-valor': 'Flujo Biodigestor 1',
        'flujo-bio2-valor': 'Flujo Biodigestor 2',
        'nivel-bio1-valor': 'Nivel Biodigestor 1',
        'nivel-bio2-valor': 'Nivel Biodigestor 2'
    };
    
    let elementosOk = 0;
    let elementosFaltantes = [];
    
    Object.entries(elementos).forEach(([id, descripcion]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elementosOk++;
            const valor = elemento.textContent || '--';
            console.log(`✅ ${descripcion}: ${valor}`);
        } else {
            elementosFaltantes.push(descripcion);
            console.log(`❌ ${descripcion}: NO ENCONTRADO`);
        }
    });
    
    console.log(`\n📊 Resumen: ${elementosOk}/${Object.keys(elementos).length} elementos encontrados`);
}

// Verificar conexión con el servidor
async function verificarConexion() {
    console.log("\n🌐 Verificando conexión con el servidor...");
    
    try {
        const response = await fetch('/api/estado_conexion');
        const data = await response.json();
        
        if (data.conectado) {
            console.log("✅ Conexión con servidor: OK");
            console.log(`   - Base de datos: ${data.db_conectada ? 'CONECTADA' : 'DESCONECTADA'}`);
            console.log(`   - Registros hoy: ${data.registros_hoy || 0}`);
        } else {
            console.log("❌ Conexión con servidor: ERROR");
        }
    } catch (error) {
        console.log("❌ Error verificando conexión:", error.message);
    }
}

// Ejecutar diagnóstico completo
function ejecutarDiagnostico() {
    console.log("🚀 Ejecutando diagnóstico completo...\n");
    
    verificarPestanas();
    verificarFunciones();
    verificarElementosDOM();
    verificarConexion();
    
    console.log("\n🔍 === DIAGNÓSTICO COMPLETADO ===");
    console.log("💡 Si hay errores, revisa:");
    console.log("   1. Que todos los scripts estén cargados correctamente");
    console.log("   2. Que no haya errores de JavaScript en la consola");
    console.log("   3. Que el servidor esté funcionando correctamente");
    console.log("   4. Que la base de datos esté conectada");
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ejecutarDiagnostico);
} else {
    ejecutarDiagnostico();
}

// Exponer funciones globalmente
window.diagnosticoSIBIA = {
    verificarPestanas,
    verificarFunciones,
    verificarElementosDOM,
    verificarConexion,
    ejecutarDiagnostico
};

console.log("💡 Usa window.diagnosticoSIBIA.ejecutarDiagnostico() para repetir el diagnóstico"); 