FROM python:3.11-slim
WORKDIR /app

# 复制依赖文件
COPY github-collector/requirements.txt .
RUN pip install -r requirements.txt

# 复制代码（base_worker.py 在父目录）
COPY base_worker.py .
COPY github-collector/github_collector_worker.py .

CMD ["python", "github_collector_worker.py"]