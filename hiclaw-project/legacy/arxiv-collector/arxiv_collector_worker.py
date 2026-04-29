# arxiv_collector_worker.py
import os
import sys
import json
import requests
import xml.etree.ElementTree as ET

sys.path.append('/app')
from base_worker import BaseWorker

class ArxivCollectorWorker(BaseWorker):
    def search_papers(self, keyword: str, max_results: int = 10) -> list:
        """搜索 arXiv 论文"""
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{keyword}",
            "start": 0,
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
                "authors": [a.find('arxiv:name', ns).text for a in entry.findall('arxiv:author', ns)],
                "abstract": entry.find('arxiv:summary', ns).text.strip().replace('\n', ' '),
                "published": entry.find('arxiv:published', ns).text,
                "pdf_url": f"https://arxiv.org/pdf/{entry.find('arxiv:id', ns).text.split('/')[-1]}.pdf"
            })
        
        return papers
    
    def run(self, task: dict):
        keyword = task.get("keyword", "machine learning")
        max_results = task.get("max_results", 10)
        papers = self.search_papers(keyword, max_results)
        self.send_task_complete(task.get("task_id"), {"papers": papers, "keyword": keyword})

if __name__ == "__main__":
    worker = ArxivCollectorWorker()
    worker.listen()  # 常驻模式