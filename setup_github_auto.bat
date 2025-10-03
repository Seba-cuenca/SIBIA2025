@echo off
echo 🔧 Configurando Sincronizacion Automatica con GitHub...
echo.

cd SIBIA_GITHUB

echo 📁 Configurando repositorio Git...
git init
git remote add origin https://github.com/Seba-cuenca/SIBIA2025.git

echo 📝 Configurando credenciales...
git config --global user.name "Seba-cuenca"
git config --global user.email "seba-cuenca@example.com"
git config --global credential.helper store

echo ✅ Configuracion completada!
echo.
echo 🚀 Para iniciar la sincronizacion automatica:
echo    Ejecuta: start_auto_sync.bat
echo.
pause
