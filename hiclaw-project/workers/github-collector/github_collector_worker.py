# github_collector_worker.py
import os
import sys
import json
import requests

# 1. 修复路径：改为你本地的项目根目录（和 Arxiv 脚本保持一致）
project_root = "D:\\HiClaw_Project\\hiclaw-project"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from base_worker import BaseWorker

class GitHubCollectorWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        # 同 Arxiv 脚本的房间 ID（或根据需求修改为指定 Room）
        self.room_id = "!CeUycuSgzOBLlMrqsw:localhost"
        # GitHub API 基础地址
        self.github_api_url = "https://api.github.com/search/repositories"
        # 可选：添加 GitHub Token（避免 API 调用限流，需自行替换为真实 Token）
        self.github_token = os.getenv("GITHUB_TOKEN", "")  # 推荐通过环境变量配置
        self.worker_type = "developer"

    def join_room(self):
        homeserver = os.getenv("MATRIX_HOMESERVER")
        token = os.getenv("MATRIX_ACCESS_TOKEN")

        url = f"{homeserver}/_matrix/client/r0/join/{self.room_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            res = requests.post(url, headers=headers)
            print(f"[JOIN] status: {res.status_code}, response: {res.text}")
        except Exception as e:
            print(f"[JOIN ERROR] {e}")       
    def search_repos(self, keyword: str, max_results: int = 10) -> list:
        """搜索 GitHub 仓库，按 Star 数降序排序"""
        # 构建请求头（带 Token 避免限流）
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        # GitHub API 参数：按关键词搜索、按星数排序、返回指定数量
        params = {
            "q": keyword,
            "sort": "stars",       # 按 Star 数排序（热度核心指标）
            "order": "desc",       # 降序（星数越高越靠前）
            "per_page": max_results
        }

        try:
            response = requests.get(self.github_api_url, headers=headers, params=params)
            response.raise_for_status()  # 触发 HTTP 错误异常
            repos_data = response.json()
            
            # 解析并封装仓库信息
            repos = []
            for item in repos_data.get("items", []):
                repos.append({
                    "repo_name": item["full_name"],  # 仓库全名（作者/仓库名）
                    "title": item["name"],           # 仓库短名称
                    "description": item["description"].strip().replace("\n", " ") if item["description"] else "无描述",
                    "stars": item["stargazers_count"],  # Star 数
                    "html_url": item["html_url"],       # 仓库链接
                    "language": item["language"] or "未知"  # 开发语言
                })
            return repos
        except requests.exceptions.RequestException as e:
            print(f"[!] GitHub API 请求失败: {e}")
            return []

    def run(self, task: dict):
    # =========================
    # 1. 关键词统一（修复）
    # =========================
        keywords = task.get("keywords")
        if not keywords:
            keywords = [task.get("keyword", "LLM")]

        max_results = task.get("max_results", 5)
        task_id = task.get("task_id", "manual_test")

        print(f"[*] 正在采集 GitHub 项目: {keywords}...")

        all_repos = []
    # =========================
    # 2. 去重容器（核心）
    # =========================
        seen = set()

        for kw in keywords:
            repos = self.search_repos(kw, max_results)

            for r in repos:
                repo_id = r["html_url"]
            # 去重
                if repo_id in seen:
                    continue

                seen.add(repo_id)

                r["keyword"] = kw
                all_repos.append(r)
    # =========================
    # 3. 人类可读输出（Element）
    # =========================
        if all_repos:
            display_text = f"📢 GitHub 采集成功 ({', '.join(keywords)})\n\n"

            for repo in all_repos:
                display_text += (
                    f"🔥 {repo['repo_name']} (⭐ {repo['stars']})\n"
                    f"📝 {repo['description']}\n"
                    f"🔗 {repo['html_url']}\n"
                    f"💻 {repo['language']}\n"
                    f"🏷 keyword: {repo['keyword']}\n\n"
                )
        else:
            display_text = "❌ 未找到任何项目"
    # 👉 人类视图（必须保留）
        self.send_message(self.room_id, display_text)
    # =========================
    # 4. 机器结构输出（Manager）
    # =========================
        result_data = {
            "type": "github_result",
            "worker_type": "developer",
            "keywords": keywords,
            "repos": all_repos
        }

        self.send_task_complete(task_id, result_data)

        print("[+ DONE] 完成")

if __name__ == "__main__":
    worker = GitHubCollectorWorker()
    
    worker.join_room()
    # 手动触发测试（关键词可替换为 Agent、LLM 等）
    print("=== 正在执行 GitHub 初次测试任务 ===")
    worker.run({"task_id": "init_test", "keyword": "Agent"})
    
    # 进入常驻监听模式
    worker.listen()