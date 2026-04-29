FROM python:3.11-slim
WORKDIR /app

COPY daily-report/requirements.txt .
RUN pip install -r requirements.txt

COPY base_worker.py .
COPY daily-report/daily_report_worker.py .

CMD ["python", "-u", "daily_report_worker.py"]