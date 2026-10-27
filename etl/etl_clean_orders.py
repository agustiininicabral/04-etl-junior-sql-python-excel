"""Clean order CSV data and preserve rejected rows with explicit reasons."""

from __future__ import annotations

import argparse
import math
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "discount_rate",
}


def parse_date(value: Any):
    text = str(value).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", text):
        return pd.to_datetime(text, format="%d/%m/%Y", errors="coerce")
    return pd.NaT


def parse_money(value: Any) -> float | None:
    text = str(value).strip().replace("$", "").replace(",", "")
    if not text or text.lower() in {"nan", "none"}:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def parse_discount(value: Any) -> float | None:
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return 0.0
    try:
        number = float(text.replace(",", "."))
    except ValueError:
        return None
    if not math.isfinite(number) or not 0 <= number <= 0.8:
        return None
    return number


def _positive_integer(value: Any) -> int | None:
    try:
        number = float(str(value).strip())
    except ValueError:
        return None
    if not math.isfinite(number) or number <= 0 or not number.is_integer():
        return None
    return int(number)


def clean_orders(
    input_path: str | Path,
    output_path: str | Path,
    rejected_path: str | Path | None = None,
) -> dict[str, int]:
    """Write valid orders and a separate CSV of rejected source rows."""
    source = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    missing = REQUIRED_COLUMNS - set(source.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {', '.join(sorted(missing))}")

    parsed_dates = source["order_date"].apply(parse_date)
    parsed_prices = source["unit_price"].apply(parse_money)
    parsed_discounts = source["discount_rate"].apply(parse_discount)
    parsed_ids = {
        column: source[column].apply(_positive_integer)
        for column in ("order_id", "customer_id", "product_id", "quantity")
    }

    reasons: list[list[str]] = [[] for _ in range(len(source))]
    for index in range(len(source)):
        if pd.isna(parsed_dates.iloc[index]):
            reasons[index].append("invalid order_date")
        if pd.isna(parsed_prices.iloc[index]) or parsed_prices.iloc[index] <= 0:
            reasons[index].append("unit_price must be a positive number")
        if pd.isna(parsed_discounts.iloc[index]):
            reasons[index].append("discount_rate must be between 0 and 0.8")
        for column in ("order_id", "customer_id", "product_id"):
            if pd.isna(parsed_ids[column].iloc[index]):
                reasons[index].append(f"{column} must be a positive integer")
        if pd.isna(parsed_ids["quantity"].iloc[index]):
            reasons[index].append("quantity must be a positive integer")

    duplicate_orders = source["order_id"].duplicated(keep=False)
    for index, is_duplicate in enumerate(duplicate_orders):
        if is_duplicate:
            reasons[index].append("duplicate order_id")

    valid_mask = [not row_reasons for row_reasons in reasons]
    rejected = source.loc[[not valid for valid in valid_mask]].copy()
    rejected["source_row"] = [index + 2 for index, valid in enumerate(valid_mask) if not valid]
    rejected["reject_reason"] = ["; ".join(row) for row, valid in zip(reasons, valid_mask) if not valid]

    clean = source.loc[valid_mask].copy()
    clean["order_date"] = [
        parsed_dates.iloc[index].date().isoformat()
        for index, valid in enumerate(valid_mask)
        if valid
    ]
    for column, values in parsed_ids.items():
        clean[column] = [int(values.iloc[index]) for index, valid in enumerate(valid_mask) if valid]
    clean["unit_price"] = [
        parsed_prices.iloc[index] for index, valid in enumerate(valid_mask) if valid
    ]
    clean["discount_rate"] = [
        parsed_discounts.iloc[index] for index, valid in enumerate(valid_mask) if valid
    ]
    clean["net_amount"] = [
        float(
            (
                Decimal(str(parsed_prices.iloc[index]))
                * Decimal(int(parsed_ids["quantity"].iloc[index]))
                * (Decimal("1") - Decimal(str(parsed_discounts.iloc[index])))
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        for index, valid in enumerate(valid_mask)
        if valid
    ]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output, index=False)
    rejects_output = Path(rejected_path) if rejected_path else output.with_name("orders_rejected.csv")
    rejects_output.parent.mkdir(parents=True, exist_ok=True)
    rejected.to_csv(rejects_output, index=False)

    return {
        "input_rows": len(source),
        "clean_rows": len(clean),
        "rejected_rows": len(rejected),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input_path", default="data/orders_dirty.csv")
    parser.add_argument("--out", dest="output_path", default="data/orders_clean.csv")
    parser.add_argument("--rejected", default=None)
    args = parser.parse_args()
    stats = clean_orders(args.input_path, args.output_path, args.rejected)
    print(
        f"Input: {stats['input_rows']}; clean: {stats['clean_rows']}; "
        f"rejected: {stats['rejected_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
