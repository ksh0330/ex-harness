from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import http.client
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

from examples.web import make_server
from fde.records import Conflict, Store

ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.db = self.work / "records.sqlite3"

    def cli(self, *args, cwd=ROOT):
        return subprocess.run([sys.executable, "-m", "examples.batch", *map(str, args)], cwd=cwd, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})

    def start_server(self):
        server = make_server(self.db, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.assertEqual(server.server_address[0], "0.0.0.0")
        self.assertGreater(server.server_port, 0)
        def stop():
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
        self.addCleanup(stop)
        return server

    def request(self, server, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        payload = json.dumps(body) if body is not None else None
        try:
            connection.request(method, path, payload, headers or {"Content-Type": "application/json"})
            response = connection.getresponse()
            raw = response.read()
            content = json.loads(raw) if "application/json" in response.getheader("Content-Type", "") else raw
            return response.status, content
        finally:
            connection.close()

    def test_http_full_flow_persists_and_batch_exports_same_records(self):
        server = self.start_server()
        self.assertEqual(self.request(server, "GET", "/health"), (200, {"status": "ok"}))
        status, html = self.request(server, "GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("동네 수리 접수".encode(), html)
        status, item = self.request(server, "POST", "/api/items", {"title": "  brake repair  "})
        self.assertEqual(status, 201)
        path = f"/api/items/{item['id']}"
        self.assertEqual(self.request(server, "PATCH", path, {"status": "done"})[0], 409)
        self.assertEqual(self.request(server, "PATCH", path, {"status": "active"})[0], 200)
        self.assertEqual(self.request(server, "PATCH", path, {"status": "done"})[1]["status"], "done")
        self.assertEqual(self.request(server, "GET", "/api/items?q=brake&status=done&order=title&limit=1&offset=0")[1]["items"][0]["title"], "brake repair")
        second_server = self.start_server()
        self.assertEqual(self.request(second_server, "GET", "/api/summary")[1], {"open": 0, "active": 0, "done": 1})
        result = self.cli("export", "--db", self.db)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["records"][0]["status"], "done")

    def test_http_invalid_input_never_creates_a_record(self):
        server = self.start_server()
        for body in ({}, [], {"title": " "}, {"title": "x", "role": "admin"}, {"title": "x", "status": "bad"}):
            with self.subTest(body=body):
                self.assertEqual(self.request(server, "POST", "/api/items", body)[0], 400)
        self.assertEqual(self.request(server, "POST", "/api/items", {"title": "x"}, {"Content-Type": "text/plain"})[0], 400)
        self.assertEqual(self.request(server, "POST", "/api/items", {"title": "x"}, {"Content-Type": "application/json", "Origin": "https://evil.example"})[0], 400)
        self.assertEqual(self.request(server, "POST", "/api/items", {"title": "x" * 17000})[0], 400)
        for path in ("/api/items?limit=0", "/api/items?offset=-1", "/api/items?order=evil", "/api/items?q=a&q=b", "/api/items?role=admin"):
            self.assertEqual(self.request(server, "GET", path)[0], 400)
        self.assertEqual(self.request(server, "PATCH", "/api/items/999", {"status": "active"})[0], 404)
        self.assertEqual(self.request(server, "GET", "/unknown")[0], 404)
        self.assertEqual(self.request(server, "GET", "/api/items")[1], {"items": []})

    def test_http_bad_json_and_database_failure_have_controlled_errors(self):
        server = self.start_server()
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            connection.request("POST", "/api/items", b"{broken", {"Content-Type": "application/json"})
            response = connection.getresponse()
            self.assertEqual(response.status, 400)
            self.assertIn("error", json.loads(response.read()))
        finally:
            connection.close()
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("DROP TABLE records")
        self.assertEqual(self.request(server, "GET", "/api/items"), (503, {"error": "database unavailable"}))

    def test_csv_import_export_and_no_overwrite(self):
        source = ROOT / "examples/data/archive.csv"
        result = self.cli("import", source, "--db", self.db)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"imported": 3})
        report = self.work / "report.json"
        result = self.cli("export", "--db", self.db, "--output", report)
        self.assertEqual(result.returncode, 0, result.stderr)
        content = report.read_bytes()
        self.assertEqual(json.loads(content)["summary"], {"open": 1, "active": 1, "done": 1})
        result = self.cli("export", "--db", self.db, "--output", report)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report.read_bytes(), content)

    def test_csv_late_invalid_row_preserves_existing_data(self):
        Store(self.db).add({"title": "keep"})
        bad = self.work / "bad.csv"
        bad.write_text("name,stage\n" + "good,queued\n" * 100 + "bad,unknown\n", encoding="utf-8")
        result = self.cli("import", bad, "--db", self.db)
        self.assertEqual(result.returncode, 2)
        self.assertEqual([r["title"] for r in Store(self.db).list()], ["keep"])
        fresh = self.work / "fresh.sqlite3"
        self.assertEqual(self.cli("import", bad, "--db", fresh).returncode, 2)
        self.assertFalse(fresh.exists())

    def test_csv_headers_limits_and_missing_database(self):
        bad = self.work / "bad.csv"
        for content in ("name,name\nx,x\n", "name,stage\nx\n", "name,stage\nx,queued,extra\n", "name,stage\n" + "x,queued\n" * 1001, "x" * 1_000_001):
            bad.write_text(content, encoding="utf-8")
            result = self.cli("import", bad, "--db", self.db)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertFalse(self.db.exists())
        self.assertEqual(self.cli("export", "--db", self.db).returncode, 2)
        self.assertFalse(self.db.exists())

    def test_export_includes_more_than_one_page(self):
        Store(self.db).add_many([{"title": str(i)} for i in range(205)])
        result = self.cli("export", "--db", self.db)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)["records"]), 205)

    def test_database_error_mid_batch_rolls_back(self):
        store = Store(self.db)
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("CREATE TRIGGER reject_bad BEFORE INSERT ON records WHEN NEW.title = 'reject' BEGIN SELECT RAISE(ABORT, 'test rejection'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            store.add_many([{"title": "first"}, {"title": "reject"}])
        self.assertEqual(store.list(), [])

    def test_concurrent_transitions_allow_one_winner(self):
        store = Store(self.db)
        record = store.add({"title": "one"})
        def attempt(_):
            try:
                store.transition(record["id"], "active")
                return "changed"
            except Conflict:
                return "conflict"
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(attempt, range(2)))
        self.assertEqual(sorted(outcomes), ["changed", "conflict"])

    def test_optional_installed_kit_runs_outside_source(self):
        target = self.work / "target"
        result = subprocess.run([sys.executable, str(ROOT / "tools/install.py"), "--target", str(target), "--apply", "--with-examples"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        kit = target / ".harness/kit"
        result = self.cli("import", "examples/data/archive.csv", "--db", "archive.sqlite3", cwd=kit)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["imported"], 3)

    def test_web_command_prints_actual_port_and_serves_health(self):
        process = subprocess.Popen([sys.executable, "-m", "examples.web", "--db", str(self.db), "--port", "0"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            line = process.stdout.readline().strip()
            self.assertRegex(line, r"^Listening on 0\.0\.0\.0:[1-9][0-9]*$")
            port = int(line.rsplit(":", 1)[1])
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            try:
                connection.request("GET", "/health")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.loads(response.read()), {"status": "ok"})
            finally:
                connection.close()
        finally:
            process.terminate()
            process.communicate(timeout=5)


if __name__ == "__main__":
    unittest.main()
