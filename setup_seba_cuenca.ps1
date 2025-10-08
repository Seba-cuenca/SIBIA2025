# Script automático para Seba-cuenca/SIBIA2025
# Configuración específica para warm-calculus-473421

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SIBIA - Config Google Cloud" -ForegroundColor Cyan
Write-Host "   Proyecto: warm-calculus-473421" -ForegroundColor Cyan
Write-Host "   Repo: Seba-cuenca/SIBIA2025" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$projectId = "warm-calculus-473421-j7"
$saName = "github-actions-sibia"
$saEmail = "$saName@$projectId.iam.gserviceaccount.com"
$keyFile = "gcloud-key-sibia.json"

# 1. Verificar gcloud instalado
Write-Host "1. Verificando Google Cloud SDK..." -ForegroundColor Yellow
$gcloudInstalled = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudInstalled) {
    Write-Host "   ERROR: Google Cloud SDK no instalado" -ForegroundColor Red
    Write-Host "   Descargar: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Despues de instalar, REINICIAR PowerShell y ejecutar de nuevo" -ForegroundColor Cyan
    pause
    exit 1
}
Write-Host "   OK - Google Cloud SDK instalado" -ForegroundColor Green
Write-Host ""

# 2. Login
Write-Host "2. Verificando sesion..." -ForegroundColor Yellow
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $currentAccount) {
    Write-Host "   Iniciando sesion..." -ForegroundColor Cyan
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ERROR: Login fallido" -ForegroundColor Red
        pause
        exit 1
    }
}
Write-Host "   OK - Sesion activa: $currentAccount" -ForegroundColor Green
Write-Host ""

# 3. Configurar proyecto
Write-Host "3. Configurando proyecto..." -ForegroundColor Yellow
gcloud config set project $projectId 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK - Proyecto: $projectId" -ForegroundColor Green
} else {
    Write-Host "   ERROR: No se pudo configurar el proyecto" -ForegroundColor Red
    Write-Host "   Verifica que tienes acceso a: $projectId" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host ""

# 4. Habilitar APIs
Write-Host "4. Habilitando APIs necesarias..." -ForegroundColor Yellow
$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "   Habilitando $api..." -ForegroundColor Cyan
    gcloud services enable $api --project=$projectId 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK - $api" -ForegroundColor Green
    } else {
        Write-Host "   YA HABILITADA - $api" -ForegroundColor Gray
    }
}
Write-Host ""

# 5. Verificar si Service Account ya existe
Write-Host "5. Configurando Service Account..." -ForegroundColor Yellow
$saExists = gcloud iam service-accounts list --filter="email:$saEmail" --format="value(email)" 2>$null

if ($saExists) {
    Write-Host "   Service Account ya existe: $saEmail" -ForegroundColor Gray
} else {
    Write-Host "   Creando Service Account..." -ForegroundColor Cyan
    gcloud iam service-accounts create $saName `
        --display-name="GitHub Actions SIBIA Deploy" `
        --description="Service Account para deploy automatico desde GitHub" `
        --project=$projectId 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK - Service Account creado" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: No se pudo crear Service Account" -ForegroundColor Red
        pause
        exit 1
    }
}

# 6. Asignar roles
Write-Host "   Asignando roles..." -ForegroundColor Cyan
$roles = @(
    "roles/run.admin",
    "roles/storage.admin",
    "roles/iam.serviceAccountUser"
)

foreach ($role in $roles) {
    gcloud projects add-iam-policy-binding $projectId `
        --member="serviceAccount:$saEmail" `
        --role=$role `
        --quiet 2>$null
}
Write-Host "   OK - Roles asignados" -ForegroundColor Green
Write-Host ""

# 7. Crear key JSON
Write-Host "6. Generando credenciales..." -ForegroundColor Yellow
if (Test-Path $keyFile) {
    $overwrite = Read-Host "   $keyFile ya existe. Sobreescribir? (s/n)"
    if ($overwrite -ne 's') {
        Write-Host "   Usando key existente" -ForegroundColor Gray
    } else {
        Remove-Item $keyFile -Force
        gcloud iam service-accounts keys create $keyFile `
            --iam-account=$saEmail `
            --project=$projectId 2>$null
        Write-Host "   OK - Nueva key generada" -ForegroundColor Green
    }
} else {
    gcloud iam service-accounts keys create $keyFile `
        --iam-account=$saEmail `
        --project=$projectId 2>$null
    Write-Host "   OK - Key generada: $keyFile" -ForegroundColor Green
}
Write-Host ""

# 8. Instrucciones finales
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   CONFIGURAR GITHUB SECRET" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Abrir GitHub:" -ForegroundColor Yellow
Write-Host "   https://github.com/Seba-cuenca/SIBIA2025/settings/secrets/actions" -ForegroundColor White
Write-Host ""
Write-Host "2. Click: New repository secret" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Agregar secret:" -ForegroundColor Yellow
Write-Host "   Name: GCP_SA_KEY" -ForegroundColor Cyan
Write-Host "   Value: [Contenido completo de $keyFile]" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Para copiar el archivo:" -ForegroundColor Yellow
Write-Host "   notepad $keyFile" -ForegroundColor White
Write-Host "   (Copiar TODO, desde { hasta })" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   PROXIMO PASO: DEPLOY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Una vez configurado el secret en GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'Deploy automatico configurado'" -ForegroundColor White
Write-Host "  git push origin SIBIA_GITHUB" -ForegroundColor White
Write-Host ""
Write-Host "El deploy se ejecutara automaticamente!" -ForegroundColor Green
Write-Host "Ver progreso en: https://github.com/Seba-cuenca/SIBIA2025/actions" -ForegroundColor Cyan
Write-Host ""

# Abrir automáticamente el archivo de key
$openKey = Read-Host "Abrir $keyFile ahora para copiar? (s/n)"
if ($openKey -eq 's') {
    notepad $keyFile
}

Write-Host ""
Write-Host "IMPORTANTE: NO subir $keyFile a GitHub!" -ForegroundColor Red
Write-Host "(Ya esta en .gitignore)" -ForegroundColor Gray
Write-Host ""
Write-Host "Configuracion completada!" -ForegroundColor Green
Write-Host ""
