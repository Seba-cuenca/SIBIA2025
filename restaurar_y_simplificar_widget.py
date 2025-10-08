#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RESTAURAR BACKUP Y CREAR WIDGET SIMPLE
======================================
"""

from pathlib import Path
import shutil

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'
DASHBOARD_PATH = TEMPLATES_DIR / 'dashboard_hibrido.html'
BACKUP_PATH = TEMPLATES_DIR / 'dashboard_hibrido.html.backup'

# Widget HTML simple (sin JavaScript complejo)
WIDGET_HTML_SIMPLE = '''
                    <!-- Predicción de Fallos ML (Simple - Sin JS complejo) -->
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
'''

# JavaScript simple y funcional
JS_SIMPLE = '''
// ============================================
// PREDICCIÓN DE FALLOS - VERSIÓN SIMPLE
// ============================================

function testPrediccionManual() {
    const resultadoDiv = document.getElementById('resultado-prediccion-test');
    resultadoDiv.innerHTML = '<div style="color: #00d4ff;"><i class="fas fa-spinner fa-spin"></i> Prediciendo...</div>';
    
    // Datos de prueba
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

console.log('✅ Widget de Predicción (simple) cargado');
'''

def restaurar_y_simplificar():
    """Restaura backup y agrega widget simple"""
    print("=" * 60)
    print("🔄 RESTAURANDO BACKUP Y SIMPLIFICANDO WIDGET")
    print("=" * 60)
    
    # 1. Verificar que existe el backup
    if not BACKUP_PATH.exists():
        print("❌ No existe el backup")
        return False
    
    print("\n1️⃣ Restaurando backup...")
    shutil.copy(BACKUP_PATH, DASHBOARD_PATH)
    print("   ✅ Backup restaurado")
    
    # 2. Leer contenido
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # 3. Insertar widget simple
    print("\n2️⃣ Insertando widget simple...")
    marcador = "                </div>\n\n                <!-- Tabla de Rendimiento por Materiales -->"
    
    if marcador in contenido:
        contenido_nuevo = contenido.replace(
            marcador,
            f"                </div>\n{WIDGET_HTML_SIMPLE}\n                </div>\n\n                <!-- Tabla de Rendimiento por Materiales -->"
        )
        print("   ✅ Widget insertado")
    else:
        print("   ⚠️  Marcador no encontrado")
        return False
    
    # 4. Agregar JavaScript simple
    print("\n3️⃣ Agregando JavaScript simple...")
    if "</script>" in contenido_nuevo:
        partes = contenido_nuevo.rsplit("</script>", 1)
        contenido_nuevo = f"{partes[0]}\n\n{JS_SIMPLE}\n\n</script>{partes[1]}"
        print("   ✅ JavaScript agregado")
    
    # 5. Guardar
    print("\n4️⃣ Guardando...")
    with open(DASHBOARD_PATH, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    print("   ✅ Archivo guardado")
    
    print("\n" + "=" * 60)
    print("✅ WIDGET SIMPLE INTEGRADO")
    print("=" * 60)
    print("\n📝 Siguiente paso:")
    print("   1. Recarga el navegador: Ctrl + F5")
    print("   2. Deberías ver el widget sin errores")
    print("   3. Haz clic en 'Probar Predicción'")
    
    return True

if __name__ == '__main__':
    exito = restaurar_y_simplificar()
    raise SystemExit(0 if exito else 1)
