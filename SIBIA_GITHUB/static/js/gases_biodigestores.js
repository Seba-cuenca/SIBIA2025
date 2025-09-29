// =============================================================================
// FUNCIONES PARA ACTUALIZAR GASES DE BIODIGESTORES
// =============================================================================

// Función para actualizar gases del Biodigestor 040
function actualizarGasesBio040() {
    console.log('Actualizando gases Biodigestor 040...');
    
    fetch('/gases_biodigestor_040')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos Bio 040:', data);
            mostrarGasesBiodigestor('040', data);
        })
        .catch(error => {
            console.error('Error obteniendo gases Bio 040:', error);
            mostrarErrorGases('040');
        });
}

// Función para actualizar gases del Biodigestor 050
function actualizarGasesBio050() {
    console.log('Actualizando gases Biodigestor 050...');
    
    fetch('/gases_biodigestor_050')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos Bio 050:', data);
            mostrarGasesBiodigestor('050', data);
        })
        .catch(error => {
            console.error('Error obteniendo gases Bio 050:', error);
            mostrarErrorGases('050');
        });
}

// Función para actualizar gases del Motor 070
function actualizarGasesMotor070() {
    console.log('Actualizando gases Motor 070...');
    
    fetch('/composicion_gas_completa')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos Motor 070:', data);
            mostrarGasesMotor('070', data);
        })
        .catch(error => {
            console.error('Error obteniendo gases Motor 070:', error);
            mostrarErrorGases('motor-070');
        });
}

// Función para mostrar los datos de gases de un biodigestor
function mostrarGasesBiodigestor(bioId, data) {
    const contenedor = document.getElementById(`gases-bio-${bioId}`);
    if (!contenedor) {
        console.error(`No se encontró contenedor para Bio ${bioId}`);
        return;
    }
    
    // Verificar que tengamos datos de gases
    if (!data.gases) {
        console.error(`No hay datos de gases para Bio ${bioId}`);
        mostrarErrorGases(bioId);
        return;
    }
    
    // Actualizar cada gas
    const gases = ['co2', 'ch4', 'o2', 'h2s'];
    gases.forEach(gas => {
        const gasDiv = contenedor.querySelector(`[data-gas="${gas}"]`);
        if (gasDiv && data.gases[gas]) {
            const valorElement = gasDiv.querySelector('.sensor-valor');
            const estadoElement = gasDiv.querySelector('.sensor-estado');
            
            if (valorElement) {
                const valor = data.gases[gas].valor || '--';
                const unidad = gas === 'h2s' ? ' ppm' : '%';
                valorElement.textContent = valor !== '--' ? valor + unidad : '--';
            }
            
            if (estadoElement) {
                const estado = data.gases[gas].estado || 'DESCONOCIDO';
                estadoElement.textContent = estado;
                estadoElement.className = `sensor-estado badge bg-${getColorByEstado(estado)}`;
            }
        }
    });
    
    // Actualizar estado general
    const estadoGeneralElement = document.getElementById(`estado-general-${bioId}`);
    if (estadoGeneralElement) {
        const estado = data.estado_general || 'DESCONOCIDO';
        estadoGeneralElement.textContent = `Estado: ${estado}`;
        estadoGeneralElement.className = `badge bg-${getColorByEstado(estado)}`;
    }
    
    // Actualizar fecha
    const fechaElement = document.getElementById(`fecha-${bioId}`);
    if (fechaElement) {
        const fecha = data.timestamp || new Date().toLocaleString();
        fechaElement.textContent = `Última actualización: ${fecha}`;
    }
    
    // Actualizar la tabla de comparación
    actualizarTablaComparacion();
}

// Función para mostrar los datos de gases del motor
function mostrarGasesMotor(motorId, data) {
    // Los datos vienen en formato diferente para el motor
    // El endpoint devuelve: metano, oxigeno, dioxido_carbono, sulfidrico
    
    // CO2
    if (data.dioxido_carbono) {
        actualizarGasMotor('co2', data.dioxido_carbono, '070AIT01AO3');
    }
    
    // CH4
    if (data.metano) {
        actualizarGasMotor('ch4', data.metano, '070AIT01AO2');
    }
    
    // O2
    if (data.oxigeno) {
        actualizarGasMotor('o2', data.oxigeno, '070AIT01AO1');
    }
    
    // H2S
    if (data.sulfidrico) {
        actualizarGasMotor('h2s', data.sulfidrico, '070AIT01AO4');
    }
    
    // Actualizar estado general
    const estadoGeneralElement = document.getElementById('estado-general-070');
    if (estadoGeneralElement) {
        const estado = data.estado_general || data.estado || 'NORMAL';
        estadoGeneralElement.textContent = `Estado: ${estado.toUpperCase()}`;
        estadoGeneralElement.className = `badge bg-${getColorByEstado(estado)}`;
    }
    
    // Actualizar fecha
    const fechaElement = document.getElementById('fecha-070');
    if (fechaElement) {
        const fecha = data.timestamp || new Date().toLocaleString();
        fechaElement.textContent = `Última actualización: ${fecha}`;
    }
    
    // Actualizar la tabla de comparación
    actualizarTablaComparacion();
}

// Función auxiliar para actualizar un gas específico del motor
function actualizarGasMotor(gas, datos, sensor) {
    const valorElement = document.getElementById(`motor070-${gas}-valor`);
    const estadoElement = document.getElementById(`motor070-${gas}-estado`);
    
    if (valorElement && datos) {
        const valor = datos.valor !== undefined ? datos.valor : '--';
        const unidad = gas === 'h2s' ? ' ppm' : ' %';
        valorElement.textContent = valor !== '--' ? valor + unidad : '-- ' + unidad.trim();
    }
    
    if (estadoElement && datos) {
        const estado = datos.estado || 'NORMAL';
        estadoElement.textContent = estado;
        estadoElement.className = `badge bg-${getColorByEstado(estado)}`;
    }
}

// Función para mostrar error en los gases
function mostrarErrorGases(id) {
    if (id === '040' || id === '050') {
        const contenedor = document.getElementById(`gases-bio-${id}`);
        if (contenedor) {
            const gases = ['co2', 'ch4', 'o2', 'h2s'];
            gases.forEach(gas => {
                const gasDiv = contenedor.querySelector(`[data-gas="${gas}"]`);
                if (gasDiv) {
                    const valorElement = gasDiv.querySelector('.sensor-valor');
                    const estadoElement = gasDiv.querySelector('.sensor-estado');
                    
                    if (valorElement) valorElement.textContent = '--';
                    if (estadoElement) {
                        estadoElement.textContent = 'ERROR';
                        estadoElement.className = 'sensor-estado badge bg-danger';
                    }
                }
            });
            
            const estadoGeneralElement = document.getElementById(`estado-general-${id}`);
            if (estadoGeneralElement) {
                estadoGeneralElement.textContent = 'Estado: ERROR';
                estadoGeneralElement.className = 'badge bg-danger';
            }
        }
    } else if (id === 'motor-070') {
        ['co2', 'ch4', 'o2', 'h2s'].forEach(gas => {
            const valorElement = document.getElementById(`motor070-${gas}-valor`);
            const estadoElement = document.getElementById(`motor070-${gas}-estado`);
            
            if (valorElement) valorElement.textContent = '-- ' + (gas === 'h2s' ? 'ppm' : '%');
            if (estadoElement) {
                estadoElement.textContent = 'ERROR';
                estadoElement.className = 'badge bg-danger';
            }
        });
    }
}

// Función para actualizar la tabla de comparación
function actualizarTablaComparacion() {
    console.log('Actualizando tabla de comparación...');
    
    // Obtener los valores actuales de cada biodigestor y motor
    const gases = ['co2', 'ch4', 'o2', 'h2s'];
    
    gases.forEach(gas => {
        // Obtener valores del Bio 040
        const bio040Div = document.querySelector(`#gases-bio-040 [data-gas="${gas}"] .sensor-valor`);
        const bio040Valor = bio040Div ? parseFloat(bio040Div.textContent) || 0 : 0;
        
        // Obtener valores del Bio 050
        const bio050Div = document.querySelector(`#gases-bio-050 [data-gas="${gas}"] .sensor-valor`);
        const bio050Valor = bio050Div ? parseFloat(bio050Div.textContent) || 0 : 0;
        
        // Obtener valores del Motor 070
        const motor070Element = document.getElementById(`motor070-${gas}-valor`);
        const motor070Valor = motor070Element ? parseFloat(motor070Element.textContent) || 0 : 0;
        
        // Calcular promedio de biodigestores
        const promedio = (bio040Valor + bio050Valor) / 2;
        
        // Calcular diferencia
        const diferencia = motor070Valor - promedio;
        
        // Actualizar la tabla
        document.getElementById(`comp-${gas}-bio040`).textContent = bio040Valor.toFixed(2);
        document.getElementById(`comp-${gas}-bio050`).textContent = bio050Valor.toFixed(2);
        document.getElementById(`comp-${gas}-promedio`).textContent = promedio.toFixed(2);
        document.getElementById(`comp-${gas}-motor`).textContent = motor070Valor.toFixed(2);
        document.getElementById(`comp-${gas}-diferencia`).textContent = diferencia > 0 ? `+${diferencia.toFixed(2)}` : diferencia.toFixed(2);
        
        // Determinar estado según la diferencia
        let estado = 'NORMAL';
        let colorClase = 'bg-success';
        
        if (gas === 'ch4') {
            // Para metano, queremos que sea similar o mayor en el motor
            if (diferencia < -5) {
                estado = 'ALERTA';
                colorClase = 'bg-warning';
            } else if (diferencia < -10) {
                estado = 'CRÍTICO';
                colorClase = 'bg-danger';
            }
        } else if (gas === 'o2') {
            // Para oxígeno, queremos que sea bajo
            if (Math.abs(diferencia) > 1) {
                estado = 'ALERTA';
                colorClase = 'bg-warning';
            } else if (Math.abs(diferencia) > 2) {
                estado = 'CRÍTICO';
                colorClase = 'bg-danger';
            }
        } else if (gas === 'h2s') {
            // Para H2S, queremos que sea bajo
            if (Math.abs(diferencia) > 100) {
                estado = 'ALERTA';
                colorClase = 'bg-warning';
            } else if (Math.abs(diferencia) > 200) {
                estado = 'CRÍTICO';
                colorClase = 'bg-danger';
            }
        } else if (gas === 'co2') {
            // Para CO2, diferencias moderadas son aceptables
            if (Math.abs(diferencia) > 5) {
                estado = 'ALERTA';
                colorClase = 'bg-warning';
            } else if (Math.abs(diferencia) > 10) {
                estado = 'CRÍTICO';
                colorClase = 'bg-danger';
            }
        }
        
        const estadoElement = document.getElementById(`comp-${gas}-estado`);
        if (estadoElement) {
            estadoElement.textContent = estado;
            estadoElement.className = `badge ${colorClase}`;
        }
    });
    
    // Actualizar estado general del sistema
    actualizarEstadoGeneralSistema();
    
    // Actualizar recomendaciones
    actualizarRecomendacionesSistema();
}

// Función auxiliar para obtener el color según el estado
function getColorByEstado(estado) {
    const estadoUpper = (estado || '').toUpperCase();
    switch (estadoUpper) {
        case 'NORMAL': return 'success';
        case 'ALERTA': return 'warning';
        case 'CRÍTICO':
        case 'CRITICO': return 'danger';
        case 'ERROR': return 'danger';
        default: return 'secondary';
    }
}

// Función para actualizar todo el sistema de gases
function actualizarSistemaGasesCompleto() {
    console.log('Actualizando sistema completo de gases...');
    actualizarGasesBio040();
    actualizarGasesBio050();
    actualizarGasesMotor070();
}

// Función principal que es llamada desde otros scripts
function actualizarGasesBiodigestores() {
    console.log('🌬️ Actualizando gases biodigestores...');
    actualizarSistemaGasesCompleto();
}

// Función para actualizar el estado general del sistema
function actualizarEstadoGeneralSistema() {
    const estados = [];
    
    // Recolectar todos los estados de la tabla
    ['co2', 'ch4', 'o2', 'h2s'].forEach(gas => {
        const estadoElement = document.getElementById(`comp-${gas}-estado`);
        if (estadoElement) {
            estados.push(estadoElement.textContent);
        }
    });
    
    // Determinar el estado general
    let estadoGeneral = 'NORMAL';
    if (estados.includes('CRÍTICO')) {
        estadoGeneral = 'CRÍTICO';
    } else if (estados.includes('ALERTA')) {
        estadoGeneral = 'ALERTA';
    }
    
    const sistemaEstadoElement = document.getElementById('sistema-estado-general');
    if (sistemaEstadoElement) {
        sistemaEstadoElement.textContent = `Estado del Sistema: ${estadoGeneral}`;
        sistemaEstadoElement.className = `badge bg-${getColorByEstado(estadoGeneral)}`;
    }
}

// Función para actualizar las recomendaciones del sistema
function actualizarRecomendacionesSistema() {
    const recomendaciones = [];
    
    // Obtener valores para análisis
    const ch4Bio040 = parseFloat(document.getElementById('comp-ch4-bio040')?.textContent) || 0;
    const ch4Bio050 = parseFloat(document.getElementById('comp-ch4-bio050')?.textContent) || 0;
    const ch4Motor = parseFloat(document.getElementById('comp-ch4-motor')?.textContent) || 0;
    const o2Motor = parseFloat(document.getElementById('comp-o2-motor')?.textContent) || 0;
    const h2sBio040 = parseFloat(document.getElementById('comp-h2s-bio040')?.textContent) || 0;
    const h2sBio050 = parseFloat(document.getElementById('comp-h2s-bio050')?.textContent) || 0;
    const h2sMotor = parseFloat(document.getElementById('comp-h2s-motor')?.textContent) || 0;
    
    // Análisis de metano
    if (ch4Motor < 50) {
        recomendaciones.push('⚠️ CH4 bajo en motor. Revisar calidad del biogás.');
    }
    if (Math.abs(ch4Bio040 - ch4Bio050) > 10) {
        recomendaciones.push('📊 Diferencia significativa de CH4 entre biodigestores.');
    }
    
    // Análisis de oxígeno
    if (o2Motor > 2) {
        recomendaciones.push('🔴 O2 alto en motor. Posible entrada de aire en el sistema.');
    }
    
    // Análisis de H2S
    if (h2sMotor > 500) {
        recomendaciones.push('💨 H2S elevado en motor. Revisar sistema de desulfuración.');
    }
    if (h2sBio040 > 500 || h2sBio050 > 500) {
        recomendaciones.push('⚠️ H2S elevado en biodigestores. Ajustar proceso de digestión.');
    }
    
    // Si no hay problemas
    if (recomendaciones.length === 0) {
        recomendaciones.push('✅ Sistema operando dentro de parámetros normales.');
    }
    
    // Actualizar el listado de recomendaciones
    const listaElement = document.getElementById('recomendaciones-sistema-gases');
    if (listaElement) {
        listaElement.innerHTML = recomendaciones.map(rec => `<li>${rec}</li>`).join('');
    }
}

// Exportar funciones para uso global
window.actualizarGasesBio040 = actualizarGasesBio040;
window.actualizarGasesBio050 = actualizarGasesBio050;
window.actualizarGasesMotor070 = actualizarGasesMotor070;
window.actualizarSistemaGasesCompleto = actualizarSistemaGasesCompleto;
window.actualizarGasesBiodigestores = actualizarGasesBiodigestores;
window.actualizarTablaComparacion = actualizarTablaComparacion;

console.log('Módulo de gases de biodigestores cargado correctamente'); 