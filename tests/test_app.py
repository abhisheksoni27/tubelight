import json
import tempfile
import unittest
from pathlib import Path

from lightbulb.server import create_app


class VisualLogsSmokeTest(unittest.TestCase):
    def test_api_config_returns_log_path(self):
        app = create_app(log_file=Path("/tmp/does-not-exist.log"))
        client = app.test_client()

        response = client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.get_json() or {}
        self.assertIn("logFile", data)
        self.assertEqual(data["logFile"], str(Path("/tmp/does-not-exist.log")))

    def test_root_serves_html(self):
        app = create_app(log_file=Path("/tmp/does-not-exist.log"))
        client = app.test_client()

        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Visual Logs</title>", response.get_data(as_text=True))

    def test_date_range_filtering(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            first = {
                "text": "2026-04-13 00:00:00.000 | INFO | first log",
                "record": {
                    "time": {"repr": "2026-04-13 00:00:00.000000+00:00"},
                    "level": {"name": "INFO"},
                    "message": "first log",
                    "module": "test",
                    "file": {"name": "test.py", "path": "test.py"},
                    "line": 1,
                    "process": {"id": 1},
                    "thread": {"name": "MainThread"},
                },
            }
            second = {
                "text": "2026-04-13 02:00:00.000 | INFO | second log",
                "record": {
                    "time": {"repr": "2026-04-13 02:00:00.000000+00:00"},
                    "level": {"name": "INFO"},
                    "message": "second log",
                    "module": "test",
                    "file": {"name": "test.py", "path": "test.py"},
                    "line": 2,
                    "process": {"id": 1},
                    "thread": {"name": "MainThread"},
                },
            }
            tmp.write(json.dumps(first) + "\n")
            tmp.write(json.dumps(second) + "\n")
            tmp.flush()

        app = create_app(log_file=Path(tmp.name))
        client = app.test_client()

        response = client.get(
            "/api/logs?start=2026-04-13T01:00%2B00:00&end=2026-04-13T03:00%2B00:00&limit=100"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json() or {}
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["records"][0]["message"], "second log")


if __name__ == "__main__":
    unittest.main()
