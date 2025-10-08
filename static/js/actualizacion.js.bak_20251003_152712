/**
 * Sistema de actualización automática para la interfaz de usuario del sistema de biodigestores.
 * Este script maneja la actualización de datos en tiempo real para la interfaz.
 */

// Variables globales
let intervaloActualizacion = null; // Guarda referencia al intervalo de actualización
const INTERVALO_MS = 3000; // 3 segundos entre actualizaciones - DATOS EN TIEMPO REAL
let graficoStock = null;

/**
 * Función helper para formatear números de forma segura
 */
function safeToFixed(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return (0).toFixed(decimals);
    }
    return parseFloat(value).toFixed(decimals);
}

/**
 * Muestra u oculta los indicadores de carga
 * @param {boolean} mostrar - Indica si mostrar (true) u ocultar (false) los indicadores
 */
function mostrarSpinner(mostrar) {
    try {
        // Convertir a booleano para asegurar valores válidos
        const shouldShow = !!mostrar;
        const displayValue = shouldShow ? 'block' : 'none';
        const displayInline = shouldShow ? 'inline' : 'none';
        
        // Actualizar el spinner principal si existe
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = displayValue;
        }
        
        // Actualizar el spinner de navegación si existe
        const spinnerNav = document.getElementById('spinnerActualizacion');
        if (spinnerNav) {
            spinnerNav.style.display = displayInline;
        }
    } catch (error) {
        console.error('Error al mostrar/ocultar spinners:', error);
    }
}

/**
 * Actualiza las tablas y valores de la interfaz obteniendo datos del servidor
 * Esta es la función principal que realiza las peticiones a los endpoints
 */
function actualizarTablas() {
    mostrarSpinner(true);
    
    // Actualizar stock actual (con sincronización automática)
    fetch(window.location.origin + '/stock_actual?t=' + new Date().getTime())
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos recibidos:", data);
            
            // Extraer el stock del objeto de respuesta
            let stockData = data;
            if (data && data.status === 'success' && data.stock) {
                stockData = data.stock;
                console.log("✅ Stock extraído de respuesta exitosa");
            } else if (data && typeof data === 'object' && !data.status) {
                // Formato anterior sin wrapper
                stockData = data;
                console.log("📦 Usando formato anterior de stock");
            } else {
                console.warn("Formato de datos de stock inesperado:", data);
                return;
            }
            
            window.datosDistribucionGlobal = stockData; // Guardar datos globalmente

            // === INICIO: CORRECCIÓN FORMATO STOCK ===
            // Verificar si 'stockData' es un objeto y convertirlo a array si es necesario
            let stockArray = [];
            if (stockData && typeof stockData === 'object' && !Array.isArray(stockData)) {
                stockArray = Object.entries(stockData).map(([material, detalles]) => ({
                    material: material,
                    cantidad: detalles.total_tn || 0,
                    total_solido: detalles.total_solido || 0,
                    st_porcentaje: detalles.st_porcentaje || 0, // Agregar ST%
                    ultima_actualizacion: detalles.ultima_actualizacion || '-'
                }));
                 console.log("Datos de stock (objeto) convertidos a array para tabla.");
            } else if (Array.isArray(stockData)) {
                 stockArray = stockData; // Ya es un array
                 console.log("Datos de stock (array) recibidos.");
            } else {
                console.warn("Formato de datos de stock inesperado o vacío:", stockData);
                return;
            }
            // === FIN: CORRECCIÓN FORMATO STOCK ===
            
            const tabla = document.getElementById('stock-actual-table');
            if (tabla) {
                const tbody = tabla.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = '';
                    
                    // Usar stockArray procesado
                    stockArray.forEach(item => {
                        if (item && item.material) {
                            const fila = document.createElement('tr');
                            const cantidad = parseFloat(item.cantidad || 0);
                            
                            // Formatear total_tn con separador de miles y sin decimales
                            const formattedTn = cantidad.toLocaleString('es-ES', { minimumFractionDigits: 0, maximumFractionDigits: 0 });

                            // Formatear ST a porcentaje entero, usando st_porcentaje del endpoint actualizado
                            let formattedSt = 'N/A';
                            const stPorcentaje = item.st_porcentaje;

                            if (typeof stPorcentaje === 'number' && !isNaN(stPorcentaje)) {
                                formattedSt = Math.round(stPorcentaje); // Ya es %, solo redondear
                            }

                            fila.innerHTML = `
                                <td>${item.material}</td>
                                <td>${formattedTn}</td>
                                <td>${formattedSt}%</td>
                                <td>${item.ultima_actualizacion || '-'}</td>
                            `;
                            tbody.appendChild(fila);
                        }
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error al actualizar stock:', error);
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al actualizar el stock');
            }
        })
        .finally(() => {
            mostrarSpinner(false);
        });

    // Actualizar distribución actual
    fetch(window.location.origin + '/seguimiento_horario')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos recibidos:", data);

            // ---> AGREGADO: Depuración de KW por tipo <---
            console.log("[DEBUG] KW Sólidos recibido:", data.kw_generados_solidos);
            console.log("[DEBUG] KW Líquidos recibido:", data.kw_generados_liquidos);
            // ---> FIN AGREGADO <---
            
            // Validar que los datos sean un objeto y no un array u otro tipo
            if (!data || typeof data !== 'object' || Array.isArray(data)) {
                console.error("Formato de datos incorrecto:", data);
                return;
            }
            
            // IMPORTANTE: Verificar estructura de datos antes de acceder a propiedades
            // Esto evita el error 'list object has no attribute materiales_solidos'
            if (!data.materiales_solidos || typeof data.materiales_solidos !== 'object') {
                console.error("Datos sin materiales_solidos válidos:", data);
                data.materiales_solidos = {};
            }
            
            if (!data.materiales_liquidos || typeof data.materiales_liquidos !== 'object') {
                console.error("Datos sin materiales_liquidos válidos:", data);
                data.materiales_liquidos = {};
            }
            
            // Obtener valores con validaciones para evitar errores
            let kwObjetivo = parseFloat(data.kw_objetivo || 0);
            let kwGenerados = parseFloat(data.kw_generados || 0.1); // Mínimo 0.1 para evitar división por cero
            let porcentajeMetano = parseFloat(data.porcentaje_metano || 0);
            let totalSolidos = parseFloat(data.total_solidos || 0);
            let totalLiquidos = parseFloat(data.total_liquidos || 0);
            
            // Calcular porcentaje de avance con protección contra división por cero
            let porcentajeKw = kwObjetivo > 0 ? (kwGenerados / kwObjetivo) * 100 : 0;
            
            // Limitar porcentaje a 100 como máximo
            porcentajeKw = Math.min(porcentajeKw, 100);
            
            // Debug para ayudar a encontrar problemas
            console.log("Valores calculados:", {
                kwObjetivo, kwGenerados, porcentajeMetano, 
                totalSolidos, totalLiquidos, porcentajeKw
            });
            
            // Actualizar valores en la interfaz con formato
            // Verificar que existan los elementos antes de modificarlos
            // --- ELIMINADO: Bloque que intentaba actualizar IDs incorrectos --- 
            /*
            const elementosId = [
                'kw-objetivo', 'kw-generados', 'porcentaje-metano', 
                'total-solidos', 'total-liquidos'
            ];
            const valores = [
                kwObjetivo.toFixed(2),
                kwGenerados.toFixed(2),
                porcentajeMetano.toFixed(2) + '%',
                totalSolidos.toFixed(2) + ' TN',
                totalLiquidos.toFixed(2) + ' TN'
            ];
            
            elementosId.forEach((id, index) => {
                const elemento = document.getElementById(id);
                if (elemento) {
                    elemento.innerText = valores[index];
                    console.log(`Actualizado ${id} con valor ${valores[index]}`);
                } else {
                    console.log(`Elemento ${id} no encontrado`);
                }
            });
            */
            // --- FIN ELIMINADO ---
            
            // === INICIO: Reactivar actualización de campos principales ===
            // IDs corregidos basados en la inspección del HTML
            const kwObjetivoEl = document.getElementById('kw_objetivo_display'); 
            if (kwObjetivoEl) kwObjetivoEl.innerText = kwObjetivo.toFixed(2);
            else console.warn("Elemento con ID 'kw_objetivo_display' no encontrado.");

            const kwGeneradosEl = document.getElementById('kw_generados_display');
            if (kwGeneradosEl) kwGeneradosEl.innerText = kwGenerados.toFixed(2);
            else console.warn("Elemento con ID 'kw_generados_display' no encontrado.");

            const porcentajeMetanoEl = document.getElementById('porcentaje_metano_display');
            if (porcentajeMetanoEl) porcentajeMetanoEl.innerText = porcentajeMetano.toFixed(2) + '%';
            else console.warn("Elemento con ID 'porcentaje_metano_display' no encontrado.");

            const totalSolidosEl = document.getElementById('total_solidos_display');
            if (totalSolidosEl) totalSolidosEl.innerText = totalSolidos.toFixed(2);
            else console.warn("Elemento con ID 'total_solidos_display' no encontrado.");

            const totalLiquidosEl = document.getElementById('total_liquidos_display');
            if (totalLiquidosEl) totalLiquidosEl.innerText = totalLiquidos.toFixed(2);
            else console.warn("Elemento con ID 'total_liquidos_display' no encontrado.");
            // === FIN: Reactivar actualización ===

            // Actualizar tablas de materiales
            // --- CORREGIDO: Usar IDs correctos del tbody ---
            // === ELIMINADO: Estas llamadas parecen ser para el pop-up, no la vista principal ===
            // actualizarTablaMateriales('tabla-materiales-solidos-body', data.materiales_solidos);
            // actualizarTablaMateriales('tabla-materiales-liquidos-body', data.materiales_liquidos);
            // === FIN ELIMINADO ===
            
            // --- Actualizar los totales en los footers de las tablas --- 
            // --- CORREGIDO: Usar IDs correctos de los spans en tfoot ---
            const totalSolidosElement = document.getElementById('total-solidos-mezcla'); 
            if (totalSolidosElement) totalSolidosElement.innerText = totalSolidos.toFixed(2) + ' TN';
            // Mantener actualización del % metano general si es necesario en el footer, aunque no parece haber un ID específico para ello
            // const promedioMetanoSolidosElement = document.getElementById('promedio-metano-solidos'); 
            // if (promedioMetanoSolidosElement) promedioMetanoSolidosElement.innerText = porcentajeMetano.toFixed(2) + ' %';

            const totalLiquidosElement = document.getElementById('total-liquidos-mezcla'); 
            if (totalLiquidosElement) totalLiquidosElement.innerText = totalLiquidos.toFixed(2) + ' TN';
            // const promedioMetanoLiquidosElement = document.getElementById('promedio-metano-liquidos');
            // if (promedioMetanoLiquidosElement) promedioMetanoLiquidosElement.innerText = porcentajeMetano.toFixed(2) + ' %'; 

            // --- Actualizar Resumen Generación Biodigestor 1 --- (Y potencialmente otros)
            const numBiodigestores = data.num_biodigestores || 1; // Obtener num_biodigestores si está en los datos, sino asumir 1
            console.log(`[JS] Usando numBiodigestores: ${numBiodigestores}`);
            
            // Calcular valores por biodigestor
            const kwObjetivoPorBio = kwObjetivo / numBiodigestores;
            const kwGeneradosPorBio = kwGenerados / numBiodigestores;
            const totalSolidosPorBio = totalSolidos / numBiodigestores;
            const totalLiquidosPorBio = totalLiquidos / numBiodigestores;
            // AGREGADO: Desglose KW por biodigestor
            const kwGenSolidosPorBio = (data.kw_generados_solidos || 0) / numBiodigestores;
            const kwGenLiquidosPorBio = (data.kw_generados_liquidos || 0) / numBiodigestores;
            
            // Actualizar para cada biodigestor (asumiendo que hay elementos con los IDs)
            for (let i = 1; i <= numBiodigestores; i++) {
                const kwObjBioEl = document.getElementById(`kw-objetivo-bio${i}`);
                if (kwObjBioEl) kwObjBioEl.innerText = kwObjetivoPorBio.toFixed(2);
                
                const kwGenBioEl = document.getElementById(`kw-generados-bio${i}`);
                if (kwGenBioEl) kwGenBioEl.innerText = kwGeneradosPorBio.toFixed(2);
                
                const metanoBioEl = document.getElementById(`metano-bio${i}`);
                if (metanoBioEl) metanoBioEl.innerText = porcentajeMetano.toFixed(2); // El % metano es general
                
                const totalSolidosBioEl = document.getElementById(`total-solidos-bio${i}`);
                if (totalSolidosBioEl) totalSolidosBioEl.innerText = totalSolidosPorBio.toFixed(2);
                
                const totalLiquidosBioEl = document.getElementById(`total-liquidos-bio${i}`);
                if (totalLiquidosBioEl) totalLiquidosBioEl.innerText = totalLiquidosPorBio.toFixed(2);
                
                // AGREGADO: Actualizar desglose KW por biodigestor
                const kwGenSolBioEl = document.getElementById(`kw-gen-solidos-bio${i}`);
                if (kwGenSolBioEl) kwGenSolBioEl.innerText = kwGenSolidosPorBio.toFixed(2);
                
                const kwGenLiqBioEl = document.getElementById(`kw-gen-liquidos-bio${i}`);
                if (kwGenLiqBioEl) kwGenLiqBioEl.innerText = kwGenLiquidosPorBio.toFixed(2);

                // --- AGREGADO: Actualizar tablas y totales de planificación del biodigestor i ---
                // Preparar datos divididos para las tablas
                const materialesSolidosPorBio = {};
                for (const [mat, info] of Object.entries(data.materiales_solidos || {})) {
                    materialesSolidosPorBio[mat] = { 
                        ...info, // Copiar otras propiedades (st, metano)
                        cantidad: (info.cantidad || 0) / numBiodigestores 
                    };
                }
                const materialesLiquidosPorBio = {};
                for (const [mat, info] of Object.entries(data.materiales_liquidos || {})) {
                    materialesLiquidosPorBio[mat] = { 
                         ...info, // Copiar otras propiedades (st, metano)
                        cantidad: (info.cantidad || 0) / numBiodigestores 
                    };
                }

                // Llamar a actualizarTablaMateriales con los IDs específicos y datos divididos
                actualizarTablaMateriales(`tabla-materiales-solidos-body-bio${i}`, materialesSolidosPorBio);
                actualizarTablaMateriales(`tabla-materiales-liquidos-body-bio${i}`, materialesLiquidosPorBio);

                // Actualizar totales en el footer de las tablas de planificación
                const totalSolidosMezclaBioEl = document.getElementById(`total-solidos-mezcla-bio${i}`);
                if (totalSolidosMezclaBioEl) totalSolidosMezclaBioEl.innerText = totalSolidosPorBio.toFixed(2) + ' TN';

                const totalLiquidosMezclaBioEl = document.getElementById(`total-liquidos-mezcla-bio${i}`);
                if (totalLiquidosMezclaBioEl) totalLiquidosMezclaBioEl.innerText = totalLiquidosPorBio.toFixed(2) + ' TN';
                 // --- FIN AGREGADO --- 

            }

            // --- Actualizar Resumen General ---            
            const totalKwObj = document.getElementById('total-kw-objetivo');
            if (totalKwObj) { totalKwObj.innerText = kwObjetivo.toFixed(2); }

            // --- AGREGADO: Actualizar los demás elementos del Resumen General ---
            const totalKwGen = document.getElementById('total-kw-generados');
            if (totalKwGen) { totalKwGen.innerText = kwGenerados.toFixed(2); }

            const totalMetano = document.getElementById('total-metano');
            if (totalMetano) { totalMetano.innerText = porcentajeMetano.toFixed(2); }

            const resumenSolidos = document.getElementById('resumen-total-solidos');
            if (resumenSolidos) { resumenSolidos.innerText = totalSolidos.toFixed(2); }

            const resumenLiquidos = document.getElementById('resumen-total-liquidos');
            if (resumenLiquidos) { resumenLiquidos.innerText = totalLiquidos.toFixed(2); }
            // --- FIN AGREGADO ---

            // --- AGREGADO: Actualizar desglose KW y % usados en Resumen General ---
            const resumenKwGenSolidos = document.getElementById('resumen-kw-gen-solidos');
            if (resumenKwGenSolidos) { resumenKwGenSolidos.innerText = (data.kw_generados_solidos || 0).toFixed(2); }

            const resumenKwGenLiquidos = document.getElementById('resumen-kw-gen-liquidos');
            if (resumenKwGenLiquidos) { resumenKwGenLiquidos.innerText = (data.kw_generados_liquidos || 0).toFixed(2); }
            
            const resumenPercUsoSolidos = document.getElementById('resumen-perc-uso-solidos');
            if (resumenPercUsoSolidos) { resumenPercUsoSolidos.innerText = (data.porcentaje_uso_solidos_calc || 0).toFixed(1); }
            
            const resumenPercUsoLiquidos = document.getElementById('resumen-perc-uso-liquidos');
            if (resumenPercUsoLiquidos) { resumenPercUsoLiquidos.innerText = (data.porcentaje_uso_liquidos_calc || 0).toFixed(1); }
            
            const resumenPercPurin = document.getElementById('resumen-perc-purin');
            if (resumenPercPurin) { resumenPercPurin.innerText = (data.porcentaje_purin_calc || 0).toFixed(1); }
            
            const resumenPercSa7 = document.getElementById('resumen-perc-sa7');
            if (resumenPercSa7) { resumenPercSa7.innerText = (data.porcentaje_sa7_reemplazo_calc || 0).toFixed(1); }
            // --- FIN AGREGADO ---

            // Actualizar la barra de progreso
            let progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = porcentajeKw.toFixed(2) + '%';
                progressBar.setAttribute('aria-valuenow', porcentajeKw.toFixed(2));
                progressBar.innerHTML = `${porcentajeKw.toFixed(2)}% (${kwGenerados.toFixed(2)} / ${kwObjetivo.toFixed(2)} KW)`;
            } else {
                console.log("Barra de progreso no encontrada");
            }
            
            console.log("Valores actualizados en la interfaz");
        })
        .catch(error => {
            console.error('Error al obtener la distribución actual:', error);
        })
        .finally(() => {
            mostrarSpinner(false);
        });
        
    // Actualizar el seguimiento horario
    actualizarSeguimientoHorarioCompleto();
    
    // Actualizar temperaturas y niveles si la función existe
    if (typeof actualizarTemperaturasNiveles === 'function') {
        actualizarTemperaturasNiveles();
    }
}

/**
 * Actualiza una tabla de materiales con los datos recibidos
 * @param {string} tableId - ID del tbody de la tabla
 * @param {object} materiales - Objeto con los materiales a mostrar
 */
function actualizarTablaMateriales(tableId, materiales) {
    try {
        const tbody = document.getElementById(tableId);
        if (!tbody) {
            console.log(`Tabla ${tableId} no encontrada`);
            return;
        }
        
        // Limpiar tabla
        tbody.innerHTML = '';
        
        // Si no hay materiales, mostrar una fila vacía
        if (!materiales || Object.keys(materiales).length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Sin datos disponibles</td></tr>';
            return;
        }
        
        // Agregar materiales a la tabla
        Object.entries(materiales).forEach(([nombre, info]) => {
            if (!info || typeof info !== 'object') {
                console.warn(`Material ${nombre} con información inválida:`, info);
                return;
            }
            
            const cantidad = parseFloat(info.cantidad || 0);
            const st = parseFloat(info.st || 0) * 100; // Convertir a porcentaje
            const metano = parseFloat(info.porcentaje_metano || 0);
            
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${nombre}</td>
                <td>${cantidad.toFixed(2)}</td>
                <td>${st.toFixed(2)}</td>
                <td>${metano.toFixed(2)}</td>
            `;
            tbody.appendChild(fila);
        });
    } catch (error) {
        console.error(`Error al actualizar tabla ${tableId}:`, error);
    }
}

/**
 * Actualiza la información específica de un biodigestor
 * @param {number} numBio - Número del biodigestor
 * @param {object} data - Datos del biodigestor
 */
function updateBiodigestorData(numBio, data) {
    try {
        // Validar parámetros de entrada
        if (!numBio || !data || typeof data !== 'object') {
            console.warn('Parámetros inválidos en updateBiodigestorData:', {numBio, data});
            return;
        }
        
        // Actualizar datos de sólidos y líquidos si existen los elementos
        const solidosElement = document.querySelector(`#biodigestor-${numBio} .solidos-cantidad`);
        const liquidosElement = document.querySelector(`#biodigestor-${numBio} .liquidos-cantidad`);
        
        if (solidosElement && data.solidos !== undefined) {
            const solidos = parseFloat(data.solidos);
            solidosElement.textContent = isNaN(solidos) ? "0.00" : solidos.toFixed(2);
        }
        
        if (liquidosElement && data.liquidos !== undefined) {
            const liquidos = parseFloat(data.liquidos);
            liquidosElement.textContent = isNaN(liquidos) ? "0.00" : liquidos.toFixed(2);
        }

        // Actualizar barra de progreso si existe
        const progressBar = document.querySelector(`#biodigestor-${numBio} .progress-bar`);
        if (progressBar && data.porcentaje_completado !== undefined) {
            const porcentaje = parseFloat(data.porcentaje_completado);
            const porcentajeValido = isNaN(porcentaje) ? 0 : Math.min(Math.max(porcentaje, 0), 100);
            progressBar.style.width = `${porcentajeValido}%`;
            progressBar.setAttribute('aria-valuenow', porcentajeValido);
            progressBar.textContent = `${porcentajeValido.toFixed(0)}%`;
        }
    } catch (error) {
        console.error('Error en updateBiodigestorData:', error);
    }
}

/**
 * Inicia la actualización automática de la interfaz
 * Configura el intervalo periódico y actualiza la UI
 */
function iniciarActualizacionAutomatica() {
    try {
        const btnIniciar = document.getElementById('btnIniciarActualizacion');
        const btnDetener = document.getElementById('btnDetenerActualizacion');
        
        if (btnIniciar) {
            btnIniciar.style.display = 'none';
        }
        
        if (btnDetener) {
            btnDetener.style.display = 'inline-block';
        }
        
        // Detener cualquier intervalo existente para evitar duplicados
        if (intervaloActualizacion) {
            clearInterval(intervaloActualizacion);
        }
        
        // Realizar una actualización inmediata
        actualizarTablas();
        
        // Configurar la actualización periódica
        intervaloActualizacion = setInterval(actualizarTablas, INTERVALO_MS);
        
        // Mostrar mensaje de éxito si existe toastr
        if (typeof toastr !== 'undefined') {
            toastr.success('Actualización automática iniciada');
        }
        
        console.log('Actualización automática iniciada');
    } catch (error) {
        console.error('Error al iniciar actualización automática:', error);
    }
}

/**
 * Detiene la actualización automática de la interfaz
 * Limpia el intervalo y actualiza la UI
 */
function detenerActualizacionAutomatica() {
    try {
        if (intervaloActualizacion) {
            clearInterval(intervaloActualizacion);
            intervaloActualizacion = null;
        }
        
        const btnIniciar = document.getElementById('btnIniciarActualizacion');
        const btnDetener = document.getElementById('btnDetenerActualizacion');
        
        if (btnIniciar) {
            btnIniciar.style.display = 'inline-block';
        }
        
        if (btnDetener) {
            btnDetener.style.display = 'none';
        }
        
        mostrarSpinner(false);
        
        // Mostrar mensaje de información si existe toastr
        if (typeof toastr !== 'undefined') {
            toastr.info('Actualización automática detenida');
        }
        
        console.log('Actualización automática detenida');
    } catch (error) {
        console.error('Error al detener actualización automática:', error);
    }
}

/**
 * Función para sintetizar voz y reproducir texto
 * @param {string} texto - Texto a reproducir
 */
function hablar(texto) {
    // Validar que el texto sea una cadena y no esté vacío
    if (!texto || typeof texto !== 'string' || texto.trim() === '') {
        console.warn('Texto de voz inválido o vacío');
        return;
    }
    
    // Verificar soporte para síntesis de voz
    if (!window.speechSynthesis) {
        console.warn('Este navegador no soporta la síntesis de voz');
        return;
    }
    
    try {
        window.speechSynthesis.cancel(); // Detener cualquier voz anterior
        const utter = new SpeechSynthesisUtterance(texto);
        
        // Configurar con valores por defecto en caso de error
        utter.lang = 'es-ES';
        utter.rate = 1;
        utter.pitch = 1;
        utter.volume = 1;
        
        // Agregar manejo de errores para la síntesis
        utter.onerror = (event) => {
            console.error('Error en síntesis de voz:', event);
        };
        
        // Reproducir la voz
        window.speechSynthesis.speak(utter);
    } catch (e) {
        console.warn('Error al reproducir voz:', e);
    }
}

/**
 * Inicializa la actualización automática cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando actualizaciones automáticas...');
    
    // Inicializar gráfico de stock
    inicializarGraficoStock();
    
    // Cargar datos iniciales
    actualizarStockEnInterfaz();
    actualizarTablas();
    
    // Configurar actualizaciones periódicas
    iniciarActualizacionAutomatica();
    
    // Configurar evento para borrar stock
    const btnConfirmarBorrarStock = document.getElementById('btnConfirmarBorrarStock');
    if (btnConfirmarBorrarStock) {
        btnConfirmarBorrarStock.addEventListener('click', function() {
            borrarStock();
        });
    }
});

/**
 * Actualiza la sección de seguimiento horario, incluyendo el plan de 24 horas para cada biodigestor.
 */
function actualizarSeguimientoHorarioCompleto() {
    console.log("Iniciando actualización de seguimiento horario...");
    mostrarSpinner(true);
    
    // Limpiar cualquier mensaje de error anterior
    const bioContainer = document.getElementById('biodigestoresContainer');
    if (bioContainer) {
        // Comprobar si hay contenido del spinner pero no biodigestores
        const spinnerVisible = bioContainer.querySelector('.spinner-border');
        const biodigestorCards = bioContainer.querySelectorAll('.biodigestor-card');
        console.log(`Estado actual: spinner visible=${!!spinnerVisible}, biodigestores existentes=${biodigestorCards.length}`);
    }
    
    fetch(window.location.origin + '/seguimiento_horario')
        .then(response => {
            console.log(`Respuesta de API: status=${response.status}`);
            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status} obteniendo planificación horaria.`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos recibidos de seguimiento horario:", data);
            
            // CORRECCIÓN: El endpoint devuelve directamente los datos, no con wrapper success/data
            if (data.error) {
                console.error('Error en respuesta de /seguimiento_horario:', data.error);
                toastr.error(data.error || 'No se pudo cargar el seguimiento horario.');
                return;
            }

            console.log(`Fecha actual: ${data.fecha}`);
            console.log(`Hora actual: ${data.hora_actual}`);
            console.log(`Biodigestores en datos: ${Object.keys(data.biodigestores || {}).length}`);
            
            const horaActual = data.hora_actual || new Date().getHours();

            // Inicializar los biodigestores si no se han creado
            console.log("Llamando a inicializarBiodigestores con los datos recibidos...");
            inicializarBiodigestores(data.biodigestores);

            // Actualizar hora en los formularios de registro
            document.querySelectorAll('[id^="hora_actual_sistema_form_bio"]').forEach(span => {
                span.textContent = horaActual;
            });
            document.querySelectorAll('input[name="hora_actual"]').forEach(input => {
                input.value = horaActual;
            });

            // Procesar cada biodigestor
            console.log("Actualizando datos de cada biodigestor...");
            for (const bioIdStr in data.biodigestores) {
                if (data.biodigestores.hasOwnProperty(bioIdStr)) {
                    const biodigestorData = data.biodigestores[bioIdStr];
                    const plan24h = biodigestorData.plan_24_horas;

                    // Actualizar el progreso diario
                    const biodigestorElement = document.getElementById(`biodigestor_${bioIdStr}`);
                    if (biodigestorElement && plan24h) {
                        console.log(`Actualizando biodigestor #${bioIdStr}`);
                        
                        // Actualizar tabla de seguimiento horario
                        const tabla = biodigestorElement.querySelector('table tbody');
                        if (tabla) {
                            tabla.innerHTML = '';
                            
                            for (let hora = 0; hora < 24; hora++) {
                                const horaData = plan24h[hora.toString()] || {
                                    objetivo_ajustado: { total_solidos: 0, total_liquidos: 0 },
                                    real: { total_solidos: 0, total_liquidos: 0 }
                                };
                                
                                const fila = document.createElement('tr');
                                if (hora === horaActual) {
                                    fila.setAttribute('data-hora-actual', 'true');
                                    fila.classList.add('hora-actual');
                                }
                                
                                fila.innerHTML = `
                                    <td>${hora.toString().padStart(2, '0')}:00</td>
                                    <td>${horaData.objetivo_ajustado.total_solidos.toFixed(1)}</td>
                                    <td>${horaData.objetivo_ajustado.total_liquidos.toFixed(1)}</td>
                                    <td>${horaData.real.total_solidos.toFixed(1)}</td>
                                    <td>${horaData.real.total_liquidos.toFixed(1)}</td>
                                    <td>
                                        <button class="btn btn-sm btn-primary" onclick="editarHora(${bioIdStr}, ${hora})">
                                            Editar
                                        </button>
                                    </td>
                                `;
                                tabla.appendChild(fila);
                            }
                        }
                    }
                }
            }
            
            // Mostrar mensaje de éxito
            if (typeof toastr !== 'undefined') {
                // toastr.success('Seguimiento horario actualizado correctamente');
            }
        })
        .catch(error => {
            console.error('Error al actualizar seguimiento horario:', error);
            
            // Mostrar error en el contenedor
            const bioContainer = document.getElementById('biodigestoresContainer');
            if (bioContainer) {
                bioContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h5>Error al cargar seguimiento horario</h5>
                        <p>Detalles: ${error.message}</p>
                        <button class="btn btn-warning btn-sm" onclick="actualizarSeguimientoHorarioCompleto()">
                            Reintentar
                        </button>
                    </div>
                `;
            }
            
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al cargar seguimiento horario: ' + error.message);
            }
        })
        .finally(() => {
            mostrarSpinner(false);
        });
}

/**
 * Inicializa los biodigestores en el contenedor, usando la plantilla
 * @param {Object} biodigestoresData - Datos de los biodigestores recibidos de la API
 */
function inicializarBiodigestores(biodigestoresData) {
    console.log("Inicializando biodigestores con datos:", biodigestoresData);
    
    // Obtener el contenedor donde se crearán los biodigestores
    const container = document.getElementById('biodigestoresContainer');
    if (!container) {
        console.error('No se encontró el contenedor de biodigestores');
        return;
    }
    
    // Limpiar contenedor siempre (eliminamos la validación que prevenía la inicialización)
    // Eliminar el spinner de carga y cualquier contenido previo
    container.innerHTML = '';
    
    // Obtener la plantilla
    const template = document.getElementById('plantillaBiodigestor');
    if (!template) {
        console.error('No se encontró la plantilla de biodigestor');
        return;
    }
    
    // Para cada biodigestor en los datos
    let contadorBiodigestores = 0;
    for (const bioId in biodigestoresData) {
        if (biodigestoresData.hasOwnProperty(bioId)) {
            contadorBiodigestores++;
            console.log(`Creando biodigestor #${bioId}`);
            
            // Clonar la plantilla
            const clone = template.content.cloneNode(true);
            
            // Configurar el ID y el título
            const biodigestorCard = clone.querySelector('.biodigestor-card');
            biodigestorCard.id = `biodigestor_${bioId}`;
            
            const biodigestorTitle = clone.querySelector('.biodigestor-title');
            biodigestorTitle.textContent = `Biodigestor #${bioId}`;
            
            // NUEVO: Configurar IDs de las tablas internas de materiales
            // ¡¡¡IMPORTANTE!!! Reemplaza '.clase-placeholder-solidos tbody' y '.clase-placeholder-liquidos tbody'
            // con los selectores CSS correctos para los tbody dentro de tu plantillaBiodigestor.
            const tablaSolidosBody = clone.querySelector('.clase-placeholder-solidos tbody'); 
            if (tablaSolidosBody) {
                tablaSolidosBody.id = `tabla-materiales-solidos-body-${bioId}`;
                console.log(`Asignado ID ${tablaSolidosBody.id} a tabla sólidos de bio ${bioId}`);
            } else {
                console.warn(`No se encontró tbody de sólidos para bio ${bioId} usando selector '.clase-placeholder-solidos tbody' en plantilla clonada.`);
            }

            const tablaLiquidosBody = clone.querySelector('.clase-placeholder-liquidos tbody');
            if (tablaLiquidosBody) {
                tablaLiquidosBody.id = `tabla-materiales-liquidos-body-${bioId}`;
                console.log(`Asignado ID ${tablaLiquidosBody.id} a tabla líquidos de bio ${bioId}`);
            } else {
                console.warn(`No se encontró tbody de líquidos para bio ${bioId} usando selector '.clase-placeholder-liquidos tbody' en plantilla clonada.`);
            }
            // FIN NUEVO
            
            // Agregar el biodigestor al contenedor
            container.appendChild(clone);
        }
    }
    
    console.log(`Total de biodigestores creados: ${contadorBiodigestores}`);
    
    // Si no había biodigestores en los datos
    if (Object.keys(biodigestoresData).length === 0) {
        console.warn("No hay biodigestores configurados en los datos recibidos");
        container.innerHTML = `
            <div class="alert alert-warning">
                No hay biodigestores configurados. Configure el número de biodigestores en la sección de Parámetros.
            </div>
        `;
    }
    
    // Configurar el evento para el botón de guardar alimentación
    const btnGuardarAlimentacion = document.getElementById('btnGuardarAlimentacion');
    if (btnGuardarAlimentacion) {
        btnGuardarAlimentacion.addEventListener('click', function() {
            const form = document.getElementById('formRegistrarAlimentacion');
            if (form) {
                const biodigestorId = document.getElementById('biodigestor_id').value;
                const hora = document.getElementById('hora_alimentacion').value;
                const solidosReales = parseFloat(document.getElementById('solidos_reales_tn').value) || 0;
                const liquidosReales = parseFloat(document.getElementById('liquidos_reales_tn').value) || 0;
                const operario = document.getElementById('operario_alimentacion').value;
                
                if (!operario) {
                    const alertaAlimentacion = document.getElementById('alertaAlimentacion');
                    alertaAlimentacion.textContent = 'Por favor ingrese el nombre del operario';
                    alertaAlimentacion.className = 'alert alert-danger';
                    alertaAlimentacion.style.display = 'block';
                    return;
                }
                
                // Enviar datos al servidor
                fetch('/registrar_alimentacion', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        biodigestor: parseInt(biodigestorId),
                        hora: parseInt(hora),
                        solidos_reales_tn: solidosReales,
                        liquidos_reales_tn: liquidosReales,
                        operario: operario
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const alertaAlimentacion = document.getElementById('alertaAlimentacion');
                    if (data.success) {
                        // Cerrar modal
                        const modalElement = document.getElementById('modalRegistrarAlimentacion');
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        modal.hide();
                        
                        // Mostrar mensaje de éxito
                        toastr.success('Alimentación registrada correctamente');
                        
                        // Actualizar datos
                        setTimeout(actualizarSeguimientoHorarioCompleto, 500);
                    } else {
                        // Mostrar error
                        alertaAlimentacion.textContent = data.error || 'Error al registrar alimentación';
                        alertaAlimentacion.className = 'alert alert-danger';
                        alertaAlimentacion.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error al registrar alimentación:', error);
                    const alertaAlimentacion = document.getElementById('alertaAlimentacion');
                    alertaAlimentacion.textContent = 'Error de conexión al registrar alimentación';
                    alertaAlimentacion.className = 'alert alert-danger';
                    alertaAlimentacion.style.display = 'block';
                });
            }
        });
    } else {
        console.warn("No se encontró el botón de guardar alimentación");
    }
}

/**
 * Inicializa el gráfico de stock
 */
function inicializarGraficoStock() {
    const ctx = document.getElementById('graficoStock');
    if (!ctx) {
        console.warn('No se encontró el elemento para el gráfico de stock');
        return;
    }
    
    console.log('Inicializando gráfico de stock');
    
    // Opciones modificadas para el gráfico de stock
    graficoStock = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Cantidad (TN)',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Esto es importante para que se ajuste al contenedor
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Toneladas (TN)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Material'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(2)} TN`;
                        }
                    }
                }
            },
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 0,
                    bottom: 10
                }
            }
        }
    });
}

/**
 * Actualiza el stock en la interfaz
 */
function actualizarStockEnInterfaz() {
    fetch('/obtener_stock_actual_json')
        .then(response => response.json())
        .then(data => {
            // Verificar si 'data' es un objeto y no un array
            if (data && typeof data === 'object' && !Array.isArray(data)) {
                // Convertir el objeto de stock en un array de objetos
                // Cada item del array representará un material y sus propiedades
                const stockArray = Object.entries(data).map(([material, detalles]) => {
                    return {
                        material: material,
                        cantidad: detalles.total_tn || 0,
                        total_solido: detalles.total_solido || 0, // Mantener como porcentaje si así viene
                        ultima_actualizacion: detalles.ultima_actualizacion || '-'
                    };
                });
                actualizarGraficoStock(stockArray);

                // Adicionalmente, actualicemos la tabla de stock aquí también
                // ya que la lógica anterior en actualizarTablas para el stock
                // también esperaba un array.
                const tablaStockBody = document.querySelector('#stock-actual-table tbody');
                if (tablaStockBody) {
                    tablaStockBody.innerHTML = ''; // Limpiar
                    stockArray.forEach(item => {
                        const fila = document.createElement('tr');
                        const cantidad = parseFloat(item.cantidad || 0);
                        // Formatear total_solido como porcentaje si es un número
                        let totalSolidoStr = '0.00 %';
                        if (typeof item.total_solido === 'number') {
                            totalSolidoStr = item.total_solido.toFixed(2) + ' %';
                        } else if (typeof item.total_solido === 'string') {
                            // Si ya es un string (ej. "40.0%"), usarlo directamente
                            totalSolidoStr = item.total_solido.includes('%') ? item.total_solido : parseFloat(item.total_solido).toFixed(2) + ' %';
                        }

                        fila.innerHTML = `
                            <td>${item.material}</td>
                            <td>${isNaN(cantidad) ? "0.00" : cantidad.toFixed(2)}</td>
                            <td>${totalSolidoStr}</td>
                            <td>${item.ultima_actualizacion || '-'}</td>
                        `;
                        tablaStockBody.appendChild(fila);
                    });
                }

            } else if (Array.isArray(data)) {
                // Si ya es un array (comportamiento anterior, por si acaso)
                actualizarGraficoStock(data);
            } else {
                console.error('Formato de datos incorrecto o datos nulos:', data);
            }
        })
        .catch(error => {
            console.error('Error obteniendo datos de stock:', error);
            if (typeof toastr !== 'undefined') {
                toastr.error('Error al obtener datos de stock para el gráfico.');
            }
        });
}

/**
 * Actualiza el gráfico de stock con los datos obtenidos
 * @param {Array} stockData - Array de objetos con datos de stock
 */
function actualizarGraficoStock(stockData) {
    if (!graficoStock) {
        console.warn('El gráfico de stock no está inicializado');
        return;
    }
    
    // Asegurarse de que stockData sea un array
    if (!Array.isArray(stockData)) {
        console.error("actualizarGraficoStock esperaba un array, recibió:", typeof stockData);
        return;
    }
    
    // Filtrar materiales con stock > 0
    const materialesConStock = stockData.filter(item => item.cantidad > 0);
    
    // Preparar datos para el gráfico
    const labels = materialesConStock.map(item => item.material);
    const cantidades = materialesConStock.map(item => item.cantidad);
    const solidosInfo = materialesConStock.map(item => item.total_solido);
    
    // Actualizar gráfico
    graficoStock.data.labels = labels;
    graficoStock.data.datasets[0].data = cantidades;
    // Guardar datos de sólidos para los tooltips
    graficoStock.data.datasets[0].solidosData = solidosInfo;
    
    // Generar colores dinámicos basados en la cantidad de materiales
    const colores = generarColores(labels.length);
    graficoStock.data.datasets[0].backgroundColor = colores.map(c => c + '0.6');
    graficoStock.data.datasets[0].borderColor = colores;
    
    graficoStock.update();
    console.log('Gráfico de stock actualizado con', labels.length, 'materiales');
}

/**
 * Genera colores aleatorios para los gráficos
 * @param {number} cantidad - Cantidad de colores a generar
 * @returns {Array} - Array de colores en formato rgba
 */
function generarColores(cantidad) {
    // Colores predefinidos para consistencia
    const coloresBase = [
        'rgba(54, 162, 235, ', // Azul
        'rgba(255, 99, 132, ', // Rojo
        'rgba(255, 206, 86, ', // Amarillo
        'rgba(75, 192, 192, ', // Verde agua
        'rgba(153, 102, 255, ', // Púrpura
        'rgba(255, 159, 64, ',  // Naranja
        'rgba(199, 199, 199, ', // Gris
        'rgba(83, 102, 255, ',  // Azul oscuro
        'rgba(255, 99, 71, ',   // Tomate
        'rgba(50, 205, 50, '    // Lima
    ];
    
    const colores = [];
    for (let i = 0; i < cantidad; i++) {
        colores.push(coloresBase[i % coloresBase.length] + '1)');
    }
    
    return colores;
}

/**
 * Borra todo el stock
 */
function borrarStock() {
    fetch('/borrar_stock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Cerrar modal
            const modalBorrarStock = bootstrap.Modal.getInstance(document.getElementById('modalBorrarStock'));
            if (modalBorrarStock) {
                modalBorrarStock.hide();
            }
            
            // Mostrar mensaje de éxito
            alert('Stock borrado correctamente');
            
            // Actualizar la interfaz
            actualizarStockEnInterfaz();
            
            // Recargar la página para refrescar todos los datos
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            alert('Error al borrar stock: ' + (data.message || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error de conexión:', error);
        alert('Error de conexión al intentar borrar stock');
    });
}

/**
 * Actualiza específicamente la solapa de energía con manejo de estados
 * Muestra mensajes claros cuando la base de datos está caída
 */
function actualizarSistemaEnergiaCompleto() {
    console.log('🔄 === ACTUALIZANDO SISTEMA COMPLETO DE ENERGÍA ===');
    
    // 1. Actualizar generación (ya funciona)
    if (typeof actualizarGeneracionActualConEstado === 'function') {
        actualizarGeneracionActualConEstado();
    }
    
    // 2. Actualizar energía inyectada (corregido)
    actualizarEnergiaInyectadaConEstado();
    
    // 3. Actualizar porcentaje (corregido)
    setTimeout(() => {
        actualizarPorcentajeProduccionConEstado();
    }, 500);
    
    console.log('✅ Sistema de energía actualizado completamente');
}

/**
 * Actualiza la generación actual con manejo de estados
 */
function actualizarGeneracionActualConEstado() {
    return fetch('/generacion_actual?t=' + Date.now())
        .then(response => response.json())
        .then(data => {
            // CORREGIDO: IDs que coinciden con el HTML
            const elemento = document.getElementById('energia-generacion-valor');
            const estadoElemento = document.getElementById('energia-generacion-estado');
            const fechaElemento = document.getElementById('energia-generacion-fecha');
            
            if (elemento) {
                elemento.textContent = `${data.kw_actual || 0}`;
            }
            
            if (fechaElemento) {
                fechaElemento.textContent = `Última actualización: ${data.fecha_ultima_lectura || '--'}`;
            }
            
            if (estadoElemento) {
                const estado = data.estado || 'desconocido';
                const mensaje = data.mensaje || 'Sin información';
                
                // Mostrar estado con colores
                if (estado === 'conectado') {
                    estadoElemento.innerHTML = '<span class="badge bg-success">🟢 DATOS REALES DESDE GRAFANA - conectado</span>';
                    estadoElemento.title = mensaje;
                } else if (estado.includes('simulado')) {
                    estadoElemento.innerHTML = '<span class="badge bg-warning">🟡 BASE DE DATOS CAÍDA - Sistema usando datos simulados</span>';
                    estadoElemento.title = mensaje;
                } else {
                    estadoElemento.innerHTML = '<span class="badge bg-danger">🔴 ERROR DE CONEXIÓN - Datos simulados de emergencia</span>';
                    estadoElemento.title = mensaje;
                }
            }
            
            // Actualizar el consumo de planta automáticamente
            actualizarConsumoPlanta();
            
            console.log('🔥 Generación actualizada:', data.kw_actual, 'kW -', data.estado);
            return data;
        })
        .catch(error => {
            console.error('❌ Error actualizando generación:', error);
            const estadoElemento = document.getElementById('energia-generacion-estado');
            if (estadoElemento) {
                estadoElemento.innerHTML = '<span class="badge bg-danger">🔴 ERROR DE CONEXIÓN - Datos simulados de emergencia</span>';
                estadoElemento.title = `Error: ${error.message}`;
            }
            throw error;
        });
}

/**
 * Actualiza la energía inyectada con manejo de estados - CORREGIDO
 */
function actualizarEnergiaInyectadaConEstado() {
    return fetch('/energia_inyectada_red?t=' + Date.now())
        .then(response => response.json())
        .then(data => {
            // IDs CORRECTOS del HTML
            const elemento = document.getElementById('energia-inyectada-valor');
            const estadoElemento = document.getElementById('energia-inyectada-estado');
            const fechaElemento = document.getElementById('energia-inyectada-fecha');
            
            if (elemento) {
                elemento.textContent = `${data.kw_inyectado_red.toFixed(1)}`;
                console.log('✅ Energía inyectada actualizada:', data.kw_inyectado_red, 'kW');
            }
            
            if (fechaElemento) {
                fechaElemento.textContent = `Última actualización: ${data.fecha_ultima_lectura || '--'}`;
            }
            
            if (estadoElemento) {
                const estado = data.estado || 'desconocido';
                const mensaje = data.mensaje || 'Sin información';
                
                // Mostrar estado con colores
                if (estado === 'conectado') {
                    estadoElemento.innerHTML = '<span class="badge bg-success">🟢 DATOS REALES kwPta</span>';
                    estadoElemento.title = mensaje;
                } else if (estado.includes('simulado')) {
                    estadoElemento.innerHTML = '<span class="badge bg-warning">🟡 DATOS SIMULADOS</span>';
                    estadoElemento.title = mensaje;
                } else {
                    estadoElemento.innerHTML = '<span class="badge bg-danger">🔴 ERROR CONEXIÓN</span>';
                    estadoElemento.title = mensaje;
                }
            }
            
            // CALCULAR CONSUMO AUTOMÁTICAMENTE
            actualizarConsumoPlanta();
            
            console.log('⚡ Energía inyectada actualizada:', data.kw_inyectado_red, 'kW -', data.estado);
            return data;
        })
        .catch(error => {
            console.error('❌ Error actualizando energía inyectada:', error);
            const elemento = document.getElementById('energia-inyectada-valor');
            const estadoElemento = document.getElementById('energia-inyectada-estado');
            
            if (elemento) elemento.textContent = '0.0';
            if (estadoElemento) {
                estadoElemento.innerHTML = '<span class="badge bg-danger">🔴 ERROR</span>';
            }
            throw error;
        });
}

/**
 * Actualiza el porcentaje de producción con manejo de estados
 */
function actualizarPorcentajeProduccionConEstado() {
    return fetch('/porcentaje_produccion?t=' + Date.now())
        .then(response => response.json())
        .then(data => {
            const elementoPorcentaje = document.getElementById('energia-porcentaje-valor');
            const elementoBarra = document.getElementById('energia-porcentaje-barra');
            const elementoColor = document.getElementById('energia-porcentaje-color');
            const estadoGeneral = document.getElementById('energia-estado-general');
            
            if (elementoPorcentaje) {
                elementoPorcentaje.textContent = data.porcentaje_cumplido.toFixed(2);
            }
            
            if (elementoBarra) {
                const porcentaje = Math.min(data.porcentaje_cumplido, 100);
                elementoBarra.style.width = porcentaje + '%';
                elementoBarra.setAttribute('aria-valuenow', porcentaje);
            }
            
            // Cambiar color según el porcentaje
            if (elementoColor && elementoBarra) {
                let colorClass = 'text-danger';
                let barraClass = 'bg-danger';
                
                if (data.porcentaje_cumplido >= 90) {
                    colorClass = 'text-success';
                    barraClass = 'bg-success';
                } else if (data.porcentaje_cumplido >= 70) {
                    colorClass = 'text-warning';
                    barraClass = 'bg-warning';
                }
                
                elementoColor.className = colorClass + ' mb-2';
                elementoBarra.className = 'progress-bar ' + barraClass;
            }
            
            if (estadoGeneral) {
                const estado = data.estado || 'normal';
                if (estado === 'alto') {
                    estadoGeneral.innerHTML = '<span class="badge bg-success">🟢 ALTO RENDIMIENTO</span>';
                } else if (estado === 'normal') {
                    estadoGeneral.innerHTML = '<span class="badge bg-warning">🟡 RENDIMIENTO NORMAL</span>';
                } else {
                    estadoGeneral.innerHTML = '<span class="badge bg-danger">🔴 BAJO RENDIMIENTO</span>';
                }
            }
            
            console.log('📊 Porcentaje actualizado:', safeToFixed(data.porcentaje_cumplido) + '%');
            return data;
        })
        .catch(error => {
            console.error('❌ Error actualizando porcentaje:', error);
            throw error;
        });
}

/**
 * Actualiza el consumo de planta calculando Generación - Inyectada
 */
function actualizarConsumoPlanta() {
    const elementoGeneracion = document.getElementById('energia-generacion-valor');
    const elementoInyectada = document.getElementById('energia-inyectada-valor');
    const elementoConsumo = document.getElementById('energia-consumo-valor');
    const estadoConsumo = document.getElementById('energia-consumo-estado');
    
    if (elementoGeneracion && elementoInyectada && elementoConsumo) {
        const generacion = parseFloat(elementoGeneracion.textContent) || 0;
        const inyectada = parseFloat(elementoInyectada.textContent) || 0;
        const consumo = generacion - inyectada;
        
        elementoConsumo.textContent = consumo.toFixed(1);
        
        if (estadoConsumo) {
            if (consumo > 0) {
                estadoConsumo.innerHTML = '<span class="badge bg-success">✅ CALCULADO</span>';
            } else {
                estadoConsumo.innerHTML = '<span class="badge bg-warning">⚠️ VERIFICAR</span>';
            }
        }
        
        console.log(`🏭 Consumo planta: ${generacion} - ${inyectada} = ${consumo.toFixed(1)} kW`);
    }
}

/**
 * Funciones individuales para actualizar cada componente
 */
function actualizarGeneracionActual() {
    actualizarGeneracionActualConEstado();
}

function actualizarEnergiaInyectada() {
    actualizarEnergiaInyectadaConEstado().then(() => {
        // Actualizar el consumo después de actualizar la inyección
        actualizarConsumoPlanta();
    });
}

function actualizarPorcentajeProduccion() {
    actualizarPorcentajeProduccionConEstado();
}

/**
 * Actualiza los KPIs del dashboard
 */
function actualizarKPIs() {
    console.log("Actualizando KPIs...");
    
    fetch('/datos_kpi')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos KPI recibidos:", data);
            
            if (data.error) {
                console.error("Error en datos KPI:", data.error);
                return;
            }
            
            // Actualizar elementos KPI en la interfaz
            const kpiContainer = document.getElementById('kpi-container');
            if (kpiContainer) {
                // Actualizar valores de KPI usando los campos correctos del backend
                const elementos = {
                    'kw-generados-planificados': data.kwGen || 0,
                    'kw-generados-real': data.kwGen || 0,
                    'diferencia-vs-planificado': 0, // Calcular si es necesario
                    'kw-inyectados-real': data.kwDesp || 0,
                    'kw-consumidos-planta': data.kwPta || 0
                };
                
                Object.entries(elementos).forEach(([id, valor]) => {
                    const elemento = document.getElementById(id);
                    if (elemento) {
                        if (typeof valor === 'number') {
                            elemento.textContent = valor.toFixed(2) + ' kW';
                        } else {
                            elemento.textContent = valor;
                        }
                    }
                });
                
                // Actualizar datos de generación actual
                if (data.generacion_actual) {
                    const genActual = document.getElementById('generacion-actual-kw');
                    if (genActual) {
                        genActual.textContent = (data.generacion_actual.kw_actual || 0).toFixed(2) + ' kW';
                    }
                }
                
                // Actualizar porcentaje de producción
                if (data.porcentaje_produccion) {
                    const porcProd = document.getElementById('porcentaje-produccion');
                    if (porcProd) {
                        porcProd.textContent = (data.porcentaje_produccion.porcentaje_cumplido || 0).toFixed(1) + '%';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error actualizando KPIs:', error);
        });
}

/**
 * Actualiza los registros de 15 minutos
 */
function actualizarRegistros15min() {
    console.log("Actualizando registros de 15 minutos...");
    
    fetch('/registros_15min')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos registros 15min recibidos:", data);
            
            if (data.status !== 'success') {
                console.error("Error en registros 15min:", data.message);
                return;
            }
            
            // Actualizar resumen de registros
            const resumenContainer = document.getElementById('resumen-15min');
            if (resumenContainer && data.resumen) {
                const resumen = data.resumen;
                resumenContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-3">
                            <strong>Total KW Generado:</strong><br>
                            ${(resumen.total_kw_generado || 0).toFixed(2)} kW
                        </div>
                        <div class="col-md-3">
                            <strong>Total KW Inyectado:</strong><br>
                            ${(resumen.total_kw_inyectado || 0).toFixed(2)} kW
                        </div>
                        <div class="col-md-3">
                            <strong>Consumo Planta:</strong><br>
                            ${(resumen.total_consumo_planta || 0).toFixed(2)} kW
                        </div>
                        <div class="col-md-3">
                            <strong>Total Registros:</strong><br>
                            ${resumen.total_registros || 0} / 96
                        </div>
                    </div>
                `;
            }
            
            // Actualizar tabla de registros
            const tablaRegistros = document.getElementById('tabla-registros-15min');
            if (tablaRegistros && data.registros) {
                const tbody = tablaRegistros.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = '';
                    
                    // Mostrar últimos 10 registros
                    const ultimosRegistros = data.registros.slice(-10);
                    ultimosRegistros.forEach(registro => {
                        const fila = document.createElement('tr');
                        fila.innerHTML = `
                            <td>${registro.timestamp || '-'}</td>
                            <td>${(registro.kw_generado || 0).toFixed(2)}</td>
                            <td>${(registro.kw_spot || 0).toFixed(2)}</td>
                            <td>${(registro.consumo_planta || 0).toFixed(2)}</td>
                        `;
                        tbody.appendChild(fila);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error actualizando registros 15min:', error);
        });
}

/**
 * Actualiza el histórico semanal
 */
function actualizarHistoricoSemanal() {
    console.log("Actualizando histórico semanal...");
    
    fetch('/historico_semanal')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos histórico semanal recibidos:", data);
            
            if (data.error) {
                console.error("Error en histórico semanal:", data.error);
                return;
            }
            
            // Actualizar estadísticas semanales
            const estadisticasContainer = document.getElementById('estadisticas-semanales');
            if (estadisticasContainer) {
                estadisticasContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-3">
                            <strong>Total Registros:</strong><br>
                            ${data.total_registros || 0}
                        </div>
                        <div class="col-md-3">
                            <strong>Promedio KW:</strong><br>
                            ${(data.promedio_kw || 0).toFixed(2)} kW
                        </div>
                        <div class="col-md-3">
                            <strong>Eficiencia Promedio:</strong><br>
                            ${(data.promedio_eficiencia || 0).toFixed(1)}%
                        </div>
                        <div class="col-md-3">
                            <strong>Mejor Día:</strong><br>
                            ${(data.mejor_dia || 0).toFixed(2)} kW
                        </div>
                    </div>
                `;
            }
            
            // Actualizar tabla semanal
            const tablaSemanal = document.getElementById('tabla-historico-semanal');
            if (tablaSemanal && data.registros) {
                const tbody = tablaSemanal.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = '';
                    
                    data.registros.forEach(registro => {
                        const fila = document.createElement('tr');
                        fila.innerHTML = `
                            <td>${registro.semana || '-'}</td>
                            <td>${(registro.kw_generados || 0).toFixed(2)}</td>
                            <td>${(registro.kw_promedio_diario || 0).toFixed(2)}</td>
                            <td>${(registro.eficiencia_porcentaje || 0).toFixed(1)}%</td>
                            <td>${registro.dias_registrados || 0}</td>
                        `;
                        tbody.appendChild(fila);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error actualizando histórico semanal:', error);
        });
}

// Modificar la función de actualización principal para incluir las nuevas funciones
function actualizarTablasCompleto() {
    console.log("Ejecutando actualización completa...");
    
    // Actualizar funciones existentes
    actualizarTablas();
    
    // Actualizar nuevas funciones
    actualizarKPIs();
    actualizarRegistros15min();
    actualizarHistoricoSemanal();
    actualizarSeguimientoHorarioCompleto();
    actualizarSistemaEnergiaCompleto();
}

// Modificar el evento DOMContentLoaded para usar la función completa
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando todas las actualizaciones automáticas...');
    
    // Inicializar gráfico de stock
    inicializarGraficoStock();
    
    // Cargar datos iniciales completos
    actualizarStockEnInterfaz();
    actualizarTablasCompleto();
    
    // Configurar actualizaciones periódicas con la función completa
    if (intervaloActualizacion) {
        clearInterval(intervaloActualizacion);
    }
    intervaloActualizacion = setInterval(actualizarTablasCompleto, INTERVALO_MS);
    
    // Configurar evento para borrar stock
    const btnConfirmarBorrarStock = document.getElementById('btnConfirmarBorrarStock');
    if (btnConfirmarBorrarStock) {
        btnConfirmarBorrarStock.addEventListener('click', function() {
            borrarStock();
        });
    }
    
    console.log('✅ Todas las actualizaciones automáticas iniciadas');
}); 