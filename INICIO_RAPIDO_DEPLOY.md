# ⚡ INICIO RÁPIDO - DEPLOY A GOOGLE CLOUD

## 🎯 OBJETIVO
Tener SIBIA corriendo en una IP pública y que cualquier cambio que hagas en Windsurf se despliegue automáticamente con `git push`.

---

## ✅ LO QUE YA ESTÁ LISTO

| Item | Estado |
|------|--------|
| Dockerfile | ✅ Creado |
| GitHub Actions CI/CD | ✅ Configurado |
| requirements.txt | ✅ Actualizado |
| Scripts de configuración | ✅ Listos |
| Git conectado a GitHub | ✅ Verificado |
| Documentación completa | ✅ Disponible |

---

## 📋 PASOS PARA DESPLEGAR (5 minutos)

### **PASO 1: Instalar Google Cloud SDK** ☁️

**Descargar e instalar:**
https://cloud.google.com/sdk/docs/install

**Después de instalar, REINICIAR PowerShell y verificar:**
```powershell
gcloud --version
```

---

### **PASO 2: Configurar Google Cloud** ⚙️

**Ejecutar script automático:**
```powershell
.\setup_gcloud.ps1
```

**El script te pedirá:**
1. Login en Google Cloud (se abre navegador)
2. Seleccionar tu proyecto (o crear uno nuevo)
3. Generará automáticamente las credenciales

**Tiempo estimado:** 2-3 minutos

---

### **PASO 3: Configurar Secrets en GitHub** 🔐

1. **Abrir tu repositorio en GitHub**

2. **Ir a:** `Settings` → `Secrets and variables` → `Actions`

3. **Click:** `New repository secret`

4. **Agregar Secret 1:**
   - Name: `GCP_PROJECT_ID`
   - Value: `[El PROJECT_ID que aparece en setup_gcloud.ps1]`

5. **Agregar Secret 2:**
   - Name: `GCP_SA_KEY`
   - Value: `[Todo el contenido de gcloud-key.json]`

**Para copiar gcloud-key.json:**
```powershell
notepad gcloud-key.json
# Copiar TODO (desde { hasta })
```

**Tiempo estimado:** 2 minutos

---

### **PASO 4: Deploy** 🚀

```powershell
# 1. Ver archivos nuevos
git status

# 2. Agregar todo
git add .

# 3. Commit
git commit -m "feat: Sistema de deploy automático a Google Cloud"

# 4. Push (DEPLOY AUTOMÁTICO)
git push origin main
```

**¡ESO ES TODO!** El deploy se ejecuta automáticamente.

---

### **PASO 5: Obtener tu URL** 🌐

Después de 5-10 minutos (primer deploy):

```powershell
gcloud run services describe sibia-app `
  --platform managed `
  --region us-central1 `
  --format 'value(status.url)'
```

**Tu app estará en:**
```
https://sibia-app-XXXXX-uc.a.run.app
```

---

## 🔄 FLUJO DE TRABAJO DIARIO

### **Desarrollar localmente:**
```powershell
# Trabajar en Windsurf normalmente
# Hacer cambios, probar localmente...
python app_CORREGIDO_OK_FINAL.py
```

### **Desplegar a producción:**
```powershell
git add .
git commit -m "descripción de cambios"
git push
```

**¡Listo!** En ~5 min los cambios están en la nube.

---

## 📊 VERIFICAR DEPLOY

### **Ver progreso en GitHub:**
1. Ir a tu repo en GitHub
2. Click en `Actions`
3. Ver workflow ejecutándose

### **Ver logs en Cloud:**
```powershell
gcloud run services logs read sibia-app --region us-central1 --limit 50
```

---

## 🐛 PROBLEMAS COMUNES

### **"Google Cloud SDK no instalado"**
- Descargar: https://cloud.google.com/sdk/docs/install
- Reiniciar PowerShell después de instalar

### **"Permission denied" en GitHub Actions**
- Verificar que agregaste los 2 secrets en GitHub
- Verificar que `GCP_SA_KEY` tiene TODO el JSON

### **"Service not found"**
- El primer deploy tarda 5-10 minutos
- Verificar en GitHub Actions que terminó exitosamente

### **"Port error"**
- Cloud Run usa puerto 8080 automáticamente
- Ya está configurado en el código ✅

---

## 📁 ARCHIVOS CREADOS

```
├── Dockerfile                              # Containeriza la app
├── .dockerignore                           # Archivos a ignorar
├── requirements.txt                        # Dependencias (actualizado)
├── .github/
│   └── workflows/
│       └── deploy-gcloud.yml              # GitHub Actions CI/CD
├── cloudbuild.yaml                        # Alternativa de deploy
├── setup_gcloud.ps1                       # Configuración automática
├── verificar_deploy.ps1                   # Script de verificación
├── GUIA_DESPLIEGUE_GOOGLE_CLOUD.md       # Guía completa (detallada)
└── INICIO_RAPIDO_DEPLOY.md               # Esta guía (resumen)
```

---

## 💰 COSTOS

**Google Cloud ofrece:**
- ✅ $300 USD gratis para nuevas cuentas
- ✅ 2 millones de requests/mes GRATIS
- ✅ Capa gratuita permanente

**Para SIBIA:** ~$0-10 USD/mes en producción real

---

## 🎓 DOCUMENTACIÓN

- **Guía rápida:** Este archivo
- **Guía completa:** `GUIA_DESPLIEGUE_GOOGLE_CLOUD.md`
- **Docs oficiales:** https://cloud.google.com/run/docs

---

## ✅ CHECKLIST

Antes de hacer push:
- [ ] Google Cloud SDK instalado
- [ ] `setup_gcloud.ps1` ejecutado
- [ ] 2 secrets configurados en GitHub
- [ ] `git push` ejecutado

Después del deploy:
- [ ] GitHub Actions ejecutado exitosamente (verde ✅)
- [ ] URL obtenida con `gcloud run services describe`
- [ ] App accesible en la URL
- [ ] Health check OK: `https://tu-url/health`

---

## 🚀 VENTAJAS DE ESTE SETUP

✅ **Deploy automático:** `git push` → app actualizada en 5 min  
✅ **Escalado automático:** Soporta de 0 a miles de usuarios  
✅ **Siempre disponible:** 99.9% uptime  
✅ **Económico:** Capa gratuita generosa  
✅ **IP pública:** Accesible desde cualquier lugar  
✅ **HTTPS automático:** Certificado SSL incluido  
✅ **Fácil de usar:** Solo necesitas `git push`  

---

## 📞 SOPORTE RÁPIDO

### **Verificar estado:**
```powershell
.\verificar_deploy.ps1
```

### **Ver logs:**
```powershell
gcloud run services logs tail sibia-app --region us-central1
```

### **Reiniciar servicio:**
```powershell
gcloud run services update sibia-app --region us-central1
```

---

## 🎉 ¡LISTO!

Una vez completados los 5 pasos, tendrás:

```
Tu código en Windsurf
    ↓ git push
GitHub (tu repositorio)
    ↓ Deploy automático
Google Cloud Run
    ↓
https://sibia-app-xxxxx.run.app ← Tu app corriendo 24/7
```

**Cualquier cambio → `git push` → Automáticamente en producción**

---

**© 2025 AutoLinkSolutions SRL**  
**SIBIA - Sistema Inteligente de Biogás Avanzado**
