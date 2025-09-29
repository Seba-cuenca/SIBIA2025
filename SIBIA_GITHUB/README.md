# SIBIA - Sistema Inteligente de Biodigestores Industriales Avanzados

## 🏢 AutoLinkSolutions SRL
**Copyright © 2025 AutoLinkSolutions SRL. Todos los derechos reservados.**

## 🚀 Descripción
SIBIA es un sistema completo de monitoreo y control de biodigestores industriales con inteligencia artificial, análisis predictivo y gestión automatizada.

## ✨ Características Principales
- 🤖 **Asistente IA** con síntesis de voz gratuita
- 📊 **Dashboard** interactivo de biodigestores
- 🧮 **Calculadora** de parámetros de biodigestores
- 📈 **Análisis predictivo** con Machine Learning
- 🔧 **Mantenimiento predictivo**
- 📱 **Interfaz responsive** y PWA
- 🎵 **Sistema de voz gratuito** sin límites

## 🛠️ Tecnologías
- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **IA:** XGBoost, Redes Neuronales, Algoritmos Genéticos
- **Voz:** Parler-TTS + Edge-TTS (Gratuito)
- **Base de Datos:** MySQL, SQLAlchemy
- **Despliegue:** Railway, GitHub Actions

## 🚀 Despliegue Automático
Este proyecto está configurado para despliegue automático en Railway:
- Cada push a `main` activa el despliegue
- CI/CD configurado con GitHub Actions
- Health check en `/health`

## 📋 Instalación Local
```bash
pip install -r requirements.txt
python app_CORREGIDO_OK_FINAL.py
```

## 🔧 Variables de Entorno
- `FLASK_ENV=production`
- `DEBUG=false`
- `SECRET_KEY=sibia-autolinksolutions-2025-secure-key`
- `HUGGINGFACE_API_KEY=opcional` (para Parler-TTS)
- `RAILWAY_TOKEN=opcional` (para deploy automático)

## 📞 Soporte
**AutoLinkSolutions SRL**
- Email: info@autolinksolutions.com
- Web: www.autolinksolutions.com

## 📄 Licencia
Copyright © 2025 AutoLinkSolutions SRL. Todos los derechos reservados.
