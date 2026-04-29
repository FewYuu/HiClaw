# HiClaw Project

项目简介
本项目基于 HiClaw 框架，实现一个多 Agent 数据采集系统。
通过 Worker-Manager 架构，从 GitHub 和 arXiv 获取数据，并通过 Matrix 进行消息通信与展示。

功能说明
GitHub 数据采集
arXiv 论文采集
多 Worker 协同运行
基于 Matrix 的消息通信
前端展示数据结果

项目结构
workers/        当前使用的 Worker
legacy/         早期版本代码
config/         配置文件示例
docs/           实验相关文档
docker-compose.yml

运行方法
1. 启动系统服务
docker-compose up -d
2. 配置环境变量
复制配置文件并填写：
cp config/example.env .env
3. 运行 Worker
python workers/github_collector_worker.py
python workers/arxiv_collector_worker.py

技术栈
Python
Docker
Matrix
HiClaw

说明
本项目为课程实验项目，仅用于学习与演示。
