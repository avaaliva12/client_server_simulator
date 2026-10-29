# Client–Server Communication Simulator

A local Flask learning app with live HTTP responses, SQLite request logging, request history, response-time analytics, and Chart.js charts. No account or API key is needed.

## Windows setup
1. Extract the ZIP and open the `client_server_simulator` folder. Type `powershell` in File Explorer's address bar and press Enter.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If activation is blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.
3. Install and run:
   ```powershell
   py -m pip install -r requirements.txt
   py app.py
   ```
4. Visit http://127.0.0.1:5000. Leave PowerShell open; press Ctrl+C to stop. Python 3.9+ is required. Bootstrap and Chart.js use public CDNs, so internet is needed to load the styling and charts.

SQLite creates `request_logs.db` automatically. Delete it while the app is stopped to reset history.

## Demo endpoints
- GET `/api/hello`, `/api/devices`, `/api/status` return 200.
- POST `/api/echo` echoes a JSON object with 201; invalid/missing JSON gets 400.
- GET `/api/not-found` demonstrates 404. GET `/api/server-error` safely demonstrates 500 without crashing Flask.
- PUT and DELETE are available in the simulator and return a helpful response for unsupported combinations.

Requests are made to real Flask routes, timed server-side with `time.perf_counter()`, and stored with status, result, and timestamp. Page and dashboard requests are not logged as simulated traffic. The status page checks this Flask app, not your network or Wi-Fi.

## Project files
`app.py` contains Flask routes and response handling; `database.py` initializes SQLite, writes parameterized logs and calculates summaries; `templates/` contains the four pages and shared layout; `static/` contains the styles and browser scripts; `requirements.txt` lists Flask.
