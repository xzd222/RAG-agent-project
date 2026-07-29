# RAG Agent Project

基于 LangChain、通义千问和 Chroma 的轻量级 RAG Agent 原型，提供本地知识库增强的智能问答能力。

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Agent 框架 | LangChain | 1.3.11 |
| 大语言模型 | 通义千问 (DashScope) | qwen-max |
| 嵌入模型 | DashScope Embeddings | text-embedding-v4 |
| 向量数据库 | Chroma | 1.5.9 |
| 前端界面 | Streamlit | 1.49.0 |

## 功能

- **Streamlit 聊天界面**：简洁的对话式交互
- **LangChain Agent**：ReAct 模式编排，支持工具调用
- **Chroma 本地向量库**：持久化存储，支持增量入库
- **本地知识库检索增强问答**：基于 txt/pdf 文档的 RAG
- **Mock 工具集**：天气、用户 ID、当前月份
- **流式输出**：实时展示 AI 回答

## 目录结构

```
.
├── app.py                  # Streamlit 入口
├── agent/                  # Agent 编排与工具
│   ├── react_agent.py      # ReAct Agent
│   └── tools/
│       └── agent_tools.py  # 工具定义
├── rag/                    # RAG 服务与向量库
│   ├── rag_service.py      # RAG 检索回答
│   └── vector_store.py     # Chroma 向量库
├── model/                  # 模型工厂
│   └── factory.py          # ChatModel / Embedding 工厂
├── utils/                  # 通用工具
│   ├── config_handler.py   # 配置加载
│   ├── file_handler.py     # 文件处理 (MD5/PDF/TXT)
│   ├── logger_handler.py   # 日志
│   ├── path_tool.py        # 路径工具
│   └── prompt_loader.py    # 提示词加载
├── config/                 # 配置文件
│   ├── agent.yml           # 模型配置
│   ├── chroma.yml          # 向量库/切片配置
│   ├── prompts.yml         # 提示词路径
│   └── rag.yml             # RAG 配置
├── prompts/                # 提示词模板
│   ├── main_prompt.txt     # 系统提示词
│   ├── rag_summarize.txt   # RAG 总结提示词
│   └── report_prompt.txt   # 报告提示词
└── data/                   # 知识库文件目录
```

## 快速开始

### 1. 环境准备

```powershell
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key
```

> 前往 [阿里云 DashScope](https://dashscope.aliyun.com/) 获取 API Key。

### 3. 添加知识库文件

将 `.txt` 或 `.pdf` 文件放入 `data/` 目录。应用启动时会自动扫描并入库。

### 4. 启动应用

```powershell
streamlit run app.py
```

浏览器打开 `http://localhost:8501` 即可使用。

## 运行验证

```powershell
# 语法检查
python -m compileall app.py agent rag model utils

# Agent 初始化检查
python -c "from agent.react_agent import ReactAgent; ReactAgent(); print('ReactAgent init ok')"

# RAG 初始化检查
python -c "from rag.rag_service import RagSummarizeService; RagSummarizeService(); print('RAG init ok')"
```

## 配置说明

| 文件 | 用途 |
|------|------|
| `config/agent.yml` | 对话模型名称 (`chat_model_name`)、嵌入模型名称 (`embedding_model_name`) |
| `config/chroma.yml` | 向量库路径、top-k、切片大小/重叠、知识库文件类型 |
| `config/prompts.yml` | 各提示词模板文件路径 |

## 知识库管理

- 支持格式：`.txt`、`.pdf`
- 文件通过 MD5 校验去重，已入库文件不会重复处理
- 内容变更后（MD5 变化）会在下次启动时重新入库
- 向量库持久化存储在 `chroma_db/` 目录（不提交至 Git）

## 开发

开发前请阅读本地 `AGENTS.md`（不包含在仓库中）。

## License

MIT
