// DIAGNÓSTICO URGENTE SIBIA
console.log("🚨 === DIAGNÓSTICO URGENTE SIBIA ===");

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log("🔍 Ejecutando diagnóstico urgente...");
        
        // 1. Verificar pestañas
        console.log("\n📑 VERIFICANDO PESTAÑAS:");
        const pestanasFlujo = document.getElementById('flujo-volumetrico-tab');
        const contenidoFlujo = document.getElementById('flujo-volumetrico');
        console.log("- Pestaña flujo volumétrico:", pestanasFlujo ? "✅ ENCONTRADA" : "❌ NO ENCONTRADA");
        console.log("- Contenido flujo volumétrico:", contenidoFlujo ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
        
        // 2. Verificar elementos de gases
        console.log("\n🌬️ VERIFICANDO ELEMENTOS DE GASES:");
        const elementosGases = [
            'co2-bio1', 'ch4-bio1', 'o2-bio1', 'h2s-bio1',
            'co2-bio2', 'ch4-bio2', 'o2-bio2', 'h2s-bio2',
            'co2-motor', 'ch4-motor', 'o2-motor', 'h2s-motor'
        ];
        
        elementosGases.forEach(id => {
            const elemento = document.getElementById(id);
            console.log(`- ${id}:`, elemento ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
        });
        
        // 3. Verificar registros 15min
        console.log("\n⏱️ VERIFICANDO REGISTROS 15MIN:");
        const elementosRegistros = [
            'total-kw-generado-15min', 'total-kw-inyectado-15min', 
            'total-consumo-planta-15min', 'total-registros-15min'
        ];
        
        elementosRegistros.forEach(id => {
            const elemento = document.getElementById(id);
            const valor = elemento ? elemento.textContent : 'NO ENCONTRADO';
            console.log(`- ${id}: ${valor}`);
        });
        
        // 4. Probar endpoints
        console.log("\n🌐 PROBANDO ENDPOINTS:");
        probarEndpoints();
        
        // 5. Verificar funciones JavaScript
        console.log("\n🔧 VERIFICANDO FUNCIONES:");
        const funciones = [
            'actualizarGasesBiodigestores',
            'actualizarSistemaVolumetrico', 
            'actualizarRegistros15min',
            'iniciarSistemaReconexion'
        ];
        
        funciones.forEach(func => {
            console.log(`- ${func}:`, typeof window[func] === 'function' ? "✅ DISPONIBLE" : "❌ NO DISPONIBLE");
        });
        
        // 6. Forzar actualización
        console.log("\n🔄 FORZANDO ACTUALIZACIÓN DE DATOS:");
        setTimeout(() => {
            forzarActualizacionCompleta();
        }, 2000);
        
    }, 1000);
});

async function probarEndpoints() {
    const endpoints = [
        '/registros_15min',
        '/040ait01ao1', '/040ait01ao2', '/040ait01ao3', '/040ait01ao4',
        '/050ait01ao1', '/050ait01ao2', '/050ait01ao3', '/050ait01ao4',
        '/040ft01', '/050ft01'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint, { timeout: 3000 });
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${endpoint}: OK - Valor: ${data.valor || data.resumen?.total_registros || 'N/A'}`);
            } else {
                console.log(`❌ ${endpoint}: Error ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: ${error.message}`);
        }
    }
}

function forzarActualizacionCompleta() {
    console.log("🚀 Forzando actualización completa...");
    
    // Actualizar gases
    if (typeof window.actualizarGasesBiodigestores === 'function') {
        console.log("🌬️ Actualizando gases...");
        window.actualizarGasesBiodigestores();
    }
    
    // Actualizar flujo volumétrico
    if (typeof window.actualizarSistemaVolumetrico === 'function') {
        console.log("💧 Actualizando flujo volumétrico...");
        window.actualizarSistemaVolumetrico();
    }
    
    // Actualizar registros 15min
    if (typeof window.actualizarRegistros15min === 'function') {
        console.log("⏱️ Actualizando registros 15min...");
        window.actualizarRegistros15min();
    } else {
        // Intentar con función corregida
        console.log("⏱️ Intentando con función corregida...");
        actualizarRegistros15minManual();
    }
}

async function actualizarRegistros15minManual() {
    try {
        const response = await fetch('/registros_15min');
        const data = await response.json();
        console.log("📊 Datos registros 15min:", data);
        
        if (data.status === 'success' && data.resumen) {
            // Actualizar elementos si existen
            const elementos = {
                'total-kw-generado-15min': data.resumen.total_kw_generado,
                'total-kw-inyectado-15min': data.resumen.total_kw_inyectado,
                'total-consumo-planta-15min': data.resumen.total_consumo_planta,
                'total-registros-15min': data.resumen.total_registros
            };
            
            Object.entries(elementos).forEach(([id, valor]) => {
                const elemento = document.getElementById(id);
                if (elemento) {
                    elemento.textContent = typeof valor === 'number' ? valor.toFixed(2) : valor;
                    console.log(`✅ Actualizado ${id}: ${valor}`);
                } else {
                    console.log(`❌ No encontrado elemento: ${id}`);
                }
            });
        }
    } catch (error) {
        console.error("❌ Error actualizando registros 15min:", error);
    }
}

// Mostrar resultado en pantalla
function mostrarResultadoDiagnostico() {
    const resultado = document.createElement('div');
    resultado.style.cssText = `
        position: fixed; top: 10px; right: 10px; z-index: 9999;
        background: #f8f9fa; border: 2px solid #007bff; border-radius: 8px;
        padding: 15px; max-width: 300px; font-family: monospace; font-size: 12px;
    `;
    resultado.innerHTML = `
        <h5>🔍 Diagnóstico SIBIA</h5>
        <div id="diagnostico-resultado">Ejecutando...</div>
        <button onclick="this.parentElement.remove()" style="margin-top: 10px;">Cerrar</button>
    `;
    document.body.appendChild(resultado);
    
    setTimeout(() => {
        document.getElementById('diagnostico-resultado').innerHTML = `
            <p>✅ Diagnóstico completado</p>
            <p>📋 Revisa la consola (F12) para detalles</p>
        `;
    }, 5000);
}

// Ejecutar al cargar
setTimeout(mostrarResultadoDiagnostico, 2000);

console.log("🚨 Diagnóstico urgente cargado"); 