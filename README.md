# RAG Agent Project

这是一个基于 LangChain、通义千问和 Chroma 的轻量级 RAG Agent 原型。

## 功能

- Streamlit 聊天界面
- LangChain Agent 编排
- Chroma 本地向量库
- 本地知识库检索增强问答
- Mock 工具：天气、用户 ID、当前月份

## 目录

- `app.py`：Streamlit 入口
- `agent/`：Agent 编排与工具
- `rag/`：RAG 服务与向量库
- `model/`：模型工厂
- `utils/`：配置、路径、日志、文件工具
- `config/`：配置文件
- `prompts/`：提示词模板
- `data/`：知识库原始文件目录

## 环境变量

在项目根目录创建 `.env`，配置通义千问 / DashScope 凭证：

```env
DASHSCOPE_API_KEY=your_api_key
```

`.env` 不应提交到 Git。

## 安装

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 运行

```powershell
streamlit run app.py
```

## 知识库

把 `.txt` 或 `.pdf` 文件放入 `data/` 目录。

应用启动时会自动扫描 `data/` 目录并增量写入 Chroma 向量库。已经入库的文件通过 MD5 校验自动跳过；新增或内容发生变化的文件会在下一次启动时处理。

## 验证

```powershell
python -m compileall app.py agent rag model utils
python -c "from agent.react_agent import ReactAgent; ReactAgent(); print('ReactAgent init ok')"
python -c "from rag.rag_service import RagSummarizeService; RagSummarizeService(); print('RAG init ok')"
```

启动 Streamlit 后会自动执行知识库入库：

```powershell
streamlit run app.py
```

## 开发规范

开发前请先阅读 `AGENTS.md`。
