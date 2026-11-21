"""Reconcile a two-column order export locally with Python 3.9+."""
import argparse
import csv
import json
import os
import re
from collections import defaultdict
from decimal import Decimal
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

SAMPLE = "order_id,amount\n0007,19.50\n 0007,19.5\n0012,12.00\n0012,21.00\n0015,4.25\n"
MONEY = re.compile(r"[+-]?[0-9]{1,16}(?:\.[0-9]{1,2})?")


def inspect_orders(source):
    reader = csv.reader(source, strict=True)
    header = next(reader, [])
    header = [name.lstrip("\ufeff").strip() for name in header]
    if sorted(header) != ["amount", "order_id"]:
        raise ValueError("Expected exactly two column names: order_id and amount.")
    id_col, amount_col = header.index("order_id"), header.index("amount")
    groups, review, ready = defaultdict(list), [], []
    records = duplicates = 0
    for record, fields in enumerate(reader, start=1):
        records += 1
        order_id = fields[id_col].strip() if id_col < len(fields) else ""
        raw = fields[amount_col].strip() if amount_col < len(fields) else ""
        row = {"record": record, "order_id": order_id, "fields": fields, "amount": raw}
        reason = ""
        if len(fields) != 2:
            reason = "wrong number of fields"
        elif not order_id:
            reason = "missing order ID"
        elif not MONEY.fullmatch(raw):
            reason = "invalid amount"
        if not order_id:
            review.append(dict(row, reason=reason))
        else:
            groups[order_id].append((row, reason, None if reason else Decimal(raw)))

    for order_id, entries in groups.items():
        amounts = {value for _, reason, value in entries if not reason}
        if any(reason for _, reason, _ in entries) or len(amounts) != 1:
            for row, reason, _ in entries:
                fallback = "conflicting amounts" if len(amounts) > 1 else "another row for this ID is invalid"
                review.append(dict(row, reason=reason or fallback))
        else:
            ready.append({"order_id": order_id, "amount": format(amounts.pop(), ".2f")})
            duplicates += len(entries) - 1
    total = sum((Decimal(row["amount"]) for row in ready), Decimal("0.00"))
    return {"records": records, "ready": ready, "duplicates": duplicates,
            "review": sorted(review, key=lambda row: row["record"]), "ready_total": format(total, ".2f")}


def reconcile(source):
    """Original three-value interface for well-formed order imports."""
    report = inspect_orders(source)
    clean = {r["order_id"]: Decimal(r["amount"]) for r in report["ready"]}
    conflicts = defaultdict(list)
    for row in report["review"]:
        if row["reason"] != "conflicting amounts":
            raise ValueError(f"Record {row['record']}: {row['reason']}")
        conflicts[row["order_id"]].append(Decimal(row["amount"]))
    return clean, dict(conflicts), report["duplicates"]


def export_bundle(report, destination):
    """Publish a complete local archive without replacing an existing file."""
    with TemporaryDirectory(dir=destination.parent) as staging:
        archive = Path(staging) / "report.zip"
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
            for name, columns in (("ready", ["order_id", "amount"]),
                                  ("review", ["record", "order_id", "amount", "reason", "fields"])):
                output = StringIO(newline="")
                writer = csv.DictWriter(output, columns)
                writer.writeheader()
                for row in report[name]:
                    values = dict(row)
                    if "fields" in values:
                        values["fields"] = json.dumps(values["fields"], ensure_ascii=False)
                    writer.writerow(values)
                bundle.writestr(name + ".csv", output.getvalue())
            summary = {key: report[key] for key in ("records", "duplicates", "ready_total")}
            summary.update(ready=len(report["ready"]), review=len(report["review"]))
            bundle.writestr("summary.json", json.dumps(summary, indent=2) + "\n")
        os.link(archive, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", nargs="?", type=Path, help="UTF-8 CSV with order_id and amount")
    parser.add_argument("--json", action="store_true", help="include accepted rows and every exception")
    parser.add_argument("--export", type=Path, metavar="NEW.zip", help="save ready.csv, review.csv and summary.json")
    args = parser.parse_args()
    try:
        if args.csv_file:
            with args.csv_file.open(encoding="utf-8-sig", newline="") as source:
                report = inspect_orders(source)
        else:
            report = inspect_orders(StringIO(SAMPLE))
        if args.export:
            export_bundle(report, args.export)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        parser.exit(2, f"CSV processing error: {exc}\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{report['records']} input records | {len(report['ready'])} ready | "
              f"{report['duplicates']} duplicates | {len(report['review'])} held")
        print(f"Accepted total: {report['ready_total']}")
        for row in report["review"]:
            print(f"Record {row['record']}, order {row['order_id']!r}: {row['reason']}")


if __name__ == "__main__":
    main()
