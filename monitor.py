import argparse
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone

DB_FILE = "monitoring.db"
LOG_FILE = "sample_logs.txt"
ENDPOINTS = [
    "https://google.com",
    "https://httpbin.org"
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        source TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        details TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def log_incident(conn, source, incident_type, details):
    timestamp = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO incidents (timestamp, source, incident_type, details) VALUES (?, ?, ?, ?)",
        (timestamp, source, incident_type, details)
    )
    conn.commit()
    print(f"[ALERT] {timestamp} | {source} | {incident_type}: {details}")

def analyze_logs(conn, filepath, threshold=2):
    error_streaks ={}
    flagged = set()

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            _, service, status, code = parts[0], parts[1], parts[2], parts[3]

            if status == "ERROR":
                error_streaks[service] = error_streaks.get(service, 0) + 1
                if error_streaks[service] >= threshold and service not in flagged:
                    flagged.add(service)
                    log_incident(
                        conn,
                        service,
                        "CONSECUTIVE_LOG_ERRORS",
                        f"Detected {error_streaks[service]} consecutive errors (latest HTTP {code})"
                    )
            else:
                error_streaks[service] = 0

def check_endpoints(conn, urls):
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                print(f"[HEALTHY] {url} -> HTTP {response.status}")
        except urllib.error.HTTPError as err:
            log_incident(conn, url, "ENDPOINT_DOWN", f"Return HTTP {err.code}")
        except Exception as err:
            log_incident(conn, url, "CONNECTION_FAILED", str(err))

def show_report(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, source, incident_type, details FROM incidents ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    print("\n=== Recent Incidents Report ===")
    if not rows:
        print("No incidents to show.")
    for row in rows:
        print(f"#:{row[0]} | {row[1]} | {row[2]} | [{row[3]}]: {row[4]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server Health Monitor")
    parser.add_argument("--report", action="store_true", help="Show incident report")
    args = parser.parse_args()

    conn = init_db()
    try:
        if args.report:
            show_report(conn)
        else:
            print("\n=== Starting Health Checks ===")
            analyze_logs(conn, LOG_FILE, threshold=2)
            check_endpoints(conn, ENDPOINTS)
            print("=== Checks Completed. Run 'python3 monitor.py --report' to view a summary. ===\n")
    finally:
        conn.close()