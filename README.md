# Automated Server & Endpoint Health Monitor

A lightweight Python infrastructure monitoring tool  built in a Linux (WSL) environment that parses service logs for consecutive failure streaks, probes live HTTP endpoints, and stores incident alerts in a relational SQLite database.

## Features
- **Log streak Analysis:** Tracks consecutive 'ERROR' events per service and triggers alerts when failure thresholds are breached.
- **Live HTTP Endpoint Checks:** Monitors service availability with timeout handling and HTTP status validation.
- **SQL Incident Persistence & CLI Reporting:** Logs timestamped alerts to SQLite and queries recent history via '--report'.
- **Container-Ready:** Includes a lightweight 'Dockerfile' for isolated Linux deployment.

## Usage
Run a health check:
```bash
python3 monitor.py
```

View the 10 most recent logged incidents:
```bash
python3 monitor.py --report
```