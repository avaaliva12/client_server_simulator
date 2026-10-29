from datetime import datetime, timezone
import time
from flask import Flask, jsonify, render_template, request
from database import get_connection, initialize_database, save_log, summarize_logs

app = Flask(__name__)
initialize_database()
DEVICES = [{"id":1,"name":"Temperature Sensor","status":"online"},{"id":2,"name":"Door Monitor","status":"online"},{"id":3,"name":"Garden Meter","status":"offline"}]

def response_for_request():
    path, method = request.path, request.method
    if path == "/api/hello" and method == "GET": return {"message":"Hello from the Flask server!","application":"Client–Server Simulator"}, 200
    if path == "/api/devices" and method == "GET": return {"devices":DEVICES,"count":len(DEVICES)}, 200
    if path == "/api/status" and method == "GET": return {"available":True,"application":"Client–Server Simulator","server_time":datetime.now(timezone.utc).isoformat()}, 200
    if path == "/api/echo" and method == "POST":
        if not request.is_json: return {"error":"Content-Type must be application/json."}, 400
        data=request.get_json(silent=True)
        if not isinstance(data,dict): return {"error":"Please provide a valid JSON object."}, 400
        return {"message":"Your JSON was received.","received":data}, 201
    if path == "/api/not-found": return {"error":"The requested demo resource was not found.","path":path}, 404
    if path == "/api/server-error": return {"error":"Controlled 500 demonstration. Flask is still running."}, 500
    return {"error":"No demo endpoint matches this path and method.","path":path,"method":method}, 404

@app.before_request
def start_timer(): request.started_at=time.perf_counter()
@app.after_request
def record(response):
    # GET requests use api_get while other verbs use simulate_request.
    # Both are simulator traffic and should appear in SQLite analytics.
    if request.endpoint in {"simulate_request", "api_get"}:
        try: save_log(request.method,request.path,response.status_code,(time.perf_counter()-request.started_at)*1000)
        except Exception: app.logger.exception("Could not save request log")
    return response
@app.get("/")
def dashboard(): return render_template("dashboard.html",stats=summarize_logs())
@app.get("/simulator")
def simulator(): return render_template("simulator.html")
@app.get("/history")
def history():
    method,status,date=request.args.get("method","").upper(),request.args.get("status",""),request.args.get("date","")
    clauses=[]; values=[]
    if method in {"GET","POST","PUT","DELETE"}: clauses.append("method = ?"); values.append(method)
    if status.isdigit(): clauses.append("status_code = ?"); values.append(int(status))
    if date: clauses.append("date(timestamp) = ?"); values.append(date)
    where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
    with get_connection() as conn: logs=conn.execute("SELECT * FROM request_logs"+where+" ORDER BY id DESC LIMIT 500",values).fetchall()
    return render_template("history.html",logs=logs,filters={"method":method,"status":status,"date":date})
@app.get("/server-status")
def server_status(): return render_template("server_status.html",stats=summarize_logs(),server_time=datetime.now().astimezone())
@app.get("/api/stats")
def api_stats(): return jsonify(summarize_logs())
@app.get("/api/<path:demo_path>")
def api_get(demo_path):
    body,status=response_for_request(); return jsonify(body),status
@app.route("/api/<path:demo_path>",methods=["POST","PUT","DELETE","PATCH","OPTIONS"])
def simulate_request(demo_path):
    body,status=response_for_request(); return jsonify(body),status
@app.errorhandler(404)
def missing(error):
    if request.path.startswith("/api/"): return jsonify({"error":"API route not found."}),404
    return render_template("base.html",page_error="Page not found",page_error_detail="Use the navigation bar to return."),404
if __name__ == "__main__": app.run(debug=True)


