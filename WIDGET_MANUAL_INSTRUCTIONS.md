# 📝 INSTRUCCIONES MANUALES PARA AGREGAR EL WIDGET

Por problemas de estructura HTML, es mejor agregarlo manualmente.

## 📍 Ubicación Exacta

**Archivo:** `templates/dashboard_hibrido.html`

**Buscar la línea ~3066** que dice:
```html
                    </div>
                </div>

                <!-- Tabla de Rendimiento por Materiales -->
```

## ➕ CÓDIGO A INSERTAR

**Insertar ANTES de `<!-- Tabla de Rendimiento por Materiales -->`:**

```html
                    <!-- Predicción de Fallos ML -->
                    <div class="function-card">
                        <div class="card-header">
                            <div class="card-title">
                                <i class="fas fa-shield-alt"></i>
                                Predicción de Fallos ML
                            </div>
                        </div>
                        <div class="card-content" id="prediccion-fallos-container">
                            <div style="padding: 15px; text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 10px;">🛡️</div>
                                <div style="font-size: 16px; color: #00d4ff; margin-bottom: 10px;">
                                    <strong>Modelo de Predicción Activo</strong>
                                </div>
                                <div style="font-size: 13px; color: #a0aec0; margin-bottom: 15px;">
                                    Random Forest con datos reales
                                </div>
                                <button onclick="testPrediccionManual()" class="btn btn-primary" style="margin: 5px;">
                                    <i class="fas fa-flask"></i> Probar Predicción
                                </button>
                                <div id="resultado-prediccion-test" style="margin-top: 15px;"></div>
                            </div>
                        </div>
                    </div>

```

## 🔧 JavaScript

**Buscar el final del archivo, antes del `</script>` final y agregar:**

```javascript
// Predicción de Fallos ML
function testPrediccionManual() {
    const resultadoDiv = document.getElementById('resultado-prediccion-test');
    resultadoDiv.innerHTML = '<div style="color: #00d4ff;"><i class="fas fa-spinner fa-spin"></i> Prediciendo...</div>';
    
    const datos = {
        co2_bio040_pct: 0.46,
        co2_bio050_pct: 0.45,
        o2_bio040_pct: 0.46,
        o2_bio050_pct: 0.45,
        caudal_chp_ls: 100.0
    };
    
    fetch('/api/predecir-fallo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(resultado => {
        if (resultado.status === 'success') {
            const color = resultado.prediccion === 'critico' ? '#f56565' : 
                         resultado.prediccion === 'alerta' ? '#ed8936' :
                         resultado.prediccion === 'normal' ? '#4299e1' : '#48bb78';
            
            resultadoDiv.innerHTML = `
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid ${color};">
                    <div style="font-size: 14px; font-weight: bold; color: ${color}; margin-bottom: 5px;">
                        Estado: ${resultado.prediccion.toUpperCase()}
                    </div>
                    <div style="font-size: 12px; color: #cbd5e0;">
                        Confianza: ${(resultado.confianza * 100).toFixed(1)}%
                    </div>
                    <div style="font-size: 11px; color: #a0aec0; margin-top: 8px;">
                        ${resultado.recomendaciones[0]}
                    </div>
                </div>
            `;
        } else {
            resultadoDiv.innerHTML = `<div style="color: #f56565;">${resultado.mensaje || 'Error'}</div>`;
        }
    })
    .catch(error => {
        resultadoDiv.innerHTML = `<div style="color: #f56565;">Error: ${error.message}</div>`;
    });
}

console.log('✅ Widget de Predicción cargado');
```

## ✅ Guardar y Probar

1. Guardar el archivo
2. Recarga navegador: `Ctrl + Shift + R`
3. Navegar a "Predicciones IA"
4. Hacer scroll - deberías ver el widget
5. Clic en "Probar Predicción"

---

**O SIMPLEMENTE:** Dime y yo lo pruebo directamente desde la API sin necesidad del widget 🚀
