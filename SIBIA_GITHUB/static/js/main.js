// ===== ARCHIVO JAVASCRIPT PRINCIPAL PARA SIBIA =====
// Este archivo maneja toda la lógica del frontend

document.addEventListener('DOMContentLoaded', function() {
    console.log('SIBIA - Sistema iniciado y listo para operar.');

    const avisoVolumetrico = document.getElementById('aviso-volumetrico-reorganizado');
    if (avisoVolumetrico) {
        avisoVolumetrico.style.display = 'none';
    }

    inicializarEventos();
    actualizarTodosLosSistemas(); // Primera carga inmediata de datos

    // Iniciar el ciclo de actualización global y unificado
    setInterval(actualizarTodosLosSistemas, 5000); // Cada 5 segundos
});

// ===== INICIALIZACIÓN DE EVENTOS =====
function inicializarEventos() {
    // Botón Guardar Configuración
    const btnGuardarConfig = document.getElementById('btnGuardarConfig');
    if (btnGuardarConfig) {
        btnGuardarConfig.addEventListener('click', guardarParametrosGlobales);
    }

    // Botón Calcular Mezcla (Calculadora)
    const btnCalcularMezcla = document.getElementById('btnCalcularMezcla');
    if (btnCalcularMezcla) {
        btnCalcularMezcla.addEventListener('click', calcularMezclaManual);
    }

    // Botón Borrar Stock
    const btnBorrarStock = document.getElementById('btnBorrarStock');
    if (btnBorrarStock) {
        btnBorrarStock.addEventListener('click', borrarStock);
    }

    // Eventos de pestañas
    const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            manejarCambioTab(targetId);
        });
        
        // Prevenir cierre accidental de pestañas
        tab.addEventListener('click', function(event) {
            // Solo manejar clicks en pestañas válidas
            if (this.getAttribute('data-bs-target')) {
                const targetId = this.getAttribute('data-bs-target');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    // Asegurar que la pestaña se mantenga abierta
                    setTimeout(() => {
                        if (!targetElement.classList.contains('show')) {
                            const tab = new bootstrap.Tab(this);
                            tab.show();
                        }
                    }, 100);
                }
            }
        });
    });

    // Botón registrar KW reales
    window.registrarKWReales = registrarKWReales;
    
    // Funciones globales para pestañas
    window.cargarPlanMensual = cargarPlanMensual;
    window.cargarPlanSemanal = cargarPlanSemanal;
    window.cargarHistoricoDiario = cargarHistoricoDiario;
}

// ===== MANEJO DE PESTAÑAS =====
function manejarCambioTab(targetId) {
    switch(targetId) {
        case '#kpis':
            cargarKPIs();
            break;
        case '#seguimiento-horario':
            cargarSeguimientoHorario();
            break;
        case '#analisis-economico':
            cargarAnalisisEconomico();
            break;
        case '#logistica-panel':
            actualizarTablaStock();
            break;
        case '#plan-mensual':
            cargarPlanMensual();
            break;
        case '#plan-semanal':
            cargarPlanSemanal();
            break;
        case '#historico':
            cargarHistoricoDiario();
            break;
    }
}

// ===== FUNCIONES DE CONFIGURACIÓN =====
function guardarParametrosGlobales() {
    const campos = [
        'kw_objetivo_param', 'num_biodigestores_param', 'porcentaje_purin_param', 
        'porcentaje_liquidos_param', 'porcentaje_solidos_param',
        'porcentaje_sa7_reemplazo_param', 'max_materiales_solidos_param', 
        'min_materiales_solidos_param', 'max_porcentaje_material_param',
        'factor_correccion_purin_param', 'consumo_chp_global_param', 
        'objetivo_metano_diario_param', 'compensacion_automatica_param', 
        'usar_optimizador_metano_param'
    ];

    const datos = {};
    let error = false;

    campos.forEach(id => {
        const elemento = document.getElementById(id);
        if (!elemento) {
            console.error(`Campo no encontrado: ${id}`);
            error = true;
            return;
        }
        
        const key = id.replace('_param', '');
        datos[key] = (elemento.type === 'checkbox') ? elemento.checked : elemento.value;
    });

    if (error) {
        if (typeof toastr !== 'undefined') {
            toastr.error('Error en el formulario de configuración');
    } else {
            alert('Error en el formulario de configuración');
        }
        return;
    }

    const btn = document.getElementById('btnGuardarConfig');
    btn.disabled = true;
    btn.textContent = 'Guardando...';

    fetch('/actualizar_configuracion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (typeof toastr !== 'undefined') {
                toastr.success('Configuración guardada exitosamente');
            } else {
                alert('Configuración guardada exitosamente');
            }
            setTimeout(() => window.location.reload(), 1500);
        } else {
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al guardar: ' + (data.message || 'Error desconocido'));
            } else {
                alert('Error al guardar: ' + (data.message || 'Error desconocido'));
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Error de conexión al guardar configuración');
        } else {
            alert('Error de conexión al guardar configuración');
        }
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Guardar Cambios';
    });
}

// ===== FUNCIONES DE KW REALES =====
function registrarKWReales() {
    const kwGenerados = document.getElementById('kw_generados_real').value;
    const kwInyectados = document.getElementById('kw_inyectados_real').value;

    if (!kwGenerados || !kwInyectados) {
        if (typeof toastr !== 'undefined') {
            toastr.warning('Por favor, complete ambos campos de KW');
    } else {
            alert('Por favor, complete ambos campos de KW');
        }
        return;
    }

    const datos = {
        kw_generados_real: parseFloat(kwGenerados),
        kw_inyectados_real: parseFloat(kwInyectados)
    };

    fetch('/registrar_kw_reales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensaje) {
            if (typeof toastr !== 'undefined') {
                toastr.success('KW reales registrados exitosamente');
                    } else {
                alert('KW reales registrados exitosamente');
            }
            actualizarDisplayKWReales(datos);
        } else {
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al registrar KW reales');
            } else {
                alert('Error al registrar KW reales');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Error de conexión al registrar KW reales');
                } else {
            alert('Error de conexión al registrar KW reales');
        }
    });
}

// ===== FUNCIONES DE KW AUTOMÁTICOS =====
function actualizarKWAutomaticos() {
    fetch('/kw_automaticos_calculados')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            actualizarCamposKWAutomaticos(data.datos_calculados);
        } else {
            console.error('Error obteniendo KW automáticos:', data.message);
        }
    })
    .catch(error => {
        console.error('Error actualizando KW automáticos:', error);
    });
}

function actualizarCamposKWAutomaticos(datos) {
    // Actualizar campos de entrada con valores calculados
    const kwGeneradosInput = document.getElementById('kw_generados_real');
    const kwInyectadosInput = document.getElementById('kw_inyectados_real');
    
    if (kwGeneradosInput) {
        kwGeneradosInput.value = datos.kw_generados_calculado;
        kwGeneradosInput.style.backgroundColor = '#e8f5e8'; // Verde claro para indicar automático
    }
    
    if (kwInyectadosInput) {
        kwInyectadosInput.value = datos.kw_inyectados_calculado;
        kwInyectadosInput.style.backgroundColor = '#e8f5e8'; // Verde claro para indicar automático
    }
    
    // Actualizar displays de diferencia vs plan
    actualizarDiferenciaVsPlan(datos);
    
    // Actualizar indicador de progreso
    actualizarIndicadorProgreso(datos);
    
    // Si hay botón de guardar automático, habilitarlo
    const btnGuardarAutomatico = document.getElementById('btn-guardar-automatico');
    if (btnGuardarAutomatico) {
        btnGuardarAutomatico.disabled = datos.total_registros < 10;
        btnGuardarAutomatico.title = datos.total_registros < 10 ? 
            'Necesita al menos 10 registros para cálculo automático' : 
            'Guardar valores calculados automáticamente';
    }
}

function actualizarDiferenciaVsPlan(datos) {
    const diferenciaKwEl = document.getElementById('diferencia_kw_display');
    const diferenciaPorcEl = document.getElementById('diferencia_porc_display');
    
    if (diferenciaKwEl && datos.puede_calcular_diferencia) {
        diferenciaKwEl.textContent = datos.diferencia_vs_plan_kw;
        diferenciaKwEl.className = datos.diferencia_vs_plan_kw >= 0 ? 'text-success' : 'text-danger';
    }
    
    if (diferenciaPorcEl && datos.puede_calcular_diferencia) {
        diferenciaPorcEl.textContent = datos.diferencia_vs_plan_porc.toFixed(1) + '%';
        diferenciaPorcEl.className = datos.diferencia_vs_plan_porc >= 0 ? 'text-success' : 'text-danger';
    }
}

function actualizarIndicadorProgreso(datos) {
    // Buscar elementos de progreso en la página
    const elementos = [
        'formula_calculo',
        'progreso_registros_15min',
        'estado_calculo_automatico'
    ];
    
    elementos.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            switch(id) {
                case 'formula_calculo':
                    elemento.textContent = datos.formula_calculo;
                    break;
                case 'progreso_registros_15min':
                    elemento.textContent = `${datos.total_registros}/96 registros (${datos.porcentaje_completado}%)`;
                    break;
                case 'estado_calculo_automatico':
                    if (datos.dia_completado) {
                        elemento.innerHTML = '<i class="fas fa-check-circle text-success"></i> Día completado - Cálculo final disponible';
                    } else if (datos.puede_calcular_diferencia) {
                        elemento.innerHTML = '<i class="fas fa-calculator text-info"></i> Cálculo automático disponible';
                    } else {
                        elemento.innerHTML = '<i class="fas fa-clock text-warning"></i> Recopilando datos...';
                    }
                    break;
            }
        }
    });
}

function guardarKWAutomaticos() {
    const datos = {
        usar_automatico: true
    };

    const btn = document.getElementById('btn-guardar-automatico');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Guardando...';
    }

    fetch('/registrar_kw_reales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensaje) {
            if (typeof toastr !== 'undefined') {
                toastr.success(data.mensaje);
            } else {
                alert(data.mensaje);
            }
            
            // Actualizar displays con los datos guardados
            if (data.datos_guardados) {
                actualizarDisplayKWReales(data.datos_guardados);
            }
            
            // Limpiar indicadores visuales de automático
            limpiarIndicadoresAutomaticos();
            
        } else {
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al guardar KW automáticos');
            } else {
                alert('Error al guardar KW automáticos');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Error de conexión al guardar KW automáticos');
        } else {
            alert('Error de conexión al guardar KW automáticos');
        }
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Guardar Automático';
        }
    });
}

function limpiarIndicadoresAutomaticos() {
    const kwGeneradosInput = document.getElementById('kw_generados_real');
    const kwInyectadosInput = document.getElementById('kw_inyectados_real');
    
    if (kwGeneradosInput) {
        kwGeneradosInput.style.backgroundColor = '';
    }
    
    if (kwInyectadosInput) {
        kwInyectadosInput.style.backgroundColor = '';
    }
}

function actualizarDisplayKWReales(datos) {
    const kwGeneradosDisplay = document.getElementById('kw_generados_real_display');
    const kwInyectadosDisplay = document.getElementById('kw_inyectados_real_display');
    const kwConsumidosDisplay = document.getElementById('kw_consumidos_planta_real_display');
    
    if (kwGeneradosDisplay) kwGeneradosDisplay.textContent = datos.kw_generados_real.toLocaleString();
    if (kwInyectadosDisplay) kwInyectadosDisplay.textContent = datos.kw_inyectados_real.toLocaleString();
    if (kwConsumidosDisplay) kwConsumidosDisplay.textContent = (datos.kw_generados_real - datos.kw_inyectados_real).toLocaleString();
}

// ===== FUNCIONES DE CALCULADORA DE MEZCLAS =====
function calcularMezclaManual() {
    const solidos = {};
    const liquidos = {};

    // Recopilar datos de sólidos
    document.querySelectorAll('.material-solido').forEach(input => {
        if (input.value && parseFloat(input.value) > 0) {
            solidos[input.dataset.material] = input.value;
        }
    });

    // Recopilar datos de líquidos
    document.querySelectorAll('.material-liquido').forEach(input => {
        if (input.value && parseFloat(input.value) > 0) {
            liquidos[input.dataset.material] = input.value;
        }
    });

    if (Object.keys(solidos).length === 0 && Object.keys(liquidos).length === 0) {
        if (typeof toastr !== 'undefined') {
            toastr.warning('Por favor, ingrese al menos un material con cantidad');
            } else {
            alert('Por favor, ingrese al menos un material con cantidad');
        }
        return;
    }

    const btn = document.getElementById('btnCalcularMezcla');
    btn.disabled = true;
    btn.textContent = 'Calculando...';

    fetch('/calcular_mezcla_manual', {
                method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ solidos, liquidos })
    })
    .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
            mostrarResultadosCalculadora(data.resultado);
            if (typeof toastr !== 'undefined') {
                toastr.success('Mezcla calculada exitosamente');
                } else {
                alert('Mezcla calculada exitosamente');
            }
        } else {
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al calcular mezcla: ' + (data.message || 'Error desconocido'));
            } else {
                alert('Error al calcular mezcla: ' + (data.message || 'Error desconocido'));
            }
                }
            })
            .catch(error => {
        console.error('Error:', error);
        if (typeof toastr !== 'undefined') {
            toastr.error('Error de conexión al calcular mezcla');
        } else {
            alert('Error de conexión al calcular mezcla');
        }
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Calcular Mezcla';
    });
}

function mostrarResultadosCalculadora(resultado) {
    const container = document.getElementById('resultadosMezcla');
    if (!container) return;

    // Guardar resultado globalmente para el botón de detalle
    window.ultimoResultadoCalculadora = resultado;

    // Actualizar totales
    const totalSolidosEl = document.getElementById('total-solidos-resultado');
    const totalLiquidosEl = document.getElementById('total-liquidos-resultado');
    const porcentajeMetanoEl = document.getElementById('porcentaje-metano-resultado');
    const kwDiaEl = document.getElementById('kw-dia-resultado');

    if (totalSolidosEl) totalSolidosEl.textContent = resultado.totales.tn_solidos.toFixed(2);
    if (totalLiquidosEl) totalLiquidosEl.textContent = resultado.totales.tn_liquidos.toFixed(2);
    if (porcentajeMetanoEl) porcentajeMetanoEl.textContent = resultado.totales.porcentaje_metano.toFixed(2);
    if (kwDiaEl) kwDiaEl.textContent = resultado.totales.kw_total_generado.toFixed(2);

    // Mostrar botón de cálculo detallado
    const contenedorBoton = document.getElementById('contenedor-boton-calculo');
    if (contenedorBoton) {
        contenedorBoton.style.display = 'block';
        const btnVerCalculo = document.getElementById('btn-ver-calculo');
        if (btnVerCalculo) {
            btnVerCalculo.onclick = function() {
                mostrarCalculoDetallado(resultado);
            };
        }
    }

    container.style.display = 'block';
}

// ===== FUNCIONES PARA BALANCE VOLUMÉTRICO =====
function actualizarBalanceVolumetrico() {
    const contenedor = document.getElementById('balance-volumetrico-card');
    fetch('/balance_volumetrico_completo')
        .then(response => {
            if (!response.ok) throw new Error('Fallo en la respuesta del servidor');
            gestionarEstadoConexion(contenedor, true, '.card-header');
            return response.json();
        })
        .then(data => mostrarBalanceVolumetrico(data))
        .catch(error => {
            console.error('Error al actualizar balance volumétrico:', error);
            gestionarEstadoConexion(contenedor, false, '.card-header');
        });
}

function mostrarBalanceVolumetrico(data) {
    // Actualizar biodigestor 1
    if (data.biodigestores && data.biodigestores['1'] && !data.biodigestores['1'].error) {
        const bio1 = data.biodigestores['1'];
        actualizarTarjetaBalance('1', bio1);
    }
    
    // Actualizar biodigestor 2
    if (data.biodigestores && data.biodigestores['2'] && !data.biodigestores['2'].error) {
        const bio2 = data.biodigestores['2'];
        actualizarTarjetaBalance('2', bio2);
    }
    
    // Actualizar totales de planta
    if (data.totales_planta) {
        actualizarTotalesPlanta(data.totales_planta, data.estado_general);
    }
}

function actualizarTarjetaBalance(biodigestorId, datos) {
    const prefijo = `balance-${biodigestorId}`;
    
    // Nivel
    const nivelElement = document.getElementById(`${prefijo}-nivel`);
    const volumenElement = document.getElementById(`${prefijo}-volumen`);
    if (nivelElement && volumenElement) {
        nivelElement.textContent = `${datos.nivel.porcentaje.toFixed(1)}%`;
        volumenElement.textContent = `${datos.nivel.volumen_m3.toFixed(0)} m³`;
    }
    
    // Flujo
    const flujoElement = document.getElementById(`${prefijo}-flujo`);
    const flujoDiarioElement = document.getElementById(`${prefijo}-flujo-diario`);
    if (flujoElement && flujoDiarioElement) {
        flujoElement.textContent = `${datos.flujo_entrada.valor_m3_h.toFixed(1)} m³/h`;
        flujoDiarioElement.textContent = `${datos.flujo_entrada.volumen_diario_m3.toFixed(0)} m³/día`;
    }
    
    // Volumen libre y tiempo
    const libreElement = document.getElementById(`${prefijo}-libre`);
    const tiempoElement = document.getElementById(`${prefijo}-tiempo`);
    if (libreElement && tiempoElement) {
        libreElement.textContent = `${datos.nivel.volumen_libre_m3.toFixed(0)} m³`;
        
        const tiempoHoras = datos.estimaciones.tiempo_llenado_completo_horas;
        if (tiempoHoras === Infinity) {
            tiempoElement.textContent = '∞ horas';
        } else {
            tiempoElement.textContent = `${tiempoHoras.toFixed(1)} horas`;
        }
    }
    
    // Barra de progreso
    const barraElement = document.getElementById(`${prefijo}-barra`);
    const porcentajeElement = document.getElementById(`${prefijo}-porcentaje`);
    if (barraElement && porcentajeElement) {
        const porcentaje = datos.nivel.porcentaje;
        barraElement.style.width = `${porcentaje}%`;
        porcentajeElement.textContent = `${porcentaje.toFixed(1)}%`;
        
        // Cambiar color según nivel
        barraElement.className = 'progress-bar';
        if (porcentaje > 90) {
            barraElement.classList.add('bg-danger');
        } else if (porcentaje > 85) {
            barraElement.classList.add('bg-warning');
        } else {
            barraElement.classList.add(biodigestorId === '1' ? 'bg-primary' : 'bg-success');
        }
    }
    
    // Alertas
    const alertasElement = document.getElementById(`${prefijo}-alertas`);
    if (alertasElement && datos.alertas) {
        alertasElement.innerHTML = '';
        datos.alertas.forEach(alerta => {
            const span = document.createElement('span');
            span.className = obtenerClaseAlerta(alerta);
            span.textContent = alerta;
            alertasElement.appendChild(span);
            alertasElement.appendChild(document.createTextNode(' '));
        });
    }
}

function actualizarTotalesPlanta(totales, estadoGeneral) {
    // Volumen total
    const volumenTotalElement = document.getElementById('balance-total-volumen');
    if (volumenTotalElement) {
        volumenTotalElement.textContent = `${totales.volumen_actual_m3.toFixed(0)} m³`;
    }
    
    // Ocupación
    const ocupacionElement = document.getElementById('balance-total-ocupacion');
    if (ocupacionElement) {
        ocupacionElement.textContent = `${totales.porcentaje_ocupacion_planta.toFixed(1)}%`;
    }
    
    // Flujo total
    const flujoTotalElement = document.getElementById('balance-total-flujo');
    const flujoDiarioTotalElement = document.getElementById('balance-total-flujo-diario');
    if (flujoTotalElement && flujoDiarioTotalElement) {
        flujoTotalElement.textContent = `${totales.flujo_total_entrada_m3_h.toFixed(1)} m³/h`;
        flujoDiarioTotalElement.textContent = `${totales.capacidad_entrada_diaria_m3.toFixed(0)} m³/día`;
    }
    
    // Estado general
    const estadoElement = document.getElementById('balance-estado-general');
    if (estadoElement) {
        estadoElement.textContent = estadoGeneral;
        estadoElement.className = obtenerClaseEstadoGeneral(estadoGeneral);
    }
}

function obtenerClaseAlerta(alerta) {
    if (alerta.includes('🔴 CRÍTICO')) {
        return 'badge bg-danger me-1';
    } else if (alerta.includes('🟡 ALERTA')) {
        return 'badge bg-warning me-1';
    } else {
        return 'badge bg-success me-1';
    }
}

function obtenerClaseEstadoGeneral(estado) {
    switch (estado) {
        case 'NORMAL': return 'text-success';
        case 'ALERTA': return 'text-warning';
        case 'CRÍTICO': return 'text-danger';
        default: return 'text-info';
    }
}

function mostrarErrorBalanceVolumetrico(mensaje) {
    console.error('Error balance volumétrico:', mensaje);
    
    // Mostrar error en las tarjetas
    ['1', '2'].forEach(id => {
        const prefijos = [`balance-${id}-nivel`, `balance-${id}-flujo`, `balance-${id}-libre`, `balance-${id}-tiempo`];
        prefijos.forEach(prefijo => {
            const element = document.getElementById(prefijo);
            if (element) {
                element.textContent = '-- Error';
            }
        });
        
        const alertasElement = document.getElementById(`balance-${id}-alertas`);
        if (alertasElement) {
            alertasElement.innerHTML = '<span class="badge bg-danger">Error de conexión</span>';
        }
    });
    
    if (typeof toastr !== 'undefined') {
        toastr.error(mensaje);
    }
}

// ===== FUNCIONES PARA SENSORES COMPLETOS =====
function actualizarSensoresCompletos() {
    console.log('Actualizando sensores completos...');
    
    fetch('/sensores_completos_resumen')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                mostrarErrorSensoresCompletos(data.mensaje || 'Error obteniendo sensores completos');
            } else {
                mostrarSensoresCompletos(data);
            }
        })
        .catch(error => {
            console.error('Error obteniendo sensores completos:', error);
            mostrarErrorSensoresCompletos('Error de conexión con sensores completos');
        });
}

function mostrarSensoresCompletos(data) {
    if (!data.sensores) {
        mostrarErrorSensoresCompletos('Datos de sensores no disponibles');
        return;
    }
    
    // Actualizar sensores de presión y flujo
    actualizarPresionYFlujo(data.sensores);
    
    // Actualizar sensores de pH
    actualizarPHSensores(data.sensores);
    
    // Actualizar temperaturas adicionales
    actualizarTemperaturasAdicionales(data.sensores);
    
    // Actualizar generación adicional
    actualizarGeneracionAdicional(data.sensores);
    
    // Actualizar gases secundarios
    actualizarGasesSecundarios(data.sensores);
    
    // Actualizar estado general
    actualizarEstadoGeneralCompletos(data);
}

function actualizarPresionYFlujo(sensores) {
    // Presión línea de gas
    if (sensores.presion && sensores.presion.linea_gas) {
        const presionElement = document.getElementById('presion-linea-gas');
        if (presionElement) {
            const valor = sensores.presion.linea_gas.valor;
            presionElement.textContent = `${valor} bar`;
            presionElement.className = `text-${obtenerColorPorEstado(sensores.presion.linea_gas.estado)} mb-1`;
        }
    }
    
    // Flujo de biogás
    if (sensores.flujo && sensores.flujo.biogas) {
        const flujoElement = document.getElementById('flujo-biogas');
        if (flujoElement) {
            const valor = sensores.flujo.biogas.valor;
            flujoElement.textContent = `${valor} m³/h`;
            flujoElement.className = `text-${obtenerColorPorEstado(sensores.flujo.biogas.estado)} mb-1`;
        }
    }
}

function actualizarPHSensores(sensores) {
    // pH Biodigestor 1
    if (sensores.ph && sensores.ph.biodigestor_1) {
        const ph1Element = document.getElementById('ph-biodigestor-1');
        if (ph1Element) {
            const valor = sensores.ph.biodigestor_1.valor;
            ph1Element.textContent = `${valor} pH`;
            ph1Element.className = `text-${obtenerColorPorEstado(sensores.ph.biodigestor_1.estado)} mb-1`;
        }
    }
    
    // pH Biodigestor 2
    if (sensores.ph && sensores.ph.biodigestor_2) {
        const ph2Element = document.getElementById('ph-biodigestor-2');
        if (ph2Element) {
            const valor = sensores.ph.biodigestor_2.valor;
            ph2Element.textContent = `${valor} pH`;
            ph2Element.className = `text-${obtenerColorPorEstado(sensores.ph.biodigestor_2.estado)} mb-1`;
        }
    }
}

function actualizarTemperaturasAdicionales(sensores) {
    // Temperatura adicional Biodigestor 1
    if (sensores.temperatura && sensores.temperatura.adicional_biodigestor_1) {
        const temp1Element = document.getElementById('temp-adicional-bio1');
        if (temp1Element) {
            const valor = sensores.temperatura.adicional_biodigestor_1.valor;
            temp1Element.textContent = `${valor} °C`;
            temp1Element.className = `text-${obtenerColorPorEstado(sensores.temperatura.adicional_biodigestor_1.estado)} mb-1`;
        }
    }
    
    // Temperatura adicional Biodigestor 2
    if (sensores.temperatura && sensores.temperatura.adicional_biodigestor_2) {
        const temp2Element = document.getElementById('temp-adicional-bio2');
        if (temp2Element) {
            const valor = sensores.temperatura.adicional_biodigestor_2.valor;
            temp2Element.textContent = `${valor} °C`;
            temp2Element.className = `text-${obtenerColorPorEstado(sensores.temperatura.adicional_biodigestor_2.estado)} mb-1`;
        }
    }
    
    // Temperatura línea de gas
    if (sensores.temperatura && sensores.temperatura.linea_gas) {
        const tempLineaElement = document.getElementById('temp-linea-gas');
        if (tempLineaElement) {
            const valor = sensores.temperatura.linea_gas.valor;
            tempLineaElement.textContent = `${valor} °C`;
            tempLineaElement.className = `text-${obtenerColorPorEstado(sensores.temperatura.linea_gas.estado)} mb-1`;
        }
    }
}

function actualizarGeneracionAdicional(sensores) {
    // Generación secundaria
    if (sensores.energia && sensores.energia.generacion_secundaria) {
        const genSecElement = document.getElementById('gen-secundaria');
        if (genSecElement) {
            const valor = sensores.energia.generacion_secundaria.valor;
            genSecElement.textContent = `${valor} kW`;
            genSecElement.className = `text-${obtenerColorPorEstado(sensores.energia.generacion_secundaria.estado)} mb-1`;
        }
    }
    
    // Generación terciaria
    if (sensores.energia && sensores.energia.generacion_terciaria) {
        const genTerElement = document.getElementById('gen-terciaria');
        if (genTerElement) {
            const valor = sensores.energia.generacion_terciaria.valor;
            genTerElement.textContent = `${valor} kW`;
            genTerElement.className = `text-${obtenerColorPorEstado(sensores.energia.generacion_terciaria.estado)} mb-1`;
        }
    }
}

function actualizarGasesSecundarios(sensores) {
    // Oxígeno secundario
    if (sensores.gases && sensores.gases.oxigeno_secundario) {
        const o2Element = document.getElementById('o2-secundario');
        if (o2Element) {
            const valor = sensores.gases.oxigeno_secundario.valor;
            o2Element.textContent = `${valor}%`;
            o2Element.className = `text-${obtenerColorPorEstado(sensores.gases.oxigeno_secundario.estado)} mb-1`;
        }
    }
    
    // Metano secundario
    if (sensores.gases && sensores.gases.metano_secundario) {
        const ch4Element = document.getElementById('ch4-secundario');
        if (ch4Element) {
            const valor = sensores.gases.metano_secundario.valor;
            ch4Element.textContent = `${valor}%`;
            ch4Element.className = `text-${obtenerColorPorEstado(sensores.gases.metano_secundario.estado)} mb-1`;
        }
    }
    
    // CO2 secundario
    if (sensores.gases && sensores.gases.co2_secundario) {
        const co2Element = document.getElementById('co2-secundario');
        if (co2Element) {
            const valor = sensores.gases.co2_secundario.valor;
            co2Element.textContent = `${valor}%`;
            co2Element.className = `text-${obtenerColorPorEstado(sensores.gases.co2_secundario.estado)} mb-1`;
        }
    }
    
    // H2S secundario
    if (sensores.gases && sensores.gases.h2s_secundario) {
        const h2sElement = document.getElementById('h2s-secundario');
        if (h2sElement) {
            const valor = sensores.gases.h2s_secundario.valor;
            h2sElement.textContent = `${valor} ppm`;
            h2sElement.className = `text-${obtenerColorPorEstado(sensores.gases.h2s_secundario.estado)} mb-1`;
        }
    }
}

function actualizarEstadoGeneralCompletos(data) {
    // Estado general
    const estadoElement = document.getElementById('estado-general-completos');
    if (estadoElement) {
        estadoElement.textContent = data.estado_general || 'DESCONOCIDO';
        estadoElement.className = `mb-0 text-${obtenerColorPorEstado(data.estado_general)}`;
    }
    
    // Contador de sensores
    const contadorElement = document.getElementById('sensores-completos-count');
    if (contadorElement) {
        const total = data.total_sensores || 13;
        const normales = data.sensores_normales || 0;
        contadorElement.textContent = `${normales} de ${total} sensores operativos`;
    }
    
    // Calcular y mostrar pH promedio
    const phPromedioElement = document.getElementById('ph-promedio');
    if (phPromedioElement && data.sensores && data.sensores.ph) {
        const ph1 = data.sensores.ph.biodigestor_1?.valor || 7.0;
        const ph2 = data.sensores.ph.biodigestor_2?.valor || 7.0;
        const promedio = ((ph1 + ph2) / 2).toFixed(1);
        phPromedioElement.textContent = promedio;
    }
    
    // Estado presión línea
    const estadoPresionElement = document.getElementById('estado-presion-linea');
    if (estadoPresionElement && data.sensores && data.sensores.presion) {
        const estado = data.sensores.presion.linea_gas?.estado || 'NORMAL';
        estadoPresionElement.textContent = estado;
    }
    
    // Generación total adicional
    const genTotalElement = document.getElementById('gen-total-adicional');
    if (genTotalElement && data.sensores && data.sensores.energia) {
        const genSec = data.sensores.energia.generacion_secundaria?.valor || 0;
        const genTer = data.sensores.energia.generacion_terciaria?.valor || 0;
        const total = (genSec + genTer).toFixed(1);
        genTotalElement.textContent = `${total} kW`;
    }
}

function obtenerColorPorEstado(estado) {
    const estadoUpper = estado ? estado.toUpperCase() : 'DESCONOCIDO';
    switch (estadoUpper) {
        case 'NORMAL': return 'success';
        case 'ALERTA': return 'warning';
        case 'CRÍTICO': 
        case 'CRITICO': return 'danger';
        case 'ERROR': return 'danger';
        default: return 'secondary';
    }
}

function mostrarErrorSensoresCompletos(mensaje) {
    console.error('Error sensores completos:', mensaje);
    
    // Mostrar error en elementos principales
    const elementos = [
        'presion-linea-gas', 'flujo-biogas', 'ph-biodigestor-1', 'ph-biodigestor-2',
        'temp-adicional-bio1', 'temp-adicional-bio2', 'temp-linea-gas',
        'gen-secundaria', 'gen-terciaria', 'o2-secundario', 'ch4-secundario',
        'co2-secundario', 'h2s-secundario'
    ];
    
    elementos.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = '-- Error';
            element.className = 'text-danger mb-1';
        }
    });
    
    // Estado general
    const estadoElement = document.getElementById('estado-general-completos');
    if (estadoElement) {
        estadoElement.textContent = 'ERROR';
        estadoElement.className = 'mb-0 text-danger';
    }
    
    if (typeof toastr !== 'undefined') {
        toastr.error(mensaje);
    }
}

// =============================================================================
// GESTIÓN DE ESTADO DE CONEXIÓN Y ACTUALIZACIÓN AUTOMÁTICA
// =============================================================================

function gestionarEstadoConexion(elementoContenedor, exito) {
    if (!elementoContenedor) return;
    
    // El badge de estado es el primer badge, el de conexión es el segundo.
    let badgeConexion = elementoContenedor.querySelector('.sensor-conectado');

    // Si no existe el span para el estado de conexión, lo creamos dinámicamente.
    if (!badgeConexion) {
        badgeConexion = document.createElement('span');
        badgeConexion.className = 'badge sensor-conectado ms-1';
        const badgeEstado = elementoContenedor.querySelector('.badge');
        if (badgeEstado && badgeEstado.parentElement) {
            badgeEstado.parentElement.appendChild(badgeConexion);
        } else {
             // Fallback por si no hay otro badge
            elementoContenedor.appendChild(badgeConexion);
        }
    }
    
    badgeConexion.style.display = 'inline-block';
    if (exito) {
        badgeConexion.textContent = 'Conectado';
        badgeConexion.className = 'badge sensor-conectado ms-1 bg-success text-white';
    } else {
        badgeConexion.textContent = 'Desconectado';
        badgeConexion.className = 'badge sensor-conectado ms-1 bg-danger text-white';
    }
}

// =============================================================================
// FUNCIONES DE ACTUALIZACIÓN (MODIFICADAS)
// =============================================================================

function actualizarSensoresCriticos() {
    fetch('/sensores_criticos_resumen')
        .then(response => {
            const exito = response.ok;
            gestionarEstadoConexion(document.getElementById('card-presion-bio1'), exito);
            gestionarEstadoConexion(document.getElementById('card-presion-bio2'), exito);
            gestionarEstadoConexion(document.getElementById('card-flujo-bio1'), exito);
            gestionarEstadoConexion(document.getElementById('card-flujo-bio2'), exito);
            gestionarEstadoConexion(document.getElementById('card-nivel-bio1'), exito);
            gestionarEstadoConexion(document.getElementById('card-nivel-bio2'), exito);
            if (!exito) throw new Error('Error de red');
            return response.json();
        })
        .then(data => mostrarSensoresCriticos(data))
        .catch(error => console.error('Error al actualizar sensores críticos:', error.message));
}

function actualizarBalanceVolumetrico() {
    fetch('/balance_volumetrico_completo')
        .then(response => {
            const exito = response.ok;
            gestionarEstadoConexion(document.getElementById('balance-volumetrico-card').querySelector('.card-header'), exito);
            if (!exito) throw new Error('Error de red');
            return response.json();
        })
        .then(data => mostrarBalanceVolumetrico(data))
        .catch(error => console.error('Error al actualizar balance:', error.message));
}

function actualizarSistemaGasesCompleto() {
    // Esta función ya se encarga de sus propios fetch, pero podemos añadir un estado general
    const contenedor = document.getElementById('gases-biodigestores');
    gestionarEstadoConexion(contenedor, true, '.card-header'); // Asumimos éxito inicial, los fetch individuales lo corregirán
    
    actualizarGasesBio040(); // Estas funciones internas deberían ser modificadas también
    actualizarGasesBio050();
    actualizarGasesMotor070();
}

// =============================================================================
// CICLO DE ACTUALIZACIÓN PRINCIPAL
// =============================================================================

function actualizarTodosLosSistemas() {
    actualizarSensoresCriticos();
    actualizarBalanceVolumetrico();
    actualizarGeneracionActual();
    actualizarPorcentajeProduccion();
    actualizarTemperaturasBiodigestores();
    
    // Si la pestaña de gases está activa, también la actualizamos
    if(document.getElementById('gases-biodigestores')?.classList.contains('active')) {
            actualizarSistemaGasesCompleto();
        }
}

// ===== FUNCIONES DE CARGA DE PESTAÑAS =====

function cargarPlanMensual() {
    console.log("📆 Cargando plan mensual...");
    if (typeof cargarPlanMensualCorregido === 'function') {
        cargarPlanMensualCorregido();
    } else {
        console.warn("⚠️ Función cargarPlanMensualCorregido no disponible");
    }
}

function cargarPlanSemanal() {
    console.log("📅 Cargando plan semanal...");
    if (typeof cargarPlanSemanalCorregido === 'function') {
        cargarPlanSemanalCorregido();
    } else {
        console.warn("⚠️ Función cargarPlanSemanalCorregido no disponible");
    }
}

function cargarHistoricoDiario() {
    console.log("📊 Cargando histórico diario...");
    if (typeof inicializarHistoricoDiario === 'function') {
        inicializarHistoricoDiario();
    } else {
        console.warn("⚠️ Función inicializarHistoricoDiario no disponible");
    }
}

function cargarKPIs() {
    console.log("📈 Cargando KPIs...");
    if (typeof actualizarKPIsCorregido === 'function') {
        actualizarKPIsCorregido();
    } else {
        console.warn("⚠️ Función actualizarKPIsCorregido no disponible");
    }
}

function cargarSeguimientoHorario() {
    console.log("⏰ Cargando seguimiento horario...");
    // Implementar carga de seguimiento horario
}

function cargarAnalisisEconomico() {
    console.log("💰 Cargando análisis económico...");
    // Implementar carga de análisis económico
}
