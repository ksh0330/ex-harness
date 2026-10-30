from pathlib import Path
import tempfile
import unittest

from fde.records import Conflict, NotFound, Store, validate_record


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "records.sqlite3"
        self.store = Store(self.db)

    def test_validate_normalizes_and_rejects_invalid_input(self):
        self.assertEqual(validate_record({"title": "  수리 요청  "}), {"title": "수리 요청", "status": "open"})
        for value in (None, [], {}, {"title": " "}, {"title": 7}, {"title": "a" * 201},
                      {"title": "x\nheader"}, {"title": "x", "status": "unknown"},
                      {"title": "x", "id": 1}, {"title": "x", "status": None}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_record(value)

    def test_persistence_and_allowed_state_transitions(self):
        record = self.store.add({"title": "접수"})
        self.assertEqual(Store(self.db).get(record["id"]), record)
        with self.assertRaises(Conflict):
            self.store.transition(record["id"], "done")
        self.assertEqual(self.store.get(record["id"])["status"], "open")
        self.store.transition(record["id"], "active")
        self.assertEqual(self.store.transition(record["id"], "done")["status"], "done")
        with self.assertRaises(Conflict):
            self.store.transition(record["id"], "open")
        with self.assertRaises(NotFound):
            self.store.transition(999, "active")

    def test_batch_is_atomic_and_empty_batch_is_valid(self):
        self.store.add({"title": "original"})
        with self.assertRaises(ValueError):
            self.store.add_many([{"title": "valid"}, {"title": "bad", "status": "invalid"}])
        self.assertEqual([r["title"] for r in self.store.list()], ["original"])
        self.assertEqual(self.store.add_many([]), [])

    def test_search_filter_sort_and_page_are_literal(self):
        self.store.add_many([{"title": "B_100%", "status": "active"}, {"title": "A"}, {"title": "C"}])
        self.assertEqual(len(self.store.list(q="100%")), 1)
        self.assertEqual(len(self.store.list(q="_")), 1)
        self.assertEqual(self.store.list(q="' OR 1=1 --"), [])
        self.assertEqual(self.store.list(status="active")[0]["title"], "B_100%")
        self.assertEqual(self.store.list(order="title", limit=1, offset=1)[0]["title"], "B_100%")
        self.assertEqual(self.store.summary(), {"open": 2, "active": 1, "done": 0})
        for kwargs in ({"order": "id; DROP TABLE records"}, {"limit": 0}, {"limit": True}, {"offset": -1}, {"status": "x"}, {"q": "x" * 201}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.store.list(**kwargs)

    def test_identifier_validation(self):
        for value in (True, 0, -1, "1", 2**64):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.store.get(value)


if __name__ == "__main__":
    unittest.main()
