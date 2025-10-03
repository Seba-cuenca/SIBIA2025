from flask import Flask, render_template, request, jsonify
import pandas as pd
import random

app = Flask(__name__)

# Configuración del motor Jenbacher J420
MOTOR_CONFIG = {
    'potencia_kw': 1239,
    'consumo_l_s': 170,
}

def cargar_materiales_excel(archivo_excel='DIETA_SEBA.xlsx'):
    """Carga los materiales desde el Excel"""
    try:
        df = pd.read_excel(archivo_excel, sheet_name='SEBA')
        df = df[df['Tipo'].notna()]
        df = df[df['m3/TnSV'].notna()]
        
        materiales = []
        for idx, row in df.iterrows():
            nombre = str(row['Tipo']).lower()
            
            # Clasificar automáticamente
            tipo = 'solido'
            if 'purin' in nombre or 'purín' in nombre:
                tipo = 'purin'
            elif any(x in nombre for x in ['lactosa', 'suero', 'gomas', 'grasa']):
                tipo = 'liquido'
            
            material = {
                'id': idx,
                'nombre': str(row['Tipo']),
                'tipo': tipo,
                'st_pct': float(row['ST %']) if pd.notna(row['ST %']) else 0,
                'sv_pct': float(row['SV %']) if pd.notna(row['SV %']) else 0,
                'svt_pct': float(row['SVT %']) if pd.notna(row['SVT %']) else 0,
                'carbohidratos': float(row['Carbohidratos %']) if pd.notna(row['Carbohidratos %']) else 0,
                'lipidos': float(row['Lipidos %']) if pd.notna(row['Lipidos %']) else 0,
                'proteinas': float(row['Proteinas %']) if pd.notna(row['Proteinas %']) else 0,
                'm3_biogas_por_tn': float(row['m3/TnSV']),
                'stock_disponible': float(row['Tn SV']) if pd.notna(row['Tn SV']) else 0,
                'densidad': float(row['Densidad (kg/L)']) if 'Densidad (kg/L)' in row and pd.notna(row['Densidad (kg/L)']) else 1.0,
            }
            materiales.append(material)
        
        return materiales
    except Exception as e:
        print(f"Error cargando Excel: {e}")
        return []

def calcular_generacion_electrica(m3_biogas_por_tn, consumo_motor_l_s, 
                                   potencia_motor_kw, porcentaje_ch4=60):
    """Calcula kWh generados por tonelada"""
    consumo_m3_h = (consumo_motor_l_s / 1000) * 3600
    horas_operacion = m3_biogas_por_tn / consumo_m3_h if consumo_m3_h > 0 else 0
    kwh_generados = potencia_motor_kw * horas_operacion
    m3_ch4_por_tn = m3_biogas_por_tn * (porcentaje_ch4 / 100)
    
    return {
        'm3_biogas_por_tn': m3_biogas_por_tn,
        'm3_ch4_por_tn': round(m3_ch4_por_tn, 2),
        'horas_operacion': round(horas_operacion, 3),
        'kwh_generados': round(kwh_generados, 2),
    }

def calcular_toneladas_purin(m3_purin, densidad_purin=1.05):
    """Convierte m³ de purín a toneladas"""
    return m3_purin * densidad_purin

def generar_receta_con_purin(kwh_objetivo, porcentaje_ch4, m3_purin, 
                             materiales_disponibles, consumo_motor, potencia_motor,
                             modo='energetico', pct_solidos_kw=60, pct_liquidos_kw=40, 
                             pct_purin_kw=0, incluir_purin=True, num_materiales=5):
    """
    Genera receta considerando m³ de purín recibido
    """
    
    # 1. Calcular toneladas de purín disponible
    purin_materiales = [m for m in materiales_disponibles if m['tipo'] == 'purin']
    tn_purin = 0
    kwh_purin = 0
    m3_biogas_purin = 0
    m3_ch4_purin = 0
    
    if incluir_purin and m3_purin > 0 and purin_materiales:
        # Usar el primer material de tipo purín encontrado
        mat_purin = purin_materiales[0]
        tn_purin = calcular_toneladas_purin(m3_purin, mat_purin['densidad'])
        
        calc_purin = calcular_generacion_electrica(
            mat_purin['m3_biogas_por_tn'],
            consumo_motor,
            potencia_motor,
            porcentaje_ch4
        )
        
        kwh_purin = tn_purin * calc_purin['kwh_generados']
        m3_biogas_purin = tn_purin * mat_purin['m3_biogas_por_tn']
        m3_ch4_purin = tn_purin * calc_purin['m3_ch4_por_tn']
    
    # 2. Calcular kWh restantes para otros materiales
    kwh_restante = kwh_objetivo - kwh_purin
    
    if kwh_restante < 0:
        kwh_restante = 0
    
    # 3. Separar materiales por tipo (excluyendo purín)
    solidos = [m for m in materiales_disponibles if m['tipo'] == 'solido' and m['stock_disponible'] > 0]
    liquidos = [m for m in materiales_disponibles if m['tipo'] == 'liquido' and m['stock_disponible'] > 0]
    
    # 4. Calcular kWh por tonelada para cada material
    for mat in solidos + liquidos:
        calc = calcular_generacion_electrica(
            mat['m3_biogas_por_tn'],
            consumo_motor,
            potencia_motor,
            porcentaje_ch4
        )
        mat['kwh_por_tn'] = calc['kwh_generados']
        mat['m3_ch4_por_tn'] = calc['m3_ch4_por_tn']
    
    # 5. Ordenar por rendimiento
    solidos.sort(key=lambda x: x['kwh_por_tn'], reverse=True)
    liquidos.sort(key=lambda x: x['kwh_por_tn'], reverse=True)
    
    # 6. Seleccionar materiales según el número solicitado y modo
    receta = []
    
    if modo == 'energetico':
        # Modo energético: seleccionar los mejores sin restricción de tipo
        todos_materiales = solidos + liquidos
        todos_materiales.sort(key=lambda x: x['kwh_por_tn'], reverse=True)
        
        # Tomar los N mejores materiales
        materiales_seleccionados = todos_materiales[:num_materiales]
        
        kwh_acumulado = 0
        for mat in materiales_seleccionados:
            if kwh_acumulado >= kwh_restante:
                break
            
            kwh_faltante = kwh_restante - kwh_acumulado
            toneladas_necesarias = kwh_faltante / mat['kwh_por_tn']
            toneladas_usar = min(toneladas_necesarias, mat['stock_disponible'])
            
            if toneladas_usar > 0.01:
                kwh_generado = toneladas_usar * mat['kwh_por_tn']
                receta.append({
                    'material': mat['nombre'],
                    'tipo': mat['tipo'],
                    'toneladas': round(toneladas_usar, 2),
                    'stock_disponible': mat['stock_disponible'],
                    'kwh_por_tn': mat['kwh_por_tn'],
                    'kwh_total': round(kwh_generado, 2),
                    'm3_biogas': round(toneladas_usar * mat['m3_biogas_por_tn'], 2),
                    'm3_ch4': round(toneladas_usar * mat['m3_ch4_por_tn'], 2),
                    # Datos de laboratorio
                    'st_pct': mat['st_pct'],
                    'sv_pct': mat['sv_pct'],
                    'svt_pct': mat['svt_pct'],
                    'carbohidratos': mat['carbohidratos'],
                    'lipidos': mat['lipidos'],
                    'proteinas': mat['proteinas'],
                    'densidad': mat['densidad']
                })
                kwh_acumulado += kwh_generado
    
    else:  # modo volumétrico
        # Distribuir kWh según porcentajes definidos
        kwh_para_solidos = kwh_restante * (pct_solidos_kw / 100)
        kwh_para_liquidos = kwh_restante * (pct_liquidos_kw / 100)
        
        # Seleccionar materiales sólidos
        num_solidos = max(1, num_materiales // 2)
        materiales_solidos_sel = solidos[:num_solidos]
        
        kwh_acumulado_solidos = 0
        for mat in materiales_solidos_sel:
            if kwh_acumulado_solidos >= kwh_para_solidos:
                break
            
            kwh_faltante = kwh_para_solidos - kwh_acumulado_solidos
            toneladas_necesarias = kwh_faltante / mat['kwh_por_tn']
            toneladas_usar = min(toneladas_necesarias, mat['stock_disponible'])
            
            if toneladas_usar > 0.01:
                kwh_generado = toneladas_usar * mat['kwh_por_tn']
                receta.append({
                    'material': mat['nombre'],
                    'tipo': mat['tipo'],
                    'toneladas': round(toneladas_usar, 2),
                    'stock_disponible': mat['stock_disponible'],
                    'kwh_por_tn': mat['kwh_por_tn'],
                    'kwh_total': round(kwh_generado, 2),
                    'm3_biogas': round(toneladas_usar * mat['m3_biogas_por_tn'], 2),
                    'm3_ch4': round(toneladas_usar * mat['m3_ch4_por_tn'], 2),
                    'st_pct': mat['st_pct'],
                    'sv_pct': mat['sv_pct'],
                    'svt_pct': mat['svt_pct'],
                    'carbohidratos': mat['carbohidratos'],
                    'lipidos': mat['lipidos'],
                    'proteinas': mat['proteinas'],
                    'densidad': mat['densidad']
                })
                kwh_acumulado_solidos += kwh_generado
        
        # Seleccionar materiales líquidos
        num_liquidos = num_materiales - len(receta)
        materiales_liquidos_sel = liquidos[:num_liquidos]
        
        kwh_acumulado_liquidos = 0
        for mat in materiales_liquidos_sel:
            if kwh_acumulado_liquidos >= kwh_para_liquidos:
                break
            
            kwh_faltante = kwh_para_liquidos - kwh_acumulado_liquidos
            toneladas_necesarias = kwh_faltante / mat['kwh_por_tn']
            toneladas_usar = min(toneladas_necesarias, mat['stock_disponible'])
            
            if toneladas_usar > 0.01:
                kwh_generado = toneladas_usar * mat['kwh_por_tn']
                receta.append({
                    'material': mat['nombre'],
                    'tipo': mat['tipo'],
                    'toneladas': round(toneladas_usar, 2),
                    'stock_disponible': mat['stock_disponible'],
                    'kwh_por_tn': mat['kwh_por_tn'],
                    'kwh_total': round(kwh_generado, 2),
                    'm3_biogas': round(toneladas_usar * mat['m3_biogas_por_tn'], 2),
                    'm3_ch4': round(toneladas_usar * mat['m3_ch4_por_tn'], 2),
                    'st_pct': mat['st_pct'],
                    'sv_pct': mat['sv_pct'],
                    'svt_pct': mat['svt_pct'],
                    'carbohidratos': mat['carbohidratos'],
                    'lipidos': mat['lipidos'],
                    'proteinas': mat['proteinas'],
                    'densidad': mat['densidad']
                })
                kwh_acumulado_liquidos += kwh_generado
    
    # 7. Agregar purín a la receta si se usa
    if incluir_purin and tn_purin > 0:
        mat_purin = purin_materiales[0]
        receta.insert(0, {
            'material': mat_purin['nombre'],
            'tipo': 'purin',
            'toneladas': round(tn_purin, 2),
            'stock_disponible': m3_purin,
            'kwh_por_tn': calc_purin['kwh_generados'],
            'kwh_total': round(kwh_purin, 2),
            'm3_biogas': round(m3_biogas_purin, 2),
            'm3_ch4': round(m3_ch4_purin, 2),
            'm3_purin': m3_purin,
            'st_pct': mat_purin['st_pct'],
            'sv_pct': mat_purin['sv_pct'],
            'svt_pct': mat_purin['svt_pct'],
            'carbohidratos': mat_purin['carbohidratos'],
            'lipidos': mat_purin['lipidos'],
            'proteinas': mat_purin['proteinas'],
            'densidad': mat_purin['densidad']
        })
    
    # 8. Construir resumen
    return construir_resumen(receta, kwh_objetivo, porcentaje_ch4, consumo_motor, 
                            potencia_motor, modo, m3_purin, incluir_purin)

def construir_resumen(receta, kwh_objetivo, porcentaje_ch4, consumo_motor, 
                     potencia_motor, modo, m3_purin=0, incluir_purin=False):
    """Construye el resumen de resultados"""
    total_toneladas = sum(r['toneladas'] for r in receta)
    total_biogas = sum(r['m3_biogas'] for r in receta)
    total_ch4 = sum(r['m3_ch4'] for r in receta)
    total_kwh = sum(r['kwh_total'] for r in receta)
    
    consumo_m3_h = (consumo_motor / 1000) * 3600
    horas_operacion = total_biogas / consumo_m3_h if consumo_m3_h > 0 else 0
    
    # Calcular porcentajes en la mezcla
    tn_solidos = sum(r['toneladas'] for r in receta if r['tipo'] == 'solido')
    tn_liquidos = sum(r['toneladas'] for r in receta if r['tipo'] == 'liquido')
    tn_purin = sum(r['toneladas'] for r in receta if r['tipo'] == 'purin')
    
    for r in receta:
        r['porcentaje_mezcla'] = round((r['toneladas'] / total_toneladas) * 100, 1) if total_toneladas > 0 else 0
    
    return {
        'receta': receta,
        'resumen': {
            'modo': modo,
            'kwh_objetivo': kwh_objetivo,
            'kwh_generado': round(total_kwh, 2),
            'cumplimiento': round((total_kwh / kwh_objetivo) * 100, 1) if kwh_objetivo > 0 else 0,
            'total_toneladas': round(total_toneladas, 2),
            'total_biogas_m3': round(total_biogas, 2),
            'total_ch4_m3': round(total_ch4, 2),
            'horas_operacion': round(horas_operacion, 2),
            'dias_operacion': round(horas_operacion / 24, 2),
            'potencia_motor': potencia_motor,
            'porcentaje_ch4': porcentaje_ch4,
            'm3_purin': m3_purin,
            'incluir_purin': incluir_purin,
            'proporciones': {
                'toneladas_solidos': round(tn_solidos, 2),
                'toneladas_liquidos': round(tn_liquidos, 2),
                'toneladas_purin': round(tn_purin, 2),
                'porcentaje_solidos': round((tn_solidos / total_toneladas * 100) if total_toneladas > 0 else 0, 1),
                'porcentaje_liquidos': round((tn_liquidos / total_toneladas * 100) if total_toneladas > 0 else 0, 1),
                'porcentaje_purin': round((tn_purin / total_toneladas * 100) if total_toneladas > 0 else 0, 1)
            }
        }
    }

# RUTAS

@app.route('/')
def index():
    materiales = cargar_materiales_excel()
    return render_template('calculadora.html', materiales=materiales, motor_config=MOTOR_CONFIG)

@app.route('/materiales')
def obtener_materiales():
    materiales = cargar_materiales_excel()
    return jsonify(materiales)

@app.route('/calcular_mezcla', methods=['POST'])
def calcular_mezcla():
    """Calcula la mezcla según parámetros del usuario"""
    data = request.get_json()
    
    kwh_objetivo = float(data.get('kwh_objetivo'))
    porcentaje_ch4 = float(data.get('porcentaje_ch4', 65))
    m3_purin = float(data.get('m3_purin', 0))
    modo = data.get('modo', 'energetico')
    pct_solidos_kw = float(data.get('pct_solidos_kw', 60))
    pct_liquidos_kw = float(data.get('pct_liquidos_kw', 40))
    pct_purin_kw = float(data.get('pct_purin_kw', 0))
    incluir_purin = data.get('incluir_purin', True)
    num_materiales = int(data.get('num_materiales', 5))
    consumo = float(data.get('consumo_motor', MOTOR_CONFIG['consumo_l_s']))
    potencia = float(data.get('potencia_motor', MOTOR_CONFIG['potencia_kw']))
    
    materiales = cargar_materiales_excel()
    
    resultado = generar_receta_con_purin(
        kwh_objetivo, porcentaje_ch4, m3_purin, materiales,
        consumo, potencia, modo, pct_solidos_kw, pct_liquidos_kw,
        pct_purin_kw, incluir_purin, num_materiales
    )
    
    return jsonify(resultado)

@app.route('/sugerir_materiales', methods=['POST'])
def sugerir_materiales():
    """Sugiere los mejores materiales disponibles"""
    data = request.get_json()
    num_materiales = int(data.get('num_materiales', 5))
    porcentaje_ch4 = float(data.get('porcentaje_ch4', 65))
    
    materiales = cargar_materiales_excel()
    
    # Calcular rendimiento de cada material
    for mat in materiales:
        if mat['stock_disponible'] > 0:
            calc = calcular_generacion_electrica(
                mat['m3_biogas_por_tn'],
                MOTOR_CONFIG['consumo_l_s'],
                MOTOR_CONFIG['potencia_kw'],
                porcentaje_ch4
            )
            mat['kwh_por_tn'] = calc['kwh_generados']
        else:
            mat['kwh_por_tn'] = 0
    
    # Ordenar por rendimiento
    materiales.sort(key=lambda x: x['kwh_por_tn'], reverse=True)
    
    # Tomar los mejores N
    sugeridos = materiales[:num_materiales]
    
    return jsonify({
        'materiales_sugeridos': [
            {
                'nombre': m['nombre'],
                'tipo': m['tipo'],
                'kwh_por_tn': round(m['kwh_por_tn'], 2),
                'm3_biogas_por_tn': m['m3_biogas_por_tn'],
                'stock_disponible': m['stock_disponible']
            }
            for m in sugeridos
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
