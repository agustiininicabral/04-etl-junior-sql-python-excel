import argparse
from pathlib import Path
import pandas as pd
import re

def parse_date(x: str):
    x = str(x).strip()
    # acepta YYYY-MM-DD o DD/MM/YYYY
    if re.match(r"^\d{4}-\d{2}-\d{2}$", x):
        return pd.to_datetime(x, format="%Y-%m-%d", errors="coerce")
    if re.match(r"^\d{2}/\d{2}/\d{4}$", x):
        return pd.to_datetime(x, format="%d/%m/%Y", errors="coerce")
    return pd.NaT

def parse_money(x: str):
    x = str(x).strip()
    x = x.replace("$","").replace(",","")
    try:
        return float(x)
    except:
        return None

def parse_discount(x: str):
    x = str(x).strip()
    if x == "" or x.lower() == "nan":
        return 0.0
    x = x.replace(",", ".")
    try:
        v = float(x)
        return v
    except:
        return 0.0

def main():
    ap = argparse.ArgumentParser(description="ETL Junior: limpia orders_dirty.csv y genera orders_clean.csv")
    ap.add_argument("--in", dest="inp", default="data/orders_dirty.csv")
    ap.add_argument("--out", dest="out", default="data/orders_clean.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)

    df["order_date"] = df["order_date"].apply(parse_date)
    df["unit_price"] = df["unit_price"].apply(parse_money)
    df["discount_rate"] = df["discount_rate"].apply(parse_discount)

    # reglas de calidad
    df = df.dropna(subset=["order_date","unit_price"])
    df["quantity"] = df["quantity"].astype(int)
    df["discount_rate"] = df["discount_rate"].clip(lower=0, upper=0.8)
    df["net_amount"] = (df["unit_price"] * df["quantity"] * (1 - df["discount_rate"])).round(2)

    df["order_date"] = df["order_date"].dt.date.astype(str)

    df.to_csv(args.out, index=False)
    print("OK: generado", args.out, "filas:", len(df))

if __name__ == "__main__":
    main()