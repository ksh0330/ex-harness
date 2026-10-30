"""Media archive CSV import and JSON export, sharing the record capability."""

import argparse
import csv
import json
from pathlib import Path
import sqlite3
import sys

from fde.records import Store, validate_record

STAGE_MAP = {"queued": "open", "processing": "active", "complete": "done"}


def read_csv(path):
    if path.stat().st_size > 1_000_000:
        raise ValueError("CSV exceeds 1 MB")
    records = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != ["name", "stage"]:
            raise ValueError("CSV header must be name,stage")
        for line, row in enumerate(reader, start=2):
            if len(records) >= 1000:
                raise ValueError("CSV exceeds 1000 records")
            if None in row or row["stage"] not in STAGE_MAP:
                raise ValueError(f"CSV row {line}: invalid columns or stage")
            records.append(validate_record({"title": row["name"], "status": STAGE_MAP[row["stage"]]}))
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    incoming = sub.add_parser("import", help="validate entire CSV before a single transaction")
    incoming.add_argument("input", type=Path)
    incoming.add_argument("--db", type=Path, required=True)
    outgoing = sub.add_parser("export", help="JSON to stdout, or a new file without overwrite")
    outgoing.add_argument("--db", type=Path, required=True)
    outgoing.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            records = read_csv(args.input)  # No database creation on invalid input.
            result = Store(args.db).add_many(records)
            print(json.dumps({"imported": len(result)}))
        else:
            if not args.db.is_file():
                raise ValueError("database does not exist")
            store = Store(args.db)
            records, offset = [], 0
            while page := store.list(offset=offset):
                records.extend(page)
                offset += len(page)
            content = json.dumps({"records": records, "summary": store.summary()}, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                with args.output.open("x", encoding="utf-8") as stream:
                    stream.write(content)
            else:
                print(content, end="")
        return 0
    except (OSError, ValueError, csv.Error, sqlite3.Error) as exc:
        print(f"batch: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
