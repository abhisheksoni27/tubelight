from __future__ import annotations

import argparse
import os

from .server import create_app


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Visual Logs viewer.")
    parser.add_argument("--log-file", "-l", help="Path to the log file to watch")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the web server"
    )
    parser.add_argument(
        "--port", type=int, default=5111, help="Port to bind the web server"
    )
    args = parser.parse_args(argv)

    env_log_file = os.environ.get("LOG_FILE")
    app = create_app(args.log_file or env_log_file)

    print(f"Watching log file: {app.config['LOG_FILE']}")
    app.run(host=args.host, port=args.port, debug=True)
