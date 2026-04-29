# daily_report_worker.py
import os
import sys
import json
from datetime import datetime

sys.path.append('/app')
from base_worker import BaseWorker

class DailyReportWorker(BaseWorker):
    def generate_report(self, github_results: list, arxiv_results: list) -> str:
        """生成日报 Markdown"""
        report = f"""# 📊 HiClaw 技术日报

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔥 热门 GitHub 仓库

"""
        for repo in github_results[:5]:
            report += f"""### 📦 {repo['name']}
- ⭐ Stars: {repo['stars']} | 🍴 Forks: {repo['forks']}
- 📝 {repo['description'] or '无描述'}

"""

        report += f"""## 📄 最新 arXiv 论文

"""
        for paper in arxiv_results[:5]:
            report += f"""### 📖 {paper['title']}
- 👤 作者: {', '.join(paper['authors'][:3])}
- 📅 发布日期: {paper['published'][:10]}

---

"""
        return report
    
    def run(self, task: dict):
        github_results = task.get("github_results", [])
        arxiv_results = task.get("arxiv_results", [])
        report = self.generate_report(github_results, arxiv_results)
        
        target_room = task.get("target_room", self.manager_room)
        self.send_message(target_room, report, "m.text")

if __name__ == "__main__":
    worker = DailyReportWorker()
    worker.listen()  # 常驻模式