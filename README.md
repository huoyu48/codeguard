# CodeGuard - AI 代码审查自动化平台

面向开发团队的 AI 代码审查平台，通过 GitHub Webhook 自动监听代码提交事件，触发 AI Agent 对代码变更进行多维度审查，并将审查结果以结构化评论自动回写到 Pull Request。

## 技术栈

- **后端框架**: FastAPI
- **Agent 编排**: LangChain + LangGraph
- **任务队列**: Celery + Redis
- **向量数据库**: ChromaDB (RAG 知识库)
- **持久化**: PostgreSQL
- **监控**: Prometheus + Grafana
- **部署**: Docker Compose

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/huoyu48/codeguard.git
cd codeguard

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 3. 启动服务
docker-compose up --build
```

## 项目结构

```
codeguard/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── api/                 # 路由层 (Webhook, Reviews, Auth)
│   ├── agent/               # LangGraph 多 Agent 审查流水线
│   ├── tasks/               # Celery 异步任务
│   ├── services/            # 业务逻辑层
│   ├── models/              # 数据模型
│   └── middleware/           # 中间件 (限流/熔断/日志)
├── tests/                   # 测试
├── monitoring/              # Prometheus + Grafana
├── docs/                    # 文档
└── docker-compose.yml       # 容器编排
```

## License

MIT
