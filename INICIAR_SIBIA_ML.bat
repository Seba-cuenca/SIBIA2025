@echo off
REM ============================================================================
REM SCRIPT DE INICIO AUTOMATICO SIBIA CON ML
REM ============================================================================
REM Este script inicia SIBIA con aprendizaje continuo automaticamente
REM Doble clic para iniciar
REM ============================================================================

title SIBIA - Sistema Inteligente con ML

echo.
echo ============================================================================
echo    SIBIA - Sistema Inteligente de Biogas Avanzado
echo    Con Aprendizaje Continuo ML
echo    (C) 2025 AutoLinkSolutions SRL
echo ============================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

echo Iniciando sistema...
echo.

REM Ejecutar script de inicio
python iniciar_sibia_ml.py

if errorlevel 1 (
    echo.
    echo ERROR al iniciar SIBIA
    pause
    exit /b 1
)

echo.
echo Sistema detenido correctamente
pause
