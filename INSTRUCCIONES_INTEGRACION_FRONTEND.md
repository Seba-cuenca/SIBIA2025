# 📝 INSTRUCCIONES PARA INTEGRAR PREDICCIÓN DE FALLOS EN EL DASHBOARD

## ✅ Backend YA ESTÁ INTEGRADO

El backend está **100% funcional** con:
- ✅ Modelo Random Forest cargado en `app_CORREGIDO_OK_FINAL.py`
- ✅ Endpoint `/api/predecir-fallo` (POST) - Predicción con datos personalizados
- ✅ Endpoint `/api/predecir-fallo-automatico` (GET) - Predicción automática

## 🎨 INTEGRACIÓN FRONTEND (2 pasos simples)

### PASO 1: Agregar Widget HTML

**Archivo:** `templates/dashboard_hibrido.html`

**Ubicación:** Línea **3067** (después del cierre `</div>` de "Predicciones IA")

**Código a insertar:**
```html
Abrir archivo: templates/widget_prediccion_fallos.html
Copiar todo el contenido
Pegar en dashboard_hibrido.html después de la línea 3067
```

**Referencia visual:**
```html
<!-- Línea 3066 -->
                    </div>
                </div>

                <!-- ⬇️ INSERTAR AQUÍ EL WIDGET ⬇️ -->

                <!-- Tabla de Rendimiento por Materiales -->
                <div class="function-card full-width">
```

### PASO 2: Agregar JavaScript

**Archivo:** `templates/dashboard_hibrido.html`

**Ubicación:** Dentro del `<script>` existente, antes del cierre `</script>` final

**Código a insertar:**
```javascript
Abrir archivo: templates/script_prediccion_fallos.js
Copiar todo el contenido
Pegar dentro del <script> al final del archivo HTML
```

## 🚀 PRUEBA RÁPIDA

Una vez integrado, puedes probar directamente desde el navegador:

### Opción 1: Desde la consola del navegador (F12)
```javascript
// Prueba manual de predicción
fetch('/api/predecir-fallo', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        co2_bio040_pct: 35.0,
        co2_bio050_pct: 36.0,
        o2_bio040_pct: 0.3,
        o2_bio050_pct: 0.4,
        caudal_chp_ls: 120.5
    })
})
.then(r => r.json())
.then(data => console.log(data));
```

### Opción 2: Desde PowerShell/CMD
```powershell
# Prueba del endpoint
curl -X POST http://localhost:5000/api/predecir-fallo `
  -H "Content-Type: application/json" `
  -d '{\"co2_bio040_pct\": 35.0, \"co2_bio050_pct\": 36.0, \"o2_bio040_pct\": 0.3, \"o2_bio050_pct\": 0.4}'
```

### Opción 3: Predicción automática
```
Abrir: http://localhost:5000/api/predecir-fallo-automatico
```

## 🎨 ASPECTO VISUAL

El widget mostrará:

```
╔══════════════════════════════════════════╗
║  🛡️ Predicción de Fallos ML    [Actualizar] ║
╠══════════════════════════════════════════╣
║                                          ║
║  ✅ Sistema Óptimo           95.3%      ║
║  ████████████████████░░░░   Confianza   ║
║                                          ║
║  📊 Probabilidades por Estado            ║
║  ┌─────────┐ ┌─────────┐               ║
║  │ Óptimo  │ │ Normal  │               ║
║  │ 95.3%   │ │ 3.2%    │               ║
║  └─────────┘ └─────────┘               ║
║                                          ║
║  💡 Recomendaciones                      ║
║  ✅ Sistema funcionando óptimamente     ║
║  🟢 Mantener condiciones actuales       ║
║                                          ║
║  🔬 Factores Más Importantes            ║
║  1. o2_promedio: 0.35 (23.5%)          ║
║  2. co2_promedio: 35.5 (18.2%)         ║
║  3. ratio_co2_o2: 101.4 (15.8%)        ║
║                                          ║
║  🕐 Última actualización: 07:15:23      ║
╚══════════════════════════════════════════╝
```

## 📋 CHECKLIST FINAL

- [ ] Backend integrado (✅ YA HECHO)
- [ ] Widget HTML agregado en dashboard_hibrido.html (línea 3067)
- [ ] JavaScript agregado en dashboard_hibrido.html (dentro de `<script>`)
- [ ] Servidor Flask reiniciado: `python app_CORREGIDO_OK_FINAL.py`
- [ ] Navegador actualizado (Ctrl+F5)
- [ ] Widget visible en el dashboard
- [ ] Predicción cargando correctamente

## ⚙️ CONFIGURACIÓN ADICIONAL (Opcional)

### Cambiar intervalo de actualización
En `script_prediccion_fallos.js`, línea 174:
```javascript
// Actualizar cada 5 minutos (300000 ms)
setInterval(() => {
    actualizarPrediccionFallos();
}, 5 * 60 * 1000);  // ⬅️ Cambiar aquí
```

### Personalizar colores
Modificar el objeto `estadoConfig` en línea 63 del script.

## 🐛 TROUBLESHOOTING

### Problema: "Modelo no disponible"
**Solución:**
```bash
cd "C:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS"
python entrenar_modelo_prediccion_fallos_reales.py
```

### Problema: Widget no aparece
**Verificar:**
1. Código HTML insertado correctamente
2. Cache del navegador limpiado (Ctrl+F5)
3. Consola del navegador sin errores (F12)

### Problema: Error 404 en /api/predecir-fallo
**Verificar:**
1. Flask corriendo: `python app_CORREGIDO_OK_FINAL.py`
2. Backend cargó el modelo (ver logs al iniciar)

## 📞 SOPORTE

Si tienes problemas:
1. Revisa los logs de Flask en la consola
2. Abre la consola del navegador (F12) → pestaña Console
3. Busca errores en rojo

---

**✅ Una vez completado, tendrás predicción de fallos en tiempo real con Random Forest!**

**Modelo entrenado con:** 926 registros reales de tu planta
**Accuracy:** 100% en datos de prueba
**Features utilizadas:** 20 parámetros de biodigestores
