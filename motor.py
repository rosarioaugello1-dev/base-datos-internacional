#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
motor.py — Baja las series del config y genera MAESTRO.xlsx

Uso:
    python3 motor.py                      # usa config_diarias.csv
    python3 motor.py mi_config.csv

Proveedores soportados:
    FRED_CSV   -> descarga directa de FRED, sin clave (columna codigo_serie = ID de FRED)
    DBNOMICS   -> API de DBnomics (codigo_serie = PROVEEDOR/DATASET/CODIGO)
    SCRAPER    -> CSV propio publicado en una URL fija (columna url_api)
"""

import io
import sys
import datetime as dt
from pathlib import Path

import pandas as pd
import requests

CONFIG = Path(sys.argv[1] if len(sys.argv) > 1 else "config_diarias.csv")
SALIDA = Path("salidas")
TIMEOUT = 60


# ---------------------------------------------------------------------------
# Un bajador por proveedor. Todos devuelven: fecha | valor | serie_id
# ---------------------------------------------------------------------------

def bajar_fred(fila):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fila['codigo_serie']}"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    # FRED cambió el nombre de la primera columna con el tiempo: DATE / observation_date
    df.columns = ["fecha", "valor"]
    # En FRED los datos faltantes vienen como un punto
    df["valor"] = pd.to_numeric(df["valor"].replace(".", pd.NA), errors="coerce")
    return df


def bajar_dbnomics(fila):
    url = ("https://api.db.nomics.world/v22/series"
           f"?observations=1&series_ids={fila['codigo_serie']}")
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    docs = r.json()["series"]["docs"]
    if not docs:
        raise ValueError("la API respondió pero no devolvió ninguna serie")
    doc = docs[0]
    df = pd.DataFrame({"fecha": doc["period"], "valor": doc["value"]})
    # DBnomics marca los faltantes con la cadena "NA"
    df["valor"] = pd.to_numeric(df["valor"].replace("NA", pd.NA), errors="coerce")
    return df


def bajar_scraper(fila):
    df = pd.read_csv(fila["url_api"])
    return df.rename(columns={df.columns[0]: "fecha", df.columns[1]: "valor"})


BAJADORES = {"FRED_CSV": bajar_fred, "DBNOMICS": bajar_dbnomics, "SCRAPER": bajar_scraper}


# ---------------------------------------------------------------------------

def main():
    if not CONFIG.exists():
        sys.exit(f"No encuentro {CONFIG}")

    cfg = pd.read_csv(CONFIG, encoding="utf-8-sig")
    cfg = cfg[cfg["prioridad"] == 1]
    print(f"{len(cfg)} series marcadas con prioridad 1\n")

    partes, errores = [], []
    for _, fila in cfg.iterrows():
        etiqueta = str(fila["serie_id"])
        try:
            bajador = BAJADORES.get(str(fila["proveedor"]).strip())
            if bajador is None:
                raise ValueError(f"proveedor desconocido: {fila['proveedor']}")

            df = bajador(fila)
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df = df.dropna(subset=["fecha", "valor"])
            if df.empty:
                raise ValueError("la fuente respondió pero no trajo datos válidos")

            df["serie_id"] = etiqueta
            partes.append(df[["fecha", "valor", "serie_id"]])
            ultima = df["fecha"].max().date()
            atraso = (dt.date.today() - ultima).days
            alerta = "  <-- ATRASADA" if atraso > 10 else ""
            print(f"  OK    {etiqueta:16s} {len(df):>6} obs   hasta {ultima}{alerta}")

        except Exception as e:
            errores.append((etiqueta, str(e)))
            print(f"  FALLA {etiqueta:16s} {e}")

    if not partes:
        sys.exit("\nNo se pudo bajar ninguna serie. Revisá el config y la conexión.")

    datos = pd.concat(partes, ignore_index=True).sort_values(["serie_id", "fecha"])
    SALIDA.mkdir(exist_ok=True)
    datos.to_csv(SALIDA / "series_largo.csv", index=False)

    # --- Armado del MAESTRO -------------------------------------------------
    orden = [s for s in cfg["serie_id"] if s in set(datos["serie_id"])]

    with pd.ExcelWriter(SALIDA / "MAESTRO.xlsx", engine="openpyxl",
                        datetime_format="yyyy-mm-dd") as xls:
        for hoja, grupo in cfg.groupby("hoja_destino", sort=False):
            ids = [s for s in orden if s in set(grupo["serie_id"])]
            if not ids:
                continue
            sub = datos[datos["serie_id"].isin(ids)]
            ancho = sub.pivot(index="fecha", columns="serie_id", values="valor")
            ancho = ancho.reindex(columns=ids)      # orden fijo: no romper vínculos
            ancho.index.name = "Fecha"
            ancho.to_excel(xls, sheet_name=str(hoja)[:31])

        meta = (datos.groupby("serie_id")
                     .agg(primer_dato=("fecha", "min"), ultimo_dato=("fecha", "max"),
                          observaciones=("valor", "size"))
                     .reset_index()
                     .merge(cfg[["serie_id", "nombre_en_excel", "proveedor",
                                 "codigo_serie", "frecuencia", "notas"]],
                            on="serie_id", how="left"))
        meta["dias_de_atraso"] = (pd.Timestamp.today().normalize() - meta["ultimo_dato"]).dt.days
        meta["actualizado_el"] = pd.Timestamp.today().normalize()
        meta.to_excel(xls, sheet_name="_METADATOS", index=False)

    print(f"\nMAESTRO.xlsx generado: {len(orden)} series, "
          f"{datos['fecha'].min().date()} a {datos['fecha'].max().date()}")

    if errores:
        (SALIDA / "errores.txt").write_text(
            "\n".join(f"{s}: {e}" for s, e in errores), encoding="utf8")
        print(f"{len(errores)} series fallaron (ver salidas/errores.txt)")


if __name__ == "__main__":
    main()
