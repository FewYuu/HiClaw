# arxiv_collector_worker.py
import os
import sys
import json
import requests
import xml.etree.ElementTree as ET

# 1. 修复路径：改为你本地的项目根目录
project_root = "D:\\HiClaw_Project\\hiclaw-project"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from base_worker import BaseWorker

class ArxivCollectorWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        # 你的新房间 ID
        self.room_id = "!PndehuSLAcQSPWjgUx:localhost"

    def search_papers(self, keyword: str, max_results: int = 10) -> list:
        """搜索 arXiv 论文"""
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{keyword}",
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        response = requests.get(url, params=params)
        
        ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(response.content)
        papers = []
        
        for entry in root.findall('arxiv:entry', ns):
            papers.append({
                "arxiv_id": entry.find('arxiv:id', ns).text.split('/')[-1],
                "title": entry.find('arxiv:title', ns).text.strip().replace('\n', ' '),
                "pdf_url": f"https://arxiv.org/pdf/{entry.find('arxiv:id', ns).text.split('/')[-1]}.pdf"
            })
        return papers
    
    def run(self, task: dict):
        # 获取任务参数
        keyword = task.get("keyword", "machine learning")
        max_results = task.get("max_results", 5)
        task_id = task.get("task_id", "manual_test")
        
        print(f"[*] 正在采集论文: {keyword}...")
        papers = self.search_papers(keyword, max_results)
        
        # --- 修改点：将结果发送到你的 Element 房间展示 ---
        if papers:
            display_text = f"📢 arXiv 采集成功 (关键词: {keyword}):\n\n"
            for p in papers:
                display_text += f"• {p['title']}\n  🔗 {p['pdf_url']}\n\n"
        else:
            display_text = f"❌ 未找到关键词 '{keyword}' 相关的论文。"
            
        # 调用父类的 send_message 发送到你的房间
        self.send_message(self.room_id, display_text)
        
        # --- 保持成员 1 的逻辑：回传给 Manager ---
        # 增加 worker_type 字段以符合第二周任务要求
        result_data = {
            "papers": papers, 
            "keyword": keyword,
            "worker_type": "developer"
        }
        self.send_task_complete(task_id, result_data)
        print(f"[+ DONE] 结果已同步至 Element 房间！")

if __name__ == "__main__":
    worker = ArxivCollectorWorker()
    
    # 为了让你运行脚本就能立刻看到效果，我们手动触发一次
    print("=== 正在执行初次测试任务 ===")
    worker.run({"task_id": "init_test", "keyword": "Artificial Intelligence"})
    
    # 进入常驻监听模式
    worker.listen()