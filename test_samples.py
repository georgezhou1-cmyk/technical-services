"""Run with python3 -m unittest -v. Tests use only local fixtures."""
import csv
import json
import tempfile
import unittest
from decimal import Decimal
from io import StringIO
from pathlib import Path
from urllib.error import HTTPError
from zipfile import ZipFile

import api_quickstart_demo as api
import csv_import_demo as orders
import sqlite_report_demo as sql


class ImportTests(unittest.TestCase):
    def test_original_contract_and_total(self):
        clean, conflicts, repeats = orders.reconcile(StringIO(orders.SAMPLE))
        self.assertEqual(clean, {"0007": Decimal("19.50"), "0015": Decimal("4.25")})
        self.assertEqual(conflicts, {"0012": [Decimal("12.00"), Decimal("21.00")]})
        self.assertEqual(repeats, 1)

    def test_invalid_peer_holds_whole_group(self):
        report = orders.inspect_orders(StringIO("amount,order_id\n1.00,001\nNaN,001\n-2.50,002\n4,\n5,003,extra\n"))
        self.assertEqual(report["ready"], [{"order_id": "002", "amount": "-2.50"}])
        self.assertEqual([r["record"] for r in report["review"]], [1, 2, 4, 5])
        self.assertEqual(report["ready_total"], "-2.50")
        self.assertEqual(report["records"], len(report["ready"]) + report["duplicates"] + len(report["review"]))

    def test_bom_crlf_and_quoted_fields(self):
        report = orders.inspect_orders(StringIO('\ufefforder_id,amount\r\n"a,b",0.01\r\n"a,b",0.01\r\n'))
        self.assertEqual(report["ready"], [{"order_id": "a,b", "amount": "0.01"}])
        self.assertEqual(report["duplicates"], 1)

    def test_reject_duplicate_or_missing_headers(self):
        for header in ("amount,amount", "order_id", ""):
            with self.subTest(header=header), self.assertRaises(ValueError):
                orders.inspect_orders(StringIO(header))

    def test_no_rounding_or_silent_malformed_csv(self):
        for raw in ("3.141", "1e2", "Infinity", ""):
            with self.subTest(raw=raw):
                report = orders.inspect_orders(StringIO("order_id,amount\nx," + raw + "\n"))
                self.assertEqual(report["review"][0]["reason"], "invalid amount")
        with self.assertRaises(csv.Error):
            orders.inspect_orders(StringIO('order_id,amount\n"x,1\n'))

    def test_export_matches_report_and_preserves_existing_archive(self):
        report = orders.inspect_orders(StringIO(orders.SAMPLE))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "orders.zip"
            orders.export_bundle(report, path)
            with ZipFile(path) as archive:
                ready = list(csv.DictReader(StringIO(archive.read("ready.csv").decode())))
                review = list(csv.DictReader(StringIO(archive.read("review.csv").decode())))
                self.assertEqual(ready, report["ready"])
                self.assertEqual([row["order_id"] for row in review], ["0012", "0012"])
                self.assertEqual(json.loads(archive.read("summary.json"))["ready_total"], "23.75")
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                orders.export_bundle(report, path)
            self.assertEqual(path.read_bytes(), original)


class ApiTests(unittest.TestCase):
    def test_fixture_and_empty_page(self):
        self.assertEqual(api.parse_tags(api.FIXTURE)[0], ("demo-v2", "a" * 40))
        self.assertEqual(api.parse_tags([]), [])

    def test_bad_payload(self):
        for data in ({}, [None], [{"name": "v1", "commit": {}}]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                api.parse_tags(data)

    def test_parameters_before_network(self):
        for repo, limit in (("not a repo", 3), ("owner/..", 1), ("python/cpython", 0)):
            with self.subTest(repo=repo, limit=limit), self.assertRaises(ValueError):
                api.load_tags(repo, limit)

    def test_http_diagnostics(self):
        err = HTTPError("", 403, "", {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "123"}, None)
        self.assertIn("123", api.http_message(err))
        self.assertIn("public visibility", api.http_message(HTTPError("", 404, "", {}, None)))


class SQLiteTests(unittest.TestCase):
    def test_ties_and_query_plans(self):
        before, after = sql.compare(20000, 7, 3)
        self.assertEqual(before[1], [(19967, 99), (19927, 99), (19887, 99)])
        self.assertEqual(after[1], before[1])
        self.assertTrue(any("orders_recent" in step for step in after[0]))

    def test_empty_and_sparse_reports(self):
        for size, account, expected in ((0, 0, []), (10, 2, [(2, 0)]), (10, 30, [])):
            with self.subTest(size=size, account=account):
                self.assertEqual(sql.compare(size, account, 3)[1][1], expected)


if __name__ == "__main__":
    unittest.main()
