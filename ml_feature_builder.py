"""
Construye un feature store ML a partir de data/*.parquet|json
- Une series históricas por fecha (diario)
- Crea ventanas móviles (24h y 7d) para variables clave
- Exporta a data/features_ml.parquet y .json
"""
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import re

BASE = Path(os.path.dirname(os.path.abspath(__file__)))
DATA = BASE / 'data'
DATA.mkdir(exist_ok=True)

def _to_float_heur(v):
    import math
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    s = str(v).strip()
    if s == '' or s.lower() in {'nan', 'none'}:
        return None
    # quitar espacios y %
    s = s.replace(' ', '').replace('%','')
    # si tiene puntos de miles y coma decimal: 26.781,79 -> 26781.79
    if s.count(',') == 1 and s.count('.') >= 1 and s.rfind(',') > s.rfind('.'):
        s = s.replace('.', '').replace(',', '.')
    # si solo tiene coma como decimal: 26682,05 -> 26682.05
    elif s.count(',') == 1 and '.' not in s:
        s = s.replace(',', '.')
    # eliminar caracteres no numéricos restantes salvo signo y punto
    import re as _re
    m = _re.search(r"[-+]?\d*\.?\d+", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None

def _load_any(name: str) -> pd.DataFrame:
    pqt = DATA / f"{name}.parquet"
    jsn = DATA / f"{name}.json"
    # Priorizar JSON para evitar dependencia de pyarrow/fastparquet
    if jsn.exists():
        return pd.read_json(jsn)
    if pqt.exists():
        try:
            return pd.read_parquet(pqt)
        except Exception:
            pass
    return pd.DataFrame()


def build_features() -> dict:
    # Cargar bases
    hist = _load_any('historico_planta')  # contiene gases, caudal, despacho, materiales diarios
    alim = _load_any('alimentacion_horaria')  # opcional
    fos = _load_any('analisis_quimico_fos_tac')  # opcional
    desp_sub = None
    # Si falta despacho_total_kwh_d, intentar extraer directamente del Excel 'Diario'
    try:
        BASE_XLS = BASE / 'GVBIO_-_Registro_de_planta_3.xlsx'
        if BASE_XLS.exists() and ('despacho_total_kwh_d' not in hist.columns):
            xl = pd.ExcelFile(BASE_XLS)
            if any(re.search(r"diario", s, re.I) for s in xl.sheet_names):
                sh = next(s for s in xl.sheet_names if re.search(r"diario", s, re.I))
                raw = xl.parse(sh, header=None)
                found = False
                # probar múltiples filas como encabezado
                for hdr_row in range(0, min(150, len(raw))):
                    headers = [str(v).strip() if v is not None else '' for v in list(raw.iloc[hdr_row].values)]
                    # criterio: algún header contiene ambas palabras
                    if not any(("despacho" in h.lower() and "total" in h.lower()) for h in headers):
                        continue
                    # construir DF con ese header
                    tmp = raw.iloc[hdr_row+1:].copy()
                    tmp.columns = [h if h else f"col_{i}" for i, h in enumerate(headers)]
                    # localizar columna de despacho
                    desp_cols = [c for c in tmp.columns if ("despacho" in c.lower() and "total" in c.lower())]
                    if not desp_cols:
                        continue
                    # detectar columna de fecha por parseabilidad
                    best_col, best_hits = None, -1
                    for c in tmp.columns:
                        s = pd.to_datetime(tmp[c], errors='coerce')
                        hits = s.notna().sum()
                        if hits > best_hits:
                            best_hits, best_col = hits, c
                    if best_col is None or best_hits <= 0:
                        continue
                    sub = tmp[[best_col, desp_cols[0]]].rename(columns={best_col:'fecha', desp_cols[0]:'despacho_total_kwh_d'})
                    # parseo de fecha tolerante
                    sub['fecha'] = pd.to_datetime(sub['fecha'], errors='coerce')
                    # intentar dayfirst si muchos NaN
                    if sub['fecha'].isna().mean() > 0.5:
                        sub['fecha'] = pd.to_datetime(sub['fecha'], errors='coerce', dayfirst=True)
                    sub['fecha'] = sub['fecha'].dt.floor('D')
                    # números en formato europeo
                    sub['despacho_total_kwh_d'] = sub['despacho_total_kwh_d'].map(_to_float_heur)
                    sub = sub.dropna(subset=['fecha'])
                    if not sub.empty:
                        desp_sub = sub
                        # merge mínimo en hist
                        if 'fecha' not in hist.columns and 'fecha_hora' in hist.columns:
                            hist['fecha'] = pd.to_datetime(hist['fecha_hora'], errors='coerce').dt.floor('D')
                        if 'fecha' in hist.columns:
                            hist = hist.merge(sub, on='fecha', how='left')
                        if hist.empty:
                            hist = sub.copy()
                        found = True
                        break
    except Exception:
        pass

    # Normalizaciones de tiempo
    if 'fecha_hora' in hist.columns:
        hist['fecha_hora'] = pd.to_datetime(hist['fecha_hora'], errors='coerce')
        hist['fecha'] = hist['fecha_hora'].dt.floor('D')
    elif 'fecha' in hist.columns:
        hist['fecha'] = pd.to_datetime(hist['fecha'], errors='coerce').dt.floor('D')
    else:
        hist['fecha'] = pd.NaT

    if not hist.empty:
        # Intentar mapear aliases de columnas provenientes de multi-header
        import re, unicodedata
        def norm(s: str) -> str:
            s = unicodedata.normalize('NFKD', s)
            s = ''.join(ch for ch in s if not unicodedata.combining(ch))
            s = s.lower()
            s = re.sub(r"\s+", " ", s)
            return s
        alias_map = {}
        for c in list(hist.columns):
            cn = norm(str(c))
            # Caudal CHP (l/s)
            if re.search(r"caudal.*chp.*(l/?s|ls)", cn) or ("datos de consumo del motor" in cn and "caudal chp" in cn):
                alias_map[c] = 'caudal_chp_ls'
            # Despacho total (puede venir sin unidad explícita)
            if re.search(r"\bdespacho\s*total\b", cn) or re.search(r"despacho.*total.*kwh", cn) or re.search(r"energia.*(total|diaria).*kwh", cn):
                alias_map[c] = 'despacho_total_kwh_d'
            # Despacho SPOT SMEC kWh/d
            if re.search(r"despacho.*(spot|smec).*kwh", cn):
                alias_map[c] = 'despacho_spot_smec_kwh_d'
        # Aplicar mapeos: crear columnas estándar si no existen
        for raw, std in alias_map.items():
            if std not in hist.columns:
                hist[std] = pd.to_numeric(hist[raw], errors='coerce')
        # Armar base por fecha tomando fechas de hist o, si faltan, de desp_sub
        if 'fecha' in hist.columns and hist['fecha'].notna().any():
            base = hist[['fecha']].drop_duplicates().copy()
        elif desp_sub is not None and not desp_sub.empty:
            base = desp_sub[['fecha']].drop_duplicates().copy()
        else:
            base = pd.DataFrame({'fecha': []})
        if desp_sub is not None and not desp_sub.empty:
            base = base.merge(desp_sub[['fecha','despacho_total_kwh_d']], on='fecha', how='left')
        # Seleccionar columnas numéricas relevantes
        keep_cols = [c for c in hist.columns if any(k in c for k in ['ch4', 'co2', 'o2', 'h2s', 'caudal_chp_ls', 'despacho_total_kwh_d', 'despacho_spot_smec_kwh_d', 'purin_tn','grasa_tn','grano_descarte_me_tn','contenido_ruminal_tn','polvillo_maiz_tn','expeller_tn'])]
        if keep_cols and 'fecha' in hist.columns:
            base = base.merge(hist[['fecha'] + keep_cols], on='fecha', how='left')
        # Agregar FOS/TAC por día si existe
        if not fos.empty:
            if 'fecha_hora' in fos.columns:
                fos['fecha'] = pd.to_datetime(fos['fecha_hora'], errors='coerce').dt.floor('D')
            elif 'fecha' in fos.columns:
                fos['fecha'] = pd.to_datetime(fos['fecha'], errors='coerce').dt.floor('D')
            fos_day = fos.groupby('fecha', as_index=False).agg({'fos':'mean','tac':'mean'})
            base = base.merge(fos_day, on='fecha', how='left')
        # Agregar alimentación diaria si existe (detección flexible de columnas)
        if not alim.empty:
            if 'fecha_hora' in alim.columns:
                alim['fecha'] = pd.to_datetime(alim['fecha_hora'], errors='coerce').dt.floor('D')
            # detectar columnas presentes
            def pick(cols, candidates):
                for cand in candidates:
                    if cand in cols:
                        return cand
                # probar regex simple
                import re
                for c in cols:
                    if re.search(r"solidos", str(c), re.I) and 'solidos' in candidates[0]:
                        return c
                    if re.search(r"liquid", str(c), re.I) and 'liquidos' in candidates[0]:
                        return c
                return None
            cols = list(alim.columns)
            c_sol = pick(cols, ['solidos_real_tn','total_solidos','solidos','solidos_tn'])
            c_liq = pick(cols, ['liquidos_real_tn','total_liquidos','liquidos','liquidos_tn'])
            agg_spec = {}
            rename_map = {}
            if c_sol:
                agg_spec[c_sol] = 'sum'
                rename_map[c_sol] = 'solidos_real_tn'
            if c_liq:
                agg_spec[c_liq] = 'sum'
                rename_map[c_liq] = 'liquidos_real_tn'
            if agg_spec:
                alim_day = alim.groupby('fecha', as_index=False).agg(agg_spec).rename(columns=rename_map)
                base = base.merge(alim_day, on='fecha', how='left')
        # Ventanas móviles diarias: necesitamos un índice de fecha continua
        df = base.sort_values('fecha').set_index('fecha')
        df_24 = df.rolling(window=1, min_periods=1).mean()  # diario ya agregado
        # Ventanas 7d (medias)
        df_7d = df.rolling(window=7, min_periods=1).mean().add_suffix('_mean7d')
        # Juntar
        feats = pd.concat([df, df_7d], axis=1).reset_index()
    else:
        feats = pd.DataFrame()

    # Guardar
    out_pqt = DATA / 'features_ml.parquet'
    out_json = DATA / 'features_ml.json'
    if not feats.empty:
        try:
            feats.to_parquet(out_pqt, index=False)
        except Exception:
            pass
        feats.to_json(out_json, orient='records', force_ascii=False, indent=2, date_format='iso')

    return {
        'rows': int(feats.shape[0] if feats is not None else 0),
        'cols': int(feats.shape[1] if feats is not None else 0),
        'files': {'parquet': str(out_pqt), 'json': str(out_json)}
    }


if __name__ == '__main__':
    info = build_features()
    print(json.dumps({'status':'success','features':info}, ensure_ascii=False, indent=2))
