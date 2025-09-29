/**
 * Calculadora de mezclas para biodigestores
 * Este script maneja la lógica para calcular la mezcla óptima de materiales
 */

// Variables globales
let graficoMezcla = null;
let materialesBase = {}; // Almacena información de los materiales base
let ultimaRespuestaCalculadora = null; // Variable global para guardar la última respuesta

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando calculadora de mezclas...');
    
    // Obtener materiales base
    obtenerMaterialesBase();
    
    // Inicializar eventos
    inicializarEventosCalculadora();
    
    // Inicializar gráfico
    inicializarGraficoMezcla();

    document.getElementById('guardar-parametros-btn').addEventListener('click', guardarParametrosGlobales);
});

/**
 * Obtiene los materiales base del servidor
 */
function obtenerMaterialesBase() {
    fetch(window.location.origin + '/obtener_materiales_base_json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && typeof data === 'object') {
                materialesBase = data;
                console.log('Materiales base recibidos:', data);
            } else {
                console.error('Formato de datos incorrecto para materiales base:', data);
            }
        })
        .catch(error => {
            console.error('Error al obtener materiales base:', error);
        });
}

/**
 * Inicializa los eventos para la calculadora
 */
function inicializarEventosCalculadora() {
    // Botón calcular mezcla
    const btnCalcular = document.getElementById('btnCalcularMezcla');
    if (btnCalcular) {
        btnCalcular.addEventListener('click', calcularMezcla);
    } else {
        console.warn('No se encontró el botón para calcular mezcla');
    }
    
    // Eventos para inputs de materiales (validación de stock)
    document.querySelectorAll('.material-solido, .material-liquido').forEach(input => {
        input.addEventListener('input', function() {
            const material = this.dataset.material;
            const stock = parseFloat(this.dataset.stock || 0);
            const cantidad = parseFloat(this.value || 0);
            
            // Validar que no exceda el stock
            if (cantidad > stock) {
                toastr.warning(`La cantidad de ${material} excede el stock disponible (${stock.toFixed(2)} TN)`);
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
}

/**
 * Inicializa el gráfico de la mezcla
 */
function inicializarGraficoMezcla() {
    const ctx = document.getElementById('graficoMezcla');
    if (ctx) {
        graficoMezcla = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Sólidos', 'Líquidos'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Distribución de KW por tipo de material'
                    }
                }
            }
        });
    } else {
        console.warn('No se encontró el elemento para el gráfico de mezcla');
    }
}

/**
 * Calcula la mezcla basada en los valores ingresados
 */
function calcularMezcla() {
    console.log('Calculando mezcla...');
    
    // Obtener valores de inputs
    const datosMateriales = {
        materiales_solidos: {},
        materiales_liquidos: {}
    };
    
    // Recolectar datos de sólidos
    document.querySelectorAll('.material-solido').forEach(input => {
        const material = input.dataset.material;
        const cantidad = parseFloat(input.value || 0);
        
        if (cantidad > 0) {
            datosMateriales.materiales_solidos[material] = cantidad;
        }
    });
    
    // Recolectar datos de líquidos
    document.querySelectorAll('.material-liquido').forEach(input => {
        const material = input.dataset.material;
        const cantidad = parseFloat(input.value || 0);
        
        if (cantidad > 0) {
            datosMateriales.materiales_liquidos[material] = cantidad;
        }
    });
    
    console.log('Datos recolectados:', datosMateriales);
    
    // Validar que haya al menos un material
    if (Object.keys(datosMateriales.materiales_solidos).length === 0 && Object.keys(datosMateriales.materiales_liquidos).length === 0) {
        mostrarAlerta('Debe ingresar al menos un material para realizar el cálculo', 'warning');
        return;
    }
    
    // Enviar datos al servidor para cálculo
    fetch(window.location.origin + '/calcular_mezcla_manual', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ solidos: datosMateriales.materiales_solidos, liquidos: datosMateriales.materiales_liquidos })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('spinner-calculadora').style.display = 'none';
        if (data.status === 'error' || !data.resultado) {
            const errorMessage = data.message || 'Ocurrió un error desconocido.';
            mostrarAlerta(`Error: ${errorMessage}`, 'danger');
            ultimaRespuestaCalculadora = null; // Limpiar en caso de error
        } else {
            mostrarAlerta('Cálculo realizado con éxito.', 'success');
            mostrarResultadosCalculadora(data.resultado);
            ultimaRespuestaCalculadora = data.resultado; // Guardar solo la parte del resultado
        }
    })
    .catch(error => {
        console.error('Error en fetch /calcular_mezcla:', error);
        document.getElementById('spinner-calculadora').style.display = 'none';
        mostrarAlerta(`Error de conexión: ${error.message}`, 'danger');
        ultimaRespuestaCalculadora = null; // Limpiar en caso de error
    });
}

/**
 * Muestra los resultados del cálculo en la interfaz
 * @param {Object} data - Datos de la mezcla calculada
 */
function mostrarResultadosCalculadora(data) {
    const resultadosDiv = document.getElementById('resultadosMezcla');
    if (!resultadosDiv) {
        console.error('No se encontró el contenedor de resultados');
        return;
    }
    
    // Mostrar contenedor
    resultadosDiv.style.display = 'block';
    
    const totales = data.totales || {};
    
    // Actualizar valores básicos
    const totalSolidos = document.getElementById('total-solidos-resultado');
    const totalLiquidos = document.getElementById('total-liquidos-resultado');
    const porcentajeMetano = document.getElementById('porcentaje-metano-resultado');
    const kwDia = document.getElementById('kw-dia-resultado');
    
    if (totalSolidos) totalSolidos.textContent = parseFloat(totales.tn_solidos || 0).toFixed(2);
    if (totalLiquidos) totalLiquidos.textContent = parseFloat(totales.tn_liquidos || 0).toFixed(2);
    if (porcentajeMetano) porcentajeMetano.textContent = parseFloat(totales.porcentaje_metano || 0).toFixed(2);
    if (kwDia) kwDia.textContent = parseFloat(totales.kw_total_generado || 0).toFixed(2);
    
    // Actualizar y mostrar botón de cálculo detallado
    const btnContainer = document.getElementById('contenedor-boton-calculo');
    if (btnContainer) {
        btnContainer.style.display = 'block';
        const btnVerCalculo = document.getElementById('btn-ver-calculo');
        if (btnVerCalculo) {
            btnVerCalculo.onclick = function() {
                mostrarCalculoDetallado();
            };
        }
    }
    
    // Actualizar gráfico
    actualizarGraficoMezcla(data);
}

/**
 * Muestra una alerta en la calculadora
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de alerta (success, warning, error, info)
 */
function mostrarAlerta(mensaje, tipo) {
    const alertaDiv = document.getElementById('alertaCalculadora');
    if (!alertaDiv) {
        console.error('No se encontró el contenedor de alertas');
        return;
    }
    
    // Convertir tipo a clase de Bootstrap
    const claseAlerta = {
        'success': 'alert-success',
        'warning': 'alert-warning',
        'error': 'alert-danger',
        'info': 'alert-info'
    }[tipo] || 'alert-info';
    
    // Configurar alerta
    alertaDiv.className = `alert ${claseAlerta} mt-3`;
    alertaDiv.innerHTML = mensaje;
    alertaDiv.style.display = 'block';
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        alertaDiv.style.display = 'none';
    }, 5000);
}

/**
 * Guarda la mezcla actual como planificación diaria
 */
function guardarComoMezclaActual() {
    const confirmacion = confirm('¿Desea guardar esta mezcla como la planificación diaria actual?');
    if (!confirmacion) return;
    
    // Recolectar datos (similar a calcularMezcla)
    const datosMateriales = {
        solidos: {},
        liquidos: {}
    };
    
    document.querySelectorAll('.material-solido').forEach(input => {
        const material = input.dataset.material;
        const cantidad = parseFloat(input.value || 0);
        
        if (cantidad > 0) {
            datosMateriales.solidos[material] = cantidad;
        }
    });
    
    document.querySelectorAll('.material-liquido').forEach(input => {
        const material = input.dataset.material;
        const cantidad = parseFloat(input.value || 0);
        
        if (cantidad > 0) {
            datosMateriales.liquidos[material] = cantidad;
        }
    });
    
    fetch('/guardar_mezcla_como_actual', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(datosMateriales)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta('Mezcla guardada como planificación diaria actual', 'success');
        } else {
            mostrarAlerta(data.error || 'Error al guardar la mezcla', 'error');
        }
    })
    .catch(error => {
        console.error('Error en la petición:', error);
        mostrarAlerta('Error de conexión al guardar la mezcla', 'error');
    });
}

/**
 * Actualiza el gráfico de la mezcla con los datos calculados
 * @param {Object} data - Datos de la mezcla calculada
 */
function actualizarGraficoMezcla(data) {
    if (graficoMezcla) {
        const totales = data.totales || {};
        const kwGeneradosSolidos = parseFloat(totales.kw_solidos || 0);
        const kwGeneradosLiquidos = parseFloat(totales.kw_liquidos || 0);
        
        const dataGrafico = [kwGeneradosSolidos, kwGeneradosLiquidos];
        
        graficoMezcla.data.datasets[0].data = dataGrafico;
        graficoMezcla.update();
    }
}

/**
 * Abre una ventana con la explicación detallada del cálculo
 */
function mostrarCalculoDetallado() {
    const modalBody = document.getElementById('detalle-calculo-body');
    
    // Buscar la última respuesta guardada en la variable global
    const data = ultimaRespuestaCalculadora;

    if (!data || !data.totales) {
        modalBody.innerHTML = '<p>No hay datos de cálculo detallado para mostrar. Por favor, realice un cálculo primero.</p>';
        return;
    }

    // Determinar el material principal de la mezcla
    let materialPrincipal = '';
    let cantidadPrincipal = 0;

    const solidos = data.materiales_solidos || {};
    const liquidos = data.materiales_liquidos || {};
    
    // Revisar materiales sólidos
    for (const [material, info] of Object.entries(solidos)) {
        const cantidadNum = parseFloat(info.cantidad_tn || 0);
        if (cantidadNum > cantidadPrincipal) {
            materialPrincipal = material;
            cantidadPrincipal = cantidadNum;
        }
    }
    
    // Revisar materiales líquidos
    for (const [material, info] of Object.entries(liquidos)) {
        const cantidadNum = parseFloat(info.cantidad_tn || 0);
        if (cantidadNum > cantidadPrincipal) {
            materialPrincipal = material;
            cantidadPrincipal = cantidadNum;
        }
    }
    
    // Si no se encontró un material principal, usar el primero que se encuentre
    if (!materialPrincipal) {
        const solidosKeys = Object.keys(solidos);
        if (solidosKeys.length > 0) {
            materialPrincipal = solidosKeys[0];
            cantidadPrincipal = parseFloat(solidos[materialPrincipal].cantidad_tn || 0);
        } else {
            const liquidosKeys = Object.keys(liquidos);
            if (liquidosKeys.length > 0) {
                materialPrincipal = liquidosKeys[0];
                cantidadPrincipal = parseFloat(liquidos[liquidosKeys[0]].cantidad_tn || 0);
            }
        }
    }
    
    // Si hay un material principal, intentar abrir la página de cálculo detallado
    if (materialPrincipal && cantidadPrincipal > 0) {
        // Esta funcionalidad depende de una ruta /ver_calculo/ que puede no existir.
        // El código ahora busca el material principal correctamente.
        window.open(`/ver_calculo/${encodeURIComponent(materialPrincipal)}/${cantidadPrincipal}`, '_blank');
    } else {
        mostrarAlerta('No hay suficientes datos para mostrar un cálculo detallado', 'warning');
    }
} 