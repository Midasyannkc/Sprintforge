"""Golden dataset for the eval harness: every real ticket in
data/tickets/tickets.json, labeled with the expected behavior the FIXED
pipeline should exhibit. Labels are derived directly from each ticket's
category (assigned when the ticket was authored, see SOURCE_DISCLOSURE.md),
not from a model's own output.
"""
import json
import os

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tickets", "tickets.json")


def load_golden_dataset():
    with open(TICKETS_PATH) as f:
        tickets = json.load(f)["tickets"]

    golden = []
    for t in tickets:
        cat = t["category"]
        expect_escalated = cat in ("injection", "weak_retrieval")
        expect_grounded = cat not in ("weak_retrieval", "injection")
        golden.append({
            "id": t["id"],
            "text": t["text"],
            "category": cat,
            "expect_escalated": expect_escalated,
            "expect_grounded": expect_grounded,
        })
    return golden


if __name__ == "__main__":
    for row in load_golden_dataset():
        print(row["id"], row["category"], "expect_escalated=", row["expect_escalated"])
