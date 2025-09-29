# Configuración de Deploy Automático para SIBIA

## 🚀 Estado del Deploy

**Última actualización:** 2025-09-28 16:43:17
**Sistema de voz:** Parler-TTS + Edge-TTS (Gratuito)
**Estado:** ✅ Listo para deploy

## 📁 Archivos Sincronizados

### Archivos Principales
- ✅ `app_CORREGIDO_OK_FINAL.py` - Aplicación principal actualizada
- ✅ `voice_system_gratuito.py` - Sistema de voz gratuito
- ✅ `requirements.txt` - Dependencias actualizadas
- ✅ `Procfile` - Configuración de producción
- ✅ `runtime.txt` - Versión de Python

### Carpetas Sincronizadas
- ✅ `templates/` - Plantillas HTML actualizadas
- ✅ `static/` - Archivos estáticos y JavaScript

### Configuración de Deploy
- ✅ `.github/workflows/deploy.yml` - GitHub Actions actualizado
- ✅ `README.md` - Documentación actualizada
- ✅ `README_DEPLOY_VOZ_GRATUITA.md` - Guía de deploy

## 🔧 Comandos para Deploy

### 1. Commit y Push a GitHub
```bash
cd SIBIA_GITHUB
git add .
git commit -m "Actualización: Sistema de voz gratuito implementado"
git push origin main
```

### 2. Verificar Deploy Automático
- El GitHub Action se ejecutará automáticamente
- Verificar en la pestaña "Actions" del repositorio
- El deploy incluirá:
  - Instalación de dependencias
  - Prueba del sistema de voz
  - Deploy a Railway (si está configurado)

## 🎵 Sistema de Voz Gratuito

### Características
- **Parler-TTS**: Modelo de alta calidad (opcional con API key)
- **Edge-TTS**: Fallback automático para español
- **Sin límites**: Uso ilimitado sin costos
- **Sin configuración**: Funciona out-of-the-box

### Variables de Entorno Opcionales
```bash
HUGGINGFACE_API_KEY=tu_api_key_aqui  # Solo para Parler-TTS
RAILWAY_TOKEN=tu_token_aqui          # Solo para deploy automático
```

## 📡 Sincronización Automática

**Cursor ya está configurado para sincronizar automáticamente** los cambios con esta carpeta GitHub.

### Script de Sincronización
```bash
python sync_to_github_simple.py
```

## ✅ Checklist de Deploy

- [x] Archivos principales actualizados
- [x] Sistema de voz gratuito implementado
- [x] GitHub Actions configurado
- [x] Documentación actualizada
- [x] Sincronización completada
- [ ] Commit y push a GitHub
- [ ] Verificar deploy automático

---

**© 2025 AutoLinkSolutions SRL**  
**Sistema SIBIA - Deploy Automático Configurado**
