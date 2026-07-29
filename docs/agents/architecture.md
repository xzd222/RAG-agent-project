# 目录架构与调用规则

---

## 完整目录树

```
├── app.py                 UI 入口：交互、流式展示、调用 Agent
├── agent/                 编排层：模型/提示词/工具组装
│   └── tools/             工具定义：业务能力 → LangChain Tool
├── rag/                   RAG 层：向量库、检索、上下文拼接、回答生成
├── model/                 模型工厂：ChatModel + EmbeddingModel 创建
├── utils/                 通用工具：配置、路径、日志、文件/提示词加载
├── config/                非敏感配置 (agent.yml / rag.yml / chroma.yml / prompts.yml)
├── prompts/               提示词模板
├── data/                  知识库原始文件（按需创建）
├── chroma_db/             Chroma 持久化（不提交）
├── logs/                  运行日志（不提交）
├── tests/                 测试用例
├── venv/                  虚拟环境（不提交）
├── requirements.txt       依赖清单
└── .env                   敏感信息（不提交）
```

---

## 层级调用规则

```
app.py (UI)
  └── agent/ (编排)
        ├── model/ (模型)
        ├── prompts/ (提示词)
        ├── agent/tools/ (工具)
        │     └── rag/ (检索 —— 仅工具层可调用)
        └── utils/ (通用能力 —— 各层均可调用)
```

### 原则

- **依赖方向**：上层 → 下层，单向
- **禁止跨层**：UI 不得直接操作向量库；Agent 不直接读取原始文档
- **职责单一**：每层只做自己的事

### 各层主要职责

| 层 | 做 | 不做 |
|----|-----|------|
| `app.py` | 输入框、流式展示、错误提示、来源引用 | 切片、向量库操作、工具逻辑、模型初始化 |
| `agent/` | 组装模型 + 提示词 + 工具 | 文档解析、向量入库、UI 展示 |
| `rag/` | 文档加载、切片、入库、检索问答 | 模型创建、工具定义 |
| `model/` | 创建 ChatModel / EmbeddingModel | 配置读取逻辑 |
| `utils/` | 配置、路径、日志、文件加载 | 业务逻辑 |
