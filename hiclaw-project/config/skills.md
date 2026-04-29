# Manager 调度规则

## Worker 路由表

| 任务类型 | 关键词 | 目标 Worker |
|----------|--------|-------------|
| GitHub 采集 | repo, repository, github, 仓库 | github-collector |
| arXiv 采集 | arxiv, paper, 论文, 学术 | arxiv-collector |
| 日报生成 | report, 日报, daily | daily-report |

## 调度优先级
1. github-collector 和 arxiv-collector 可并行执行
2. daily-report 等待采集完成后执行