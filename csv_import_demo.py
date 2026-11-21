"""Preview an order-import reconciliation using fictional data. Python 3.9+."""
import csv
from collections import defaultdict
from decimal import Decimal
from io import StringIO


def reconcile(source):
    orders = defaultdict(list)
    for row in csv.DictReader(source):
        orders[row["order_id"].strip()].append(Decimal(row["amount"].strip()))
    clean, conflicts = {}, {}
    repeats = 0
    for order_id, amounts in orders.items():
        if len(set(amounts)) == 1:
            clean[order_id] = amounts[0]
            repeats += len(amounts) - 1
        else:
            conflicts[order_id] = amounts
    return clean, conflicts, repeats


if __name__ == "__main__":
    sample = StringIO("order_id,amount\n0007,19.50\n 0007,19.5\n0012,12.00\n0012,21.00\n0015,4.25\n")
    clean, conflicts, repeats = reconcile(sample)
    assert list(clean) == ["0007", "0015"]
    assert sum(clean.values()) == Decimal("23.75")
    assert conflicts == {"0012": [Decimal("12.00"), Decimal("21.00")]}
    assert repeats == 1
    print("Ready to import: 0007, 0015 | total: $23.75")
    print("Duplicate rows removed: 1 | conflicting order held for review: 0012")
