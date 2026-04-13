import unittest
from pathlib import Path

from visuallogs.server import create_app


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


if __name__ == "__main__":
    unittest.main()
