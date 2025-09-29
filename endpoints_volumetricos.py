
# ===== ENDPOINTS PARA BALANCE VOLUMÉTRICO =====
# Agregar al final de app_CORREGIDO_OK_FINAL.py

try:
    import balance_volumetrico_sibia as bv
    
    @app.route('/balance_volumetrico_biodigestor_1')
    def balance_volumetrico_biodigestor_1():
        """Endpoint para balance volumétrico del biodigestor 1"""
        try:
            balance = bv.endpoint_balance_biodigestor_1()
            return jsonify(balance)
        except Exception as e:
            return jsonify({
                'error': True,
                'mensaje': f'Error obteniendo balance biodigestor 1: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.route('/balance_volumetrico_biodigestor_2')
    def balance_volumetrico_biodigestor_2():
        """Endpoint para balance volumétrico del biodigestor 2"""
        try:
            balance = bv.endpoint_balance_biodigestor_2()
            return jsonify(balance)
        except Exception as e:
            return jsonify({
                'error': True,
                'mensaje': f'Error obteniendo balance biodigestor 2: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.route('/balance_volumetrico_completo')
    def balance_volumetrico_completo():
        """Endpoint para balance volumétrico completo de la planta"""
        try:
            balance = bv.endpoint_balance_completo_planta()
            return jsonify(balance)
        except Exception as e:
            return jsonify({
                'error': True,
                'mensaje': f'Error obteniendo balance completo: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    print("✅ Endpoints de balance volumétrico registrados:")
    print("  - /balance_volumetrico_biodigestor_1")
    print("  - /balance_volumetrico_biodigestor_2") 
    print("  - /balance_volumetrico_completo")
    
except ImportError as e:
    print(f"⚠️ No se pudo cargar módulo de balance volumétrico: {e}")
except Exception as e:
    print(f"❌ Error registrando endpoints volumétricos: {e}")
