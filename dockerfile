FROM python:3.11-slim
WORKDIR /app
COPY monitor.py sample_logs.txt ./
CMD ["python", "monitor.py"]