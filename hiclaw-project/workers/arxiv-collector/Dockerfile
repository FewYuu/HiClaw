FROM python:3.11-slim
WORKDIR /app

COPY arxiv-collector/requirements.txt .
RUN pip install -r requirements.txt

COPY base_worker.py .
COPY arxiv-collector/arxiv_collector_worker.py .

CMD ["python", "-u", "arxiv_collector_worker.py"]