import os
import sys
import json
import requests

sys.path.append('/app')
from base_worker import BaseWorker

class GitHubCollectorWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.github_token = os.environ.get('GITHUB_TOKEN')
    
    def collect_repo(self, repo_url: str) -> dict:
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        return {
            "repo_url": repo_url,
            "name": data.get("full_name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "language": data.get("language"),
            "collected_at": data.get("pushed_at")
        }
    
    def run(self, task: dict):
        repo_url = task.get("repo_url")
        print(f"开始采集: {repo_url}")
        result = self.collect_repo(repo_url)
        self.send_task_complete(task.get("task_id"), result)
        print(f"采集完成: {result.get('name')}")

if __name__ == "__main__":
    worker = GitHubCollectorWorker()
    worker.listen()  # 常驻模式