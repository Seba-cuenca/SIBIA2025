#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIBIA - Versión Railway Optimizada
Copyright © 2025 AutoLinkSolutions SRL
"""

import os
from flask import Flask, jsonify, render_template

# Crear aplicación Flask
app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sibia-autolinksolutions-2025-secure-key')

@app.route('/')
def index():
    """Página principal"""
    try:
        return render_template('dashboard_hibrido.html')
    except:
        return jsonify({
            'message': 'SIBIA funcionando - Dashboard no disponible',
            'status': 'ok',
            'company': 'AutoLinkSolutions SRL'
        })

@app.route('/salud')
def salud():
    """Health check para Railway"""
    return jsonify({
        'status': 'ok',
        'message': 'SIBIA funcionando correctamente',
        'company': 'AutoLinkSolutions SRL',
        'copyright': '© 2025 AutoLinkSolutions SRL',
        'version': '2.0-railway'
    })

@app.route('/health')
def health():
    """Health check alternativo"""
    return jsonify({
        'status': 'ok',
        'message': 'SIBIA funcionando correctamente',
        'company': 'AutoLinkSolutions SRL',
        'copyright': '© 2025 AutoLinkSolutions SRL',
        'version': '2.0-railway'
    })

@app.route('/test')
def test():
    """Endpoint de prueba"""
    return jsonify({
        'message': 'SIBIA Railway funcionando',
        'status': 'success',
        'company': 'AutoLinkSolutions SRL',
        'timestamp': '2025-09-26'
    })

if __name__ == '__main__':
    # Configuración específica para Railway
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print("🚀 Iniciando SIBIA Railway...")
    print("© 2025 AutoLinkSolutions SRL")
    print(f"🌐 Servidor: {host}:{port}")
    print(f"🔧 Debug: {debug}")
    print("✅ Health checks configurados")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Revisa la configuración")
