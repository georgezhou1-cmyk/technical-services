# CSV import repair

**USD 49 per scoped engagement.** For an operations team whose order export is rejected by an importer or produces the wrong totals.

## What the fee covers

One CSV layout, up to 20 columns and 50,000 rows, and one destination schema. Typical fixes include column mapping, whitespace, decimal formatting, and duplicate identifiers.

## What you receive

A cleaned CSV, a separate file for rows that need a decision, and a rerunnable Python script. The delivery summary reconciles input and output row counts and the agreed control total.

## Try the sample

Five fictional rows contain two versions of order 0007 and conflicting amounts for 0012. The demo preserves the leading zeros, accepts two orders totalling $23.75, drops one equivalent repeat, and holds both conflicting rows for review.

Run from a clone of this repository with Python 3.9 or newer.

```sh
python3 csv_import_demo.py
```

[Read the sample code](csv_import_demo.py)

### Run it on your own export

Use a UTF-8 CSV with exactly two columns named `order_id` and `amount`, in either order. Text IDs retain leading zeros. Amounts accept a leading sign, up to 16 integer digits and up to two decimal places. Rows with ambiguous amounts go into review together with any other rows for the same ID.

```sh
python3 csv_import_demo.py orders.csv --export reconciled.zip
```

Open the archive to inspect the accepted orders in `ready.csv`, each held input record and its reason in `review.csv`, and the counts and accepted total in `summary.json`. Ready rows, removed duplicates and held rows add up to the input record count. Choose a fresh output name each time. Use `--json` for a machine-readable preview. When importing the results into a spreadsheet, set the order ID column to text to retain its leading zeros.

## Request this service

What tool will import the CSV? Which field identifies one record? Include a made-up header and two fictional rows that illustrate the problem. A request opens a public GitHub issue. Use fictional examples and public links. Scope, timing and payment arrangements are confirmed before paid work begins. Technical work is AI-assisted and validated against the agreed examples.

[Open a CSV import repair inquiry](https://github.com/georgezhou1-cmyk/technical-services/issues/new?title=Service+inquiry+%E2%80%94+CSV+import+repair&body=Service+requested%3A+CSV+import+repair+%28listed+fee+USD+49%29%0A%0AWhat+tool+will+import+the+CSV%3F+Which+field+identifies+one+record%3F+Include+a+made-up+header+and+two+fictional+rows+that+illustrate+the+problem.%0A%0ADesired+handoff+date+%28optional%29%3A%0A%0AThis+request+is+public.+Use+fictional+examples+and+public+links+only.) · [All services](README.md)
