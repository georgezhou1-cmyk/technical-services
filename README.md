# CSV import repair, API quickstarts and SQLite query tuning

Three small Python tools for teams working with order exports, public APIs and slow reports. Run the examples for free with Python 3.9+ and its standard library. Each example also shows the deliverable for a fixed-price service.

| When you need help | Try the example | Fixed-price service |
| --- | --- | --- |
| A CSV importer rejects orders or double-counts revenue | Reconcile five rows to two orders worth $23.75, one duplicate and two rows requiring review | [CSV import repair · $49](csv-import-repair.md) |
| Your users struggle to make the first successful API request | Read tag names and commit IDs offline, then try the same parser against a live GitHub repository | [API quickstart guide · $99](api-quickstart.md) |
| A SQLite report scans and sorts more rows than it returns | Compare query plans and verify that a composite index preserves the exact order of results | [SQLite report tuning · $129](sqlite-report-tuning.md) |

## Try all three offline

Download the repository or clone it, then run these commands from its directory.

```sh
python3 csv_import_demo.py --export sample-orders.zip
python3 api_quickstart_demo.py --offline
python3 sqlite_report_demo.py --rows 20000 --account 7 --limit 3
python3 -m unittest -v
```

Open the ZIP to see `ready.csv`, `review.csv` and `summary.json`. The CSV tool also accepts a local two-column order file. The SQLite fixture lives in memory. For a live API example, run `python3 api_quickstart_demo.py --repo python/cpython`.

## Request a service

Each service page lists its scope, deliverables and a free inquiry link. GitHub issues are public. Share a fictional example and the outcome you need. Scope, timing and payment arrangements are confirmed before paid work begins. The code and guides are AI-assisted and checked with reproducible examples.
