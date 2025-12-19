# LLM 配置指南

本项目支持多个国内外 LLM 提供商，方便国内用户学习使用。

## 支持的 LLM 提供商

### 1. DeepSeek (推荐国内用户)

**优势**：
- 国内访问速度快，无需科学上网
- 价格便宜，性能优秀
- API 兼容 OpenAI 格式

**获取 API Key**：
1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册并登录
3. 在 API Keys 页面创建新的 API Key

**配置示例**：
```bash
# .env 文件
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
```

**定价** (截至 2024年)：
- deepseek-chat: ¥1/百万 tokens (输入), ¥2/百万 tokens (输出)

---

### 2. 通义千问 Qwen (阿里云)

**优势**：
- 阿里云生态，稳定可靠
- 支持多种模型规格
- 国内访问速度快

**获取 API Key**：
1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 开通服务并获取 API Key

**配置示例**：
```bash
# .env 文件
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-plus  # 可选: qwen-turbo, qwen-max, qwen-plus
```

**模型选择**：
- `qwen-turbo`: 速度快，适合简单任务
- `qwen-plus`: 平衡性能和成本
- `qwen-max`: 最强性能，适合复杂任务

---

### 3. OpenAI (可选)

**优势**：
- 性能强大 (GPT-4)
- 生态完善

**注意**：
- 需要科学上网
- 价格相对较高

**配置示例**：
```bash
# .env 文件
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4
```

---

## 快速配置步骤

### 步骤 1: 复制环境变量模板
```bash
cp .env.example .env
```

### 步骤 2: 编辑 .env 文件
选择一个 LLM 提供商，填入对应的 API Key：

```bash
# 使用 DeepSeek (推荐)
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的_api_key

# 或使用 Qwen
LLM_PROVIDER=qwen
QWEN_API_KEY=你的_api_key

# 或使用 OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=你的_api_key
```

### 步骤 3: 测试配置
```bash
python configs/config.py
```

预期输出：
```
=== NL2SQL 配置测试 ===

环境: dev

系统配置:
  系统名称: nl2sql-langgraph
  系统版本: 0.1.0
  日志级别: INFO

LLM 配置:
  提供商: deepseek
  模型: deepseek-chat
  Base URL: https://api.deepseek.com
  API Key 已设置: 是
  Temperature: 0.0
  Max Tokens: 2000
```

---

## 常见问题

### Q1: 如何切换 LLM 提供商？
A: 修改 `.env` 文件中的 `LLM_PROVIDER` 参数即可：
```bash
LLM_PROVIDER=qwen  # 切换到通义千问
```

### Q2: DeepSeek 和 Qwen 哪个更好？
A:
- **DeepSeek**: 性价比高，适合学习和开发
- **Qwen**: 阿里云生态，企业用户推荐

### Q3: M0 模块需要配置 API Key 吗？
A: M0 阶段不需要。M0 只验证基础框架，不调用 LLM。从 M1 开始需要配置 API Key。

### Q4: 如何使用本地 Embedding 模型？
A: 在 M6 模块会详细介绍。简单来说：
```bash
# .env 文件
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 需要安装额外依赖
pip install sentence-transformers torch
```

### Q5: API Key 如何保密？
A:
- `.env` 文件已在 `.gitignore` 中，不会被提交到 git
- 永远不要将 API Key 硬编码到代码中
- 不要将 `.env` 文件分享给他人

---

## Embedding 模型配置 (M6 模块使用)

### 本地 Embedding (推荐国内用户)

使用开源中文 Embedding 模型，无需 API Key：

```bash
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

**常用中文模型**：
- `BAAI/bge-small-zh-v1.5`: 轻量级，适合入门
- `BAAI/bge-base-zh-v1.5`: 平衡性能
- `BAAI/bge-large-zh-v1.5`: 最佳性能

### 云端 Embedding

**Qwen Embedding**：
```bash
EMBEDDING_PROVIDER=qwen
QWEN_API_KEY=你的_api_key
```

**OpenAI Embedding**：
```bash
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=你的_api_key
```

---

## 推荐配置组合

### 组合 1: 全 DeepSeek (性价比最高)
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=xxx
EMBEDDING_PROVIDER=local  # DeepSeek 不提供 embedding
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

### 组合 2: 全 Qwen (阿里云生态)
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=xxx
EMBEDDING_PROVIDER=qwen
```

### 组合 3: DeepSeek + 本地 Embedding (推荐学习)
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=xxx
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

---

## 价格参考 (2024年)

| 提供商 | 模型 | 输入价格 | 输出价格 |
|--------|------|----------|----------|
| DeepSeek | deepseek-chat | ¥1/百万 tokens | ¥2/百万 tokens |
| Qwen | qwen-turbo | ¥0.3/百万 tokens | ¥0.6/百万 tokens |
| Qwen | qwen-plus | ¥4/百万 tokens | ¥12/百万 tokens |
| Qwen | qwen-max | ¥40/百万 tokens | ¥120/百万 tokens |
| OpenAI | gpt-4 | $30/百万 tokens | $60/百万 tokens |

---

## 更多资源

- [DeepSeek 文档](https://platform.deepseek.com/docs)
- [通义千问 文档](https://help.aliyun.com/zh/dashscope/)
- [LangChain 文档](https://python.langchain.com/docs/get_started/introduction)
