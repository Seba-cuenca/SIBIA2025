document.addEventListener('DOMContentLoaded', function() {
    const btnGuardar = document.getElementById('btnGuardarConfig'); // Asegúrate de que tu botón de guardar tenga este ID
    if (btnGuardar) {
        btnGuardar.addEventListener('click', guardarParametrosGlobales);
    } else {
        console.warn('Advertencia: No se encontró el botón con id="btnGuardarConfig" para guardar los parámetros.');
    }
});

function guardarParametrosGlobales() {
    // IDs esperados para cada campo del formulario. Deben coincidir con tu HTML.
    const ids_campos = [
        'kw_objetivo', 'num_biodigestores', 'porcentaje_purin', 'porcentaje_sa7_reemplazo',
        'max_materiales_solidos', 'min_materiales_solidos', 'max_porcentaje_material',
        'factor_correccion_purin', 'consumo_chp_global', 'objetivo_metano_diario',
        'compensacion_automatica_diaria', 'usar_optimizador_metano'
    ];

    const datosPayload = {};
    let error = false;

    ids_campos.forEach(id => {
        const elemento = document.getElementById(id);
        if (!elemento) {
            console.error(`Error: No se encontró el elemento del formulario con id="${id}"`);
            error = true;
            return;
        }
        if (elemento.type === 'checkbox') {
            datosPayload[id] = !!elemento.checked;
        } else if (elemento.type === 'number' || elemento.type === 'range') {
            datosPayload[id] = elemento.value === '' ? null : parseFloat(elemento.value);
        } else {
            datosPayload[id] = elemento.value;
        }
    });

    if (error) {
        alert('Error: Faltan campos en el formulario de configuración. Revisa la consola (F12) para más detalles.');
        return;
    }

    console.log('Enviando datos de configuración al servidor:', datosPayload);

    // Desactivar el botón para evitar clics duplicados
    const btnGuardar = document.getElementById('btnGuardarConfig');
    btnGuardar.disabled = true;
    btnGuardar.textContent = 'Guardando...';

    fetch('/actualizar_configuracion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(datosPayload),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('¡Configuración guardada con éxito! La página se recargará para aplicar los cambios.');
            if (data.requiresReload) {
                window.location.reload();
            }
        } else {
            alert(`Error al guardar: ${data.message || 'Ocurrió un error desconocido.'}`);
        }
    })
    .catch(err => {
        console.error('Error de red al guardar configuración:', err);
        alert('Error de conexión. No se pudo guardar la configuración.');
    })
    .finally(() => {
        // Volver a habilitar el botón
        btnGuardar.disabled = false;
        btnGuardar.textContent = 'Guardar Cambios';
    });
} 