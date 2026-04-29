# GitHubCollectorWorker / Worker 配置说明文档

本文档用于说明如何配置并运行 Worker（GitHubCollectorWorker），该 Worker 基于 Matrix + GitHub API 实现数据采集与消息分发。

---

# 一、环境变量配置

运行 Worker 前，需要配置以下环境变量。

---

## 1. MATRIX ACCESS TOKEN（必须）

### ✔ 获取方式（Element）

1. 打开 Element（Matrix 客户端）
2. 登录你的账号
3. 进入 Settings（设置）
4. 找到：
   Help & About → Access Token
5. 复制 Access Token

---

### ⚠️ 注意

- Token 等同于密码，请不要泄露
- 每个用户 Token 唯一
- 如果 Token 错误，Worker 无法发送消息

---

## 2. MATRIX HOMESERVER

用于连接 Matrix 服务端。

### ✔ 示例

MATRIX_HOMESERVER=http://localhost:8008

如果使用 Docker 环境：

MATRIX_HOMESERVER=http://synapse:8008

---

## 3. ROOM ID（房间 ID）

### ✔ 获取方法

1. 打开 Element
2. 进入目标房间
3. 点击房间设置
4. 找到 Room ID

---

### ✔ 示例

!CeUycuSgzOBLlMrqsw:localhost

---

## 4. Worker 配置示例（环境变量）

export MATRIX_ACCESS_TOKEN=your_token_here  
export MATRIX_HOMESERVER=http://localhost:8008  
export MANAGER_ROOM=!CeUycuSgzOBLlMrqsw:localhost  
export HICLAW_WORKER_NAME=github-collector  

---

# 二、GitHubCollectorWorker 说明

GitHubCollectorWorker 是一个数据采集 Worker，主要功能：

- 调用 GitHub API
- 根据关键词（LLM / Agent / RAG）搜索热门仓库
- 按 Star 数排序
- 去重处理（防止重复刷屏）
- 输出两种结果：
  - 人类可读消息（Element 房间）
  - 结构化 JSON（Manager 系统）

---

# 三、Python 环境依赖

requirements.txt 内容如下：

requests==2.31.0

---

# 四、运行方式

## 1. 本地运行

python github_collector_worker.py

---

## 2. Docker 运行（推荐）

docker-compose up -d

---

# 五、系统架构说明

GitHub API  
   ↓  
GitHubCollectorWorker  
   ↓  
去重处理（Dedup）  
   ↓  
├── Element（人类可读输出）  
└── Manager（结构化 JSON）

---

# 六、常见问题（FAQ）

## ❌ 403 Forbidden（GitHub API）

原因：
- 没有 GitHub Token
- API rate limit 超限

解决：
- 配置 GITHUB_TOKEN
- 或降低请求频率

---

## ❌ Matrix 无法发送消息

检查：
- MATRIX_ACCESS_TOKEN 是否正确
- MATRIX_HOMESERVER 是否正确
- Room ID 是否正确
- Worker 是否已 join 房间

---

## ❌ Worker 无输出

检查：
- 是否正确启动 listen loop
- 是否有 task 输入
- 是否运行 run() 方法

---

# 七、总结

GitHubCollectorWorker 是一个：

✔ 可扩展  
✔ 可去重  
✔ 支持多关键词  
✔ 支持 Matrix 消息分发  
✔ 可用于 AI Agent 系统基础组件