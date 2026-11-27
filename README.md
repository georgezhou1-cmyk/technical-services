# Fix an order import, document an API, or tune a SQLite report

Order `0012` appears twice in an export. One row says **$12**, the other **$21**. Which amount should reach the import? The CSV example holds both rows for review, keeps their original values, and adds up the orders that can go through.

| In the five-row sample | What goes into the handoff |
| --- | --- |
| `0007` appears as $19.50 and $19.5 | One $19.50 order in `ready.csv`. Its leading zeros survive. |
| `0012` has two different amounts | Both original rows in `review.csv`, each with a reason. |
| `0015` appears once at $4.25 | It joins `0007` in the ready file. The reconciled total in `summary.json` is **$23.75**. |

## Choose the handoff you need

| If you're stuck here | What you receive | Scope and free inquiry |
| --- | --- | --- |
| Your order export fails or the total looks wrong | A cleaned CSV, a review file, a rerunnable script and a total you can reconcile. Covers one layout, up to 20 columns and 50,000 rows, for one destination. | [CSV import repair · $49](csv-import-repair.md#request-this-service) |
| A developer can read your API docs but still can't make the first request | A quickstart for one documented read endpoint, with copyable curl, runnable Python, the expected result and fixes for two common failures. | [API quickstart · $99](api-quickstart.md#request-this-service) |
| A SQLite report scans thousands of rows to return a handful | A before-and-after query plan, proposed SQL and a check that the same rows come back in the same order. Covers one read-only query on up to three tables. | [SQLite report tuning · $129](sqlite-report-tuning.md#request-this-service) |

Each service page has a free inquiry link. Describe the outcome you need using fictional rows, a public API reference or a sample query. GitHub issues are public. We agree on scope, timing and payment arrangements before paid work begins.

## Try the work before you ask

Run these examples from a copy of this repository with Python 3.9+ and its standard library. All three work offline.

```sh
python3 csv_import_demo.py --export sample-orders.zip
python3 api_quickstart_demo.py --offline
python3 sqlite_report_demo.py --rows 20000 --account 7 --limit 3
python3 -m unittest -v
```

- **CSV** — Open the ZIP to inspect the accepted rows, the disputed amounts and the final count. Choose a fresh ZIP filename for each run. [CSV example and input format](csv-import-repair.md)
- **API** — The first fixture row prints `demo-v2` and `aaaaaaaaaaaa`. You can then run the same parser against the public CPython repository. [API example and live command](api-quickstart.md)
- **SQLite** — On 20,000 synthetic orders, the original plan scans and sorts. The indexed plan looks up one account and returns the same three ordered rows. [Query plans and workload options](sqlite-report-tuning.md)

The code and guides are AI-assisted and checked against reproducible examples.
