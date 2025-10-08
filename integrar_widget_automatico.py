#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE INTEGRACIÓN AUTOMÁTICA DEL WIDGET DE PREDICCIÓN DE FALLOS
===================================================================
Ejecutar con: python integrar_widget_automatico.py
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DASHBOARD_PATH = BASE_DIR / 'templates' / 'dashboard_hibrido.html'
BACKUP_PATH = BASE_DIR / 'templates' / 'dashboard_hibrido.html.backup'

# HTML del widget
WIDGET_HTML = '''
                    <!-- Predicción de Fallos ML (Random Forest con Datos Reales) -->
                    <div class="function-card">
                        <div class="card-header">
                            <div class="card-title">
                                <i class="fas fa-shield-alt"></i>
                                Predicción de Fallos ML
                            </div>
                            <button class="btn btn-sm" onclick="actualizarPrediccionFallos()" style="background: rgba(0,212,255,0.2); border: 1px solid #00d4ff; padding: 5px 10px; font-size: 11px;">
                                <i class="fas fa-sync-alt"></i> Actualizar
                            </button>
                        </div>
                        <div class="card-content" id="prediccion-fallos-container">
                            <div class="alert-item alert-info">
                                <i class="fas fa-spinner fa-spin"></i> Cargando modelo de predicción...
                            </div>
                        </div>
                    </div>
'''

# JavaScript del widget
JS_SCRIPT_PATH = BASE_DIR / 'templates' / 'script_prediccion_fallos.js'

def integrar_widget():
    """Integra el widget automáticamente"""
    print("🚀 INICIANDO INTEGRACIÓN DEL WIDGET DE PREDICCIÓN DE FALLOS")
    print("=" * 60)
    
    # 1. Backup del archivo original
    print("\n1️⃣ Creando backup del archivo original...")
    try:
        with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
            contenido_original = f.read()
        
        with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
            f.write(contenido_original)
        
        print(f"   ✅ Backup creado: {BACKUP_PATH}")
    except Exception as e:
        print(f"   ❌ Error creando backup: {e}")
        return False
    
    # 2. Buscar el punto de inserción para el widget HTML
    print("\n2️⃣ Buscando punto de inserción para el widget...")
    
    # Buscar después del cierre de "Predicciones IA"
    marcador_insercion = "                </div>\n\n                <!-- Tabla de Rendimiento por Materiales -->"
    
    if marcador_insercion in contenido_original:
        print("   ✅ Punto de inserción encontrado")
        
        # Insertar el widget
        contenido_nuevo = contenido_original.replace(
            marcador_insercion,
            f"                </div>\n{WIDGET_HTML}\n                </div>\n\n                <!-- Tabla de Rendimiento por Materiales -->"
        )
        
    else:
        print("   ⚠️  Marcador exacto no encontrado, buscando alternativa...")
        
        # Buscar marcador alternativo
        marcador_alt = "<!-- Tabla de Rendimiento por Materiales -->"
        if marcador_alt in contenido_original:
            print("   ✅ Marcador alternativo encontrado")
            contenido_nuevo = contenido_original.replace(
                marcador_alt,
                f"{WIDGET_HTML}                </div>\n\n                {marcador_alt}"
            )
        else:
            print("   ❌ No se encontró punto de inserción")
            return False
    
    # 3. Agregar JavaScript
    print("\n3️⃣ Agregando JavaScript...")
    
    try:
        with open(JS_SCRIPT_PATH, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Buscar el cierre del script principal
        marcador_js = "console.log('✅ Script de Predicción de Fallos ML cargado');"
        
        if marcador_js not in js_content:
            # El JS ya tiene el marcador al final
            pass
        
        # Insertar antes del </script> final
        if "</script>" in contenido_nuevo:
            # Encontrar el último </script>
            partes = contenido_nuevo.rsplit("</script>", 1)
            contenido_nuevo = f"{partes[0]}\n\n{js_content}\n\n</script>{partes[1]}"
            print("   ✅ JavaScript agregado")
        else:
            print("   ⚠️  No se encontró cierre de script")
    
    except Exception as e:
        print(f"   ⚠️  Error agregando JavaScript: {e}")
    
    # 4. Guardar archivo modificado
    print("\n4️⃣ Guardando archivo modificado...")
    try:
        with open(DASHBOARD_PATH, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print(f"   ✅ Archivo guardado: {DASHBOARD_PATH}")
    except Exception as e:
        print(f"   ❌ Error guardando archivo: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ INTEGRACIÓN COMPLETADA")
    print("=" * 60)
    print("\n📝 Siguiente paso:")
    print("   1. Recargar el navegador (Ctrl + F5)")
    print("   2. El widget debería aparecer en el dashboard")
    print("\n💾 Backup disponible en:")
    print(f"   {BACKUP_PATH}")
    
    return True

def main():
    """Función principal"""
    if not DASHBOARD_PATH.exists():
        print(f"❌ Error: No se encuentra el archivo {DASHBOARD_PATH}")
        return 1
    
    if not JS_SCRIPT_PATH.exists():
        print(f"❌ Error: No se encuentra el archivo {JS_SCRIPT_PATH}")
        return 1
    
    exito = integrar_widget()
    return 0 if exito else 1

if __name__ == '__main__':
    raise SystemExit(main())
