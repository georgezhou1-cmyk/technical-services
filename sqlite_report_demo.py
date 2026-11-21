"""Compare two query plans on the same synthetic order history. Python 3.9+."""
import sqlite3


def read_report(db):
    query = """SELECT id, created_day FROM orders WHERE account_id = ?
               ORDER BY created_day DESC, id DESC LIMIT 3"""
    plan = [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + query, (7,))]
    return plan, list(db.execute(query, (7,)))


if __name__ == "__main__":
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, account_id INTEGER, created_day INTEGER)")
    db.executemany("INSERT INTO orders VALUES (?, ?, ?)",
                   ((n, n % 40, n // 200) for n in range(1, 20001)))
    before, original = read_report(db)
    db.execute("CREATE INDEX orders_recent ON orders(account_id, created_day DESC, id DESC)")
    after, indexed = read_report(db)
    assert original == indexed == [(19967, 99), (19927, 99), (19887, 99)]
    assert any("SCAN orders" in step for step in before)
    assert any("orders_recent" in step for step in after)
    print("Before:", " / ".join(before))
    print("After: ", " / ".join(after))
    print("Same three rows:", indexed)
    db.close()
