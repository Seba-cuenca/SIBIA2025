#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIX SIMPLE DEL WIDGET"""

with open('templates/dashboard_hibrido.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar el widget (líneas 3069-3092 aprox)
widget_start = None
widget_end = None

for i, line in enumerate(lines):
    if '<!-- Predicción de Fallos ML (Simple - Sin JS complejo) -->' in line:
        widget_start = i
    if widget_start and '</div>\n' == line and i > widget_start + 20:
        widget_end = i + 1
        break

print(f"Widget encontrado: líneas {widget_start+1} a {widget_end}")

# Extraer el widget
widget_lines = lines[widget_start:widget_end]

# Eliminar el widget de su posición actual
del lines[widget_start:widget_end]

# Encontrar donde insertarlo (antes del cierre del contenedor de Predicciones IA)
# Buscar línea 3066 (cierre de </div> después de Predicciones IA)
for i in range(3060, 3070):
    if i < len(lines) and lines[i].strip() == '</div>' and lines[i-1].strip() == '</div>':
        # Insertar ANTES de este cierre
        lines[i:i] = widget_lines
        print(f"Widget insertado en línea {i+1}")
        break

# Guardar
with open('templates/dashboard_hibrido.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Widget reubicado correctamente")
print("Recarga el navegador: Ctrl + Shift + R")
