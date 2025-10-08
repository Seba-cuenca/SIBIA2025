# 🚀 GUÍA COMPLETA: DESPLIEGUE AUTOMÁTICO EN GOOGLE CLOUD

## 📋 RESUMEN

Esta guía te permite:
- ✅ Desplegar SIBIA en Google Cloud Run
- ✅ Trabajar localmente en Windsurf
- ✅ Push a GitHub → Deploy automático en la nube
- ✅ Aplicación corriendo 24/7 con IP pública

---

## 🎯 ARQUITECTURA

```
Tu PC (Windsurf)
    ↓ git push
GitHub Repository
    ↓ Automatic trigger
GitHub Actions / Cloud Build
    ↓ Build Docker image
Google Container Registry
    ↓ Deploy
Google Cloud Run (Tu app en la nube)
    ↓
URL pública: https://sibia-app-xxxxx.run.app
```

---

## ✅ REQUISITOS PREVIOS

### 1️⃣ **Cuenta de Google Cloud**
- Ir a: https://console.cloud.google.com
- Crear cuenta si no tienes (incluye $300 USD gratis)
- Crear un proyecto nuevo (ej: "sibia-production")

### 2️⃣ **Google Cloud SDK**
Descargar e instalar desde: https://cloud.google.com/sdk/docs/install

**Verificar instalación:**
```powershell
gcloud --version
```

### 3️⃣ **Git configurado con GitHub**
```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

---

## 🚀 CONFIGURACIÓN PASO A PASO

### **PASO 1: Configurar Google Cloud** ⚙️

#### Opción A: Automático (RECOMENDADO)

```powershell
# Ejecutar script de configuración
.\setup_gcloud.ps1
```

El script hará AUTOMÁTICAMENTE:
- ✅ Login en Google Cloud
- ✅ Configurar proyecto
- ✅ Habilitar APIs necesarias
- ✅ Crear Service Account
- ✅ Generar credenciales para GitHub

#### Opción B: Manual

```powershell
# 1. Login
gcloud auth login

# 2. Listar proyectos
gcloud projects list

# 3. Configurar proyecto
gcloud config set project TU-PROJECT-ID

# 4. Habilitar APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 5. Crear Service Account
gcloud iam service-accounts create github-actions-sibia `
  --display-name="GitHub Actions SIBIA"

# 6. Asignar roles
gcloud projects add-iam-policy-binding TU-PROJECT-ID `
  --member="serviceAccount:github-actions-sibia@TU-PROJECT-ID.iam.gserviceaccount.com" `
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding TU-PROJECT-ID `
  --member="serviceAccount:github-actions-sibia@TU-PROJECT-ID.iam.gserviceaccount.com" `
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding TU-PROJECT-ID `
  --member="serviceAccount:github-actions-sibia@TU-PROJECT-ID.iam.gserviceaccount.com" `
  --role="roles/iam.serviceAccountUser"

# 7. Crear key
gcloud iam service-accounts keys create gcloud-key.json `
  --iam-account=github-actions-sibia@TU-PROJECT-ID.iam.gserviceaccount.com
```

---

### **PASO 2: Configurar Secrets en GitHub** 🔐

1. **Ve a tu repositorio en GitHub**

2. **Click en: Settings → Secrets and variables → Actions**

3. **Click en: New repository secret**

4. **Agregar estos 2 secrets:**

#### Secret 1: `GCP_PROJECT_ID`
```
Name: GCP_PROJECT_ID
Value: TU-PROJECT-ID (ej: sibia-production-12345)
```

#### Secret 2: `GCP_SA_KEY`
```
Name: GCP_SA_KEY
Value: [Contenido COMPLETO del archivo gcloud-key.json]
```

**Para copiar el contenido:**
```powershell
# Abrir archivo y copiar TODO el contenido (incluye las llaves {})
notepad gcloud-key.json
```

---

### **PASO 3: Preparar Código para Despliegue** 📦

#### Verificar archivos creados:

```
✅ Dockerfile
✅ .dockerignore
✅ requirements.txt (con apscheduler y gunicorn)
✅ .github/workflows/deploy-gcloud.yml
✅ cloudbuild.yaml
✅ .gitignore (actualizado)
```

#### Modificar app si usa puerto específico:

El código ya está configurado para leer `PORT` de variable de entorno:
```python
port = int(os.environ.get('PORT', 5000))
```

Cloud Run usa puerto `8080` automáticamente. ✅

---

### **PASO 4: Hacer Commit y Push** 📤

```powershell
# 1. Ver cambios
git status

# 2. Agregar todos los archivos
git add .

# 3. Commit
git commit -m "feat: Deploy automático a Google Cloud Run con CI/CD"

# 4. Push a GitHub
git push origin main
```

**IMPORTANTE:** Usar `main` o `master` según tu rama principal.

---

### **PASO 5: Verificar Deploy Automático** ✅

1. **Ve a GitHub → Tu repositorio → Actions**

2. **Verás el workflow ejecutándose:**
   - ⏳ Amarillo = En progreso
   - ✅ Verde = Exitoso
   - ❌ Rojo = Error

3. **El deploy toma ~5-10 minutos la primera vez**

4. **Una vez completado, obtén la URL:**

```powershell
gcloud run services describe sibia-app `
  --platform managed `
  --region us-central1 `
  --format 'value(status.url)'
```

**Ejemplo de URL:**
```
https://sibia-app-abcd1234-uc.a.run.app
```

---

## 🌐 ACCEDER A TU APLICACIÓN

### URL pública (accesible desde cualquier lugar):
```
https://sibia-app-XXXXX-uc.a.run.app
```

### Endpoints principales:
```
https://tu-url.run.app/                    # Home
https://tu-url.run.app/dashboard           # Dashboard
https://tu-url.run.app/health              # Health check
https://tu-url.run.app/api/ml/estadisticas-aprendizaje  # ML Stats
```

---

## 🔄 FLUJO DE TRABAJO DIARIO

### **Trabajar localmente:**

```powershell
# 1. Activar entorno virtual
cd "c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS"
.\venv\Scripts\Activate.ps1

# 2. Hacer cambios en Windsurf
# ... editar código ...

# 3. Probar localmente
python app_CORREGIDO_OK_FINAL.py

# 4. Verificar en: http://localhost:5000
```

### **Desplegar cambios a la nube:**

```powershell
# 1. Ver cambios
git status

# 2. Commit
git add .
git commit -m "descripción de cambios"

# 3. Push (DEPLOY AUTOMÁTICO)
git push

# 4. Esperar ~5 min y verificar en tu URL de Cloud Run
```

**¡ESO ES TODO!** 🎉 Los cambios se despliegan automáticamente.

---

## 🛠️ COMANDOS ÚTILES

### Ver logs de la aplicación en la nube:
```powershell
gcloud run services logs read sibia-app --region us-central1 --limit 50
```

### Ver logs en tiempo real:
```powershell
gcloud run services logs tail sibia-app --region us-central1
```

### Actualizar configuración (memoria, CPU):
```powershell
gcloud run services update sibia-app `
  --region us-central1 `
  --memory 4Gi `
  --cpu 4
```

### Ver información del servicio:
```powershell
gcloud run services describe sibia-app --region us-central1
```

### Eliminar servicio (si quieres empezar de nuevo):
```powershell
gcloud run services delete sibia-app --region us-central1
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **Error: "API not enabled"**
```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### **Error: "Permission denied"**
Verificar que el Service Account tenga los roles correctos:
```powershell
gcloud projects get-iam-policy TU-PROJECT-ID
```

### **Error: "Image not found"**
Verificar que la imagen se haya subido:
```powershell
gcloud container images list
```

### **Deploy falla en GitHub Actions:**
1. Verificar secrets en GitHub (Settings → Secrets)
2. Verificar que `GCP_SA_KEY` tenga el JSON completo
3. Verificar que `GCP_PROJECT_ID` sea correcto

### **App no inicia:**
Ver logs:
```powershell
gcloud run services logs read sibia-app --region us-central1 --limit 100
```

---

## 📊 MONITOREO

### **Google Cloud Console:**
https://console.cloud.google.com/run

Aquí puedes ver:
- ✅ Número de requests
- ✅ Latencia
- ✅ Errores
- ✅ Uso de CPU/memoria
- ✅ Logs en tiempo real

### **Métricas de ML:**
```bash
curl https://tu-url.run.app/api/ml/estadisticas-aprendizaje
```

---

## 💰 COSTOS

**Google Cloud Run pricing:**
- ✅ **$300 USD gratis** para nuevas cuentas
- ✅ **2 millones requests/mes GRATIS**
- ✅ **360,000 GB-segundos/mes GRATIS**

Para SIBIA con configuración estándar:
- **~$0-10 USD/mes** en producción real
- **Gratis** durante desarrollo

**Calculadora de precios:**
https://cloud.google.com/products/calculator

---

## 🔒 SEGURIDAD

### **Proteger credenciales:**
```powershell
# NUNCA subir a GitHub:
gcloud-key.json
gcloud-config.json
```

Ya están en `.gitignore` ✅

### **Variables de entorno sensibles:**
Si necesitas API keys, agrégalas como secrets en Cloud Run:
```powershell
gcloud run services update sibia-app `
  --region us-central1 `
  --set-env-vars="API_KEY=tu-clave-secreta"
```

### **Restringir acceso (opcional):**
```powershell
# Quitar acceso público
gcloud run services remove-iam-policy-binding sibia-app `
  --region us-central1 `
  --member="allUsers" `
  --role="roles/run.invoker"

# Agregar usuarios específicos
gcloud run services add-iam-policy-binding sibia-app `
  --region us-central1 `
  --member="user:tu@email.com" `
  --role="roles/run.invoker"
```

---

## 🚀 OPTIMIZACIONES AVANZADAS

### **Custom Domain (dominio propio):**
```powershell
# Mapear tu dominio
gcloud run domain-mappings create `
  --service sibia-app `
  --domain sibia.tuempresa.com `
  --region us-central1
```

### **Auto-scaling:**
```powershell
gcloud run services update sibia-app `
  --region us-central1 `
  --min-instances 1 `
  --max-instances 10
```

### **Cloud SQL (base de datos):**
```powershell
# Conectar Cloud SQL si migras desde MySQL local
gcloud run services update sibia-app `
  --add-cloudsql-instances TU-PROJECT:us-central1:sibia-db
```

---

## 📞 SOPORTE

### **Documentación oficial:**
- Cloud Run: https://cloud.google.com/run/docs
- GitHub Actions: https://docs.github.com/actions
- Docker: https://docs.docker.com

### **Verificar estado:**
```
https://status.cloud.google.com
```

---

## ✅ CHECKLIST FINAL

Antes de hacer push:

- [ ] Google Cloud SDK instalado
- [ ] Proyecto creado en Google Cloud
- [ ] APIs habilitadas
- [ ] Service Account creado
- [ ] Secrets configurados en GitHub (`GCP_PROJECT_ID`, `GCP_SA_KEY`)
- [ ] Dockerfile creado
- [ ] requirements.txt actualizado
- [ ] .gitignore actualizado
- [ ] GitHub Actions workflow creado

Después del primer deploy:

- [ ] Workflow ejecutado exitosamente en GitHub
- [ ] URL de Cloud Run obtenida
- [ ] Aplicación accesible en la URL
- [ ] Health check funcionando: `/health`
- [ ] Dashboard cargando: `/dashboard`

---

## 🎉 ¡LISTO!

Ahora tienes:
- ✅ Aplicación corriendo 24/7 en Google Cloud
- ✅ Deploy automático con cada `git push`
- ✅ Escalado automático
- ✅ Monitoring incluido
- ✅ URL pública accesible desde cualquier lugar

**Workflow:**
```
Desarrollar en Windsurf → git push → Deploy automático → App actualizada en Cloud
```

---

**© 2025 AutoLinkSolutions SRL**  
**SIBIA - Sistema Inteligente de Biogás Avanzado**
