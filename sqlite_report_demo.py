"""Compare query plans and result order on a disposable SQLite fixture. Python 3.9+."""
import argparse
import sqlite3
from contextlib import closing
from statistics import median
from time import perf_counter_ns

QUERY = """SELECT id, created_day FROM orders WHERE account_id = ?
           ORDER BY created_day DESC, id DESC LIMIT ?"""
INDEX = "CREATE INDEX orders_recent ON orders(account_id, created_day DESC, id DESC)"


def read_report(db, account=7, limit=3):
    args = (account, limit)
    plan = [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + QUERY, args)]
    return plan, list(db.execute(QUERY, args))


def measure(db, account, limit):
    # Warm the statement before collecting seven complete fetches.
    plan, rows = read_report(db, account, limit)
    samples = []
    for _ in range(7):
        start = perf_counter_ns()
        list(db.execute(QUERY, (account, limit)))
        samples.append((perf_counter_ns() - start) / 1_000_000)
    return plan, rows, median(samples)


def compare(size, account, limit):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, account_id INTEGER, created_day INTEGER)")
        db.executemany("INSERT INTO orders VALUES (?, ?, ?)",
                       ((n, n % 40, n // 200) for n in range(1, size + 1)))
        before = measure(db, account, limit)
        db.execute(INDEX)
        after = measure(db, account, limit)
        if before[1] != after[1]:
            raise RuntimeError("Adding the index changed the ordered report.")
        return before, after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=20000, help="synthetic rows, from 0 to 500000")
    parser.add_argument("--account", type=int, default=7, help="fixture account 0 to 39")
    parser.add_argument("--limit", type=int, default=3, help="number of results, from 1 to 100")
    args = parser.parse_args()
    if not (0 <= args.rows <= 500000 and 0 <= args.account <= 39 and 1 <= args.limit <= 100):
        parser.error("Use --rows 0..500000, --account 0..39 and --limit 1..100.")
    before, after = compare(args.rows, args.account, args.limit)
    print(f"SQLite {sqlite3.sqlite_version} | {args.rows} synthetic rows | account {args.account}")
    for label, result in (("Before", before), ("After", after)):
        print(f"{label}: {' / '.join(result[0])} | median of 7 warm reads: {result[2]:.3f} ms")
    print(f"Identical ordered rows ({len(after[1])}): {after[1]}")


if __name__ == "__main__":
    main()
