# RAG Agent Project

基于 LangChain、通义千问和 Chroma 的轻量级 RAG Agent 原型，提供本地知识库增强的智能问答能力。

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Agent 框架 | LangChain | 1.3.11 |
| 大语言模型 | 通义千问 (DashScope) | qwen-max |
| 嵌入模型 | DashScope Embeddings | text-embedding-v4 |
| 向量数据库 | Chroma | 1.5.9 |
| 前端界面 | React + TypeScript + Tailwind CSS | 18 / Vite |
| 后端服务 | FastAPI + Uvicorn | 0.138 / 0.49 |
| 知识库管理 | Streamlit | 1.49.0 |

## 功能

- **React 聊天界面**：现代渐变 UI，带头像气泡、打字动画
- **LangChain Agent**：ReAct 模式编排，支持工具调用与 SSE 流式输出
- **Chroma 本地向量库**：持久化存储，MD5 增量入库
- **本地知识库检索增强问答**：基于 txt/pdf 文档的 RAG
- **Mock 工具集**：天气、用户 ID、当前月份
- **知识库管理页**：Streamlit 页面，上传/预览/删除/入库状态
- **一键启动**：FastAPI 直接托管前端静态文件，无需多终端

## 目录结构

```
.
├── api.py                     # FastAPI 后端入口（含静态文件托管）
├── manage.py                  # Streamlit 知识库管理页面
├── app.py                     # Streamlit 调试入口（保留）
├── agent/                     # Agent 编排与工具
│   ├── react_agent.py         # ReAct Agent（SSE 流式）
│   └── tools/
│       └── agent_tools.py     # 工具定义
├── rag/                       # RAG 服务与向量库
│   ├── rag_service.py         # RAG 检索回答
│   └── vector_store.py        # Chroma 向量库
├── model/                     # 模型工厂
│   └── factory.py             # ChatModel / Embedding 工厂
├── utils/                     # 通用工具
│   ├── config_handler.py      # 配置加载
│   ├── file_handler.py        # 文件处理 (MD5/PDF/TXT)
│   ├── logger_handler.py      # 日志
│   ├── path_tool.py           # 路径工具
│   └── prompt_loader.py       # 提示词加载
├── config/                    # 配置文件
│   ├── agent.yml              # 模型配置
│   ├── chroma.yml             # 向量库/切片配置
│   ├── prompts.yml            # 提示词路径
│   └── rag.yml                # RAG 配置
├── prompts/                   # 提示词模板
│   ├── main_prompt.txt        # 系统提示词
│   ├── rag_summarize.txt      # RAG 总结提示词
│   └── report_prompt.txt      # 报告提示词
├── frontend/                  # React 前端项目
│   ├── src/
│   │   ├── App.tsx            # 主聊天界面
│   │   ├── api/chat.ts        # SSE 流式 API 封装
│   │   └── components/        # UI 组件
│   ├── vite.config.ts
│   └── package.json
├── data/                      # 知识库文件目录
└── test_api.py                # API 端点测试脚本
```

## 快速开始

### 1. 环境准备

```powershell
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖 + 构建
cd frontend
npm install
npm run build
cd ..
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key
```

> 前往 [阿里云 DashScope](https://dashscope.aliyun.com/) 获取 API Key。

### 3. 添加知识库文件（可选）

将 `.txt` 或 `.pdf` 文件放入 `data/` 目录。启动时自动扫描并入库。

### 4. 启动应用

```powershell
# 一键启动：后端 + 前端页面
uvicorn api:app --port 8000
```

浏览器打开 `http://localhost:8000` 即可使用聊天界面。

### 5. 知识库管理页（按需）

```powershell
streamlit run manage.py --server.port 8502
```

打开 `http://localhost:8502` 上传、预览、管理知识库文档。

## 运行验证

```powershell
# 语法检查
python -m compileall api.py app.py manage.py agent rag model utils

# API 端点测试
python test_api.py

# Agent 初始化检查
python -c "from agent.react_agent import ReactAgent; ReactAgent(); print('ReactAgent init ok')"

# RAG 初始化检查
python -c "from rag.rag_service import RagSummarizeService; RagSummarizeService(); print('RAG init ok')"
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端聊天页面 |
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | SSE 流式聊天 |
| `/api/documents` | GET | 文档列表（含预览） |
| `/api/documents/upload` | POST | 上传文档并入库 |
| `/api/documents/{name}` | DELETE | 删除文档 |
| `/api/documents/reingest` | POST | 重新扫描入库 |

## 配置说明

| 文件 | 用途 |
|------|------|
| `config/agent.yml` | 对话模型名称、嵌入模型名称 |
| `config/chroma.yml` | 向量库路径、top-k、切片参数、文件类型 |
| `config/prompts.yml` | 各提示词模板文件路径 |

## 知识库管理

- 支持格式：`.txt`、`.pdf`
- 文件通过 MD5 校验去重，已入库文件不会重复处理
- 内容变更后（MD5 变化）在下次入库时自动更新
- 管理页可查看文件前 200 字预览
- 向量库持久化存储在 `chroma_db/` 目录（不提交至 Git）

## 开发

开发前请阅读本地 `AGENTS.md`（不包含在仓库中）。

## License

MIT
