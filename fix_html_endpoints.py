#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime

DASHBOARD = r"c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS\templates\dashboard_hibrido.html"

# Backup
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
backup = f"{DASHBOARD}.bak_{ts}"
with open(DASHBOARD, 'r', encoding='utf-8') as f:
    content = f.read()
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✅ Backup: {backup}")

# Reemplazar llamadas a sensores_criticos_resumen con mock
content = content.replace(
    "const response = await fetch('/sensores_criticos_resumen');",
    "// Endpoint eliminado - retornando datos mock\n                const response = {ok: true, json: async () => ({sensores: {}})};"
)

# Reemplazar llamadas a balance_volumetrico_completo
content = content.replace(
    "fetch('/balance_volumetrico_completo')",
    "// Endpoint eliminado\n                fetch('/health')"
)

with open(DASHBOARD, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ HTML parcheado - reinicia Flask y refresca el navegador")
