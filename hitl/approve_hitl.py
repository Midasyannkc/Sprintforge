"""Real CLI a human reviewer uses to see pending HITL items and resolve them.
Usage:
    python3 hitl/approve_hitl.py list
    python3 hitl/approve_hitl.py resolve <item_id> approved|rejected
"""
import sys

from hitl.hitl_queue import list_pending, resolve, stats


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "list":
        pending = list_pending()
        print(f"{len(pending)} pending item(s):")
        for item in pending:
            print(f"  [{item['id']}] source={item['source']} reason={item['reason']!r}")
            print(f"       payload={item['payload']}")
        print("stats:", stats())
    elif cmd == "resolve":
        item_id, resolution = sys.argv[2], sys.argv[3]
        ok = resolve(item_id, resolution)
        print(f"resolved {item_id} -> {resolution}: {'OK' if ok else 'NOT FOUND'}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
