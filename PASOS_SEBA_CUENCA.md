# 🚀 PASOS ESPECÍFICOS PARA SEBA-CUENCA

## 📋 TUS DATOS

✅ **Google Cloud Project**: `warm-calculus-473421-j7`  
✅ **GitHub Repo**: `Seba-cuenca/SIBIA2025`  
✅ **VM existente**: `autolink-vm` (IP: 34.42.138.250)  
✅ **Región**: `us-central1`  

---

## ⚡ PASOS RÁPIDOS (10 minutos)

### **PASO 1: Verificar Google Cloud SDK** ☁️

```powershell
# Verificar si está instalado
gcloud --version
```

**Si NO está instalado:**
Descargar: https://cloud.google.com/sdk/docs/install

**Si YA está instalado, continuar al PASO 2** ✅

---

### **PASO 2: Login y Configurar Proyecto** ⚙️

```powershell
# Login (se abre el navegador)
gcloud auth login

# Configurar tu proyecto
gcloud config set project warm-calculus-473421

# Verificar
gcloud config get-value project
# Debe mostrar: warm-calculus-473421
```

---

### **PASO 3: Habilitar APIs Necesarias** 🔧

```powershell
# Cloud Run
gcloud services enable run.googleapis.com

# Cloud Build
gcloud services enable cloudbuild.googleapis.com

# Container Registry
gcloud services enable containerregistry.googleapis.com

# Secret Manager (opcional)
gcloud services enable secretmanager.googleapis.com
```

**Tiempo:** ~2 minutos

---

### **PASO 4: Crear Service Account para GitHub** 🔐

```powershell
# Crear Service Account
gcloud iam service-accounts create github-actions-sibia `
  --display-name="GitHub Actions SIBIA Deploy" `
  --description="Service Account para deploy automatico desde GitHub"

# Asignar roles necesarios
gcloud projects add-iam-policy-binding warm-calculus-473421 `
  --member="serviceAccount:github-actions-sibia@warm-calculus-473421.iam.gserviceaccount.com" `
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding warm-calculus-473421 `
  --member="serviceAccount:github-actions-sibia@warm-calculus-473421.iam.gserviceaccount.com" `
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding warm-calculus-473421 `
  --member="serviceAccount:github-actions-sibia@warm-calculus-473421.iam.gserviceaccount.com" `
  --role="roles/iam.serviceAccountUser"

# Crear key JSON
gcloud iam service-accounts keys create gcloud-key-sibia.json `
  --iam-account=github-actions-sibia@warm-calculus-473421.iam.gserviceaccount.com
```

**Resultado:** Archivo `gcloud-key-sibia.json` creado ✅

---

### **PASO 5: Configurar Secret en GitHub** 🔑

1. **Abrir:** https://github.com/Seba-cuenca/SIBIA2025/settings/secrets/actions

2. **Click:** `New repository secret`

3. **Crear Secret:**
   - **Name:** `GCP_SA_KEY`
   - **Value:** Copiar TODO el contenido de `gcloud-key-sibia.json`

**Para copiar el archivo:**
```powershell
notepad gcloud-key-sibia.json
# Copiar TODO (desde { hasta } incluyendo las llaves)
```

**IMPORTANTE:** Copiar **TODO** el JSON, debe empezar con `{` y terminar con `}`

---

### **PASO 6: Hacer Push y Deploy** 🚀

```powershell
# En tu directorio del proyecto
cd "c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS"

# Ver archivos modificados
git status

# Agregar todos los cambios
git add .

# Commit
git commit -m "feat: Deploy automatico a Google Cloud Run configurado"

# Push (esto ejecuta el deploy automáticamente)
git push origin SIBIA_GITHUB
```

**El deploy se ejecuta automáticamente al hacer push ✅**

---

### **PASO 7: Verificar Deploy** ✅

1. **Ver progreso en GitHub:**
   - Ir a: https://github.com/Seba-cuenca/SIBIA2025/actions
   - Ver workflow ejecutándose
   - Esperar ~5-10 minutos (primer deploy)

2. **Una vez completado, obtener URL:**

```powershell
gcloud run services describe sibia-app `
  --platform managed `
  --region us-central1 `
  --format 'value(status.url)'
```

**Tu app estará en:** `https://sibia-app-xxxxx-uc.a.run.app`

---

## 🌐 ACCEDER A TU APLICACIÓN

### **URL Pública (después del deploy):**
```
https://sibia-app-[ID-GENERADO]-uc.a.run.app
```

### **Endpoints principales:**
```
https://tu-url.run.app/                    # Home
https://tu-url.run.app/dashboard           # Dashboard principal
https://tu-url.run.app/health              # Health check
https://tu-url.run.app/api/ml/estadisticas-aprendizaje
```

---

## 🔄 FLUJO DE TRABAJO DIARIO

### **Desarrollar localmente:**
```powershell
# Trabajar en Windsurf
# Hacer cambios en tu código
# Probar localmente
python app_CORREGIDO_OK_FINAL.py
```

### **Desplegar cambios:**
```powershell
git add .
git commit -m "descripción de cambios"
git push origin SIBIA_GITHUB
```

**¡Listo!** En ~5 minutos los cambios están en la nube.

---

## 📊 COMANDOS ÚTILES

### **Ver logs en tiempo real:**
```powershell
gcloud run services logs tail sibia-app --region us-central1
```

### **Ver últimos 50 logs:**
```powershell
gcloud run services logs read sibia-app --region us-central1 --limit 50
```

### **Ver info del servicio:**
```powershell
gcloud run services describe sibia-app --region us-central1
```

### **Actualizar recursos (más memoria/CPU):**
```powershell
gcloud run services update sibia-app `
  --region us-central1 `
  --memory 4Gi `
  --cpu 4
```

### **Reiniciar servicio:**
```powershell
gcloud run services update sibia-app --region us-central1 --set-env-vars="RESTART=$(date +%s)"
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **Error: "API not enabled"**
```powershell
# Habilitar Cloud Run API
gcloud services enable run.googleapis.com --project=warm-calculus-473421
```

### **Error: "Permission denied" en GitHub Actions**
✅ **Verificar que agregaste el secret `GCP_SA_KEY` en:**
https://github.com/Seba-cuenca/SIBIA2025/settings/secrets/actions

✅ **Verificar que copiaste TODO el JSON (incluye `{` y `}`)**

### **Deploy falla en GitHub Actions:**
1. Ver logs en: https://github.com/Seba-cuenca/SIBIA2025/actions
2. Ver error específico en el paso que falló
3. Verificar que las APIs estén habilitadas

### **App no responde:**
```powershell
# Ver logs
gcloud run services logs read sibia-app --region us-central1 --limit 100

# Ver estado
gcloud run services describe sibia-app --region us-central1
```

---

## 🎯 DIFERENCIA CON TU VM ACTUAL

### **VM Actual (autolink-vm):**
- IP fija: 34.42.138.250
- Requiere gestionar servidor
- Siempre corriendo (costo fijo)
- Requiere SSH para actualizar

### **Cloud Run (NUEVO):**
- URL automática con HTTPS
- Escala automáticamente
- Solo pagas por uso real
- Deploy automático con `git push`

**Puedes mantener ambos o migrar completamente a Cloud Run** ✅

---

## ✅ CHECKLIST

Antes de hacer push:
- [ ] Google Cloud SDK instalado y configurado
- [ ] Proyecto `warm-calculus-473421` configurado
- [ ] APIs habilitadas (Run, Build, Container Registry)
- [ ] Service Account creado
- [ ] Secret `GCP_SA_KEY` agregado en GitHub
- [ ] Archivos modificados: `deploy-gcloud.yml` (ya está ✅)

Después del deploy:
- [ ] GitHub Actions ejecutado (verde ✅)
- [ ] URL obtenida con `gcloud run services describe`
- [ ] App accesible en la URL
- [ ] Health check OK: `/health`
- [ ] Dashboard cargando: `/dashboard`

---

## 💰 COSTOS

**Tu proyecto tiene:**
- ✅ $300 USD crédito gratis (si es cuenta nueva)
- ✅ 2 millones requests/mes GRATIS
- ✅ 360,000 GB-segundos/mes GRATIS

**Estimación para SIBIA:**
- Desarrollo/testing: **GRATIS** (dentro de capa gratuita)
- Producción baja: **~$5-10 USD/mes**
- Producción alta: **~$20-30 USD/mes**

**Mucho más económico que mantener una VM 24/7** ✅

---

## 📞 CONTACTO Y SOPORTE

### **Proyecto Google Cloud:**
https://console.cloud.google.com/home/dashboard?project=warm-calculus-473421

### **GitHub Repo:**
https://github.com/Seba-cuenca/SIBIA2025

### **GitHub Actions (ver deploys):**
https://github.com/Seba-cuenca/SIBIA2025/actions

### **VM existente (si necesitas):**
```
ssh autolink-vm  # IP: 34.42.138.250
```

---

## 🎉 RESUMEN

Una vez completados los pasos:

```
Tu Windsurf (código local)
    ↓ git push origin SIBIA_GITHUB
GitHub: Seba-cuenca/SIBIA2025
    ↓ GitHub Actions automático
Google Cloud: warm-calculus-473421
    ↓ Deploy a Cloud Run
https://sibia-app-xxxxx.run.app ← Tu app 24/7
```

**Cualquier cambio → `git push` → Automáticamente en Cloud Run** 🚀

---

**© 2025 AutoLinkSolutions SRL**  
**SIBIA - Sistema Inteligente de Biogás Avanzado**
