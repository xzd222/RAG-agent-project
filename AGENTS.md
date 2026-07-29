# AGENTS.md

> 本文件是 AI Agent 开发规则的**入口索引**。详情按需展开到 `docs/agents/`。

---

## 一句话原则

> **配置驱动、职责单一、诚实输出、异常不吞、安全第一。**

---

## 架构速览

```
app.py                 UI 入口
  └── agent/           编排层
        ├── model/      模型工厂
        ├── agent/tools/ 工具定义
        │     └── rag/   RAG 检索
        ├── prompts/    提示词
        └── utils/      通用能力
config/               非敏感 YAML
data/                 知识库文件
tests/                测试
```

**调用链**：`app.py → agent/ → {model/, tools/, prompts/} → utils/`  
**禁止**：UI 碰向量库 · Agent 读原始文档 · 跨层调用

---

## 硬边界速查

- 🔑 密钥只存 `.env`
- 🚫 禁止裸 `except:` · 禁止 `print()` 替代日志
- 🛡️ 禁止 shell 拼接用户输入 · 禁止自主破坏性操作
- 📝 UTF-8 统一 · import 不做重初始化
- 🤥 工具不造假 (Mock 必标注) · RAG 不足必拒答
- 📂 不提交：`.env` `venv/` `chroma_db/` `logs/` `__pycache__/`

---

## 规则索引

| 需要了解 | 读这里 |
|----------|--------|
| 完整硬边界 + 安全规则 | [`docs/agents/hard-boundaries.md`](docs/agents/hard-boundaries.md) |
| 目录结构与调用规则 | [`docs/agents/architecture.md`](docs/agents/architecture.md) |
| 编码规范 + 异常处理 | [`docs/agents/coding-standards.md`](docs/agents/coding-standards.md) |
| 配置文件职责与约束 | [`docs/agents/configuration.md`](docs/agents/configuration.md) |
| Agent / Tool / RAG / Prompt / UI 详细规范 | [`docs/agents/modules.md`](docs/agents/modules.md) |
| 日志规范 | [`docs/agents/logging.md`](docs/agents/logging.md) |
| 测试要求 | [`docs/agents/testing.md`](docs/agents/testing.md) |
| Git 操作规则 | [`docs/agents/git-rules.md`](docs/agents/git-rules.md) |
| 交付标准 + 开发流程 | [`docs/agents/delivery.md`](docs/agents/delivery.md) |
