#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrena modelos ML a partir de data/features_ml.(parquet|json).
- Modelos objetivo ejemplos: despacho_total_kwh_d (regresión), caudal_chp_ls (regresión)
- Si scikit-learn no está disponible, usa regresión lineal por mínimos cuadrados (numpy) como fallback.
- Guarda artefactos en models/ (JSON y, si es posible, pickle de sklearn)
"""
import json
import os
from pathlib import Path

import pandas as pd
import numpy as np

BASE = Path(os.path.dirname(os.path.abspath(__file__)))
DATA = BASE / 'data'
MODELS = BASE / 'models'
MODELS.mkdir(exist_ok=True)


def _load_features() -> pd.DataFrame:
    jsn = DATA / 'features_ml.json'
    pqt = DATA / 'features_ml.parquet'
    # Priorizar JSON para evitar dependencias de pyarrow
    if jsn.exists():
        return pd.read_json(jsn)
    if pqt.exists():
        try:
            return pd.read_parquet(pqt)
        except Exception:
            pass
    return pd.DataFrame()


def _select_xy(df: pd.DataFrame, target: str):
    y = pd.to_numeric(df.get(target), errors='coerce')
    # features: todas las numéricas menos target y fecha
    X = df.select_dtypes(include=[np.number]).copy()
    if target in X.columns:
        X = X.drop(columns=[target])
    # quitar columnas con demasiados NaN
    X = X.loc[:, X.notna().mean() > 0.8]
    # rellenar NaN con mediana
    X = X.fillna(X.median())
    # alinear y
    mask = y.notna()
    X = X.loc[mask]
    y = y.loc[mask]
    return X, y


def train_linear(target: str) -> dict:
    df = _load_features()
    if df.empty or target not in df.columns:
        return {'status': 'no_data', 'target': target}
    X, y = _select_xy(df, target)
    if len(y) < 10:
        return {'status': 'insufficient_data', 'target': target, 'n': int(len(y))}

    # Intentar sklearn primero
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_absolute_error
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
        reg = LinearRegression()
        reg.fit(Xtr, ytr)
        pred = reg.predict(Xte)
        metrics = {
            'r2': float(r2_score(yte, pred)),
            'mae': float(mean_absolute_error(yte, pred)),
            'n_train': int(len(ytr)),
            'n_test': int(len(yte)),
        }
        # guardar
        try:
            import joblib
            joblib.dump(reg, MODELS / f'{target}_linreg.pkl')
        except Exception:
            pass
        # guardar coeficientes
        coefs = {c: float(v) for c, v in zip(X.columns, reg.coef_)}
        model_json = {
            'type': 'sklearn.LinearRegression',
            'target': target,
            'intercept': float(reg.intercept_),
            'coefficients': coefs,
            'metrics': metrics,
            'features': list(X.columns),
        }
        (MODELS / f'{target}_linreg.json').write_text(json.dumps(model_json, ensure_ascii=False, indent=2), encoding='utf-8')
        return {'status': 'success', 'target': target, 'metrics': metrics}
    except Exception:
        # Fallback: mínimos cuadrados con numpy
        X_ = np.c_[np.ones(len(X)), X.values]
        beta, *_ = np.linalg.lstsq(X_, y.values, rcond=None)
        intercept = float(beta[0])
        coefs = {c: float(v) for c, v in zip(X.columns, beta[1:])}
        # Métricas simples en train
        pred = X_.dot(beta)
        ss_res = float(np.sum((y.values - pred) ** 2))
        ss_tot = float(np.sum((y.values - np.mean(y.values)) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        mae = float(np.mean(np.abs(y.values - pred)))
        model_json = {
            'type': 'numpy.lstsq',
            'target': target,
            'intercept': intercept,
            'coefficients': coefs,
            'metrics': {'r2': r2, 'mae': mae, 'n': int(len(y))},
            'features': list(X.columns),
        }
        (MODELS / f'{target}_linreg.json').write_text(json.dumps(model_json, ensure_ascii=False, indent=2), encoding='utf-8')
        return {'status': 'success', 'target': target, 'metrics': {'r2': r2, 'mae': mae, 'n': int(len(y))}}


def main():
    targets = ['despacho_total_kwh_d', 'caudal_chp_ls']
    results = {}
    for t in targets:
        results[t] = train_linear(t)
    print(json.dumps({'status': 'success', 'trained': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
