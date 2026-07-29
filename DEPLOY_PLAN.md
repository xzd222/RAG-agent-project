# P0 + P1 上线改造计划

## Context

当前项目核心链路已跑通（Agent → RAG → 模型 → SSE 流式 → React 前端），但从原型到可上线存在安全和稳定性缺口。本计划分 P0（安全）和 P1（部署稳定性）两阶段补齐。

---

## P0 — 安全防护（预计 4 个文件）

### P0-1：CORS 白名单

**文件**：`api.py`  
**现状**：`allow_origins=["*"]`，任意域名可调用  
**改动**：新增环境变量 `ALLOWED_ORIGINS`，默认 `http://localhost:8000`，逗号分隔支持多个

```
# .env
ALLOWED_ORIGINS=http://localhost:8000,https://your-domain.com
```

### P0-2：API Token 认证

**文件**：`api.py`（新增中间件）  
**现状**：无任何认证，任何人访问就消耗 API 额度  
**方案**：简单的 Bearer Token 中间件

```
# .env
API_TOKEN=your-secret-token-change-me
```

- 前端请求自动带 `Authorization: Bearer <token>`
- API 端点校验 token，不匹配返回 401
- 健康检查 `/api/health` 免认证
- 静态页面 `/` 免认证

### P0-3：速率限制

**文件**：`api.py`（新增依赖 `slowapi`）  
**现状**：无限制，可被刷爆  
**改动**：
- 聊天接口 `/api/chat`：每分钟 20 次，每 IP
- 上传接口 `/api/documents/upload`：每分钟 10 次
- 其他接口：每分钟 60 次
- 熔断时返回 429 + "请求过于频繁，请稍后再试"

### P0-4：启动时 API Key 校验 + 延迟模型初始化

**文件**：`model/factory.py`、`api.py`  
**现状**：import 时创建模型实例，无 API Key 直接崩  
**改动**：
- `factory.py`：把模块级单例改为 `get_chat_model()` / `get_embedding_model()` 延迟函数
- `api.py`：启动事件中检查 `DASHSCOPE_API_KEY`，未配置则明确报错退出
- 影响范围：`agent/react_agent.py`、`agent/tools/agent_tools.py`、`rag/rag_service.py`、`rag/vector_store.py` 中 `from model.factory import chat_model` 需改为函数调用

---

## P1 — 部署稳定性（预计 5 个文件）

### P1-1：Docker 容器化

**文件**：`Dockerfile`、`docker-compose.yml`、`.dockerignore`  
**内容**：
- `Dockerfile`：Python 3.13-slim 基础镜像，安装依赖 + 构建前端
- `docker-compose.yml`：后端服务 + 可选 Chroma 独立服务
- `.dockerignore`：排除 venv/、__pycache__/、logs/、chroma_db/、node_modules/

### P1-2：多 Worker 支持

**文件**：`api.py`、`gunicorn_conf.py`  
**改动**：
- `api.py` 末尾改为不硬编码 `uvicorn.run()`
- 新增 `gunicorn_conf.py`：4 workers + UvicornWorker
- 启动命令：`gunicorn -c gunicorn_conf.py api:app`

### P1-3：prompt_loader 异常修复

**文件**：`utils/prompt_loader.py`  
**现状**：错误时返回 KeyError/Exception 对象，调用方当字符串用  
**改动**：不再返回异常对象，改为 `raise RuntimeError("明确错误信息")`，让调用方在初始化时直接失败，而非静默传异常对象

### P1-4：数据库迁移提示

**文件**：`rag/vector_store.py`  
**现状**：Chroma SQLite 单文件，多 worker 冲突  
**方案**：不改代码，在 README 和启动日志中明确标注：
- 单机部署：1 worker（默认），Chroma SQLite 正常工作
- 多 worker：需额外配置 Chroma Server 或切换云向量库
- 并发可通过 `gunicorn -w 1` + 多个 docker 实例水平扩展

### P1-5：健康探针增强

**文件**：`api.py`  
**改动**：`/api/health` 返回更详细信息：
```
{"status": "ok", "model": "qwen-max", "chroma": "connected", "documents": 3}
```

---

## 文件变更汇总

| 阶段 | 文件 | 操作 |
|------|------|------|
| P0 | `api.py` | 修改：CORS 白名单 + token 中间件 + 速率限制 + 启动校验 |
| P0 | `model/factory.py` | 修改：延迟初始化函数 |
| P0 | `agent/react_agent.py` | 修改：`from factory import get_chat_model` |
| P0 | `rag/rag_service.py` | 修改：同上 |
| P0 | `rag/vector_store.py` | 修改：`from factory import get_embedding_model` |
| P0 | `.env` | 修改：新增 `API_TOKEN`、`ALLOWED_ORIGINS` |
| P1 | `Dockerfile` | 新建 |
| P1 | `docker-compose.yml` | 新建 |
| P1 | `.dockerignore` | 新建 |
| P1 | `gunicorn_conf.py` | 新建 |
| P1 | `utils/prompt_loader.py` | 修改：异常时 raise 而非 return |
| P1 | `requirements.txt` | 修改：新增 `slowapi`、`gunicorn`、`uvicorn[standard]` |
| P1 | `api.py` | 修改：增强 health 端点 |
| P1 | `README.md` | 修改：部署说明 |

## 验证方式

```powershell
# P0 验证
# 1. 无 token 访问 → 401
curl http://localhost:8000/api/health          # 200 (免认证)
curl -X POST http://localhost:8000/api/chat \  # 401
  -H "Content-Type: application/json" \
  -d '{"query":"hi"}'

# 2. 带 token 访问 → 200
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer test-token-123" \
  -H "Content-Type: application/json" \
  -d '{"query":"hi"}'

# 3. 速率限制 → 429
for i in {1..25}; do curl ... ; done

# P1 验证
docker compose up --build   # 一键启动
docker compose ps           # 确认运行
curl localhost:8000/api/health
```
