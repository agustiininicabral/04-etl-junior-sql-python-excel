from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "etl"))

from etl_clean_orders import clean_orders, parse_date, parse_discount, parse_money  # noqa: E402


class EtlCleanOrdersTests(unittest.TestCase):
    def test_parsers_handle_supported_and_invalid_values(self) -> None:
        self.assertEqual(parse_date("2025-03-27").date().isoformat(), "2025-03-27")
        self.assertEqual(parse_date("27/03/2025").date().isoformat(), "2025-03-27")
        self.assertTrue(pd.isna(parse_date("not-a-date")))
        self.assertEqual(parse_money("$1,234.50"), 1234.5)
        self.assertIsNone(parse_money("unknown"))
        self.assertEqual(parse_discount(""), 0.0)
        self.assertEqual(parse_discount("0,15"), 0.15)
        self.assertIsNone(parse_discount("1.5"))

    def test_cleaner_keeps_valid_rows_and_records_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "dirty.csv"
            source.write_text(
                "order_id,order_date,customer_id,product_id,quantity,unit_price,discount_rate\n"
                "1,2025-03-27,10,20,5,$39.50,0.05\n"
                "2,31/02/2025,11,21,1,20,0\n"
                "3,2025-05-01,12,22,0,20,0\n"
                "4,2025-05-01,13,23,1,20,1.2\n",
                encoding="utf-8",
            )
            clean_path = root / "clean.csv"
            rejected_path = root / "rejected.csv"
            stats = clean_orders(source, clean_path, rejected_path)
            clean = pd.read_csv(clean_path)
            rejected = pd.read_csv(rejected_path)

        self.assertEqual(stats, {"input_rows": 4, "clean_rows": 1, "rejected_rows": 3})
        self.assertAlmostEqual(clean.loc[0, "net_amount"], 187.63)
        self.assertEqual(len(rejected), 3)
        self.assertIn("reject_reason", rejected.columns)

    def test_duplicate_order_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "dirty.csv"
            row = "1,2025-03-27,10,20,1,10,0\n"
            source.write_text(
                "order_id,order_date,customer_id,product_id,quantity,unit_price,discount_rate\n"
                + row
                + row,
                encoding="utf-8",
            )
            stats = clean_orders(source, root / "clean.csv", root / "rejected.csv")

        self.assertEqual(stats["clean_rows"], 0)
        self.assertEqual(stats["rejected_rows"], 2)


if __name__ == "__main__":
    unittest.main()
