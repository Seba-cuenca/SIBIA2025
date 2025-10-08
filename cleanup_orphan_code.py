#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para eliminar código huérfano en app_CORREGIDO_OK_FINAL.py
"""
import os
from datetime import datetime

ROOT = r"c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS"
APP_FILE = os.path.join(ROOT, 'app_CORREGIDO_OK_FINAL.py')

def cleanup_orphan_code():
    """Elimina código huérfano dejado por las redirecciones"""
    print("="*60)
    print("🧹 LIMPIANDO CÓDIGO HUÉRFANO")
    print("="*60)
    
    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{APP_FILE}.bak_cleanup_{ts}"
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(backup, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Backup creado: {backup}")
    
    # Encontrar las líneas problemáticas
    # Buscar la primera definición de asistente_ia que solo redirige
    first_asistente_ia = None
    second_asistente_ia = None
    
    for i, line in enumerate(lines):
        if "@app.route('/asistente_ia'" in line and 'POST' in line:
            if first_asistente_ia is None:
                first_asistente_ia = i
            else:
                second_asistente_ia = i
                break
    
    if first_asistente_ia and second_asistente_ia:
        print(f"\n📍 Primera definición de /asistente_ia en línea: {first_asistente_ia + 1}")
        print(f"📍 Segunda definición de /asistente_ia en línea: {second_asistente_ia + 1}")
        
        # Encontrar el return asistente_ia_v2() de la primera definición
        return_line = None
        for i in range(first_asistente_ia, second_asistente_ia):
            if 'return asistente_ia_v2()' in lines[i]:
                return_line = i
                break
        
        if return_line:
            print(f"📍 Return encontrado en línea: {return_line + 1}")
            print(f"\n🗑️ Eliminando líneas {return_line + 2} hasta {second_asistente_ia}")
            
            # Eliminar todo desde después del return hasta antes del segundo @app.route
            new_lines = lines[:return_line + 1] + ['\n\n'] + lines[second_asistente_ia:]
            
            # Guardar
            with open(APP_FILE, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            deleted_lines = second_asistente_ia - (return_line + 1)
            print(f"✅ {deleted_lines} líneas de código huérfano eliminadas")
        else:
            print("⚠️ No se encontró el return asistente_ia_v2()")
    else:
        print("⚠️ No se encontraron definiciones duplicadas de /asistente_ia")
    
    # Ahora eliminar la segunda definición y dejar solo la redirección
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar la implementación completa de asistente_ia por una redirección
    pattern_start = '@app.route(\'/asistente_ia\', methods=[\'POST\'])\ndef asistente_ia_endpoint():\n    """Endpoint para el asistente IA del Dashboard Híbrido'
    
    if pattern_start in content:
        print("\n🔄 Reemplazando implementación de /asistente_ia por redirección")
        # Encontrar el final de esta función (siguiente @app.route)
        start_idx = content.find(pattern_start)
        next_route_idx = content.find('\n@app.route', start_idx + 1)
        
        if next_route_idx > start_idx:
            # Reemplazar toda la función por una redirección simple
            replacement = """@app.route('/asistente_ia', methods=['POST'])
def asistente_ia_endpoint():
    \"\"\"DEPRECADO: Redirige a /asistente_ia_v2 para usar el asistente unificado.\"\"\"
    logger.warning("⚠️ Endpoint DEPRECADO /asistente_ia llamado, redirigiendo a /asistente_ia_v2")
    return asistente_ia_v2()

"""
            content = content[:start_idx] + replacement + content[next_route_idx:]
            
            with open(APP_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ /asistente_ia ahora redirige a /asistente_ia_v2")
    
    print("\n" + "="*60)
    print("✅ LIMPIEZA COMPLETADA")
    print("="*60)
    print("\n📋 Próximos pasos:")
    print("1. Reiniciar Flask")
    print("2. Hacer Ctrl+Shift+R en el navegador")
    print("3. Probar el asistente")

if __name__ == '__main__':
    try:
        cleanup_orphan_code()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
