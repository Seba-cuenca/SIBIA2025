# Script PowerShell para configurar Google Cloud
# Ejecutar: .\setup_gcloud.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SIBIA - Configuracion Google Cloud" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar gcloud instalado
Write-Host "1. Verificando Google Cloud SDK..." -ForegroundColor Yellow
$gcloudInstalled = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudInstalled) {
    Write-Host "ERROR: Google Cloud SDK no esta instalado" -ForegroundColor Red
    Write-Host "Descargar desde: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}
Write-Host "   OK - Google Cloud SDK instalado" -ForegroundColor Green
Write-Host ""

# 2. Login a Google Cloud
Write-Host "2. Iniciando sesion en Google Cloud..." -ForegroundColor Yellow
gcloud auth login
Write-Host "   OK - Sesion iniciada" -ForegroundColor Green
Write-Host ""

# 3. Listar y seleccionar proyecto
Write-Host "3. Seleccionando proyecto..." -ForegroundColor Yellow
Write-Host "   Proyectos disponibles:" -ForegroundColor Cyan
gcloud projects list
Write-Host ""
$projectId = Read-Host "   Ingresa el PROJECT_ID de tu proyecto"

gcloud config set project $projectId
Write-Host "   OK - Proyecto configurado: $projectId" -ForegroundColor Green
Write-Host ""

# 4. Habilitar APIs necesarias
Write-Host "4. Habilitando APIs necesarias..." -ForegroundColor Yellow
$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "   Habilitando $api..." -ForegroundColor Cyan
    gcloud services enable $api 2>$null
}
Write-Host "   OK - APIs habilitadas" -ForegroundColor Green
Write-Host ""

# 5. Crear Service Account para GitHub Actions
Write-Host "5. Creando Service Account para GitHub Actions..." -ForegroundColor Yellow
$saName = "github-actions-sibia"
$saEmail = "$saName@$projectId.iam.gserviceaccount.com"

gcloud iam service-accounts create $saName `
    --display-name="GitHub Actions SIBIA" `
    --description="Service Account para deploy automatico desde GitHub" `
    2>$null

# Asignar roles necesarios
$roles = @(
    "roles/run.admin",
    "roles/storage.admin",
    "roles/iam.serviceAccountUser"
)

foreach ($role in $roles) {
    gcloud projects add-iam-policy-binding $projectId `
        --member="serviceAccount:$saEmail" `
        --role=$role `
        2>$null
}

# Crear key JSON
$keyFile = "gcloud-key.json"
gcloud iam service-accounts keys create $keyFile `
    --iam-account=$saEmail

Write-Host "   OK - Service Account creado" -ForegroundColor Green
Write-Host "   KEY guardada en: $keyFile" -ForegroundColor Cyan
Write-Host ""

# 6. Instrucciones para GitHub Secrets
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   CONFIGURAR GITHUB SECRETS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ve a tu repositorio GitHub:" -ForegroundColor Yellow
Write-Host "  Settings > Secrets and variables > Actions > New repository secret" -ForegroundColor White
Write-Host ""
Write-Host "Agrega estos secrets:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. GCP_PROJECT_ID" -ForegroundColor Cyan
Write-Host "   Valor: $projectId" -ForegroundColor White
Write-Host ""
Write-Host "2. GCP_SA_KEY" -ForegroundColor Cyan
Write-Host "   Valor: Contenido completo del archivo $keyFile" -ForegroundColor White
Write-Host "   (Abre $keyFile y copia todo el JSON)" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   PROXIMO PASO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Una vez configurados los secrets en GitHub:" -ForegroundColor Yellow
Write-Host "  1. git add ." -ForegroundColor White
Write-Host "  2. git commit -m 'Configuracion deploy automatico'" -ForegroundColor White
Write-Host "  3. git push" -ForegroundColor White
Write-Host ""
Write-Host "El deploy se ejecutara automaticamente!" -ForegroundColor Green
Write-Host ""

# Guardar información de configuración
$configInfo = @{
    project_id = $projectId
    service_account = $saEmail
    region = "us-central1"
    service_name = "sibia-app"
    setup_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$configInfo | ConvertTo-Json | Out-File "gcloud-config.json"

Write-Host "Configuracion guardada en: gcloud-config.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: NO subas gcloud-key.json a GitHub!" -ForegroundColor Red
Write-Host "Este archivo contiene credenciales sensibles" -ForegroundColor Red
Write-Host ""
