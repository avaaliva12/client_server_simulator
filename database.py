from pathlib import Path
import sqlite3
DB_PATH=Path(__file__).with_name("request_logs.db")
def get_connection():
    connection=sqlite3.connect(DB_PATH); connection.row_factory=sqlite3.Row; return connection
def initialize_database():
    with get_connection() as conn: conn.execute("CREATE TABLE IF NOT EXISTS request_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, method TEXT NOT NULL, endpoint TEXT NOT NULL, status_code INTEGER NOT NULL, response_time_ms REAL NOT NULL, success INTEGER NOT NULL, timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
def save_log(method,endpoint,status_code,response_time_ms):
    with get_connection() as conn: conn.execute("INSERT INTO request_logs (method,endpoint,status_code,response_time_ms,success) VALUES (?,?,?,?,?)",(method,endpoint,status_code,round(response_time_ms,2),int(200<=status_code<400)))
def summarize_logs():
    with get_connection() as conn:
        totals=conn.execute("SELECT COUNT(*) total, COALESCE(SUM(success),0) successful, COUNT(*)-COALESCE(SUM(success),0) failed, COALESCE(AVG(response_time_ms),0) average_ms FROM request_logs").fetchone()
        recent=conn.execute("SELECT id,method,endpoint,status_code,response_time_ms,success,timestamp FROM request_logs ORDER BY id DESC LIMIT 20").fetchall()
        cats=conn.execute("SELECT CASE WHEN status_code<300 THEN '2xx' WHEN status_code<400 THEN '3xx' WHEN status_code<500 THEN '4xx' ELSE '5xx' END category, COUNT(*) count FROM request_logs GROUP BY category").fetchall()
    return {"total":totals["total"],"successful":totals["successful"],"failed":totals["failed"],"average_ms":round(totals["average_ms"],2),"recent":[dict(r) for r in recent],"categories":{r["category"]:r["count"] for r in cats}}
