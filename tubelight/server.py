from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path
import json
import re

from flask import Flask, jsonify, request, send_from_directory

PACKAGE_ROOT = Path(__file__).resolve().parent
LEVEL_STYLES = {
    "DEBUG": "debug",
    "INFO": "info",
    "SUCCESS": "success",
    "WARNING": "warning",
    "ERROR": "error",
    "CRITICAL": "critical",
}


LOGURU_LINE_RE = re.compile(
    r"^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s*\|\s*(?P<level>\w+)"
    r"\s*\|\s*(?P<module>[^:]+):(?P<function>[^:]+):(?P<line>\d+) - (?P<message>.*)$"
)


def parse_log_line(line: str) -> dict | None:
    if not line or line.isspace():
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        data = None

    if data:
        record = data.get("record", {})
        level = record.get("level", {})
        file_info = record.get("file", {})
        process_info = record.get("process", {})
        thread_info = record.get("thread", {})

        return {
            "time": record.get("time", {}).get("repr")
            or data.get("text", "").split(" | ", 1)[0],
            "level": level.get("name", "UNKNOWN"),
            "icon": level.get("icon", ""),
            "message": record.get("message", ""),
            "module": record.get("module", ""),
            "file": file_info.get("name", ""),
            "path": file_info.get("path", ""),
            "line": record.get("line", ""),
            "process": process_info.get("id"),
            "thread": thread_info.get("name", ""),
            "raw": data.get("text", line).rstrip("\n"),
            "levelClass": LEVEL_STYLES.get(level.get("name", ""), "unknown"),
        }

    match = LOGURU_LINE_RE.match(line.strip())
    if match:
        groups = match.groupdict()
        return {
            "time": groups["time"],
            "level": groups["level"],
            "icon": "",
            "message": groups["message"],
            "module": groups["module"],
            "file": "",
            "path": "",
            "line": groups["line"],
            "process": None,
            "thread": "",
            "raw": line.rstrip("\n"),
            "levelClass": LEVEL_STYLES.get(groups["level"], "unknown"),
        }

    return None


def tail_lines(path: Path, max_lines: int) -> list[str]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", errors="replace") as f:
        return list(deque(f, maxlen=max_lines * 4))


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        timestamp = datetime.fromisoformat(value.replace(" ", "T"))
    except ValueError:
        return None

    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=datetime.now().astimezone().tzinfo)

    return timestamp


def filter_records(
    records: list[dict],
    query: str,
    level: str,
    start: datetime | None,
    end: datetime | None,
) -> list[dict]:
    query = (query or "").strip().lower()
    level = (level or "").strip().upper()

    if start and end and start > end:
        start, end = end, start

    matched: list[dict] = []
    for record in records:
        if level and record["level"] != level:
            continue

        if query:
            searchable = " ".join(
                [
                    str(record.get(key, ""))
                    for key in ["time", "level", "message", "module", "file", "raw"]
                ]
            ).lower()
            if query not in searchable:
                continue

        if start or end:
            timestamp = parse_timestamp(record["time"])
            if timestamp is None:
                continue
            if start and timestamp < start:
                continue
            if end and timestamp > end:
                continue

        matched.append(record)

    return matched


def resolve_log_path(path_string: str | None = None) -> Path:
    if path_string:
        candidate = Path(path_string).expanduser()
        return (
            candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()
        )

    return Path.cwd() / "example.log"


def create_app(log_file: str | Path | None = None) -> Flask:
    app = Flask(
        __name__, static_folder=str(PACKAGE_ROOT / "static"), static_url_path=""
    )
    app.config["LOG_FILE"] = resolve_log_path(log_file)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/api/logs")
    def get_logs():
        log_path = Path(app.config["LOG_FILE"])
        if not log_path.exists():
            return (
                jsonify({"error": f"Log file not found: {log_path}", "records": []}),
                404,
            )

        limit = request.args.get("limit", "250")
        query = request.args.get("q", "")
        level = request.args.get("level", "")
        start_date = request.args.get("start", "")
        end_date = request.args.get("end", "")

        try:
            limit = min(max(int(limit), 1), 2000)
        except ValueError:
            limit = 250

        raw_lines = tail_lines(log_path, limit)
        parsed = [parse_log_line(line) for line in raw_lines]
        parsed = [entry for entry in parsed if entry]

        start_dt = parse_timestamp(start_date)
        end_dt = parse_timestamp(end_date)

        filtered = filter_records(parsed, query, level, start_dt, end_dt)
        filtered = filtered[:limit]

        return jsonify(
            {
                "records": filtered,
                "count": len(filtered),
                "query": query,
                "level": level.upper(),
                "limit": limit,
                "start": start_date,
                "end": end_date,
            }
        )

    @app.route("/static/<path:filename>")
    def static_files(filename: str):
        return send_from_directory(app.static_folder, filename)

    @app.route("/api/config")
    def get_config():
        return jsonify({"logFile": str(app.config["LOG_FILE"])})

    return app
