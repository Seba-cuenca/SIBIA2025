#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import re
from pathlib import Path

import pandas as pd

PATH = Path(r"c:\Users\SEBASTIAN\Desktop\PROYECTOS IA\FUNCIONARON TODAS MENOS\GVBIO_-_Registro_de_planta_3.xlsx")

def infer_kind(name: str) -> str:
    n = name.strip().lower()
    # heuristics for sensors/metrics
    if any(k in n for k in ["fecha", "hora", "datetime", "timestamp"]):
        return "datetime"
    if re.search(r"\bch4\b|metano|methane", n):
        return "ch4_pct"
    if re.search(r"\bco2\b", n):
        return "co2_pct"
    if re.search(r"\bo2\b", n):
        return "o2_pct"
    if "h2s" in n:
        return "h2s_ppm"
    if re.search(r"temp|temperatura|t\b", n):
        return "temperature_c"
    if re.search(r"nivel|lvl|lt\b", n):
        return "level_pct"
    if re.search(r"presion|presión|pt\b|bar\b", n):
        return "pressure_bar"
    if re.search(r"kwgen|kwgen|kw_gen|kw\b|potencia|generaci", n):
        return "kw"
    if re.search(r"kwh|energia|energía", n):
        return "kwh"
    if re.search(r"consumo|chp|motor|combustible", n):
        return "consumo_motor"
    if re.search(r"flujo|caudal|m3/h|m3h|m3_h", n):
        return "flow_m3h"
    if re.search(r"ph\b", n):
        return "ph"
    if re.search(r"volumen|m3\b|litro|l/h", n):
        return "volume"
    return "other"

def summarize_sheet(xls: pd.ExcelFile, sheet: str, max_rows: int = 2000):
    try:
        df = xls.parse(sheet)
    except Exception as e:
        return {"sheet": sheet, "error": str(e)}

    # Trim whitespace in headers
    df.columns = [str(c).strip() for c in df.columns]

    # Downsample for speed
    head = df.head(5)
    nonnull = df.notna().sum().to_dict()
    dtypes = {c: str(t) for c, t in df.dtypes.items()}

    # Try to parse potential datetime columns
    time_cols = []
    for c in df.columns:
        if infer_kind(c) == "datetime" or re.search(r"fecha|hora|time|date", c, re.I):
            try:
                pd.to_datetime(df[c], errors='raise')
            except Exception:
                pass

    kinds = {c: infer_kind(c) for c in df.columns}

    # Examples per column (cast to str to avoid Timestamp serialization)
    examples = {}
    for c in df.columns:
        vals = df[c].dropna().unique().tolist()[:5]
        examples[c] = [str(v) for v in vals]

    return {
        "sheet": sheet,
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),
        "nonnull": nonnull,
        "dtypes": dtypes,
        "time_candidates": time_cols,
        "kinds": kinds,
        "examples": examples,
    }

def main():
    if not PATH.exists():
        print(json.dumps({"error": f"Archivo no encontrado: {str(PATH)}"}, ensure_ascii=False))
        sys.exit(1)

    try:
        xls = pd.ExcelFile(PATH)
        sheets = xls.sheet_names
        summary = {"file": str(PATH), "sheets": sheets, "analisis": []}
        for sh in sheets:
            summary["analisis"].append(summarize_sheet(xls, sh))
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(2)

if __name__ == "__main__":
    main()
