# SIBIA - Sistema de Voz Gratuito

## 🎵 Sistema de Voz Actualizado

**SIBIA ahora incluye un sistema de voz completamente gratuito:**

- ✅ **Parler-TTS**: Modelo de alta calidad de Hugging Face
- ✅ **Edge-TTS**: Fallback automático para español
- ✅ **Sin límites**: Uso ilimitado sin costos
- ✅ **Sin API keys**: Funciona sin configuración adicional

## 🚀 Deploy Automático

### Configuración para GitHub Actions

El proyecto está configurado para deploy automático con:

1. **Railway** (si tienes token configurado)
2. **Cualquier plataforma** compatible con Python/Flask

### Variables de Entorno Opcionales

```bash
# Solo si quieres usar Parler-TTS con API key (opcional)
HUGGINGFACE_API_KEY=tu_api_key_aqui

# Para Railway (opcional)
RAILWAY_TOKEN=tu_token_aqui
```

### Instalación Local

```bash
pip install -r requirements.txt
python app_CORREGIDO_OK_FINAL.py
```

## 📡 Sincronización Automática

**Cursor ya está configurado para sincronizar automáticamente** los cambios con esta carpeta GitHub.

### Archivos Principales Actualizados

- ✅ `app_CORREGIDO_OK_FINAL.py` - Aplicación principal
- ✅ `voice_system_gratuito.py` - Sistema de voz gratuito
- ✅ `requirements.txt` - Dependencias actualizadas
- ✅ `Procfile` - Configuración de producción
- ✅ `.github/workflows/deploy.yml` - Deploy automático

## 🎯 Funcionalidades

- **Asistente IA**: Respuestas inteligentes con voz
- **Dashboard**: Monitoreo de biodigestores
- **Calculadora**: Análisis de mezclas
- **ML**: Predicciones con XGBoost
- **Voz**: Síntesis de alta calidad gratuita

## 💡 Ventajas del Nuevo Sistema

1. **Sin costos**: Eliminado Eleven Labs
2. **Sin límites**: Uso ilimitado
3. **Alta calidad**: Parler-TTS + Edge-TTS
4. **Automático**: Deploy con cada push
5. **Sincronizado**: Cambios desde Cursor

---

**© 2025 AutoLinkSolutions SRL**  
**Sistema SIBIA - Versión con Voz Gratuita**
