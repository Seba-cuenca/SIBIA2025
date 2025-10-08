#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir frontend: stock con nombres y asistente con voz
"""
import os
import re
from datetime import datetime

ROOT = r"c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS"

def backup_file(filepath):
    """Crea backup con timestamp"""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{filepath}.bak_{ts}"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup}")
    return content

def patch_actualizacion_js():
    """Corrige static/js/actualizacion.js para mostrar nombres"""
    filepath = os.path.join(ROOT, 'static/js/actualizacion.js')
    print(f"\n📝 Parcheando {filepath}...")
    
    content = backup_file(filepath)
    
    # 1. Reemplazar celda de tabla para usar nombre
    content = content.replace(
        '<td>${item.material}</td>',
        '<td>${item.nombre || item.material}</td>'
    )
    print("  ✓ Tabla usa item.nombre || item.material")
    
    # 2. Agregar nombre cuando convierte objeto a array
    content = re.sub(
        r'(\s+material: material,)\s+(\s+cantidad:)',
        r'\1\n                    nombre: (detalles && detalles.nombre) || material,\2',
        content
    )
    print("  ✓ Mapeo de objeto incluye nombre")
    
    # 3. Normalizar nombre cuando ya es array
    content = content.replace(
        'stockArray = stockData; // Ya es un array',
        'stockArray = stockData.map(it => ({ ...it, nombre: it.nombre || it.material })); // Ya es un array'
    )
    print("  ✓ Arrays normalizan nombre")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {filepath} parcheado correctamente\n")

def patch_asistente_voz_js():
    """Corrige static/js/asistente_voz.js para usar TTS del servidor"""
    filepath = os.path.join(ROOT, 'static/js/asistente_voz.js')
    print(f"📝 Parcheando {filepath}...")
    
    content = backup_file(filepath)
    
    # 1. Cambiar endpoint
    content = content.replace("'/ask_assistant'", "'/asistente_ia_v2'")
    content = content.replace('"/ask_assistant"', '"/asistente_ia_v2"')
    print("  ✓ Endpoint cambiado a /asistente_ia_v2")
    
    # 2. Agregar sintetizar: true en JSON bodies
    content = re.sub(
        r'JSON\.stringify\(\s*\{\s*pregunta\s*:\s*pregunta\s*\}\s*\)',
        'JSON.stringify({ pregunta: pregunta, sintetizar: true })',
        content
    )
    content = re.sub(
        r'JSON\.stringify\(\s*\{\s*pregunta\s*\}\s*\)',
        'JSON.stringify({ pregunta, sintetizar: true })',
        content
    )
    print("  ✓ Body incluye sintetizar: true")
    
    # 3. Agregar reproducción de audio_base64 si no existe
    if 'audio_base64' not in content:
        content = content.replace(
            "agregarMensajeChat(respuestaTexto, 'asistente');",
            """agregarMensajeChat(respuestaTexto, 'asistente');
        // Reproducir audio del backend si viene
        if (data && data.audio_base64) {
            try {
                const audio = new Audio('data:audio/mp3;base64,' + data.audio_base64);
                activarOrbeHablando();
                audio.onended = () => desactivarOrbeHablando();
                audio.play().catch(err => { console.warn('Audio blocked:', err); desactivarOrbeHablando(); });
            } catch(e) { console.warn('Error reproduciendo audio:', e); }
        }"""
        )
        print("  ✓ Reproducción de audio_base64 agregada")
    
    # 4. Agregar saludo inicial si no existe
    if 'Hola, soy SIBIA' not in content and 'inicializado correctamente' in content:
        content = content.replace(
            'console.log("Asistente de IA inicializado correctamente.");',
            '''console.log("Asistente de IA inicializado correctamente.");
    // Saludo inicial con TTS del servidor
    try {
        fetch('/asistente_ia_v2', { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ pregunta: 'Hola, soy SIBIA, tu asistente inteligente', sintetizar: true }) 
        })
        .then(r => r.json())
        .then(d => { 
            if (d && d.audio_base64) { 
                const a = new Audio('data:audio/mp3;base64,' + d.audio_base64); 
                activarOrbeHablando(); 
                a.onended = () => desactivarOrbeHablando(); 
                a.play().catch(() => desactivarOrbeHablando()); 
            } 
        })
        .catch(() => {});
    } catch(e) {}'''
        )
        print("  ✓ Saludo inicial con TTS agregado")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {filepath} parcheado correctamente\n")

def patch_dashboard_html():
    """Corrige templates/dashboard_hibrido.html para normalizar materiales"""
    filepath = os.path.join(ROOT, 'templates/dashboard_hibrido.html')
    print(f"📝 Parcheando {filepath}...")
    
    content = backup_file(filepath)
    
    # Insertar normalización de array->objeto después del check de success
    anchor = "if (data.status === 'success' && data.materiales) {"
    normalization = """
                    // Normalizar array->objeto para compatibilidad con render existente
                    if (Array.isArray(data.materiales)) {
                        const obj = {};
                        data.materiales.forEach(it => {
                            const nombre = (it && (it.nombre || it.material)) || '-';
                            obj[nombre] = {
                                total_tn: (it && (it.total_tn ?? it.cantidad_tn ?? it.cantidad)) || 0,
                                st_porcentaje: (it && it.st_porcentaje) || 0,
                                st_usado: (it && it.st_usado) || 0
                            };
                        });
                        data.materiales = obj;
                    }"""
    
    if anchor in content and 'Normalizar array->objeto' not in content:
        content = content.replace(anchor, anchor + normalization)
        print("  ✓ Normalización de array->objeto agregada")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {filepath} parcheado correctamente\n")

if __name__ == '__main__':
    print("="*60)
    print("🔧 PARCHEANDO FRONTEND PARA NOMBRES Y VOZ")
    print("="*60)
    
    try:
        patch_actualizacion_js()
        patch_asistente_voz_js()
        patch_dashboard_html()
        
        print("="*60)
        print("✅ TODOS LOS PARCHES APLICADOS EXITOSAMENTE")
        print("="*60)
        print("\n📋 Próximos pasos:")
        print("1. Reiniciar Flask")
        print("2. Hard refresh del navegador (Ctrl+F5)")
        print("3. Verificar:")
        print("   - Stock Actual muestra nombres")
        print("   - Asistente saluda con voz")
        print("   - Asistente responde con voz")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
