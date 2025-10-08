# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import json
import re
import subprocess
from datetime import datetime
from typing import Dict, Any

import pandas as pd
from flask import Blueprint, request, jsonify

bp_planta = Blueprint('bp_planta', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ALIM_FILE_JSON = os.path.join(DATA_DIR, 'alimentacion_horaria.json')
SEGUIMIENTO_FILE = os.path.join(BASE_DIR, 'seguimiento_horario.json')


def _ok_path(p: str) -> bool:
    try:
        return bool(p) and os.path.exists(p)
    except Exception:
        return False


@bp_planta.route('/upload_excel_planta', methods=['POST'])
def upload_excel_planta():
    """Sube o ingesta un Excel y actualiza históricos en data/*. Solo histórico (no afecta operación)."""
    try:
        excel_path = None
        dump_name = None
        dump_dir = os.path.join(DATA_DIR, 'excel_dump')
        os.makedirs(dump_dir, exist_ok=True)

        if 'file' in request.files and request.files['file']:
            up = request.files['file']
            dump_name = up.filename or f"planta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_path = os.path.join(dump_dir, dump_name)
            up.save(excel_path)
        else:
            payload = request.get_json(silent=True) or {}
            excel_path = payload.get('path')

        if not _ok_path(excel_path):
            return jsonify({'status': 'error', 'mensaje': f'Archivo no encontrado: {excel_path}'}), 400

        # Ejecutar el script de ingesta existente
        script_path = os.path.join(BASE_DIR, 'ingestar_excel_planta.py')
        if not os.path.exists(script_path):
            return jsonify({'status': 'error', 'mensaje': 'Script de ingesta no encontrado'}), 500

        proc = subprocess.run([
            'python', script_path, '--path', excel_path
        ], cwd=BASE_DIR, capture_output=True, text=True)

        if proc.returncode != 0:
            return jsonify({'status': 'error', 'mensaje': proc.stderr or proc.stdout}), 500

        try:
            result_json = json.loads(proc.stdout)
        except Exception:
            result_json = {'raw': proc.stdout}

        return jsonify({'status': 'success', 'ingesta': result_json})
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@bp_planta.route('/datos_planta/resumen', methods=['GET'])
def datos_planta_resumen():
    """Resumen rápido a partir de históricos (no toca la operación)."""
    try:
        hist_path = os.path.join(DATA_DIR, 'historico_planta.json')
        if not os.path.exists(hist_path):
            return jsonify({'status': 'sin_datos'})
        df = pd.read_json(hist_path)
        # Normalizar fecha
        if 'fecha_hora' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha_hora']).dt.date
        elif 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        else:
            df['fecha'] = pd.NaT

        # KPIs por día (último día disponible)
        if df['fecha'].notna().any():
            last_day = sorted([d for d in df['fecha'] if pd.notna(d)])[-1]
            dfd = df[df['fecha'] == last_day]
        else:
            dfd = df

        def mean(col):
            return float(dfd[col].dropna().mean()) if col in dfd.columns else None

        resumen = {
            'fecha': str(dfd['fecha'].iloc[0]) if len(dfd) else None,
            'ch4_bio040_pct_avg': mean('ch4_bio040_pct'),
            'ch4_bio050_pct_avg': mean('ch4_bio050_pct'),
            'ch4_motor_pct_avg': mean('ch4_motor_pct'),
            'h2s_motor_ppm_avg': mean('h2s_motor_ppm'),
            'caudal_chp_ls_avg': mean('caudal_chp_ls'),
            'despacho_total_kwh_d': mean('despacho_total_kwh_d'),
            'despacho_spot_smec_kwh_d': mean('despacho_spot_smec_kwh_d'),
            'purin_tn': mean('purin_tn'),
            'grasa_tn': mean('grasa_tn'),
            'grano_descarte_me_tn': mean('grano_descarte_me_tn'),
            'contenido_ruminal_tn': mean('contenido_ruminal_tn'),
            'polvillo_maiz_tn': mean('polvillo_maiz_tn'),
            'expeller_tn': mean('expeller_tn'),
        }
        return jsonify({'status': 'success', 'resumen': resumen})
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@bp_planta.route('/datos_planta/features_preview', methods=['GET'])
def datos_planta_features_preview():
    """Features ML básicas desde historico_planta.json (no toca operación)."""
    try:
        hist_path = os.path.join(DATA_DIR, 'historico_planta.json')
        if not os.path.exists(hist_path):
            return jsonify({'status': 'sin_datos'})
        df = pd.read_json(hist_path)
        if 'fecha_hora' in df.columns:
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
            df = df.sort_values('fecha_hora')
            df = df.set_index('fecha_hora')
        elif 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha').set_index('fecha')
        else:
            return jsonify({'status': 'error', 'mensaje': 'No hay columna temporal'}), 400

        cols = [c for c in df.columns if any(k in c for k in ['ch4', 'h2s', 'o2', 'co2', 'caudal_chp_ls', 'despacho_total_kwh_d'])]
        dfn = df[cols].apply(pd.to_numeric, errors='coerce')
        feats = {}
        for c in cols:
            s = dfn[c]
            feats[c] = {
                'mean_24h': float(s.rolling('24H').mean().dropna().iloc[-1]) if len(s.dropna()) else None,
                'std_24h': float(s.rolling('24H').std().dropna().iloc[-1]) if len(s.dropna()) else None,
                'last': float(s.dropna().iloc[-1]) if len(s.dropna()) else None,
            }
        return jsonify({'status': 'success', 'features': feats})
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@bp_planta.route('/ingesta/alimentacion_20/sincronizar', methods=['POST'])
def sincronizar_alimentacion_20():
    """Vuelca data/alimentacion_horaria.json a seguimiento_horario.json (solo si existe)."""
    try:
        if not os.path.exists(ALIM_FILE_JSON):
            return jsonify({'status': 'sin_datos', 'mensaje': 'alimentacion_horaria.json no existe'}), 404
        with open(ALIM_FILE_JSON, 'r', encoding='utf-8') as f:
            alim = json.load(f)
        if not isinstance(alim, list):
            return jsonify({'status': 'error', 'mensaje': 'Formato inesperado en alimentacion_horaria.json'}), 400
        # Cargar seguimiento
        seg = {'fecha': datetime.now().strftime('%Y-%m-%d'), 'hora_actual': datetime.now().hour, 'biodigestores': {}}
        if os.path.exists(SEGUIMIENTO_FILE):
            try:
                with open(SEGUIMIENTO_FILE, 'r', encoding='utf-8') as f:
                    seg = json.load(f)
            except Exception:
                pass
        # Estructura esperada
        seg.setdefault('biodigestores', {})
        bio1 = seg['biodigestores'].setdefault('1', {'plan_24_horas': {}, 'progreso_diario': {}})
        plan = bio1.setdefault('plan_24_horas', {})
        # Mapear por hora
        for row in alim:
            try:
                ts = pd.to_datetime(row.get('fecha_hora'))
                h = int(ts.hour)
                sol = float(row.get('solidos_real_tn') or 0)
                liq = float(row.get('liquidos_real_tn') or 0)
            except Exception:
                continue
            plan[str(h)] = plan.get(str(h), {
                'objetivo_ajustado': {'total_solidos': 0, 'total_liquidos': 0},
                'real': {'total_solidos': 0, 'total_liquidos': 0}
            })
            plan[str(h)]['real']['total_solidos'] = sol
            plan[str(h)]['real']['total_liquidos'] = liq
        # Guardar
        with open(SEGUIMIENTO_FILE, 'w', encoding='utf-8') as f:
            json.dump(seg, f, indent=4, ensure_ascii=False)
        return jsonify({'status': 'success', 'mensaje': 'Sincronizado con seguimiento_horario.json'})
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500
