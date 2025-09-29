// PARCHE PARA CORREGIR EL JAVASCRIPT DEL DASHBOARD HÍBRIDO
// Reemplazar la función guardarCambiosMateriales() existente

async function guardarCambiosMateriales() {
    console.log('💾 Guardando cambios de materiales (VERSIÓN CORREGIDA)...');
    
    const tabla = document.getElementById('tabla-gestion-materiales');
    if (!tabla) {
        console.error('❌ No se encontró la tabla de gestión de materiales');
        return;
    }
    
    const materiales = [];
    const filas = tabla.querySelectorAll('tbody tr');
    
    filas.forEach(fila => {
        const nombreMaterial = fila.getAttribute('data-material');
        if (!nombreMaterial) return;
        
        const inputs = fila.querySelectorAll('input, select');
        if (inputs.length < 14) return;
        
        const nombre = inputs[0].value;
        
        // CORREGIDO: Leer valores de laboratorio correctamente
        const st = parseFloat(inputs[1].value) || 0; // ST como porcentaje
        const sv = parseFloat(inputs[2].value) || 0; // SV como porcentaje
        const m3_tnsv = parseFloat(inputs[4].value) || 0; // M³/TNSV (calculado automáticamente)
        const metano = parseFloat(inputs[5].value) || 65; // CH4% 
        const carbohidrato_lab = parseFloat(inputs[6].value) || 0; // Carbohidratos Lab %
        const lipido_lab = parseFloat(inputs[7].value) || 0; // Lípidos Lab %
        const proteina_lab = parseFloat(inputs[8].value) || 0; // Proteínas Lab %
        
        // Obtener tipo del select específicamente
        const tipoSelect = fila.querySelector('select');
        const tipo = tipoSelect ? tipoSelect.value : 'solido';
        
        const densidad = parseFloat(inputs[10].value) || 1.0;
        
        // ENVIAR VALORES DE LABORATORIO COMO DECIMALES
        materiales.push({
            nombre: nombre,
            st: st / 100.0,  // Convertir porcentaje a decimal
            sv: sv / 100.0,  // Convertir porcentaje a decimal
            // NO enviar m3_tnsv - se calcula automáticamente en el servidor
            ch4: metano / 100.0,  // Convertir porcentaje a decimal
            carbohidratos_lab: carbohidrato_lab / 100.0,  // Valores de laboratorio como decimales
            lipidos_lab: lipido_lab / 100.0,
            proteinas_lab: proteina_lab / 100.0,
            // Mantener compatibilidad
            carbohidratos: carbohidrato_lab / 100.0,
            lipidos: lipido_lab / 100.0,
            proteinas: proteina_lab / 100.0,
            tipo: tipo,
            densidad: densidad,
            porcentaje_metano: metano  // Mantener como porcentaje
        });
        
        console.log(`📊 Material procesado: ${nombre}`);
        console.log(`   ST: ${st}% → ${st/100.0} (decimal)`);
        console.log(`   Carbohidratos: ${carbohidrato_lab}% → ${carbohidrato_lab/100.0} (decimal)`);
    });
    
    console.log('📊 Materiales a guardar:', materiales);
    
    // Enviar datos al servidor
    try {
        const response = await fetch('/actualizar_materiales_base', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                materiales: materiales
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert('✅ Cambios guardados correctamente en el servidor');
            console.log('✅ Respuesta del servidor:', result);
            // Recargar la tabla para mostrar los cambios
            await cargarGestionMaterialesEditable();
        } else {
            throw new Error(result.mensaje || 'Error al guardar cambios');
        }
    } catch (error) {
        console.error('Error guardando materiales:', error);
        alert('❌ Error al guardar cambios: ' + error.message);
    }
}
// 
FUNCIÓN PARA RECÁLCULO AUTOMÁTICO
function recalcularValoresAutomaticos(fila) {
    try {
        const inputs = fila.querySelectorAll('input, select');
        if (inputs.length < 14) return;
        
        // Obtener valores actuales
        const st = parseFloat(inputs[1].value) || 0; // ST %
        const sv = parseFloat(inputs[2].value) || 0; // SV %
        const carbohidrato_lab = parseFloat(inputs[6].value) || 0; // Carbohidratos Lab %
        const lipido_lab = parseFloat(inputs[7].value) || 0; // Lípidos Lab %
        const proteina_lab = parseFloat(inputs[8].value) || 0; // Proteínas Lab %
        
        // CALCULAR VALORES AUTOMÁTICAMENTE
        
        // 1. TNSV = ST × SV
        const tnsv = (st / 100.0) * (sv / 100.0);
        
        // 2. Valores CALCULADOS = ST × % Laboratorio
        const carbohidratos_calc = (st / 100.0) * (carbohidrato_lab / 100.0);
        const lipidos_calc = (st / 100.0) * (lipido_lab / 100.0);
        const proteinas_calc = (st / 100.0) * (proteina_lab / 100.0);
        
        // 3. M³/TNSV usando fórmula de biogás
        let m3_tnsv = 0;
        if (tnsv > 0) {
            const tn_solidos = 1.0 * (st / 100.0);
            const tn_carbohidratos = tn_solidos * carbohidratos_calc;
            const tn_lipidos = tn_solidos * lipidos_calc;
            const tn_proteinas = tn_solidos * proteinas_calc;
            
            const m3_biogas_carbohidratos = tn_carbohidratos * 750;
            const m3_biogas_lipidos = tn_lipidos * 1440;
            const m3_biogas_proteinas = tn_proteinas * 980;
            
            const m3_biogas_total = m3_biogas_carbohidratos + m3_biogas_lipidos + m3_biogas_proteinas;
            m3_tnsv = m3_biogas_total / tnsv;
        }
        
        // 4. CH4% usando valores calculados
        const total_biogas = carbohidratos_calc + lipidos_calc + proteinas_calc;
        let ch4_porcentaje = 0.65; // Valor por defecto
        if (total_biogas > 0) {
            ch4_porcentaje = ((proteinas_calc * 0.71) + (lipidos_calc * 0.68) + (carbohidratos_calc * 0.5)) / total_biogas;
        }
        
        // 5. KW/TN
        const consumo_chp = 505.0;
        const kw_tn = ((tnsv * m3_tnsv * ch4_porcentaje) / consumo_chp);
        
        // ACTUALIZAR CAMPOS EN LA INTERFAZ
        
        // TNSV (columna 3)
        inputs[3].value = (tnsv * 100).toFixed(2); // Mostrar como porcentaje
        
        // M³/TNSV (columna 4)
        inputs[4].value = m3_tnsv.toFixed(3);
        
        // CH4% (columna 5)
        inputs[5].value = (ch4_porcentaje * 100).toFixed(2);
        
        // Carbohidratos Calc (columna 9)
        if (inputs[9]) inputs[9].value = (carbohidratos_calc * 100).toFixed(2);
        
        // Lípidos Calc (columna 10)
        if (inputs[10]) inputs[10].value = (lipidos_calc * 100).toFixed(2);
        
        // Proteínas Calc (columna 11)
        if (inputs[11]) inputs[11].value = (proteinas_calc * 100).toFixed(2);
        
        // KW/TN (columna 13)
        if (inputs[13]) inputs[13].value = kw_tn.toFixed(4);
        
        console.log(`🔄 Recalculado ${fila.getAttribute('data-material')}:`);
        console.log(`   ST: ${st}% → TNSV: ${(tnsv*100).toFixed(2)}%`);
        console.log(`   Carbohidratos: ${carbohidrato_lab}% Lab → ${(carbohidratos_calc*100).toFixed(2)}% Calc`);
        console.log(`   M³/TNSV: ${m3_tnsv.toFixed(3)}`);
        console.log(`   KW/TN: ${kw_tn.toFixed(4)}`);
        
    } catch (error) {
        console.error('Error en recálculo automático:', error);
    }
}

// AGREGAR EVENTOS DE RECÁLCULO AUTOMÁTICO
function agregarEventosRecalculo() {
    const tabla = document.getElementById('tabla-gestion-materiales');
    if (!tabla) return;
    
    const filas = tabla.querySelectorAll('tbody tr');
    
    filas.forEach(fila => {
        const inputs = fila.querySelectorAll('input');
        
        // Agregar eventos a campos que deben recalcular
        if (inputs[1]) { // ST
            inputs[1].addEventListener('input', () => recalcularValoresAutomaticos(fila));
            inputs[1].addEventListener('change', () => recalcularValoresAutomaticos(fila));
        }
        if (inputs[2]) { // SV
            inputs[2].addEventListener('input', () => recalcularValoresAutomaticos(fila));
            inputs[2].addEventListener('change', () => recalcularValoresAutomaticos(fila));
        }
        if (inputs[6]) { // Carbohidratos Lab
            inputs[6].addEventListener('input', () => recalcularValoresAutomaticos(fila));
            inputs[6].addEventListener('change', () => recalcularValoresAutomaticos(fila));
        }
        if (inputs[7]) { // Lípidos Lab
            inputs[7].addEventListener('input', () => recalcularValoresAutomaticos(fila));
            inputs[7].addEventListener('change', () => recalcularValoresAutomaticos(fila));
        }
        if (inputs[8]) { // Proteínas Lab
            inputs[8].addEventListener('input', () => recalcularValoresAutomaticos(fila));
            inputs[8].addEventListener('change', () => recalcularValoresAutomaticos(fila));
        }
    });
    
    console.log('✅ Eventos de recálculo automático agregados');
}

// Llamar la función cuando se cargue la tabla
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(agregarEventosRecalculo, 1000); // Esperar a que se cargue la tabla
});