// Este script se ejecuta cuando todo el contenido de la página se ha cargado.
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Lógica para guardar los parámetros globales
    const btnGuardarConfig = document.getElementById('btnGuardarConfig');
    if (btnGuardarConfig) {
        btnGuardarConfig.addEventListener('click', guardarParametrosGlobales);
    }

    // 2. Lógica para registrar un nuevo ingreso de material
    const formRegistroIngreso = document.getElementById('formRegistroIngreso');
    if (formRegistroIngreso) {
        formRegistroIngreso.addEventListener('submit', registrarIngresoMaterial);
    }
});


/**
 * Recolecta los datos del modal de configuración y los envía al servidor.
 */
function guardarParametrosGlobales() {
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
            console.error(`Error de configuración: No se encontró el elemento del formulario con id="${id}"`);
            error = true;
            return;
        }
        
        datosPayload[id] = (elemento.type === 'checkbox') ? elemento.checked : elemento.value;
    });

    if (error) {
        alert('Error: Faltan campos en el formulario de configuración. Revisa la consola (F12) para más detalles.');
        return;
    }

    const btn = document.getElementById('btnGuardarConfig');
    btn.disabled = true;
    btn.textContent = 'Guardando...';

    fetch('/actualizar_configuracion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datosPayload),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('¡Configuración guardada con éxito! La página se recargará para aplicar los cambios.');
            window.location.reload();
        } else {
            alert(`Error al guardar: ${data.message || 'Ocurrió un error desconocido.'}`);
        }
    })
    .catch(err => {
        console.error('Error de red al guardar configuración:', err);
        alert('Error de conexión. No se pudo guardar la configuración.');
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Guardar Cambios';
    });
}

/**
 * Recolecta los datos del formulario de ingreso de material y los envía al servidor.
 */
function registrarIngresoMaterial(event) {
    event.preventDefault(); // Prevenir el envío tradicional que recarga la página

    const form = event.target;
    const formData = new FormData(form);
    const datos = Object.fromEntries(formData.entries());

    if (!datos.material || !datos.tn_descargadas || !datos.st_analizado) {
        alert('Por favor, complete todos los campos del registro.');
        return;
    }
    
    fetch('/registrar_ingreso', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            // Simplemente recargamos la página. Es la forma más fácil y segura
            // de asegurar que todo (tablas, cálculos, etc.) se actualice.
            window.location.reload();
        } else {
            alert(`Error al registrar: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error al registrar ingreso:', error);
        alert('Error de conexión al registrar el ingreso.');
    });
} 