# Visual Logs Viewer

A simple local log viewer for `example.log`.

## Run locally

1. Install dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Start the app:

   ```bash
   python app.py
   ```

3. Open the browser:

   ```
   http://127.0.0.1:5000
   ```

## Features

- Reads the last log lines from `example.log`
- Search by message, module, file, or level
- Filter by log level
- Live refresh toggle
- Clean table-based layout in the browser

## Next steps

- Add auto-scroll to newest entries
- Add row expansion for raw JSON payload
- Add timezone / date range filters
