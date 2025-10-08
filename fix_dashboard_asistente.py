#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir el endpoint del asistente en dashboard_hibrido.html
"""
import os
from datetime import datetime

ROOT = r"c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS"
DASHBOARD = os.path.join(ROOT, 'templates/dashboard_hibrido.html')

def fix_dashboard():
    """Corrige el endpoint del asistente en el dashboard"""
    print("="*60)
    print("🔧 CORRIGIENDO ENDPOINT DEL ASISTENTE EN DASHBOARD")
    print("="*60)
    
    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{DASHBOARD}.bak_endpoint_{ts}"
    with open(DASHBOARD, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup}")
    
    # Reemplazar endpoint viejo por nuevo
    old_fetch = "const response = await fetch('/asistente_ia', {"
    new_fetch = "const response = await fetch('/asistente_ia_v2', {"
    
    if old_fetch in content:
        content = content.replace(old_fetch, new_fetch)
        print("✓ Endpoint cambiado: /asistente_ia → /asistente_ia_v2")
    else:
        print("⚠ No se encontró el patrón exacto del fetch")
    
    # Agregar sintetizar: true al body
    old_body = """body: JSON.stringify({
                        pregunta: pregunta
                    })"""
    new_body = """body: JSON.stringify({
                        pregunta: pregunta,
                        sintetizar: true
                    })"""
    
    if old_body in content:
        content = content.replace(old_body, new_body)
        print("✓ Parámetro 'sintetizar: true' agregado")
    else:
        print("⚠ No se encontró el body exacto")
    
    # Agregar reproducción de audio después de mostrar respuesta
    # Buscar el bloque donde se procesa la respuesta
    audio_playback = """
                    // Reproducir audio si está disponible (TTS del servidor)
                    if (data.audio_base64 && data.tts_disponible) {
                        try {
                            const audio = new Audio('data:audio/mp3;base64,' + data.audio_base64);
                            audio.play().catch(err => console.warn('Audio bloqueado:', err));
                        } catch(e) {
                            console.warn('Error reproduciendo audio:', e);
                        }
                    }
"""
    
    # Insertar después de la línea que muestra la respuesta
    marker = "messagesContainer.innerHTML += messageHtml;"
    if marker in content and 'data.audio_base64' not in content:
        content = content.replace(marker, marker + audio_playback)
        print("✓ Reproducción de audio agregada")
    else:
        print("ℹ Audio ya estaba presente o no se encontró el marker")
    
    # Guardar
    with open(DASHBOARD, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("✅ DASHBOARD CORREGIDO")
    print("="*60)
    print("\n📋 Próximos pasos:")
    print("1. Reiniciar Flask si está corriendo")
    print("2. Hard refresh en el navegador (Ctrl+Shift+R)")
    print("3. Probar el asistente en el dashboard")
    print("\nSi no funciona, verificar en F12 → Network que llame a /asistente_ia_v2")

if __name__ == '__main__':
    try:
        fix_dashboard()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
