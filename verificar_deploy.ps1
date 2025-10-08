# Script para verificar que todo esté listo para deploy

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   VERIFICACION PRE-DEPLOY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# 1. Verificar archivos necesarios
Write-Host "1. Verificando archivos necesarios..." -ForegroundColor Yellow
$archivos = @(
    "Dockerfile",
    ".dockerignore",
    "requirements.txt",
    ".github/workflows/deploy-gcloud.yml",
    "cloudbuild.yaml"
)

foreach ($archivo in $archivos) {
    if (Test-Path $archivo) {
        Write-Host "   OK - $archivo" -ForegroundColor Green
    } else {
        Write-Host "   FALTA - $archivo" -ForegroundColor Red
        $allGood = $false
    }
}
Write-Host ""

# 2. Verificar Git
Write-Host "2. Verificando Git..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if ($gitInstalled) {
    Write-Host "   OK - Git instalado" -ForegroundColor Green
    $gitRemote = git remote -v 2>$null
    if ($gitRemote -match "github") {
        Write-Host "   OK - Conectado a GitHub" -ForegroundColor Green
    } else {
        Write-Host "   ADVERTENCIA - No conectado a GitHub" -ForegroundColor Yellow
        Write-Host "   Ejecutar: git remote add origin https://github.com/TU-USUARIO/TU-REPO.git" -ForegroundColor Gray
        $allGood = $false
    }
} else {
    Write-Host "   ERROR - Git no instalado" -ForegroundColor Red
    $allGood = $false
}
Write-Host ""

# 3. Verificar Google Cloud SDK
Write-Host "3. Verificando Google Cloud SDK..." -ForegroundColor Yellow
$gcloudInstalled = Get-Command gcloud -ErrorAction SilentlyContinue
if ($gcloudInstalled) {
    Write-Host "   OK - Google Cloud SDK instalado" -ForegroundColor Green
    $project = gcloud config get-value project 2>$null
    if ($project) {
        Write-Host "   OK - Proyecto configurado: $project" -ForegroundColor Green
    } else {
        Write-Host "   ADVERTENCIA - Sin proyecto configurado" -ForegroundColor Yellow
        Write-Host "   Ejecutar: .\setup_gcloud.ps1" -ForegroundColor Gray
        $allGood = $false
    }
} else {
    Write-Host "   ERROR - Google Cloud SDK no instalado" -ForegroundColor Red
    Write-Host "   Descargar: https://cloud.google.com/sdk/docs/install" -ForegroundColor Gray
    $allGood = $false
}
Write-Host ""

# 4. Verificar requirements.txt
Write-Host "4. Verificando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $content = Get-Content "requirements.txt" -Raw
    $deps = @("flask", "pandas", "scikit-learn", "apscheduler", "gunicorn")
    foreach ($dep in $deps) {
        if ($content -match $dep) {
            Write-Host "   OK - $dep" -ForegroundColor Green
        } else {
            Write-Host "   FALTA - $dep" -ForegroundColor Red
            $allGood = $false
        }
    }
} else {
    Write-Host "   ERROR - requirements.txt no encontrado" -ForegroundColor Red
    $allGood = $false
}
Write-Host ""

# 5. Verificar .gitignore
Write-Host "5. Verificando .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $content = Get-Content ".gitignore" -Raw
    if ($content -match "gcloud-key.json") {
        Write-Host "   OK - gcloud-key.json en .gitignore" -ForegroundColor Green
    } else {
        Write-Host "   ADVERTENCIA - gcloud-key.json NO en .gitignore" -ForegroundColor Yellow
        Write-Host "   IMPORTANTE: Agregar para no subir credenciales" -ForegroundColor Red
    }
} else {
    Write-Host "   ADVERTENCIA - .gitignore no encontrado" -ForegroundColor Yellow
}
Write-Host ""

# Resultado final
Write-Host "============================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "   TODO LISTO PARA DEPLOY" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Ejecutar: .\setup_gcloud.ps1 (si no lo hiciste)" -ForegroundColor White
    Write-Host "  2. Configurar secrets en GitHub" -ForegroundColor White
    Write-Host "  3. git add ." -ForegroundColor White
    Write-Host "  4. git commit -m 'Deploy automatico'" -ForegroundColor White
    Write-Host "  5. git push" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "   FALTAN PASOS" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Revisar errores arriba y corregir" -ForegroundColor Yellow
    Write-Host ""
}
