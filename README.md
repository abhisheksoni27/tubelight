# lightbulb

A smart browser-based log viewer for local app logs.

Lightbulb turns any local file into a searchable, live-updating table in your browser. It is ideal for development, debugging, and monitoring your app logs without needing `tail -f`.

## Features

- Render local log files in a polished browser UI
- Search by message, module, file path, or log contents
- Filter by level: `DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`, `CRITICAL`
- Date-range filtering with start/end datetime controls
- Auto-scroll to newest logs when live mode is enabled
- Click any row to expand raw log details
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
pip install lightbulb
```

## Quick start

Run the viewer with the default `example.log` in your current directory:

```bash
lightbulb
```

Or point it at a custom log file:

```bash
lightbulb --log-file /path/to/your/app.log
```

You can also use the environment variable:

```bash
LOG_FILE=/path/to/your/app.log lightbulb
```

Change the port if needed:

```bash
lightbulb --port 8080
```

Filter the current view by date range:

```bash
lightbulb --log-file /path/to/your/app.log
```

Then use the start/end controls in the browser to restrict the log window to a specific time range.

Open the viewer:

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

- `lightbulb/` — package source
- `lightbulb/static/` — browser UI assets
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
