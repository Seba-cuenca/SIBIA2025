#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREGIR UBICACIÓN DEL WIDGET
============================
El widget está fuera del contenedor, por eso no aparece
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent
DASHBOARD_PATH = BASE_DIR / 'templates' / 'dashboard_hibrido.html'

def corregir_ubicacion():
    """Mueve el widget dentro del contenedor correcto"""
    print("🔧 Corrigiendo ubicación del widget...")
    
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # El widget actual está mal ubicado (fuera del contenedor)
    # Necesitamos moverlo ANTES del cierre </div> de la línea 3067
    
    # Buscar y eliminar el widget mal ubicado
    widget_mal_ubicado = '''
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

                </div>'''
    
    # Eliminar widget mal ubicado
    contenido_limpio = contenido.replace(widget_mal_ubicado, '\n                </div>')
    
    # Widget bien formateado DENTRO del contenedor
    widget_bien_ubicado = '''
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
                </div>'''
    
    # Buscar el cierre de Predicciones IA y agregar el widget ANTES del cierre
    marcador_predicciones = '''                    </div>
                </div>

                <!-- Tabla de Rendimiento por Materiales -->'''
    
    if marcador_predicciones in contenido_limpio:
        contenido_nuevo = contenido_limpio.replace(
            marcador_predicciones,
            f'''{widget_bien_ubicado}

                <!-- Tabla de Rendimiento por Materiales -->'''
        )
        print("   ✅ Widget reubicado correctamente")
    else:
        print("   ❌ No se encontró el marcador")
        return False
    
    # Guardar
    with open(DASHBOARD_PATH, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print("   ✅ Archivo guardado")
    print("\n📝 Ahora:")
    print("   1. Recarga el navegador: Ctrl + Shift + R")
    print("   2. El widget debería aparecer en la sección 'Predicciones IA'")
    
    return True

if __name__ == '__main__':
    exito = corregir_ubicacion()
    raise SystemExit(0 if exito else 1)
