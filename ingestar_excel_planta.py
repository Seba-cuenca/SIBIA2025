#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Normaliza el Excel de planta a datasets internos.
Entrada: ruta a Excel (arg --path) o usa el archivo GVBIO_-_Registro_de_planta_3.xlsx del proyecto.
Salida:
- data/planta_excel_summary.json (resumen de hojas)
- data/historico_planta.parquet (.json)
- data/ingresos_camiones.parquet (.json)
- data/st_materiales.parquet (.json)
- data/alimentacion_horaria.parquet (.json)
- data/analisis_quimico_fos_tac.parquet (.json)
"""
import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

BASE = Path(r"c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS")
DEFAULT_XLS = BASE / 'GVBIO_-_Registro_de_planta_3.xlsx'
DATA_DIR = BASE / 'data'
DATA_DIR.mkdir(exist_ok=True)
DUMP_DIR = DATA_DIR / 'excel_dump'
DUMP_DIR.mkdir(exist_ok=True)

# Utilidades

def to_datetime_heur(x):
    try:
        return pd.to_datetime(x)
    except Exception:
        # intentos comunes dd/mm/yyyy hh:mm
        try:
            return pd.to_datetime(x, dayfirst=True, errors='coerce')
        except Exception:
            return pd.NaT

NUM_RE = re.compile(r"[-+]?\d*[\.,]?\d+")

def to_float_heur(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s == '':
        return None
    s = s.replace(' ', '').replace('%','')
    s = s.replace(',', '.')
    m = NUM_RE.search(s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None

# Resumen hojas

def summarize_sheet(xls: pd.ExcelFile, name: str) -> Dict[str, Any]:
    try:
        # Leer pocas filas y como texto para evitar parseos costosos
        df = xls.parse(name, nrows=80, dtype=str)
    except Exception as e:
        return {'sheet': name, 'error': str(e)}
    df.columns = [str(c).strip() for c in df.columns]
    # Si hay muchas columnas "ColumnaN", intentar leer con header=[0,1]
    if sum(1 for c in df.columns if 'Columna' in str(c)) > 5:
        try:
            df_multi = xls.parse(name, header=[0,1], nrows=80, dtype=str)
            df_multi.columns = ['_'.join(map(str, col)).strip('_') for col in df_multi.columns.values]
            df = df_multi
        except Exception:
            pass
    head = df.head(3).astype(str).to_dict(orient='list')
    nonnull = df.notna().sum().to_dict()
    dtypes = {c: str(t) for c, t in df.dtypes.items()}
    # Evitar volcado completo a CSV para acelerar
    return {'sheet': name, 'rows': int(df.shape[0]), 'cols': int(df.shape[1]), 'columns': list(df.columns), 'nonnull': nonnull, 'dtypes': dtypes, 'examples': head}

# Normalizadores por hoja

# Heurística: reparsear hoja detectando fila de encabezados cuando vienen muchas columnas 'Unnamed'
def _reparse_with_detected_header(xls: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    try:
        raw = xls.parse(sheet, header=None)
    except Exception:
        return xls.parse(sheet)
    # Buscar fila candidata que contenga palabras clave tipo 'Fecha' o 'Despacho total'
    header_idx = None
    keys = [r"fecha", r"despacho\s*total", r"generaci[oó]n", r"smec", r"chp", r"consumo"]
    for i in range(min(50, len(raw))):
        row_vals = ' '.join(str(v) for v in list(raw.iloc[i].values))
        import re as _re
        if any(_re.search(k, row_vals, _re.I) for k in keys):
            header_idx = i
            break
    if header_idx is None:
        return xls.parse(sheet)
    # Construir nombres de columnas desde esa fila (combinando arriba si hay multiheader)
    header = raw.iloc[header_idx].astype(str).str.strip().tolist()
    # Limpiar nombres vacíos
    cols = [c if c and c.lower() != 'nan' else f"col_{j}" for j, c in enumerate(header)]
    data = raw.iloc[header_idx+1:].copy()
    data.columns = cols
    return data

def norm_calidad_gas(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    # fecha
    cand = [c for c in df.columns if re.search(r"fecha", str(c), re.I)]
    if cand:
        out['fecha_hora'] = pd.to_datetime(df[cand[0]].apply(to_datetime_heur))
    else:
        out['fecha_hora'] = pd.NaT
    # Con multi-header, las columnas tienen formato: "Grupo_SubNombre"
    # Buscar por subcadenas en los nombres combinados
    def pick(pattern):
        for c in df.columns:
            if re.search(pattern, str(c), re.I):
                return c
        return None
    # CH4
    for tag, pat in [
        ('ch4_bio040_pct', r"(040|bio\s*1).*ch4|ch4.*(040|bio\s*1)"),
        ('ch4_bio050_pct', r"(050|bio\s*2).*ch4|ch4.*(050|bio\s*2)"),
        ('ch4_motor_pct', r"motor.*ch4|ch4.*motor|ingreso.*motor.*ch4")
    ]:
        c = pick(pat)
        if c: out[tag] = df[c].apply(to_float_heur)
    # CO2, O2, H2S
    for tag, pat in [
        ('co2_bio040_pct', r"(040|bio\s*1).*co2|co2.*(040|bio\s*1)"),
        ('co2_bio050_pct', r"(050|bio\s*2).*co2|co2.*(050|bio\s*2)"),
        ('co2_motor_pct', r"motor.*co2|co2.*motor"),
        ('o2_bio040_pct',  r"(040|bio\s*1).*o2|o2.*(040|bio\s*1)"),
        ('o2_bio050_pct',  r"(050|bio\s*2).*o2|o2.*(050|bio\s*2)"),
        ('o2_motor_pct',   r"motor.*o2|o2.*motor"),
        ('h2s_bio040_ppm', r"(040|bio\s*1).*h2s|h2s.*(040|bio\s*1)"),
        ('h2s_bio050_ppm', r"(050|bio\s*2).*h2s|h2s.*(050|bio\s*2)"),
        ('h2s_motor_ppm',  r"motor.*h2s|h2s.*motor")
    ]:
        c = pick(pat)
        if c: out[tag] = df[c].apply(to_float_heur)
    # caudal CHP l/s
    c = pick(r"caudal.*chp|chp.*(l/s|ls)|consumo.*chp")
    if c: out['caudal_chp_ls'] = df[c].apply(to_float_heur)
    return out


def norm_diario(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    cand = [c for c in df.columns if re.search(r"fecha|dia|date", str(c), re.I)]
    out['fecha'] = pd.to_datetime(df[cand[0]].apply(to_datetime_heur)) if cand else pd.NaT
    # métricas
    def map_col(tag, pats):
        for p in pats:
            for c in df.columns:
                if re.search(p, str(c), re.I):
                    out[tag] = df[c].apply(to_float_heur); return
    # Despacho total (columna AG). Capturar nombre exacto y variantes con unidades
    map_col('despacho_total_kwh_d', [
        r"^\s*despacho\s*total\s*$",
        r"\bdespacho\s*total\b.*(kwh|kwh/d)",
        r"despacho.*total",
        r"inyectad.*kwh/?d",
        r"generaci.*inyectada"
    ]) 
    map_col('despacho_spot_smec_kwh_d', [r"spot.*smec|despacho.*spot"]) 
    # materiales tn
    mats = {
        'purin_tn': [r"pur[ií]n"],
        'grasa_tn': [r"grasa"],
        'grano_descarte_me_tn': [r"grano.*descarte.*m\.?e|m\.e"],
        'contenido_ruminal_tn': [r"(contenido|rumen|ruminal)"],
        'polvillo_maiz_tn': [r"polvillo.*ma[ií]z"],
        'expeller_tn': [r"expeller"],
        'silo_sa7_tn': [r"sa\s*7|sa7|observaci"]
    }
    for tag, pats in mats.items():
        map_col(tag, pats)
    return out


def norm_fos_tac(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    cand = [c for c in df.columns if re.search(r"fecha|hora|date|time", str(c), re.I)]
    out['fecha_hora'] = pd.to_datetime(df[cand[0]].apply(to_datetime_heur)) if cand else pd.NaT
    for tag, pats in {
        'fos': [r"\bfos\b"],
        'tac': [r"\btac\b"],
    }.items():
        for p in pats:
            for c in df.columns:
                if re.search(p, str(c), re.I):
                    out[tag] = df[c].apply(to_float_heur)
                    break
    return out


def norm_st(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    # material
    mat_col = None
    for c in df.columns:
        if re.search(r"material|sustrat|nombre|producto", str(c), re.I):
            mat_col = c; break
    out['material'] = df[mat_col].astype(str).str.strip() if mat_col else None
    # ST planta
    st_col = None
    for c in df.columns:
        if re.search(r"st.*(an[aá]lisis|planta)|solidos.*totales", str(c), re.I):
            st_col = c; break
    if not st_col:
        # fallback: cualquier ST%
        for c in df.columns:
            if re.search(r"\bst\b|solidos|s[oó]lidos", str(c), re.I):
                st_col = c; break
    out['st_pct_planta'] = df[st_col].apply(to_float_heur) if st_col else None
    # fecha si existe
    fcol = None
    for c in df.columns:
        if re.search(r"fecha|date|hora|time", str(c), re.I): fcol = c; break
    out['fecha_hora'] = pd.to_datetime(df[fcol].apply(to_datetime_heur)) if fcol else pd.NaT
    return out


def norm_camiones(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    # fecha
    fcol = None
    for c in df.columns:
        if re.search(r"fecha|date|hora|time", str(c), re.I): fcol = c; break
    out['fecha_hora'] = pd.to_datetime(df[fcol].apply(to_datetime_heur)) if fcol else pd.NaT
    # material
    mcol = None
    for c in df.columns:
        if re.search(r"material|sustrat|producto|nombre", str(c), re.I): mcol = c; break
    out['material'] = df[mcol].astype(str).str.strip() if mcol else None
    # toneladas descargadas
    tcol = None
    for c in df.columns:
        if re.search(r"tn|tonelada|peso|descarg", str(c), re.I): tcol = c; break
    out['tn_descargadas'] = df[tcol].apply(to_float_heur) if tcol else None
    # ST análisis planta
    scol = None
    for c in df.columns:
        if re.search(r"st.*an[aá]lisis.*planta|st.*\(\%\).*planta", str(c), re.I): scol = c; break
    if not scol:
        for c in df.columns:
            if re.search(r"\bst\b|solidos|s[oó]lidos", str(c), re.I):
                scol = c; break
    out['st_pct_planta'] = df[scol].apply(to_float_heur) if scol else None
    return out


def norm_alimentacion_20(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    # fecha/hora
    fcol = None
    for c in df.columns:
        if re.search(r"fecha|hora|time|date", str(c), re.I): fcol = c; break
    out['fecha_hora'] = pd.to_datetime(df[fcol].apply(to_datetime_heur)) if fcol else pd.NaT
    # cantidades por hora; heurística: sólidos / líquidos / bio
    def map_col(tag, pats):
        for p in pats:
            for c in df.columns:
                if re.search(p, str(c), re.I):
                    out[tag] = df[c].apply(to_float_heur); return
    map_col('solidos_real_tn', [r"s[oó]lidos.*(real|dosif)", r"real.*s[oó]lidos", r"s[oó]lidos.*tn", r"tn.*s[oó]lidos"]) 
    map_col('liquidos_real_tn', [r"l[ií]quidos.*(real|dosif)", r"real.*l[ií]quidos", r"l[ií]quidos.*tn", r"tn.*l[ií]quidos"]) 
    map_col('bio_id', [r"bio\s*0?([1-4])", r"biodigestor\s*[1-4]"]) 
    return out


SHEET_HINTS = {
    'calidad gas y eficiencia': norm_calidad_gas,
    'diario': norm_diario,
    'fos tac': norm_fos_tac,
    'fos-tac': norm_fos_tac,
    'st': norm_st,
    'camiones': norm_camiones,
    'alimentacion 2.0': norm_alimentacion_20,
    'alimentación 2.0': norm_alimentacion_20,
}


def _normalize_name(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))  # remove accents
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def select_normalizer(sheet_name: str):
    n = _normalize_name(sheet_name)
    for key, fn in SHEET_HINTS.items():
        if _normalize_name(key) in n:
            return fn
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default=str(DEFAULT_XLS), help='Ruta al Excel')
    args = ap.parse_args()

    xls_path = Path(args.path)
    if not xls_path.exists():
        print(json.dumps({'error': f'Archivo no encontrado: {str(xls_path)}'}, ensure_ascii=False))
        return 1

    xls = pd.ExcelFile(xls_path)
    summary = {'file': str(xls_path), 'sheets': xls.sheet_names, 'analisis': []}

    # Resumen y normalización
    historico_rows: List[pd.DataFrame] = []
    camiones_rows: List[pd.DataFrame] = []
    st_rows: List[pd.DataFrame] = []
    alim_rows: List[pd.DataFrame] = []
    quim_rows: List[pd.DataFrame] = []

    for sh in xls.sheet_names:
        summary['analisis'].append(summarize_sheet(xls, sh))
        fn = select_normalizer(sh)
        if not fn:
            continue
        try:
            df = xls.parse(sh)
            df.columns = [str(c).strip() for c in df.columns]
            # Si hay multi-header (muchas ColumnaN), leer con header=[0,1]
            if sum(1 for c in df.columns if 'Columna' in str(c)) > 5:
                try:
                    df_multi = xls.parse(sh, header=[0,1])
                    # Combinar nombres: si segundo nivel no es nan, usarlo; sino solo primero
                    new_cols = []
                    for col in df_multi.columns.values:
                        if isinstance(col, tuple):
                            # col = (nivel0, nivel1)
                            n0, n1 = str(col[0]).strip(), str(col[1]).strip()
                            if n1 and n1.lower() not in ['nan', 'unnamed']:
                                new_cols.append(f"{n0}_{n1}")
                            else:
                                new_cols.append(n0)
                        else:
                            new_cols.append(str(col).strip())
                    df_multi.columns = new_cols
                    df = df_multi
                except Exception:
                    pass
            # Caso especial: hoja Diario con encabezados desalineados
            if _normalize_name(sh).startswith('diario'):
                df = _reparse_with_detected_header(xls, sh)
            norm = fn(df)
            norm['__sheet'] = sh
            # asignación por tipo
            if fn is norm_calidad_gas or fn is norm_diario:
                historico_rows.append(norm)
            elif fn is norm_camiones:
                camiones_rows.append(norm)
            elif fn is norm_st:
                st_rows.append(norm)
            elif fn is norm_alimentacion_20:
                alim_rows.append(norm)
            elif fn is norm_fos_tac:
                quim_rows.append(norm)
        except Exception as e:
            summary['analisis'].append({'sheet': sh, 'normalize_error': str(e)})

    # Concatenar y guardar
    def save_df(df: pd.DataFrame, name: str):
        pqt = DATA_DIR / f"{name}.parquet"
        jsn = DATA_DIR / f"{name}.json"
        try:
            df.to_parquet(pqt, index=False)
        except Exception:
            pass
        df.to_json(jsn, orient='records', force_ascii=False, indent=2, date_format='iso')
        return str(pqt), str(jsn)

    results = {}
    if historico_rows:
        h = pd.concat(historico_rows, ignore_index=True)
        results['historico_planta'] = save_df(h, 'historico_planta')
    if camiones_rows:
        c = pd.concat(camiones_rows, ignore_index=True)
        results['ingresos_camiones'] = save_df(c, 'ingresos_camiones')
    if st_rows:
        s = pd.concat(st_rows, ignore_index=True)
        results['st_materiales'] = save_df(s, 'st_materiales')
    if alim_rows:
        a = pd.concat(alim_rows, ignore_index=True)
        results['alimentacion_horaria'] = save_df(a, 'alimentacion_horaria')
    if quim_rows:
        q = pd.concat(quim_rows, ignore_index=True)
        results['analisis_quimico_fos_tac'] = save_df(q, 'analisis_quimico_fos_tac')

    # Guardar summary
    sum_path = DATA_DIR / 'planta_excel_summary.json'
    with open(sum_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        'status': 'success',
        'summary_file': str(sum_path),
        'outputs': results,
        'sheets': xls.sheet_names,
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
