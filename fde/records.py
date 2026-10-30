"""Validated records and a SQLite boundary, reusable without a web framework."""

from contextlib import closing, contextmanager
from pathlib import Path
import sqlite3
import unicodedata

STATES = ("open", "active", "done")
TRANSITIONS = {"open": "active", "active": "done"}


class NotFound(LookupError):
    pass


class Conflict(ValueError):
    pass


def validate_state(value):
    if value not in STATES:
        raise ValueError("status must be open, active, or done")
    return value


def validate_record(value):
    if not isinstance(value, dict) or not {"title"} <= value.keys() or value.keys() - {"title", "status"}:
        raise ValueError("record requires title and optional status only")
    title = value["title"]
    if not isinstance(title, str):
        raise ValueError("title must be text")
    title = title.strip()
    if not 1 <= len(title) <= 200 or any(unicodedata.category(c).startswith("C") for c in title):
        raise ValueError("title must contain 1..200 characters without controls")
    return {"title": title, "status": validate_state(value.get("status", "open"))}


def validate_id(value):
    if type(value) is not int or not 1 <= value <= 2**63 - 1:
        raise ValueError("id must be a positive SQLite integer")


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
                status TEXT NOT NULL CHECK(status IN ('open', 'active', 'done'))
            )""")

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.path, timeout=5)) as db:
            db.row_factory = sqlite3.Row
            with db:
                yield db

    def add(self, value):
        return self.add_many([value])[0]

    def add_many(self, values):
        records = [validate_record(value) for value in values]
        result = []
        with self.connect() as db:
            for record in records:
                cursor = db.execute("INSERT INTO records(title, status) VALUES (?, ?)", (record["title"], record["status"]))
                result.append({"id": cursor.lastrowid, **record})
        return result

    def get(self, record_id):
        validate_id(record_id)
        with self.connect() as db:
            row = db.execute("SELECT id, title, status FROM records WHERE id = ?", (record_id,)).fetchone()
        if row is None:
            raise NotFound("record not found")
        return dict(row)

    def transition(self, record_id, status):
        validate_id(record_id)
        validate_state(status)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id, title, status FROM records WHERE id = ?", (record_id,)).fetchone()
            if row is None:
                raise NotFound("record not found")
            if TRANSITIONS.get(row["status"]) != status:
                raise Conflict("allowed transitions: open -> active -> done")
            db.execute("UPDATE records SET status = ? WHERE id = ?", (status, record_id))
            return {**dict(row), "status": status}

    def list(self, *, q="", status=None, order="id", limit=100, offset=0):
        if order not in ("id", "title"):
            raise ValueError("order must be id or title")
        if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or not 0 <= offset <= 2**63 - 1:
            raise ValueError("limit must be 1..100 and offset a nonnegative SQLite integer")
        if not isinstance(q, str) or len(q) > 200:
            raise ValueError("q must be at most 200 characters")
        clauses, params = [], []
        if q:
            escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            clauses.append("title LIKE ? ESCAPE '\\'")
            params.append(f"%{escaped}%")
        if status is not None:
            clauses.append("status = ?")
            params.append(validate_state(status))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        # order is an allowlisted identifier; all values are bound parameters.
        with self.connect() as db:
            rows = db.execute(f"SELECT id, title, status FROM records{where} ORDER BY {order}, id LIMIT ? OFFSET ?", (*params, limit, offset)).fetchall()
        return [dict(row) for row in rows]

    def summary(self):
        with self.connect() as db:
            counts = db.execute("SELECT status, count(*) AS n FROM records GROUP BY status").fetchall()
        return {**dict.fromkeys(STATES, 0), **{row["status"]: row["n"] for row in counts}}
