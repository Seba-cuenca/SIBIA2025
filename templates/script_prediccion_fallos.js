// ============================================
// SCRIPT DE PREDICCIÓN DE FALLOS ML
// Random Forest con Datos Reales
// ============================================

// INSTRUCCIONES: Agregar este código al final de dashboard_hibrido.html
// dentro de la sección <script> existente, antes del </script> final

// Función para actualizar la predicción de fallos
async function actualizarPrediccionFallos() {
    console.log('🔮 Actualizando predicción de fallos...');
    
    const container = document.getElementById('prediccion-fallos-container');
    if (!container) return;
    
    // Mostrar loading
    container.innerHTML = `
        <div class="alert-item alert-info">
            <i class="fas fa-spinner fa-spin"></i> Analizando datos con Random Forest...
        </div>
    `;
    
    try {
        // Obtener datos actuales del sistema
        const datosActuales = obtenerDatosSensoresActuales();
        
        // Llamar a la API de predicción
        const response = await fetch('/api/predecir-fallo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosActuales)
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const resultado = await response.json();
        
        if (resultado.status === 'success') {
            mostrarPrediccionFallos(resultado);
        } else if (resultado.status === 'unavailable') {
            container.innerHTML = `
                <div class="alert-item alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> 
                    Modelo no disponible. Ejecutar: python entrenar_modelo_prediccion_fallos_reales.py
                </div>
            `;
        } else {
            throw new Error(resultado.mensaje || 'Error desconocido');
        }
        
    } catch (error) {
        console.error('❌ Error en predicción de fallos:', error);
        container.innerHTML = `
            <div class="alert-item alert-danger">
                <i class="fas fa-times-circle"></i> Error al predecir: ${error.message}
            </div>
        `;
    }
}

// Función para obtener datos actuales de sensores
function obtenerDatosSensoresActuales() {
    // Intentar leer del DOM o usar valores simulados
    const datosHeader = {
        co2_bio040_pct: parseFloat(document.getElementById('co2-bio040')?.textContent) || 35.0,
        co2_bio050_pct: parseFloat(document.getElementById('co2-bio050')?.textContent) || 35.0,
        o2_bio040_pct: parseFloat(document.getElementById('o2-bio040')?.textContent) || 0.5,
        o2_bio050_pct: parseFloat(document.getElementById('o2-bio050')?.textContent) || 0.5,
        caudal_chp_ls: parseFloat(document.getElementById('caudal-chp')?.textContent) || 100.0
    };
    
    console.log('📊 Datos actuales:', datosHeader);
    return datosHeader;
}

// Función para mostrar la predicción
function mostrarPrediccionFallos(resultado) {
    const container = document.getElementById('prediccion-fallos-container');
    
    // Colores y emojis según predicción
    const estadoConfig = {
        'optimo': {
            color: '#48bb78',
            bgColor: 'rgba(72, 187, 120, 0.1)',
            borderColor: '#48bb78',
            emoji: '✅',
            titulo: 'Sistema Óptimo'
        },
        'normal': {
            color: '#4299e1',
            bgColor: 'rgba(66, 153, 225, 0.1)',
            borderColor: '#4299e1',
            emoji: '✓',
            titulo: 'Funcionamiento Normal'
        },
        'alerta': {
            color: '#ed8936',
            bgColor: 'rgba(237, 137, 54, 0.1)',
            borderColor: '#ed8936',
            emoji: '⚠️',
            titulo: 'Alerta Detectada'
        },
        'critico': {
            color: '#f56565',
            bgColor: 'rgba(245, 101, 101, 0.1)',
            borderColor: '#f56565',
            emoji: '🔴',
            titulo: 'Estado Crítico'
        }
    };
    
    const config = estadoConfig[resultado.prediccion] || estadoConfig['normal'];
    const confianzaPercent = (resultado.confianza * 100).toFixed(1);
    
    // Construir HTML
    let html = `
        <div style="padding: 15px; background: ${config.bgColor}; border-left: 4px solid ${config.borderColor}; border-radius: 8px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">${config.emoji}</span>
                    <div>
                        <div style="font-size: 18px; font-weight: bold; color: ${config.color};">
                            ${config.titulo}
                        </div>
                        <div style="font-size: 12px; color: #a0aec0; margin-top: 2px;">
                            Modelo: ${resultado.modelo.tipo} | Confianza: ${confianzaPercent}%
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 24px; font-weight: bold; color: ${config.color};">
                        ${confianzaPercent}%
                    </div>
                    <div style="font-size: 11px; color: #a0aec0;">Confianza</div>
                </div>
            </div>
            
            <!-- Barra de progreso de confianza -->
            <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: ${config.color}; height: 100%; width: ${confianzaPercent}%; transition: width 0.5s;"></div>
            </div>
        </div>
        
        <!-- Probabilidades por estado -->
        <div style="margin-bottom: 15px;">
            <div style="font-size: 13px; font-weight: bold; color: #e2e8f0; margin-bottom: 8px;">
                <i class="fas fa-chart-bar"></i> Probabilidades por Estado
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
    `;
    
    // Agregar probabilidades
    for (const [estado, prob] of Object.entries(resultado.probabilidades)) {
        const probPercent = (prob * 100).toFixed(1);
        const estadoLabel = estado.charAt(0).toUpperCase() + estado.slice(1);
        const color = estadoConfig[estado]?.color || '#a0aec0';
        
        html += `
            <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 11px; color: #e2e8f0;">${estadoLabel}</span>
                    <span style="font-size: 12px; font-weight: bold; color: ${color};">${probPercent}%</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); height: 4px; border-radius: 2px; overflow: hidden;">
                    <div style="background: ${color}; height: 100%; width: ${probPercent}%;"></div>
                </div>
            </div>
        `;
    }
    
    html += `
            </div>
        </div>
        
        <!-- Recomendaciones -->
        <div style="margin-bottom: 15px;">
            <div style="font-size: 13px; font-weight: bold; color: #e2e8f0; margin-bottom: 8px;">
                <i class="fas fa-lightbulb"></i> Recomendaciones
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
    `;
    
    resultado.recomendaciones.forEach(rec => {
        html += `<div style="font-size: 12px; color: #cbd5e0; margin-bottom: 5px; padding-left: 5px;">${rec}</div>`;
    });
    
    html += `
            </div>
        </div>
        
        <!-- Features importantes -->
        <div>
            <div style="font-size: 13px; font-weight: bold; color: #e2e8f0; margin-bottom: 8px;">
                <i class="fas fa-microscope"></i> Factores Más Importantes
            </div>
            <div style="display: grid; gap: 6px;">
    `;
    
    resultado.features_importantes.forEach((feat, idx) => {
        const importanciaPercent = (feat.importancia * 100).toFixed(1);
        html += `
            <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <div style="font-size: 11px; color: #e2e8f0;">${idx + 1}. ${feat.nombre.replace(/_/g, ' ')}</div>
                        <div style="font-size: 10px; color: #a0aec0; margin-top: 2px;">Valor: ${feat.valor.toFixed(2)}</div>
                    </div>
                    <div style="font-size: 11px; font-weight: bold; color: #00d4ff;">${importanciaPercent}%</div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
        
        <!-- Footer con timestamp -->
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 10px; color: #718096; text-align: center;">
                <i class="fas fa-clock"></i> Última actualización: ${new Date(resultado.timestamp).toLocaleString('es-ES')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Reproducir alerta de voz si es crítico
    if (resultado.prediccion === 'critico') {
        console.log('🔊 Alerta crítica detectada');
        // Aquí podrías integrar con el sistema de voz si está disponible
    }
}

// Cargar predicción automáticamente al inicio
document.addEventListener('DOMContentLoaded', function() {
    // Esperar 2 segundos antes de cargar la primera predicción
    setTimeout(() => {
        actualizarPrediccionFallos();
    }, 2000);
    
    // Actualizar cada 5 minutos
    setInterval(() => {
        actualizarPrediccionFallos();
    }, 5 * 60 * 1000);
});

console.log('✅ Script de Predicción de Fallos ML cargado');
