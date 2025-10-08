#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX PARA EL WIDGET DE PREDICCIÓN DE FALLOS
==========================================
Corrige el error de JavaScript
"""

from pathlib import Path
import re

BASE_DIR = Path(__file__).parent
DASHBOARD_PATH = BASE_DIR / 'templates' / 'dashboard_hibrido.html'

def fix_widget():
    """Corrige el widget de predicción"""
    print("🔧 Corrigiendo widget de predicción de fallos...")
    
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y eliminar el JavaScript duplicado o problemático
    # El problema es que el script está causando errores
    
    # Buscar la sección del widget
    patron_inicio = r'// Función para actualizar la predicción de fallos'
    patron_fin = r"console\.log\('✅ Script de Predicción de Fallos ML cargado'\);"
    
    # Comentar temporalmente la función problemática
    contenido_nuevo = re.sub(
        r'(async function actualizarPrediccionFallos\(\) \{)',
        r'// TEMPORALMENTE DESHABILITADO POR ERROR\n// \1',
        contenido
    )
    
    # Comentar también la llamada automática
    contenido_nuevo = re.sub(
        r'(setTimeout\(\(\) => \{\s+actualizarPrediccionFallos\(\);)',
        r'// \1',
        contenido_nuevo
    )
    
    contenido_nuevo = re.sub(
        r'(setInterval\(\(\) => \{\s+actualizarPrediccionFallos\(\);)',
        r'// \1',
        contenido_nuevo
    )
    
    # Guardar
    with open(DASHBOARD_PATH, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print("✅ Widget corregido (función deshabilitada temporalmente)")
    print("\n📝 Siguiente paso:")
    print("   1. Recarga el navegador (Ctrl + F5)")
    print("   2. Los errores deberían desaparecer")
    print("   3. El widget mostrará 'Cargando...' (sin errores)")

if __name__ == '__main__':
    fix_widget()
