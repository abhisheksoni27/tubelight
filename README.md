# Visual Logs

A lightweight browser-based local log viewer for JSON and Loguru-style logs.

Visual Logs turns any local file into a searchable, live-updating table in your browser. It is ideal for development, debugging, and monitoring your app logs without needing `tail -f`.

## Features

- Render local log files in a polished browser UI
- Search by message, module, file path, or log contents
- Filter by level: `DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`, `CRITICAL`
- Live refresh support with manual refresh fallback
- Simple CLI and environment variable configuration
- Ready for pip packaging and distribution

## Installation

Install the package from source or once published on PyPI.

### From source

```bash
uv run python -m pip install -e .
```

### From PyPI

```bash
pip install visuallogs
```

## Quick start

Run the viewer with the default `example.log` in your current directory:

```bash
visuallogs
```

Or point it at a custom log file:

```bash
visuallogs --log-file /path/to/your/app.log
```

You can also use the environment variable:

```bash
LOG_FILE=/path/to/your/app.log visuallogs
```

Change the port if needed:

```bash
visuallogs --port 8080
```

Then open:

```text
http://127.0.0.1:5111
```

## Packaging for pip

Build source and wheel distributions:

```bash
uv run python -m pip install build
uv run python -m build
```

Publish to PyPI using Twine:

```bash
uv run python -m pip install twine
uv run python -m twine upload dist/*
```

## Testing

Run the included smoke tests:

```bash
uv run python -m unittest
```

## Project layout

- `visuallogs/` — package source
- `visuallogs/static/` — browser UI assets
- `app.py` — local launch wrapper
- `pyproject.toml` — packaging metadata
- `README.md` — documentation
- `LICENSE` — MIT license

## Contributing

Contributions are welcome. Open an issue or send a pull request with:

- bug reports
- UX improvements
- log format support
- authentication / multi-user features

## License

MIT
