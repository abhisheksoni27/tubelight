from collections import deque
from datetime import datetime
from pathlib import Path
import json

from flask import Flask, jsonify, request, send_from_directory

APP_ROOT = Path(__file__).resolve().parent
LOG_FILE = APP_ROOT / "example.log"

app = Flask(__name__, static_folder="static", static_url_path="")

LEVEL_STYLES = {
    "DEBUG": "debug",
    "INFO": "info",
    "SUCCESS": "success",
    "WARNING": "warning",
    "ERROR": "error",
    "CRITICAL": "critical",
}


def parse_log_line(line):
    if not line or line.isspace():
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

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


def tail_lines(path, max_lines):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", errors="replace") as f:
        return list(deque(f, maxlen=max_lines * 4))


def filter_records(records, query, level):
    query = (query or "").strip().lower()
    level = (level or "").strip().upper()

    if not query and not level:
        return records

    matched = []
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

        matched.append(record)

    return matched


def parse_timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/logs")
def get_logs():
    if not LOG_FILE.exists():
        return jsonify({"error": "example.log not found", "records": []}), 404

    limit = request.args.get("limit", "250")
    query = request.args.get("q", "")
    level = request.args.get("level", "")

    try:
        limit = min(max(int(limit), 1), 2000)
    except ValueError:
        limit = 250

    raw_lines = tail_lines(LOG_FILE, limit)
    parsed = [parse_log_line(line) for line in raw_lines]
    parsed = [entry for entry in parsed if entry]

    filtered = filter_records(parsed, query, level)
    filtered = list(reversed(filtered))
    filtered = filtered[:limit]

    return jsonify(
        {
            "records": filtered,
            "count": len(filtered),
            "query": query,
            "level": level.upper(),
            "limit": limit,
        }
    )


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
